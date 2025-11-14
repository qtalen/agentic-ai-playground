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
            await Console(team.run_stream(task="Two jars contain milk and water in the ratio 5: 4 and 2: 1 regpectively. What volume should be taken out from the first jar if volumes have to be taken out from both jars so as to fill up a third 30 l jar with milk to water in the ratio 1: 1 ?"))

    asyncio.run(main())
