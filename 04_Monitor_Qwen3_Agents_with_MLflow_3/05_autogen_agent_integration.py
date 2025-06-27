import asyncio

from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from autogen_agentchat.agents import AssistantAgent
import mlflow
from mlflow.entities import SpanType

from utils.autogen_openai_like import OpenAILikeChatCompletionClient
import utils.autogen_patching


load_dotenv("../.env")
mlflow.set_experiment("test_autogen_tracing")
# mlflow.openai.autolog()

@mlflow.trace(span_type=SpanType.TOOL)
async def web_search(query: str) -> str:
    """
    Find information on the web.
    :param query: what you want to search for.
    :return: The information on the web.
    """
    client = AsyncTavilyClient()
    response = await client.search(query, max_results=5)
    return str(response["results"])

model_client = OpenAILikeChatCompletionClient(
    model="qwen-turbo-latest",
    temperature=0.1
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message="You will help me to get useful information on the web.",
    reflect_on_tool_use=True,
)

# @mlflow.trace(span_type=SpanType.AGENT)
async def main():
    result = await agent.run(task="Get the latest news of Agentic AI.")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
