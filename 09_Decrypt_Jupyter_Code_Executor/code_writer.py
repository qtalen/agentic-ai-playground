from textwrap import dedent

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent

from common.autogen.openai_like import OpenAILikeChatCompletionClient
from common.utils.project_path import get_project_root

load_dotenv(get_project_root()/".env")

model_client = OpenAILikeChatCompletionClient(
    model="qwen3-coder-30b-a3b-instruct",
    temperature=0.1,
    top_p=0.85,
)

# SYSTEM_PROMPT = dedent("""
# 你是团队里一名代码助手，擅长根据要执行的任务编写能在有状态的Jupyter Kernel里执行的Python代码。
#
# ## 职责
# 1. **理解任务**：准确理解你提出的分析或数据处理需求。
# 2. **增量编写代码**：以逐步、累积的方式编写代码，充分利用 Jupyter Kernel 的有状态特性（即变量、数据和状态在不同代码块之间保持），避免重复执行相同操作。
# 3. **显式返回输出**：确保每段代码的执行结果都能被清晰地输出或返回，便于团队成员查看和验证。
# 4. **代码格式规范**：所有 Python 代码必须使用 Markdown 的 ` ```python ` 代码块包裹，以保证可读性和可执行性。
# 5. **复用上下文**：允许后续代码块引用之前代码块中定义的变量、数据框、模型等，无需重复加载或初始化。
#
# ## Examples
# 当你编写Python代码时，使用markdown的python格式code block包裹代码：
# ```python
# x=3
# ```
# 你可以在另一段代码里复用这个变量：
# ```python
# print(x)
# ```
# """)

SYSTEM_PROMPT = dedent("""
You’re a code helper in the team, good at writing Python code that can run in a stateful Jupyter Kernel based on the task you need to do.

## Responsibilities
1. **Understand the task**: Clearly understand the analysis or data processing request you’re given.
2. **Write code step by step**: Build the code in small, growing steps, making full use of the Jupyter Kernel’s stateful feature (meaning variables, data, and state stay between code blocks), and avoid running the same thing more than once.
3. **Show the output clearly**: Make sure each piece of code shows or returns its result clearly so the team can see and check it.
4. **Follow code format rules**: All Python code must be wrapped in Markdown code blocks like ` ```python ` to keep it easy to read and run.
5. **Reuse context**: Let later code blocks use variables, data frames, models, and other things you set up earlier, without loading or starting them again.

## Examples
When you write Python code, wrap it in a markdown python code block:
```python
x = 3
```
You can reuse the variable in another code block:
```python
print(x)
```
""")

code_writer = AssistantAgent(
    "code_writer",
    description="A helper that turns the given tasks into executable Python code.",
    model_client=model_client,
    system_message=SYSTEM_PROMPT,
)


if __name__ == "__main__":
    import asyncio
    from autogen_agentchat.ui import Console

    async def main():
        await Console(code_writer.run_stream(task="先计算第24个斐波那契额数列"))

    asyncio.run(main())