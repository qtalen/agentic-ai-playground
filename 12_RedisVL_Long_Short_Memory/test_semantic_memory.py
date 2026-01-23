import asyncio
import os
import logging

from dotenv import load_dotenv
import mlflow

from common.models import Qwen3
from common.utils.project_path import get_project_root
from common.agent_framework.openai_like import OpenAILikeChatClient
from redisvl_semantic_memory import RedisVLSemanticMemory

logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv(get_project_root() / ".env")

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Default")
mlflow.openai.autolog()

memory_provider = RedisVLSemanticMemory(
    session_tag="user_abc",
    distance_threshold=0.2,
)

agent = OpenAILikeChatClient(
    model_id=Qwen3.NEXT
).create_agent(
    name="assistant",
    instructions="You're a little helper who answers my questions in one sentence.",
    context_providers=memory_provider,
)

async def main():
    thread = agent.get_new_thread()

    while True:
        user_input = input("User: ")
        if user_input.startswith("exit"):
            break

        response = await agent.run(user_input, thread=thread)
        print(f"Assistant: {response.text}")
        print()

    memory_provider.clear()


if __name__ == "__main__":
    asyncio.run(main())
