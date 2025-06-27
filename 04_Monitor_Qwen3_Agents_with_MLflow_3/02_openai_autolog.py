import asyncio

from dotenv import load_dotenv
import openai
import mlflow
from mlflow.entities import SpanType

load_dotenv("../.env")
mlflow.set_experiment("test_openai_tracing")
mlflow.openai.autolog()

async_client = openai.AsyncClient()


def truncate_str(text: str, max_length: int = 45) -> str:
    return text if max_length <= 3 else f"{text[:max_length]}..."


@mlflow.trace(span_type=SpanType.AGENT)
async def chatbot(user_query: str, messages: list[dict[str, str]]) -> str:
    messages.append({
        "role": "user",
        "content": user_query,
    })

    response = await async_client.chat.completions.create(
        model="qwen-turbo-latest",
        temperature=0.7,
        messages=messages,
        max_tokens=100,
    )

    llm_content = response.choices[0].message.content
    messages.append({
        "role": "assistant",
        "content": llm_content
    })

    return f"🤖Tony says: {truncate_str(llm_content)}"


@mlflow.trace(span_type=SpanType.CHAIN)
async def main():
    greetings = "Hello, what can I help you with today?"
    messages = [
        {"role": "system", "content": "You are Tony, a fun chatbot."},
        {"role": "assistant", "content": greetings},
    ]

    print(f"🤖Tony says: {greetings}")

    while True:
        user_query = input(">>> ")
        if "BYE" in user_query.upper():
            break

        tony_says = await chatbot(user_query, messages)
        print(tony_says)


if __name__ == "__main__":
    asyncio.run(main())
