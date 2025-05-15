import asyncio
from typing import Literal
from textwrap import dedent

from dotenv import load_dotenv
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from utils.openai_like import OpenAILikeChatCompletionClient

load_dotenv("../.env")

model_client = OpenAILikeChatCompletionClient(
    model="qwen-plus-latest"
)

class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]

function_calling_agent = AssistantAgent(
    name="function_calling_agent",
    model_client=model_client,
    system_message="Categorize the input as happy, sad, or neutral following json format.",
    tools=[AgentResponse],
)

json_schema_agent = AssistantAgent(
    name="json_schema_agent",
    model_client=model_client,
    system_message=dedent(f"""
    Categorize the input as happy, sad, or neutral,
    And follow the JSON format defined by the following JSON schema:
    {AgentResponse.model_json_schema()}
    """)
)

structured_output_agent = AssistantAgent(
    name="structured_output_agent",
    model_client=model_client,
    system_message="Categorize the input as happy, sad, or neutral following json format.",
    output_content_type=AgentResponse
)


async def main():
    # await Console(
    #     function_calling_agent.run_stream(task="I'm happy.")
    # )
    # result = await Console(json_schema_agent.run_stream(task="I'm happy."))
    # structured_result = AgentResponse.model_validate_json(
    #     result.messages[-1].content
    # )
    # print(structured_result.thoughts)
    # print(structured_result.response)
    result = await Console(
        structured_output_agent.run_stream(task="I'm happy")
    )
    print(isinstance(result.messages[-1].content, AgentResponse))


if __name__ == "__main__":
    asyncio.run(main())

