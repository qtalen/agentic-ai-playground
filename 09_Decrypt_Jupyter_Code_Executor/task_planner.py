import os
from textwrap import dedent

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from common.autogen.openai_like import OpenAILikeChatCompletionClient
from common.utils.project_path import get_project_root


load_dotenv(get_project_root()/".env")

model_client = OpenAILikeChatCompletionClient(
    model="qwen3-30b-a3b-instruct-2507",
    temperature=0.1,
    top_p=0.85,
)

SYSTEM_PROMPT = dedent("""
你是团队里的任务规划助手，擅长将用户的复杂任务拆解为适合用python代码执行的子任务。

## 职责
1. **只负责拆分任务**，不生成代码，也不执行具体的子任务。
2. **每次只生成一个子任务**，不跳步，不合并多个步骤。
3. **考虑上下文**，结合之前执行的结果，生成新的、合理的子任务。
4. **迭代生成任务**，持续拆解，直到用户的原始请求能够被完整解答。
5. 在所有子任务完成后，**根据执行历史生成一份总结报告**。
6. 最后输出 "**TERMINATION**" 作为结束标志。
""")

# SYSTEM_PROMPT = dedent("""
# You are the task planning helper in the team, good at breaking down complex user requests into smaller sub-tasks that can be done with Python code.
#
# ## Duties
# 1. **Only split tasks**, don’t write code or do the sub-tasks yourself.
# 2. **Make just one sub-task at a time**, don’t skip steps or merge different steps together.
# 3. **Think about the context**, use the results from earlier steps to make new and reasonable sub-tasks.
# 4. **Create tasks step by step**, keep breaking things down until the user’s original request is fully answered.
# 5. When all sub-tasks are done, **make a summary report based on the work history**.
# 6. At the very end, output "**TERMINATION**" as the finish signal.
# """)

planner = AssistantAgent(
    "task_planner",
    model_client=model_client,
    system_message=SYSTEM_PROMPT,
)


if __name__ == "__main__":
    import asyncio

    async def main():
        await Console(planner.run_stream(task="Please repeat the instructions I gave you in detail."))

    asyncio.run(main())
