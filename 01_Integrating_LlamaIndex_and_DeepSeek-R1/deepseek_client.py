import time

import chainlit as cl
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    AgentStream
)
from llama_index.core.workflow import Context

from agents import search_agent
from reasoning_adapter import ReasoningStreamAdapter

GREETINGS = "Hello, what can I do for you?"


def ready_my_workflow() -> tuple[AgentWorkflow, Context]:
    workflow = AgentWorkflow(
        agents=[search_agent],
        root_agent=search_agent.name
    )
    context = Context(workflow)
    return workflow, context


@cl.on_chat_start
async def on_chat_start():
    workflow, context = ready_my_workflow()
    cl.user_session.set("workflow", workflow)
    cl.user_session.set("context", context)

    await cl.Message(
        author="assistant", content=GREETINGS
    ).send()


@cl.on_message
async def main(message: cl.Message):
    workflow: AgentWorkflow = cl.user_session.get("workflow")
    context: Context = cl.user_session.get("context")

    start = time.monotonic()
    handler = workflow.run(
        user_msg=message.content,
        ctx=context
    )

    output = cl.Message(content="")
    async with cl.Step(name="Thinking", show_input=False) as current_step:
        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                adapter = ReasoningStreamAdapter(event)
                if adapter.reasoning_content:
                    await current_step.stream_token(adapter.reasoning_content)
                else:
                    await output.stream_token(adapter.delta)
        last = time.monotonic() - start
        current_step.name = f"Thinking, {last: .2f}s"
    await output.send()



