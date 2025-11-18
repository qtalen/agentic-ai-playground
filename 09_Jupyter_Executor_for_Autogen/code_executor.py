from pathlib import Path

from autogen_ext.code_executors.docker_jupyter import (
    DockerJupyterCodeExecutor, DockerJupyterServer
)
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.code_executors.docker_jupyter._jupyter_server import JupyterConnectionInfo
from autogen_agentchat.agents import CodeExecutorAgent

server = DockerJupyterServer(
    custom_image_name="jupyter-server",
    expose_port=8888,
    token="UNSET",
    bind_dir="temp",
)

executor = DockerJupyterCodeExecutor(
    jupyter_server=server,
    timeout=600,
    output_dir=Path("temp")
)

# executor = DockerJupyterCodeExecutor(
#     jupyter_server=JupyterConnectionInfo(
#         host='127.0.0.1',
#         use_https=False,
#         port=8888,
#         token='UNSET'
#     ),
#     timeout=600,
#     output_dir=Path("temp"),
# )

code_executor = CodeExecutorAgent(
    "code_executor",
    code_executor=executor,
)


if __name__ == "__main__":
    import asyncio
    from textwrap import dedent

    async def main():
        async with executor:
            code1 = TextMessage(
                content=dedent("""
                ```python
                x = 1+2
                print("Round one: The calculation for the value of x is done.")
                ```
                """),
                source="user"
            )
            response1 = await code_executor.on_messages(messages=[code1], cancellation_token=CancellationToken())
            print(response1.chat_message.content)

            code2 = TextMessage(
                content=dedent("""
                ```python
                print("Round two: Get the value of variable x again: x=", x)
                ```
                """),
                source="user",
            )
            response2 = await code_executor.on_messages(messages=[code2], cancellation_token=CancellationToken())
            print(response2.chat_message.content)

    asyncio.run(main())
