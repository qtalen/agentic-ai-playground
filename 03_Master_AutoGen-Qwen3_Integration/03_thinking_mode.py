import asyncio
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from utils.openai_like import OpenAILikeChatCompletionClient

load_dotenv("../.env")

model_client = OpenAILikeChatCompletionClient(
    model="qwen3-30b-a3b",
    temperature=0.01,
    extra_body={"enable_thinking": False}
)

class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="Categorize the input as happy, sad, or neutral following json format.",
    output_content_type=AgentResponse,
    model_client_stream=True
)


async def main():
    await Console(
        agent.run_stream(task="I have nothing but money.")
    )

if __name__ == "__main__":
    asyncio.run(main())
