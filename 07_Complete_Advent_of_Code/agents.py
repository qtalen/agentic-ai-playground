import asyncio
from typing import Sequence, AsyncGenerator
from textwrap import dedent
from pathlib import Path
import shutil

from dotenv import load_dotenv
from autogen_core import CancellationToken
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import BaseChatMessage, BaseAgentEvent, TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.tools.code_execution import PythonCodeExecutionTool
from autogen_ext.code_executors.docker_jupyter import DockerJupyterCodeExecutor, DockerJupyterServer
from autogen_ext.code_executors.docker_jupyter._jupyter_server import JupyterConnectionInfo
from autogen_ext.code_executors.jupyter import JupyterCodeExecutor

from common.autogen.openai_like import OpenAILikeChatCompletionClient
from common.utils.project_path import get_project_root, get_current_directory

from prompts import SYS_PROMPT

load_dotenv(get_project_root() / ".env")

BINDING_DIR = Path(get_current_directory()/"temp")


class AOCAssistant:
    def __init__(
            self,
            model_name: str = "qwen3-max-preview",
    ):
        self._model_name = model_name
        self._model_client = None
        self._jupyter_server = None
        self._executor = None
        self._agent = None

        BINDING_DIR.mkdir(parents=True, exist_ok=True)
        self._init_jupyter_docker()
        # self._init_jupyter_server()
        self._init_assistant()

    async def run(
            self,
            *,
            task: str | BaseChatMessage | Sequence[BaseChatMessage] | None = None,
            cancellation_token: CancellationToken | None = None,
            file_name: str | None = None,
            file_path: Path | str | None = None,
    ) -> TaskResult:
        async for message in self.run_stream(
            task=task,
            cancellation_token=cancellation_token,
            file_name=file_name,
            file_path=file_path,
        ):
            if isinstance(message, TaskResult):
                return message
        raise ValueError("No task result output.")

    async def run_stream(
            self,
            *,
            task: str | BaseChatMessage | Sequence[BaseChatMessage] | None = None,
            cancellation_token: CancellationToken | None = None,
            file_name: str | None = None,
            file_path: Path | str | None = None,
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | TaskResult, None]:
        file_name = self._copy_file(file_name, file_path)

        input_messages = []
        if isinstance(task, str):
            input_messages.append(TextMessage(
                source="user",
                content=task
            ))
        elif isinstance(task, BaseChatMessage):
            input_messages.append(task)

        if file_name is not None:
            input_messages.append(TextMessage(
                source="user",
                content=f"The input file is `{file_name}`"
            ))

        async for message in self._agent.run_stream(
                task=input_messages,
                cancellation_token=cancellation_token):
            yield message

    async def start(self):
        await self._executor.start()

    async def stop(self):
        await self._model_client.close()
        await self._executor.stop()
        await self._jupyter_server.stop()

    async def __aenter__(self) -> "AOCAssistant":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def _init_jupyter_docker(self) -> None:
        self._jupyter_server = DockerJupyterServer(
            custom_image_name="jupyter-server:latest",
            expose_port=8888,
            bind_dir=BINDING_DIR,
        )
        self._executor = DockerJupyterCodeExecutor(
            jupyter_server=self._jupyter_server,
            timeout=600)

    def _init_jupyter_server(self) -> None:
        self._executor = DockerJupyterCodeExecutor(
            jupyter_server=JupyterConnectionInfo(host="127.0.0.1",
                                                 use_https=False,
                                                 port=8888,
                                                 token='UNSET'),
            output_dir=BINDING_DIR,
        )

    def _init_assistant(self) -> None:
        self._model_client = OpenAILikeChatCompletionClient(
            model=self._model_name,
            temperature=0.5,
            top_p=0.85,
        )

        tool = PythonCodeExecutionTool(self._executor)

        self._agent = AssistantAgent(
            'assistant',
            model_client=self._model_client,
            tools=[tool],
            model_client_stream=True,
            system_message=SYS_PROMPT,
            max_tool_iterations=30,
        )

    @staticmethod
    def _copy_file(
        file_name: str | None = None,
        file_path: Path | str | None = None,
    ) -> Path | str | None:
        if file_path is None:
            return None

        if file_name is None:
            file_name = Path(file_path).name
        dst_path = BINDING_DIR / file_name
        shutil.copy2(file_path, dst_path)
        return file_name


async def main():
    async with AOCAssistant() as agent:
        await Console(agent.run_stream(task=dedent("""
        Please repeat my instructions in detail.
                """)))


if __name__ == "__main__":
    asyncio.run(main())
