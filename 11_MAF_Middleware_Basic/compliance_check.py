import asyncio
from typing import Literal, Callable, Awaitable, AsyncIterable
from textwrap import fill

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agent_framework import (
    AgentMiddleware, AgentRunContext,
    AgentRunResponse, ChatMessage,
    AgentRunResponseUpdate, TextContent,
    Role, AgentRunContext,
    ChatMiddleware, ChatContext
)
from agent_framework_ag_ui import AGUIChatClient

from common.agent_framework.openai_like import OpenAILikeChatClient
from common.models import Qwen3
from common.utils.project_path import get_project_root


load_dotenv(get_project_root() / ".env")

class ReviewResults(BaseModel):
    is_compliance: Literal[1, 0] = Field(..., description="If compliant, it’s 1, if not compliant, it’s 0."),
    reason: str = Field(..., description="What’s the reason for non-compliance?")

class ComplianceCheckMiddleware(ChatMiddleware):
    def __init__(self, *args, **kwargs):
        self._init_compliant_agent()
        super().__init__(*args, **kwargs)

    async def process(
        self,
        context: ChatContext,
        next: Callable[[ChatContext], Awaitable[None]],
    ):
        check_result: ReviewResults = await self._get_compliance_result(context)
        if not check_result.is_compliance:
            self._output_result(
                context,
                f"We can’t keep providing the service because:\n{fill(check_result.reason)}")
            return

        await next(context)

    @staticmethod
    def _output_result(context: ChatContext, response: str) -> None:
        if context.is_streaming:
            async def output_stream() -> AsyncIterable[AgentRunResponseUpdate]:
                yield AgentRunResponseUpdate(contents=[TextContent(text=response)])
            context.result = output_stream()
        else:
            context.result = AgentRunResponse(
                messages=[ChatMessage(role=Role.ASSISTANT, text=response)]
            )

    async def _get_compliance_result(self, context: ChatContext) -> ReviewResults:
        messages = [message for message in context.messages if message.role.value == "user"][-5:]
        response = await self.agent.run(messages)
        print(f"=================>{response.text}")
        check_result = ReviewResults.model_validate_json(response.text)
        return check_result

    def _init_compliant_agent(self) -> None:
        client = AGUIChatClient(
            endpoint="http://127.0.0.1:8888/compliance"
        )
        self.agent = client.create_agent(
            name="compliance_agent",
            instructions="You’re a compliance officer, and you review user requests."
        )


chat_client = OpenAILikeChatClient(model_id=Qwen3.NEXT)

agent = chat_client.create_agent(
    name="chat_assistant",
    instructions="You are a helpful assistant. Answer the user's question in short and simple words.",
    middleware=[ComplianceCheckMiddleware()]
)


async def main():
    thread = agent.get_new_thread()

    while True:
        user_input = input("\nUser: ")

        if user_input.startswith("exit"):
            break

        stream = agent.run_stream(user_input, thread=thread)
        print("\nAssistant: ")
        async for event in stream:
            print(event.text, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())