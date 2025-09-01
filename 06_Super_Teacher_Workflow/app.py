import chainlit as cl
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent

from workflow_client import SuperTeacherFlow


MASK_MAPPING = {
    "thinker": "Thinking through the problem-solving steps...",
    "coder": "Running the code now...",
    "exe_agent": "Getting the calculation results...",
    "reviewer": "Checking the calculation results..."
}


@cl.on_chat_start
async def on_chat_start():
    flow = SuperTeacherFlow()
    await flow.start()
    cl.user_session.set("workflow", flow)

@cl.on_chat_end
async def on_chat_end():
    flow = cl.user_session.get("workflow")
    await flow.stop()

@cl.on_message
async def main(message: cl.Message):
    workflow = cl.user_session.get("workflow")
    show_text = "Thinking..."
    msg = cl.Message(content=show_text)
    await msg.send()
    streaming = False

    async for event in workflow.run_stream(task=message.content):
        if isinstance(event, TaskResult):
            continue

        if event.source and event.source in MASK_MAPPING.keys():
            show_text = MASK_MAPPING[event.source]
            msg.content = show_text
            await msg.update()
        if isinstance(event, ModelClientStreamingChunkEvent):
            if not streaming:
                show_text = ""
                msg.content = show_text
                await msg.update()
                streaming = True
            await msg.stream_token(event.content)
    await msg.update()
