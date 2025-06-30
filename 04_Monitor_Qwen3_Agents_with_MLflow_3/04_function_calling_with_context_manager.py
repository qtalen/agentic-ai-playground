import asyncio
import json
import copy
from datetime import date

from dotenv import load_dotenv
import openai
from openai.types.chat import ChatCompletionMessage
from tavily import AsyncTavilyClient
import mlflow
from mlflow.entities import SpanType

load_dotenv("../.env")
mlflow.set_experiment("test_openai_tracing")
mlflow.openai.autolog()


@mlflow.trace(span_type=SpanType.TOOL)
async def search_web(query: str) -> str:
    web_client = AsyncTavilyClient()
    response = await web_client.search(query)
    return str(response["results"])


tools = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Find information on the web.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What you want to search for."
                }
            },
            "required": ["query"]
        }
    }
}]

_tool_functions = {"search_web": search_web}

async_client = openai.AsyncOpenAI()
MODEL_NAME = "qwen-plus-latest"

# @mlflow.trace(span_type=SpanType.LLM)
async def call_llm(messages: list[dict], tools: list[dict] | None = None) \
        -> ChatCompletionMessage:
    response = await async_client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.01,
        messages=messages,
        tools=tools,
    )
    return response.choices[0].message

# @mlflow.trace(span_type=SpanType.TOOL)
async def tool_invoke(message: ChatCompletionMessage, messages: list[dict]) -> list[dict]:
    result_messages = copy.deepcopy(messages)
    tool_calls = message.tool_calls
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        tool_func = _tool_functions[function_name]
        args = json.loads(tool_call.function.arguments)
        tool_result = await tool_func(**args)
        result_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result,
        })
    return result_messages


@mlflow.trace(span_type=SpanType.AGENT)
async def search_agent(query: str) -> str:
    mlflow.update_current_trace(
        tags={
            "date": date.today().strftime("%Y%M%d"),
            "model": MODEL_NAME
        }
    )
    with mlflow.start_span(name="get_tool_calls", span_type=SpanType.LLM) as span:
        span.set_inputs({
            "query": query
        })
        messages = [{
            "role": "system",
            "content": "You are a helpful assistant, and you use search_web tool to find information on the web.",
        }, {
            "role": "user",
            "content": query,
        }]

        message = await call_llm(messages, tools)
        if len(message.content) > 0:
            span.set_outputs({
                "results": message.content
            })
            return message.content

        messages.append(message.model_dump())
        span.set_outputs({
            "tool_calls": message.tool_calls,
        })
        span.set_attributes({
            "num_of_tool_calls": len(message.tool_calls),
        })

    with mlflow.start_span(name="invoke_tools", span_type=SpanType.TOOL) as span:
        span.set_inputs({
            "tool_calls": message.tool_calls
        })
        messages = await tool_invoke(message, messages)
        tool_call_results = messages[-1: -1 - len(message.tool_calls)]
        span.set_outputs({
            "tool_call_results": tool_call_results
        })
        span.set_attributes({
            "num_of_tool_call_results": len(tool_call_results),
        })

    with mlflow.start_span(name="reflect_tool_calls", span_type=SpanType.LLM) as span:
        span.set_inputs({
            "messages": messages,
        })
        message = await call_llm(messages)
        span.set_outputs({
            "answer": message.content
        })
    return message.content


if __name__ == "__main__":
    answer = asyncio.run(search_agent("What versions does Qwen 3 have??"))
    print(answer)
