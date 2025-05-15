import asyncio
from textwrap import dedent
from typing import cast

from dotenv import load_dotenv
from rich.console import Console as RichConsole
from rich.markdown import Markdown
from pydantic import BaseModel, Field
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.tools.mcp import StdioMcpToolAdapter, StdioServerParams

from utils.openai_like import OpenAILikeChatCompletionClient

load_dotenv("../.env")

console = RichConsole(width=100)

model_client = OpenAILikeChatCompletionClient(
    model='qwen3-30b-a3b',
    temperature=0.01,
    extra_body={"enable_thinking": False}
)

class ArticleDetail(BaseModel):
    title: str
    url: str
    author: str = Field(..., description="The author of the article.")
    keywords: list[str] = Field(..., description="You need to provide me with no more than 5 keywords.")
    summary: str = Field(..., description="""
    High level summary of the article with relevant facts and details.
    Include all relevant information to provide full picture.
    """)


async def main():
    server_params = StdioServerParams(
        command="python",
        args=["-m", "mcp_server_fetch"],
        read_timeout_seconds=30
    )

    fetch = await StdioMcpToolAdapter.from_server_params(server_params, "fetch")

    agent = AssistantAgent(
        name="web_browser",
        model_client=model_client,
        tools=[fetch],
        system_message="You are a helpful assistant.",
        output_content_type=ArticleDetail,
        model_client_stream=True
    )

    result = await Console(
        agent.run_stream(task="""
        Please visit
        https://www.dataleadsfuture.com/fixing-the-agent-handoff-problem-in-llamaindexs-agentworkflow-system/
        and give me a quick summary.
        """)
    )

    output = cast(ArticleDetail, result.messages[-1].content)

    console.print(Markdown(dedent(f"""
    \n
    \n
    **📋Title:** {output.title}
    
    **🔗Link:** {output.url}
    
    **🧑‍💻Author:** {output.author}
    
    **🏷️Keywords:** {output.keywords}
    
    **📃Summary:** {output.summary}
    """)))


if __name__ == "__main__":
    asyncio.run(main())


