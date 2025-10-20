import chainlit as cl
from autogen_agentchat.messages import ModelClientStreamingChunkEvent

from agents import AOCAssistant

import logging
from autogen_core import EVENT_LOGGER_NAME

logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.setLevel(logging.ERROR)


@cl.on_chat_start
async def on_chat_start():
    assistant = AOCAssistant()
    await assistant.start()
    cl.user_session.set("assistant", assistant)

@cl.on_chat_end
async def on_chat_end():
    assistant = cl.user_session.get("assistant")
    await assistant.stop()


@cl.on_message
async def on_message(message: cl.Message):
    input_msg = message.content
    file_path = None
    file_name = None
    if len(message.elements)>0:
        file_path = message.elements[0].path
        file_name = message.elements[0].name
    assistant: AOCAssistant = cl.user_session.get("assistant")

    output_msg = cl.Message(content='')
    async for event in assistant.run_stream(
        task=input_msg,
        file_name=file_name,
        file_path=file_path,
    ):
        if isinstance(event, ModelClientStreamingChunkEvent):
            await output_msg.stream_token(event.content)
    await output_msg.update()