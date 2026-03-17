from __future__ import annotations
import asyncio
import re
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import List, Optional, Type
from pydantic import BaseModel
from typing_extensions import Self


@dataclass
class CodeBlock:
    """A code block extracted from a message."""

    code: str
    language: str


@dataclass
class CodeResult:
    """Result of a code execution."""

    exit_code: int
    output: str


class CommandLineCodeResult(CodeResult):
    """A code result class for command line code executor."""

    def __init__(
        self,
        exit_code: int,
        output: str,
        code_file: Optional[str] = None,
    ):
        super().__init__(exit_code=exit_code, output=output)
        self.code_file = code_file


class CancellationToken:
    """Very small cancellation helper, independent of Autogen."""

    def __init__(self) -> None:
        self._event = asyncio.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def is_cancellation_requested(self) -> bool:
        return self._event.is_set()

    def link_future(self, fut: asyncio.Future | asyncio.Task) -> None:
        async def watcher() -> None:
            await self._event.wait()
            if not fut.done():
                fut.cancel()

        asyncio.create_task(watcher())


class CodeExecutor(ABC):
    """Executes code blocks and returns the result.
    Subclasses should implement the abstract methods and are typically
    used as async context managers::
        async with MyExecutor(...) as executor:
            result = await executor.execute_code_blocks(...)
    """

    @abstractmethod
    async def execute_code_blocks(
        self, code_blocks: List[CodeBlock], cancellation_token: CancellationToken
    ) -> CodeResult:
        """Execute code blocks and return the result.
        Raises:
            ValueError: Errors in user inputs
            asyncio.TimeoutError: Code execution timeouts
            asyncio.CancelledError: CancellationToken evoked during execution
        """
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the code executor."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the code executor and release any resources."""
        ...

    @abstractmethod
    async def restart(self) -> None:
        """Restart the code executor."""
        ...

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.stop()
        return None


PYTHON_VARIANTS = ["python", "Python", "py"]


def lang_to_cmd(lang: str) -> str:
    """Map language to command."""
    lang = lang.lower()
    if lang in PYTHON_VARIANTS:
        return "python"
    if lang.startswith("python") or lang in ["bash", "sh"]:
        return lang
    if lang in ["shell"]:
        return "sh"
    if lang in ["pwsh", "powershell", "ps1"]:
        if shutil.which("pwsh") is not None:
            return "pwsh"
        elif shutil.which("powershell") is not None:
            return "powershell"
        else:
            raise ValueError(
                "Powershell or pwsh is not installed. Please install one of them."
            )
    else:
        raise ValueError(f"Unsupported language: {lang}")


def silence_pip(code: str, lang: str) -> str:
    """Apply -qqq flag to pip install commands."""
    if lang == "python":
        regex = r"^! ?pip install"
    elif lang in ["bash", "shell", "sh", "pwsh", "powershell", "ps1"]:
        regex = r"^pip install"
    else:
        return code

    lines = code.split("\n")
    for i, line in enumerate(lines):
        match = re.search(regex, line)
        if match is not None:
            if "-qqq" not in line:
                lines[i] = line.replace(match.group(0), match.group(0) + " -qqq")
    return "\n".join(lines)


def get_file_name_from_content(code: str, workspace_path: Path) -> Optional[str]:
    """Extract filename from code comment like '# filename: xxx'."""
    first_line = code.split("\n")[0]
    if first_line.startswith("# filename:"):
        filename = first_line.split(":")[1].strip()
        path = Path(filename)
        if not path.is_absolute:
            path = workspace_path / path
        try:
            path = path.resolve()
            relative = path.relative_to(workspace_path.resolve())
            return str(relative)
        except ValueError:
            pass
    return None
