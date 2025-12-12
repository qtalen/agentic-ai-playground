from typing import override, MutableSequence, Any
from textwrap import dedent
from copy import deepcopy

from pydantic import BaseModel
from agent_framework.openai import OpenAIChatClient
from agent_framework import ChatMessage, ChatOptions, TextContent

class OpenAILikeChatClient(OpenAIChatClient):
    @override
    def _prepare_options(
            self,
            messages: MutableSequence[ChatMessage],
            chat_options: ChatOptions) -> dict[str, Any]:
        chat_options_copy = deepcopy(chat_options) # 1
        if (
            chat_options.response_format
            and isinstance(chat_options.response_format, type)
            and issubclass(chat_options.response_format, BaseModel)
        ):
            structured_output_prompt = (
                self._build_structured_prompt(chat_options.response_format)) # 2

            if len(messages) >= 1: # 3
                first_message = messages[0]
                if str(first_message.role) == "system": # 4
                    new_system_message = ChatMessage(
                        role="system",
                        text=f"{first_message.text} {structured_output_prompt}"
                    )
                    messages = [new_system_message, *messages[1:]]
                else:
                    new_system_message = ChatMessage( # 5
                        role="system",
                        text=f"{structured_output_prompt}"
                    )
                    messages = [new_system_message, *messages]

            chat_options_copy.response_format = {"type": "json_object"}
        return super()._prepare_options(messages, chat_options_copy)

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