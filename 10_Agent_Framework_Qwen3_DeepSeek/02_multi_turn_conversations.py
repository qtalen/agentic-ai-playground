import asyncio
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agent_framework import AgentRunResponse
import mlflow

from common.utils.project_path import get_project_root
from common.models import Qwen3
from common.agent_framework.openai_like import OpenAILikeChatClient

load_dotenv(get_project_root() / ".env")

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Default")
mlflow.openai.autolog()

client = OpenAILikeChatClient(
    model_id=Qwen3.NEXT,
)

class OutText(BaseModel):
    output: str

class ETA(BaseModel):
    hours: int

agent = client.create_agent(
    instructions="You are a good assistant.",
    name="assistant",
    response_format=OutText,
)

thread = agent.get_new_thread()

async def main():
    result1 = await agent.run(
        "How many kilometers is the highway from Wuhan to Beijing?",
        thread=thread,
    )
    print(result1.text)


    final_response = await AgentRunResponse.from_agent_response_generator(
        agent.run_stream(
            "How long would it take to drive there at 120 km/h?",
            thread=thread,
            response_format=ETA,
        ),
        output_format_type=ETA
    )
    print(final_response.value)


if __name__ == "__main__":
    asyncio.run(main())
