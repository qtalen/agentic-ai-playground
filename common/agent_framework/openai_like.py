from typing import override, MutableSequence, Any
from textwrap import dedent
from copy import deepcopy

from pydantic import BaseModel
from agent_framework.openai import OpenAIChatClient
from agent_framework import ChatMessage, ChatOptions, TextContent

class OpenAILikeChatClient(OpenAIChatClient):
    @override
    def _prepare_options(self, messages: MutableSequence[ChatMessage], chat_options: ChatOptions) -> dict[str, Any]:
        chat_options_copy = deepcopy(chat_options)

        if (
            chat_options.response_format
            and isinstance(chat_options.response_format, type)
            and issubclass(chat_options.response_format, BaseModel)
        ):
            structured_output_prompt = self._build_structured_prompt(chat_options.response_format)
            messages = self._add_system_msg(messages, structured_output_prompt)
            chat_options_copy.response_format = {"type": "json_object"}

        return super()._prepare_options(messages, chat_options_copy)

    @staticmethod
    def _add_system_msg(
        orig_messages: MutableSequence[ChatMessage], addition_msg: str
    ) -> MutableSequence[ChatMessage]:
        if len(orig_messages) < 1:
            return orig_messages

        first_message = orig_messages[0]
        if (
            hasattr(first_message, "role")
            and first_message.role.value == "system"
        ):
            new_system_message = ChatMessage(
                role="system",
                text=f"{first_message.text} {addition_msg}"
            )
            messages = [new_system_message, *orig_messages[1:]]
        else:
            new_system_message = ChatMessage(
                role="system",
                text=f"{addition_msg}"
            )
            messages = [new_system_message, *orig_messages]
        return messages

    @staticmethod
    def _build_structured_prompt(response_format: type[BaseModel]) -> str:
        json_schema = response_format.model_json_schema()
        structured_output_prompt = dedent(f"""
        \n\n
        <response-format>\n
        Your response must adhere to the following JSON schema format,
        without any Markdown syntax, and without any preface or explanation:\n
        {json_schema}\n
        </response-format>
        """)

        return structured_output_prompt