import asyncio
from dotenv import load_dotenv
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console

from common.utils.project_path import get_project_root
from code_executor import code_executor, executor
from code_writer import code_writer
from task_planner import planner

text_term = TextMentionTermination("TERMINATION")
max_msg_term = MaxMessageTermination(max_messages=30)
combine_term = text_term | max_msg_term

team = RoundRobinGroupChat(
    [planner, code_writer, code_executor],
    termination_condition=combine_term
)

if __name__ == "__main__":
    async def main():
        async with executor:
            await Console(
                team.run_stream(task="Read the superstore.csv file and find the total sales for each region.")
            )

    asyncio.run(main())
