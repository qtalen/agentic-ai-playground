import asyncio
import os
from functools import lru_cache
from textwrap import dedent
from pathlib import Path
import shutil

from dotenv import load_dotenv
from agent_framework import (
    SkillsProvider, Skill, SkillResource,
    SkillScript
)
from common.agent_framework import (
    OpenAILikeChatClient,
    mlflow_log,
    UpdatableSkillsProvider,
)
from common.utils import (
    get_project_root, get_current_directory,
    CodeExecutionTool, DockerCommandLineCodeExecutor,
)
from common.models import Qwen3_5

load_dotenv(get_project_root() / ".env")

mlflow_log()

chat_client = OpenAILikeChatClient(
    model_id=Qwen3_5.Q397B_A17B,
)

@lru_cache
async def get_latest_skills() -> list[Skill]:
    """
    Pseudocode. In this hook method, you can read the skills text from the database
    and dynamically build Skill objects.
    :return:
    """
    code_style_skill = Skill(
        name="code-style",
        description="Coding style guidelines and conventions for the team",
        content=dedent("""\
            Use this skill when answering questions about coding style,
            conventions, or best practices for the team.
        """),
    )
    return [code_style_skill]

work_dir = get_current_directory()/"temp/docker_temp"

def my_runner(skill: Skill, script: SkillScript, args: dict | None = None) -> str:
    src = Path(skill.path) / script.path
    dst = Path(work_dir / script.path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)


skills_provider = UpdatableSkillsProvider(
    skill_paths=get_current_directory() / ".agents/skills",
    skills_updater=get_latest_skills,
)

code_executor = DockerCommandLineCodeExecutor(
    image="python-code-sandbox",
    work_dir=work_dir,
    delete_tmp_files=True,
    environment={
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
    }
)

code_tool = CodeExecutionTool(code_executor).execute_code

skills_agent = chat_client.as_agent(
    name="SkillsAssistant",
    instructions="You're a helpful assistant, and you'll respond to user requests according to your skills.",
    context_providers=[skills_provider],
    tools=[code_tool],
)

agent = chat_client.as_agent(
    name="Assistant",
    instructions=dedent("""
    You're a smart little helper who, for each user request, 
    picks the right task description to call a tool, gets the answer, 
    and then delivers the final result.
    """),
    tools=[skills_agent.as_tool()],
)

async def main():
    async with code_executor:
        session = agent.create_session()
        result = await agent.run(
            "Check how gold ETFs performed in February 2026 and give some investment advice.",
            session=session
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())