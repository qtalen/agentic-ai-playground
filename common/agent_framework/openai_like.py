from __future__ import annotations
import re
from typing import override, MutableSequence, Any, cast
from textwrap import dedent
from copy import copy

from pydantic import BaseModel
from agent_framework.openai import OpenAIChatClient
from agent_framework import Message
from agent_framework._types import ChatResponse, AgentResponse


_CODE_BLOCK_RE = re.compile(
    r"""^\s*```(?P<lang>\w+)?\s* \n(?P<body>.*)```\s*$""",
    re.DOTALL | re.VERBOSE,
)

def _extract_json_from_markdown(text: str) -> str:
    stripped = text.strip()
    match = _CODE_BLOCK_RE.match(stripped)
    if not match:
        return stripped
    lang = (match.group("lang") or "").lower()
    if lang and not lang.startswith("json"):
        return stripped
    body = match.group("body") or ""
    return body.strip()

def _patched_value(self) -> Any | None:
    if self._value_parsed:
        return self._value
    if (
        self._response_format is not None
        and isinstance(self._response_format, type)
        and issubclass(self._response_format, BaseModel)
    ):
        raw_text = self.text
        json_text = _extract_json_from_markdown(raw_text)
        self._value = cast(Any, self._response_format.model_validate_json(json_text))
        self._value_parsed = True
    return self._value


ChatResponse.value = property(_patched_value)  # type: ignore[assignment]
AgentResponse.value = property(_patched_value)  # type: ignore[assignment]

class OpenAILikeChatClient(OpenAIChatClient):
    @override
    def _prepare_options(self, messages: MutableSequence[Message], options: dict[str, Any]) -> dict[str, Any]:
        chat_options_copy = copy(options)
        response_format = chat_options_copy.get("response_format")

        if (
            response_format
            and isinstance(response_format, type)
            and issubclass(response_format, BaseModel)
        ):
            structured_output_prompt = self._build_structured_prompt(response_format)
            if old_instructions := chat_options_copy.get("instructions"):
                chat_options_copy["instructions"] = f"{old_instructions}\n\n{structured_output_prompt}"
            else:
                messages = [Message(role="system", text=structured_output_prompt), *messages]

            del chat_options_copy["response_format"]

        return super()._prepare_options(messages, chat_options_copy)

    @staticmethod
    def _build_structured_prompt(response_format: type[BaseModel]) -> str:
        json_schema = response_format.model_json_schema()
        structured_output_prompt = dedent(f"""
        <response-format>\n
        You must output JSON text strictly following the JSON format defined by the JSON schema below.
        Only output a JSON string, without any markdown formatting, and without any preface or explanation:\n
        {json_schema}\n
        </response-format>
        """)

        return structured_output_prompt