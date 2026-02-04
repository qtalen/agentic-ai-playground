import asyncio
import os

from dotenv import load_dotenv
import mlflow

from common.utils.project_path import get_project_root
from common.models import Qwen3
from common.agent_framework.openai_like import OpenAILikeChatClient
from redisvl_long_term_memory import LongTermMemory

load_dotenv(get_project_root() / ".env")
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Default")
mlflow.openai.autolog()

memory_provider = LongTermMemory(
)

agent = OpenAILikeChatClient(
    model_id=Qwen3.MAX
).as_agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    context_provider=memory_provider,
)

async def main():
    thread = agent.get_new_thread()

    while True:
        user_input = input("\nUser: ")
        if user_input.startswith("exit"):
            break
        stream = agent.run_stream(user_input, thread=thread)
        print("Assistant: \n")
        async for event in stream:
            print(event.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())