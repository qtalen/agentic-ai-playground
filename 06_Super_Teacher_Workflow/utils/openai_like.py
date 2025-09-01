import os
from typing import Sequence, override, Optional, Mapping, Any, AsyncGenerator, Union, Literal
import copy
from textwrap import dedent

from pydantic import BaseModel
from autogen_core.models import LLMMessage
from autogen_core.tools import Tool, ToolSchema
from autogen_core._cancellation_token import CancellationToken
from autogen_core.models._types import CreateResult, SystemMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._openai_client import CreateParams


class ModelFamily:
    QWEN = "gpt-45"
    DEEPSEEK = "gpt-45"
    R1 = "r1"


DEFAULT_MODEL_INFO = {
    "vision": False,
    "function_calling": True,
    "json_output": True,
    "family": ModelFamily.QWEN,
    "structured_output": True,
    "context_window": 32_000,
    "multiple_system_messages": True,
}

_MODEL_INFO: dict[str, dict] = {
    "qwen-max": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 32_000,
        "multiple_system_messages": True,
    },
    "qwen-max-latest": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 128_000,
        "multiple_system_messages": True,
    },
    "qwen-plus": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 128_000,
        "multiple_system_messages": True,
    },
    "qwen-plus-latest": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 128_000,
        "multiple_system_messages": True,
    },
    "qwen-turbo": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 1_000_000,
        "multiple_system_messages": True,
    },
    "qwen-turbo-latest": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 1_000_000,
        "multiple_system_messages": True,
    },
    "qwen-omni-turbo": {
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "o1",
        "structured_output": True,
        "context_window": 1_000_000,
        "multiple_system_messages": True,
    },
    "qwen-omni-turbo-latest": {
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "o1",
        "structured_output": True,
        "context_window": 1_000_000,
        "multiple_system_messages": True,
    },
    "qwen3-235b-a22b-thinking-2507": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.R1,
        "structured_output": True,
        "context_window": 128_000,
        "multiple_system_messages": True,
    },
    "deepseek-chat": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.DEEPSEEK,
        "structured_output": True,
        "context_window": 64_000,
        "multiple_system_messages": True,
    },
    "deepseek-reasoner": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.DEEPSEEK,
        "structured_output": True,
        "context_window": 64_000,
        "multiple_system_messages": True,
    }
}

extra_kwargs: set = {"extra_body"}


class OpenAILikeChatCompletionClient(OpenAIChatCompletionClient):
    def __init__(self, **kwargs):
        self.model = kwargs.get("model", "qwen-max")
        if "model_info" not in kwargs:
            kwargs["model_info"] = _MODEL_INFO.get(self.model, DEFAULT_MODEL_INFO)
        if "base_url" not in kwargs:
            kwargs["base_url"] = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")

        super().__init__(**kwargs)
        for key in extra_kwargs:  # Add the model-specific extension parameters for Qwen3 in self._create_args
            if key in kwargs:
                self._create_args[key] = kwargs[key]

    @override
    def remaining_tokens(self, messages: Sequence[LLMMessage], *, tools: Sequence[Tool | ToolSchema] = []) -> int:
        token_limit = _MODEL_INFO[self.model]["context_window"]
        return token_limit - self.count_tokens(messages, tools=tools)

    @override
    async def create(
            self,
            messages: Sequence[LLMMessage],
            *,
            tools: Sequence[Tool | ToolSchema] = [],
            tool_choice: Tool | Literal["auto", "required", "none"] = "auto",
            json_output: Optional[bool | type[BaseModel]] = None,
            extra_create_args: Mapping[str, Any] = {},
            cancellation_token: Optional[CancellationToken] = None,
    ) -> CreateResult:
        if json_output is not None and issubclass(json_output, BaseModel):
            messages = self._append_json_schema(messages, json_output)
            json_output = None
        result = await super().create(
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            json_output=json_output,
            extra_create_args=extra_create_args,
            cancellation_token=cancellation_token
        )
        return result

    @override
    async def create_stream(
            self,
            messages: Sequence[LLMMessage],
            *,
            tools: Sequence[Tool | ToolSchema] = [],
            tool_choice: Tool | Literal["auto", "required", "none"] = "auto",
            json_output: Optional[bool | type[BaseModel]] = None,
            extra_create_args: Mapping[str, Any] = {},
            cancellation_token: Optional[CancellationToken] = None,
            max_consecutive_empty_chunk_tolerance: int = 0,
            include_usage: Optional[bool] = None,
    ) -> AsyncGenerator[Union[str, CreateResult], None]:
        if json_output is not None and issubclass(json_output, BaseModel):
            messages = self._append_json_schema(messages, json_output)
            json_output = None
        async for result in super().create_stream(
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                json_output=json_output,
                extra_create_args=extra_create_args,
                cancellation_token=cancellation_token,
                max_consecutive_empty_chunk_tolerance=max_consecutive_empty_chunk_tolerance,
                include_usage=include_usage,
        ):
            yield result

    def _append_json_schema(self, messages: Sequence[LLMMessage],
                            json_output: BaseModel) -> Sequence[LLMMessage]:
        messages = copy.deepcopy(messages)
        first_message = messages[0]
        if isinstance(first_message, SystemMessage):
            first_message.content += dedent(f"""\

            <output-format>
            Your output must adhere to the following JSON schema format, 
            without any Markdown syntax, and without any preface or explanation.:

            {json_output.model_json_schema()}
            </output-format>
            """)
        return messages