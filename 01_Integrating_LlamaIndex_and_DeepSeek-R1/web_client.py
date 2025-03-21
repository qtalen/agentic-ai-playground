import time

from dotenv import load_dotenv
from llama_index.core.llms import ChatMessage
import chainlit as cl

from deepseek import DeepSeek

load_dotenv("../.env")

client = DeepSeek(
    model="deepseek-reasoner",
    is_chat_model=True,
    temperature=0.6
)


@cl.on_message
async def main(message: cl.Message):
    responses = await client.astream_chat(
        messages=[
            ChatMessage(role="user", content=message.content)
        ]
    )

    output = cl.Message(content="")
    async with cl.Step(name="Thinking", show_input=False) as current_step:
        async for response in responses:
            if (reasoning_content := response.reasoning_content) is not None:
                await current_step.stream_token(reasoning_content)
            else:
                await output.stream_token(response.delta)

    await output.send()

