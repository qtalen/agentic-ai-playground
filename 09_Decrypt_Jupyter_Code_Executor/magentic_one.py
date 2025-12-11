import asyncio
from textwrap import dedent

from dotenv import load_dotenv
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console

from common.autogen.openai_like import OpenAILikeChatCompletionClient
from common.utils.project_path import get_project_root
from code_writer import code_writer
from code_executor import executor, code_executor

load_dotenv(get_project_root() / ".env")

model_client = OpenAILikeChatCompletionClient(
    model="qwen3-max",
    temperature=0.1,
    top_p=0.85
)

team = MagenticOneGroupChat([code_writer, code_executor], model_client=model_client,
                            final_answer_prompt=dedent("""
                            根据研究的结果，为用户的[请求]撰写一份事实详尽的分析报告。
                            不仅要求有分析洞察，还要有进一步的建议。
                            报告中可以适当添加表情符以便文案不那么刻板。
                            """))


async def main(task: str):
    async with executor:
        await Console(team.run_stream(task=task))


if __name__ == "__main__":
    # asyncio.run(main("Read the superstore.csv file and give me some insight about the sales of each region."))
    asyncio.run(main("阅读`研发效能产品需求明细.xlsx`"))