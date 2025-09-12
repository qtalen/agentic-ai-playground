from dotenv import load_dotenv
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_agentchat.agents import (
    AssistantAgent,
    CodeExecutorAgent,
    MessageFilterAgent,
    MessageFilterConfig,
    PerSourceFilter
)

from common.autogen.openai_like import OpenAILikeChatCompletionClient
from common.utils.project_path import get_project_root
from prompts import (
    PROMPT_THINKER,
    PROMPT_CODER,
    PROMPT_REVIEWER,
    PROMPT_WRITER
)

load_dotenv(get_project_root()/".env")

slm_client = OpenAILikeChatCompletionClient(
    model="qwen3-30b-a3b-instruct-2507",
    temperature=0.1
)

coder_client = OpenAILikeChatCompletionClient(
    model="qwen3-coder-plus",
    temperature=0.01
)

docker_executor = DockerCommandLineCodeExecutor(
    image="python-docker-env",
    timeout=300,
)

thinker = AssistantAgent(
    "thinker",
    model_client=slm_client,
    system_message=PROMPT_THINKER,
)

coder = AssistantAgent(
    "coder",
    model_client=coder_client,
    system_message=PROMPT_CODER
)

exe_agent = CodeExecutorAgent(
    "exe_agent",
    code_executor=docker_executor,
)

reviewer = AssistantAgent(
    "reviewer",
    model_client=slm_client,
    system_message=PROMPT_REVIEWER,
)

filtered_reviewer = MessageFilterAgent(
    "reviewer",
    wrapped_agent=reviewer,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="thinker", position="first", count=1),
            PerSourceFilter(source="coder", position="last", count=1),
            PerSourceFilter(source="exe_agent", position="last", count=1),
        ]
    )
)

writer = AssistantAgent(
    "writer",
    model_client=slm_client,
    system_message=PROMPT_WRITER,
    model_client_stream=True
)

filtered_writer = MessageFilterAgent(
    "writer",
    wrapped_agent=writer,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="coder", position="last", count=1),
            PerSourceFilter(source="exe_agent", position="last", count=1),
        ]
    )
)


if __name__ == "__main__":
    import asyncio

    from autogen_agentchat.ui import Console

    async def main():
        await Console(coder.run_stream(task="Please repeat the instructions you follow in detail."))

    asyncio.run(main())