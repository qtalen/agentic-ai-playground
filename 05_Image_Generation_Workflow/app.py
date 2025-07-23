import os
from textwrap import dedent

import chainlit as cl
from llama_index.core.workflow import (Context, StopEvent)

from workflow import ImageGeneration, StreamEvent

@cl.on_chat_start
async def on_chat_start():
    workflow = ImageGeneration(timeout=300)
    context = Context(workflow)
    cl.user_session.set("context", context)
    cl.user_session.set("workflow", workflow)


@cl.on_message
async def main(message: cl.Message):
    workflow = cl.user_session.get("workflow")
    context = cl.user_session.get("context")
    msg = cl.Message(content="Generating...")
    await msg.send()
    prompt_result = ""
    translate_result = ""

    handler = workflow.run(query=message.content, ctx=context)
    async for event in handler.stream_events():
        if isinstance(event, StreamEvent):
            # # await msg.stream_token(event.delta)
            match event.target:
                case "prompt":
                    prompt_result += event.delta
                case "translate":
                    translate_result += event.delta
            msg.content = dedent(f"""
### Prompt\n
{prompt_result}

### Translate
{translate_result}

APPROVE?
            """)
            await msg.update()
        if isinstance(event, StopEvent) and event.target == "image":
            image = cl.Image(url=event.result["image_url"], name="image1", display="inline")
            msg.content = f"Revised prompt: \n{event.result['revised_prompt']}"
            msg.elements = [image]
            await msg.update()

    await handler
