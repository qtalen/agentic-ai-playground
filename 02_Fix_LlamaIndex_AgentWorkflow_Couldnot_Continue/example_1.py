from pprint import pprint
import asyncio

from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.workflow import Context
from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow, AgentInput, AgentOutput

load_dotenv("../.env")

console = Console()

model_args = {
    "is_chat_model": True,
    "is_function_calling_model": True,
    "temperature": 0.1,
    "context_window": 8000
}

llm = OpenAILike(
    model="qwen-max-latest",
    **model_args
)


async def search_web(ctx: Context, query: str) -> str:
    """
    This tool searches the internet and returns the search results.
    :param query: user's original request
    :return: Then return the search results.
    """
    tavily_client = AsyncTavilyClient()
    search_result = await tavily_client.search(str(query))
    return str(search_result)


async def record_notes(ctx: Context, notes: str, notes_title: str) -> str:
    """
    Useful for recording notes on a given topic. Your input should be notes with a title to save the notes under.
    """
    current_state = await ctx.get("state", {})
    if "research_notes" not in current_state:
        current_state["research_notes"] = {}
    current_state["research_notes"][notes_title] = notes
    await ctx.set("state", current_state)
    return "notes recorded"

search_agent = FunctionAgent(
    name="SearchAgent",
    description="You are a helpful search assistant.",
    # system_prompt="""
    # You're a search assistant.
    # You don't generate any response.
    # You only search the internet for information related to the user's request.
    # After getting the search results, you directly hand off control to the ResearchAgent.
    # """,
    system_prompt="""
    You're a helpful search assistant.
    First, you'll look up notes online related to the given topic and recorde these notes on the topic.
    Once the notes are recorded, you should hand over control to the ResearchAgent.
    """,
    tools=[search_web, record_notes],
    llm=llm,
    can_handoff_to=["ResearchAgent"]
)

research_agent = FunctionAgent(
    name="ResearchAgent",
    description="You are a helpful research assistant.",
    # system_prompt="""
    # You're a helpful report-writing assistant.
    # The system has already searched online for detailed information related to the user's request.
    # You'll review this information and draft a professional research report.
    # """,
    system_prompt="""
    You're a helpful search assistant.
    First, you'll look up notes online related to the given topic and recorde these notes on the topic.
    Once the notes are recorded, you should hand over control to the ResearchAgent.
    """,
    llm=llm
)

workflow = AgentWorkflow(
    agents=[search_agent, research_agent],
    root_agent=search_agent.name
)


async def main():
    handler = workflow.run(user_msg="What is LLamaIndex AgentWorkflow, and what problems does it solve?")
    async for event in handler.stream_events():
        if isinstance(event, AgentOutput):
            print("=" * 70)
            print(f"🤖 {event.current_agent_name}")
            if event.response.content:
                console.print(Markdown(event.response.content or ""))
            else:
                console.print(event.tool_calls)

if __name__ == "__main__":
    asyncio.run(main())
