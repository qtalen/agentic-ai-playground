from __future__ import annotations

import asyncio
import logging
import tempfile
import uuid
from concurrent.futures import Future as ConcurrentFuture
from hashlib import sha256
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union

import docker
from docker.errors import DockerException, ImageNotFound, NotFound
from docker.models.containers import Container
from pydantic import BaseModel

from common.utils.code_executor.base import (
    CancellationToken,
    CodeBlock,
    CodeExecutor,
    CommandLineCodeResult,
    get_file_name_from_content,
    lang_to_cmd,
    silence_pip,
)


logger = logging.getLogger(__name__)


class DockerCommandLineCodeExecutorConfig(BaseModel):
    """Configuration for DockerCommandLineCodeExecutor"""

    image: str = "python:3-slim"
    container_name: Optional[str] = None
    timeout: int = 60
    work_dir: Optional[str] = None
    bind_dir: Optional[str] = None
    auto_remove: bool = True
    stop_container: bool = True
    extra_volumes: Dict[str, Dict[str, str]] = {}
    extra_hosts: Dict[str, str] = {}
    init_command: Optional[str] = None
    delete_tmp_files: bool = False
    environment: Dict[str, str] = {}


async def _wait_for_ready(
    container: Container, timeout: int = 60, stop_time: float = 0.1
) -> None:
    """Wait for container to be running."""
    elapsed_time = 0.0
    while container.status != "running" and elapsed_time < timeout:
        await asyncio.sleep(stop_time)
        elapsed_time += stop_time
        await asyncio.to_thread(container.reload)
    if container.status != "running":
        raise ValueError("Container failed to start")


class DockerCommandLineCodeExecutor(CodeExecutor):
    """Executes code through a command line environment in a Docker container.

    The executor first saves each code block in a file in the working
    directory, and then executes the code file in the container.
    The executor executes the code blocks in the order they are received.
    Currently, the executor only supports Python and shell scripts.

    Args:
        image (str, optional): Docker image to use for code execution.
            Defaults to "python:3-slim".
        container_name (Optional[str], optional): Name of the Docker container.
            If None, will autogenerate a name. Defaults to None.
        timeout (int, optional): The timeout for code execution. Defaults to 60.
        work_dir (Union[Path, str], optional): The working directory for code
            execution on the host. Defaults to temporary directory.
        bind_dir (Union[Path, str], optional): The directory that will be bound
            to the container. Defaults to work_dir.
        auto_remove (bool, optional): If true, will automatically remove the Docker
            container when it is stopped. Defaults to True.
        stop_container (bool, optional): If true, will automatically stop the
            container when stop is called or when the context manager exits.
            Defaults to True.
        extra_volumes (Optional[Dict[str, Dict[str, str]]], optional): A dictionary
            of extra volumes to mount. Defaults to None.
        extra_hosts (Optional[Dict[str, str]], optional): A dictionary of host
            mappings to add to the container. Defaults to None.
        init_command (Optional[str], optional): A shell command to run before
            each execution. Defaults to None.
        delete_tmp_files (bool, optional): If true, will delete temporary files
            after execution. Defaults to False.
        environment (Optional[Dict[str, str]], optional): Environment variables
            to pass to the container. Defaults to None.
    """

    SUPPORTED_LANGUAGES: ClassVar[List[str]] = [
        "bash",
        "shell",
        "sh",
        "pwsh",
        "powershell",
        "ps1",
        "python",
    ]

    def __init__(
        self,
        image: str = "python:3-slim",
        container_name: Optional[str] = None,
        *,
        timeout: int = 60,
        work_dir: Union[Path, str, None] = None,
        bind_dir: Union[Path, str, None] = None,
        auto_remove: bool = True,
        stop_container: bool = True,
        extra_volumes: Optional[Dict[str, Dict[str, str]]] = None,
        extra_hosts: Optional[Dict[str, str]] = None,
        init_command: Optional[str] = None,
        delete_tmp_files: bool = False,
        environment: Optional[Dict[str, str]] = None,
    ):
        if timeout < 1:
            raise ValueError("Timeout must be greater than or equal to 1.")

        self._image = image
        self._timeout = timeout
        self._auto_remove = auto_remove
        self._stop_container = stop_container
        self._extra_volumes = extra_volumes if extra_volumes is not None else {}
        self._extra_hosts = extra_hosts if extra_hosts is not None else {}
        self._init_command = init_command
        self._delete_tmp_files = delete_tmp_files
        self._environment = environment if environment is not None else {}

        if container_name is None:
            self._container_name = f"code-exec-{uuid.uuid4()}"
        else:
            self._container_name = container_name

        self._work_dir: Optional[Path] = None
        if work_dir is not None:
            if isinstance(work_dir, str):
                work_dir = Path(work_dir)
            work_dir.mkdir(exist_ok=True, parents=True)
            self._work_dir = work_dir

        self._bind_dir: Optional[Path] = None
        if bind_dir is not None:
            self._bind_dir = Path(bind_dir) if isinstance(bind_dir, str) else bind_dir
        else:
            self._bind_dir = self._work_dir

        self._temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        self._container: Optional[Container] = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._cancellation_futures: List[ConcurrentFuture[None]] = []

    @property
    def timeout(self) -> int:
        """The timeout for code execution."""
        return self._timeout

    @property
    def work_dir(self) -> Path:
        """The working directory for code execution."""
        if self._work_dir is not None:
            return self._work_dir
        if self._temp_dir is not None:
            return Path(self._temp_dir.name)
        raise RuntimeError("Working directory not properly initialized")

    @property
    def bind_dir(self) -> Path:
        """The directory bound to the container."""
        if self._bind_dir is not None:
            return self._bind_dir
        return self.work_dir

    @property
    def container_name(self) -> str:
        """The container name."""
        return self._container_name

    async def _execute_command(
        self, command: List[str], cancellation_token: CancellationToken
    ) -> tuple[str, int]:
        """Execute a command in the container."""
        if self._container is None or not self._running:
            raise ValueError(
                "Container is not running. Must first be started with either start or a context manager."
            )

        exec_task = asyncio.create_task(
            asyncio.to_thread(self._container.exec_run, command)
        )
        cancellation_token.link_future(exec_task)

        try:
            result = await exec_task
            exit_code = result.exit_code
            output = (
                result.output.decode("utf-8")
                if isinstance(result.output, bytes)
                else str(result.output)
            )
            if exit_code == 124:
                output += "\n Timeout"
            return output, exit_code
        except asyncio.CancelledError:
            if self._loop and not self._loop.is_closed():
                try:
                    future: ConcurrentFuture[None] = asyncio.run_coroutine_threadsafe(
                        self._kill_running_command(command), self._loop
                    )
                    self._cancellation_futures.append(future)
                except RuntimeError as e:
                    logger.error(f"Failed to schedule kill command: {e}")
            return "Code execution was cancelled.", 1

    async def _kill_running_command(self, command: List[str]) -> None:
        """Kill a running command in the container."""
        if self._container is None or not self._running:
            return
        try:
            await asyncio.to_thread(
                self._container.exec_run, ["pkill", "-f", " ".join(command)]
            )
        except Exception as e:
            logger.warning(f"Failed to kill command: {e}")

    async def _execute_code_dont_check_setup(
        self, code_blocks: List[CodeBlock], cancellation_token: CancellationToken
    ) -> CommandLineCodeResult:
        """Execute code blocks without checking setup."""
        if self._container is None or not self._running:
            raise ValueError(
                "Container is not running. Must first be started with either start or a context manager."
            )

        if len(code_blocks) == 0:
            raise ValueError("No code blocks to execute.")

        outputs: List[str] = []
        files: List[Path] = []
        last_exit_code = 0

        try:
            for code_block in code_blocks:
                lang = code_block.language.lower()
                code = silence_pip(code_block.code, lang)

                filename = get_file_name_from_content(code, self.work_dir)
                if filename is None:
                    filename = f"tmp_code_{sha256(code.encode()).hexdigest()}.{lang}"

                code_path = self.work_dir / filename
                code_path.write_text(code, encoding="utf-8")
                files.append(code_path)

                command = ["timeout", str(self._timeout), lang_to_cmd(lang), filename]

                output, exit_code = await self._execute_command(
                    command, cancellation_token
                )
                outputs.append(output)
                last_exit_code = exit_code

                if exit_code != 0:
                    break
        finally:
            if self._delete_tmp_files:
                for file in files:
                    try:
                        file.unlink()
                    except (OSError, FileNotFoundError):
                        pass

        code_file = str(files[0]) if files else None
        return CommandLineCodeResult(
            exit_code=last_exit_code, output="".join(outputs), code_file=code_file
        )

    async def execute_code_blocks(
        self, code_blocks: List[CodeBlock], cancellation_token: CancellationToken
    ) -> CommandLineCodeResult:
        """Execute code blocks and return the result."""
        return await self._execute_code_dont_check_setup(
            code_blocks, cancellation_token
        )

    async def start(self) -> None:
        """Start the code executor."""
        if self._work_dir is None and self._temp_dir is None:
            self._temp_dir = tempfile.TemporaryDirectory()
            Path(self._temp_dir.name).mkdir(exist_ok=True)

        try:
            client = docker.from_env()
        except DockerException as e:
            if "FileNotFoundError" in str(e):
                raise RuntimeError(
                    "Failed to connect to Docker. Please ensure Docker is installed and running."
                ) from e
            raise RuntimeError(
                f"Unexpected error while connecting to Docker: {str(e)}"
            ) from e

        try:
            await asyncio.to_thread(client.images.get, self._image)
        except ImageNotFound:
            logger.info(f"Pulling image {self._image}...")
            await asyncio.to_thread(client.images.pull, self._image)

        shell_command = "/bin/sh"
        command = (
            ["-c", f"{self._init_command};exec {shell_command}"]
            if self._init_command
            else None
        )

        try:
            existing_container = await asyncio.to_thread(
                client.containers.get, self._container_name
            )
            await asyncio.to_thread(existing_container.remove, force=True)
        except NotFound:
            pass

        volumes = {str(self.bind_dir.resolve()): {"bind": "/workspace", "mode": "rw"}}
        volumes.update(self._extra_volumes)

        self._container = await asyncio.to_thread(
            client.containers.create,
            self._image,
            name=self._container_name,
            entrypoint=shell_command,
            command=command,
            tty=True,
            detach=True,
            auto_remove=self._auto_remove,
            volumes=volumes,
            working_dir="/workspace",
            extra_hosts=self._extra_hosts,
            environment=self._environment,
        )
        await asyncio.to_thread(self._container.start)

        await _wait_for_ready(self._container)

        if self._container.status != "running":
            logs_str = self._container.logs().decode("utf-8")
            raise ValueError(
                f"Failed to start container from image {self._image}. Logs: {logs_str}"
            )

        self._loop = asyncio.get_running_loop()
        self._cancellation_futures = []
        self._running = True
        logger.debug(
            f"DockerCommandLineCodeExecutor started with container: {self._container_name}"
        )

    async def stop(self) -> None:
        """Stop the code executor and release resources."""
        if not self._running:
            return

        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None

        client = docker.from_env()
        try:
            try:
                container = await asyncio.to_thread(
                    client.containers.get, self._container_name
                )
            except NotFound:
                logger.debug(
                    f"Container {self._container_name} not found during stop..."
                )
                self._running = False
                self._cancellation_futures.clear()
                return

            if self._cancellation_futures:
                if not self._loop or self._loop.is_closed():
                    logger.warning(
                        f"Executor loop is closed or unavailable. Cannot wait for cancellation futures."
                    )
                    self._cancellation_futures.clear()
                else:
                    asyncio_futures = [
                        asyncio.wrap_future(f, loop=self._loop)
                        for f in self._cancellation_futures
                        if not f.done()
                    ]
                    if asyncio_futures:
                        await asyncio.gather(*asyncio_futures, return_exceptions=True)
                    self._cancellation_futures.clear()

            logger.debug(f"Stopping container {self._container_name}...")
            await asyncio.to_thread(container.stop)
            logger.debug(f"Container {self._container_name} stopped.")

        except DockerException as e:
            logger.error(
                f"Docker error while stopping container {self._container_name}: {e}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error during stop operation: {e}")
        finally:
            self._running = False
            self._cancellation_futures.clear()

    async def restart(self) -> None:
        """Restart the Docker container."""
        if self._container is None or not self._running:
            raise ValueError(
                "Container is not running. Must first be started with either start or a context manager."
            )

        await asyncio.to_thread(self._container.restart)
        await _wait_for_ready(self._container)

        if self._container.status != "running":
            logs_str = self._container.logs().decode("utf-8")
            raise ValueError(f"Failed to restart container. Logs: {logs_str}")

    async def execute_script(
        self,
        script_path: str,
        args: dict[str, str] | None = None,
        cancellation_token: CancellationToken | None = None,
    ) -> CommandLineCodeResult:
        """Execute an external Python script file with optional command-line arguments.

        This method allows running an existing Python script inside the Docker container
        with custom arguments. The args dictionary is converted to command-line arguments
        in the form of --key value.

        Args:
            script_path: Absolute or relative path to the Python script inside the container.
                For example: "/workspace/your_script.py" or "your_script.py" (relative to work_dir).
            args: Optional dictionary of command-line arguments. Each key-value pair is
                converted to --key value. For example: {"input": "data.txt", "verbose": "true"}
                becomes --input data.txt --verbose true.

                To pass positional arguments (without -- prefix), use an empty string as the key.
                For example: {"": "input.txt output.txt"} becomes: script.py input.txt output.txt
                Multiple positional arguments are separated by spaces.
            cancellation_token: Optional token to cancel the execution. If None, the
                execution cannot be cancelled externally.

        Returns:
            CommandLineCodeResult containing the execution output and exit code.

        Raises:
            ValueError: If the container is not running.
        """
        if self._container is None or not self._running:
            raise ValueError(
                "Container is not running. Must first be started with either start or a context manager."
            )

        command = ["timeout", str(self._timeout), "python", script_path]
        if args:
            for key, value in args.items():
                if key == "":
                    command.extend(value.split())
                else:
                    command.extend([f"--{key}", value])

        if cancellation_token is None:
            cancellation_token = CancellationToken()

        output, exit_code = await self._execute_command(command, cancellation_token)
        return CommandLineCodeResult(
            exit_code=exit_code,
            output=output,
            code_file=script_path,
        )

    def to_config(self) -> DockerCommandLineCodeExecutorConfig:
        """Convert to configuration object."""
        return DockerCommandLineCodeExecutorConfig(
            image=self._image,
            container_name=self._container_name,
            timeout=self._timeout,
            work_dir=str(self._work_dir) if self._work_dir else None,
            bind_dir=str(self._bind_dir) if self._bind_dir else None,
            auto_remove=self._auto_remove,
            stop_container=self._stop_container,
            extra_volumes=self._extra_volumes,
            extra_hosts=self._extra_hosts,
            init_command=self._init_command,
            delete_tmp_files=self._delete_tmp_files,
            environment=self._environment,
        )

    @classmethod
    def from_config(
        cls, config: DockerCommandLineCodeExecutorConfig
    ) -> "DockerCommandLineCodeExecutor":
        """Create from configuration object."""
        return cls(
            image=config.image,
            container_name=config.container_name,
            timeout=config.timeout,
            work_dir=Path(config.work_dir) if config.work_dir else None,
            bind_dir=Path(config.bind_dir) if config.bind_dir else None,
            auto_remove=config.auto_remove,
            stop_container=config.stop_container,
            extra_volumes=config.extra_volumes,
            extra_hosts=config.extra_hosts,
            init_command=config.init_command,
            delete_tmp_files=config.delete_tmp_files,
            environment=config.environment,
        )
