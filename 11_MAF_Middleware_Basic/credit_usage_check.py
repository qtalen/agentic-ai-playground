import asyncio
from typing import Callable, Awaitable, AsyncIterable

from dotenv import load_dotenv
from agent_framework import (
    AgentRunContext, AgentMiddleware,
    AgentResponseUpdate, Content,
    AgentResponse, ChatMessage,
    Role
)

from common.agent_framework.openai_like import OpenAILikeChatClient
from common.models import Qwen3
from common.utils.project_path import get_project_root


load_dotenv(get_project_root() / ".env")

class CreditCheckMiddleware(AgentMiddleware):
    def __init__(self, max_credit: int = 5, *args, **kwargs):
        self.current_credit = max_credit
        super().__init__(*args, **kwargs)

    async def process(
        self,
        context: AgentRunContext,
        next: Callable[[AgentRunContext], Awaitable[None]]
    ):
        if not self._check_credit():
            context.terminate = True
            self._output_result(context, "Your credit points have run out.")
            return

        try:
            await next(context)
            self._update_credit()
        except Exception as e:
            print(e)

    def _output_result(self, context: AgentRunContext, response: str) -> None:
        if context.is_streaming:
            async def output_stream() -> AsyncIterable[AgentResponseUpdate]:
                yield AgentResponseUpdate(contents=[Content.from_text(text=response)])
            context.result = output_stream()
        else:
            context.result = AgentResponse(
                messsages=[ChatMessage(role=Role.ASSISTANT, text=response)]
            )

    def _check_credit(self) -> bool:
        print(f"Your credit points are {self.current_credit}")
        return self.current_credit > 0

    def _update_credit(self, points: int = 1) -> int:
        self.current_credit -= points
        print(f"Your remaining credit points are {self.current_credit}")
        return self.current_credit



chat_client = OpenAILikeChatClient(model_id=Qwen3.NEXT)

agent = chat_client.as_agent(
    name="assistant",
    instructions="You are a helpful assistant. Answer the user's question in short and simple words.",
    middleware=[CreditCheckMiddleware(max_credit=3)]
)



async def main():
    thread = agent.get_new_thread()

    while True:
        user_input = input("\nUser: ")
        if user_input.startswith("exit"):
            break

        stream = agent.run_stream(user_input, thread=thread)
        print("\nAssistant:\n")
        async for event in stream:
            print(event.text, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())