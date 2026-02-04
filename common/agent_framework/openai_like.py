from typing import override, MutableSequence, Any
from textwrap import dedent
from copy import deepcopy

from pydantic import BaseModel
from agent_framework.openai import OpenAIChatClient
from agent_framework import ChatMessage, Role, ChatAgent

class OpenAILikeChatClient(OpenAIChatClient):
    @override
    def _prepare_options(self, messages: MutableSequence[ChatMessage], options: dict[str, Any]) -> dict[str, Any]:
        chat_options_copy = deepcopy(options)
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
                messages = [ChatMessage(role=Role.SYSTEM, text=structured_output_prompt), *messages]
            # messages = self._add_system_msg(messages, structured_output_prompt)
            chat_options_copy["response_format"] = {"type": "json_object"}

        return super()._prepare_options(messages, chat_options_copy)

    def create_agent(self, **kwargs) -> ChatAgent:
        """
        Adapted to the older version of the API.
        """
        return super().as_agent(**kwargs)

    @staticmethod
    def _build_structured_prompt(response_format: type[BaseModel]) -> str:
        json_schema = response_format.model_json_schema()
        structured_output_prompt = dedent(f"""
        <response-format>\n
        You must output JSON text strictly following the JSON format defined by the JSON schema below.
        Do not include any markdown formatting, and do not include any preface or explanation:\n
        {json_schema}\n
        </response-format>
        """)

        return structured_output_prompt