import asyncio

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from utils.openai_like import OpenAILikeChatCompletionClient

load_dotenv("../.env")

model_client = OpenAILikeChatCompletionClient(
    model="qwen-plus-latest"
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="You are a helpful assistant."
)


async def main():
    await Console(
        agent.run_stream(task="Hi, could you introduce yourself? Are you Qwen3?")
    )


if __name__ == "__main__":
    asyncio.run(main())


