import asyncio

from dotenv import load_dotenv
import openai
import mlflow


load_dotenv("../.env")

mlflow.set_experiment("test_openai_tracing")

async_client = openai.AsyncOpenAI()


@mlflow.trace
async def main(user_query: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_query},
    ]

    response = await async_client.chat.completions.create(
        model="qwen-pluss-latest",
        temperature=0.7,
        messages=messages,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = asyncio.run(main("Please write a short poem about a summer night."))
    print(result)
