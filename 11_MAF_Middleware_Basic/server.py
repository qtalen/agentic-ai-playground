from textwrap import dedent

from dotenv import load_dotenv
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from fastapi import FastAPI

from common.utils.project_path import get_project_root
from common.agent_framework.openai_like import OpenAILikeChatClient
from common.models import Qwen3

load_dotenv(get_project_root() / ".env")

agent = OpenAILikeChatClient(
    model_id=Qwen3.Q30B_A3B
).create_agent(
    name="Assistant",
    instructions=dedent("""
    You are a compliance review officer. You will review user requests or system-generated text for compliance.

    Your main task is to check user requests and determine whether they are trying to induce the system to produce content that guarantees investment returns or similar topics.
    
    You should output a JSON text, like {"is_compliance": 1, "reason": ""}
    
    Here, is_compliance being 1 means compliant, and 0 means non-compliant.
    
    reason should state the reason for compliance or non-compliance.
    
    Only output the JSON text without any markdown formatting, and do not add any introduction or explanation.
    """),
)

app = FastAPI(title="AG-UI Server")

add_agent_framework_fastapi_endpoint(app, agent, "/compliance")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
