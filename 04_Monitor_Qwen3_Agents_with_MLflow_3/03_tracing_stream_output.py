import asyncio
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
import openai
from openai.types.chat import *
import mlflow
from mlflow.entities import SpanType
from openai.types.chat import ChatCompletionChunk

load_dotenv("../.env")

mlflow.set_experiment("test_openai_tracing")
mlflow.openai.autolog()

async_client = openai.AsyncClient()


def aggregate_chunks(outputs: list[ChatCompletionChunk]) -> str | None:
    if not outputs:
        return None

    result = ""
    for chunk in outputs:
        result += chunk.choices[0].delta.content

    return result


@mlflow.trace(span_type=SpanType.LLM, output_reducer=aggregate_chunks)
async def predict(query: str) -> AsyncGenerator[tuple[str, Any] | ChatCompletionChunk, None]:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    stream = await async_client.chat.completions.create(
        model="qwen-plus-latest",
        temperature=0.8,
        messages=messages,
        stream=True
    )
    async for chunk in stream:
        yield chunk

async def main():
    task = "Write a little poem about a summer night."
    stream = predict(task)
    async for chunk in stream:
        print(chunk.choices[-1].delta.content, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
