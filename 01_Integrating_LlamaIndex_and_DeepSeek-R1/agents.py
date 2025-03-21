import asyncio

from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent, AgentWorkflow, AgentStream, AgentOutput

from deepseek import DeepSeek
from reasoning_adapter import ReasoningStreamAdapter

load_dotenv("../.env")

llm = DeepSeek(
    model="deepseek-reasoner",
    is_chat_model=True
)


async def search_web(query: str) -> str:
    """
    A tool for searching information on the internet.
    :param query: keywords to search
    :return: the information
    """
    client = AsyncTavilyClient()
    return str(await client.search(query))


search_agent = ReActAgent(
    name="SearchAgent",
    description="A helpful agent",
    system_prompt="You are a helpful assistant that can answer any questions",
    tools=[search_web],
    llm=llm
)

