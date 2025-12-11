import asyncio
import os

from pydantic import BaseModel
from dotenv import load_dotenv
import mlflow

from common.utils.project_path import get_project_root
from common.agent_framework.openai_like import OpenAILikeChatClient
from common.models import Qwen3

load_dotenv(get_project_root() / ".env")

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Default")
mlflow.openai.autolog()

class PersonInfo(BaseModel):
    """Information about a person."""
    name: str | None = None
    age: int | None = None
    occupation: str | None = None


agent = OpenAILikeChatClient(model_id=Qwen3.NEXT).create_agent(
    instructions="You are a helpful assistant that extracts person information from text.",
    name="assistant",
)

async def main():
    response = await agent.run(
        "Please provide information about John Smith, who is a 35-year-old software engineer.",
        response_format=PersonInfo,
    )
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())