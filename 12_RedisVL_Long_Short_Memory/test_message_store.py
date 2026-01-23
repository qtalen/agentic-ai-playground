import asyncio
import os

from dotenv import load_dotenv
import mlflow

from common.models.models import Qwen3
from common.utils.project_path import get_project_root
from common.agent_framework.openai_like import OpenAILikeChatClient
from redisvl_message_store import RedisVLMessageStore


load_dotenv(get_project_root() / ".env")

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Default")
mlflow.openai.autolog()

agent = OpenAILikeChatClient(
    model_id=Qwen3.NEXT
).create_agent(
    name="assistant",
    instructions="You're a little helper who answers my questions in one sentence.",
    chat_message_store_factory=lambda: RedisVLMessageStore(
        session_tag="user_abc"
    )
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

    thread.message_store.clear()


if __name__ == "__main__":
    asyncio.run(main())

