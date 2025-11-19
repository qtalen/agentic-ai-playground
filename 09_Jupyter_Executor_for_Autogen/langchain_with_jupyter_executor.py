import asyncio
import os
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker_jupyter import DockerJupyterCodeExecutor
from autogen_ext.code_executors.docker_jupyter._jupyter_server import JupyterConnectionInfo
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

from common.utils.project_path import get_project_root

load_dotenv(get_project_root() / ".env")


executor = DockerJupyterCodeExecutor(
    jupyter_server=JupyterConnectionInfo(
        host='127.0.0.1',
        use_https=False,
        port=8888,
        token='UNSET'
    ),
    timeout=600,
    output_dir=Path("temp")
)

@tool
async def execute_code(code: str) -> str:
    """
    Use the Jupyter code executor to run your Python code.
    The runtime environment keeps its state, so you can run code step by step.
    reuse variables from earlier code blocks, and avoid writing the same code again.
    :param code: Code waiting to be run, only the code itself, no Markdown syntax
    :return: The result of the code execution.
    """
    code_blocks = [CodeBlock(code=code, language="python")]
    code_result = await executor.execute_code_blocks(code_blocks, cancellation_token=CancellationToken())

    return code_result.output


model = ChatOpenAI(
    model="qwen3-next-80b-a3b-instruct",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0.1,
    top_p=0.85,
)

agent = create_agent(
    model=model,
    tools=[execute_code],
    system_prompt=dedent("""
    You are a data analysis assistant, good at solving user questions with Python code.
    You use the `execute_code` tool to run the code and summarize the results as the answer.
    """)
)


if __name__ == "__main__":
    async def main():
        async with executor:
            result = await agent.ainvoke(
                {"messages": [
                    {"role": "user", "content": "Calculate the value of the 14th Fibonacci number."}
                ]}
            )
            for msg in result['messages']:
                print(msg.content)

    asyncio.run(main())