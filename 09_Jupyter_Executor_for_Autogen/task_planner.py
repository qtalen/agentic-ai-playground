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

planner = AssistantAgent(
    "task_planner",
    model_client=model_client,
    system_message=SYSTEM_PROMPT,
)


if __name__ == "__main__":
    import asyncio

    async def main():
        await Console(planner.run_stream(task="学校组织两个课外兴趣小组去郊外活动。第一小组每小时走4.5千米，第二小组每小时行3.5千米。\
    两组同时出发1小时后，第一小组停下来参观一个果园，用了1小时，再去追第二小组，多长时间能追上第二小组?"))

    asyncio.run(main())
