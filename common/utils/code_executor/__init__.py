from typing import Literal

from .base import (
    CodeBlock,
    CodeExecutor,
    CancellationToken,
)
from .docker import DockerCommandLineCodeExecutor

class CodeExecutionTool:
    """Tool for executing code using a CodeExecutor."""

    def __init__(self, executor: CodeExecutor) -> None:
        self._executor = executor

    async def execute_code(self, code: str, language: Literal["python", "sh"] = "python") -> str:
        """Execute code and return the output.

        Args:
            code: The code to execute.
            language: The programming language. Supported values: "python", "sh". Defaults to "python".

        Returns:
            The output of the code execution.
        """
        result = await self._executor.execute_code_blocks(
            [CodeBlock(code=code, language=language)],
            CancellationToken(),
        )
        return result.output


__ALL__ = [
    "CodeExecutionTool",
    "DockerCommandLineCodeExecutor",
]