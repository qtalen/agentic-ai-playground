import asyncio
from datetime import date

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, MessageFilterAgent, MessageFilterConfig, PerSourceFilter
from autogen_agentchat.teams import (
    DiGraphBuilder,
    GraphFlow
)
from autogen_agentchat.ui import Console
import mlflow

from common.autogen.openai_like import OpenAILikeChatCompletionClient
# import utils.autogen_patching


load_dotenv("../.env")
mlflow.autogen.autolog()
mlflow.set_experiment("test_autogen_tracing")

model_client_config = {
    "model": "qwen3-30b-a3b-instruct-2507",
    "temperature": 0.5
}

model_client = OpenAILikeChatCompletionClient(**model_client_config)

generator = AssistantAgent(
    "generator",
    model_client=model_client,
    system_message="""
    Generate a list of creative ideas.
    """
)

reviewer = AssistantAgent(
    "reviewer",
    model_client=model_client,
    system_message="""
    Review ideas and provide feedbacks, or just 'APPROVE' for final approval.
    """
)

summarizer_core = AssistantAgent(
    "summary",
    model_client=model_client,
    system_message="""
    Summarize the user request and the final feedback.
    """
)

filtered_summarizer = MessageFilterAgent(
    name="summary",
    wrapped_agent=summarizer_core,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="generator", position="last", count=1),
        ]
    )
)

builder = DiGraphBuilder()
builder.add_node(generator).add_node(reviewer).add_node(filtered_summarizer)
builder.add_edge(generator, reviewer)
builder.add_edge(reviewer, filtered_summarizer, condition=lambda msg: "APPROVE" in msg.to_model_text())
builder.add_edge(reviewer, generator, condition=lambda msg: "APPROVE" not in msg.to_model_text())
builder.set_entry_point(generator)
graph = builder.build()

flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
    max_turns=30
)

async def main():
    with mlflow.start_span(name="main") as current_span:
        mlflow.update_current_trace(
            tags={
                "date": date.today().strftime('%Y%m%d'),
                "model": model_client_config.get('model'),
            }
        )
        task = "Brainstorm ways to reduce plastic waste."
        current_span.set_inputs({"task": task})
        result = await Console(flow.run_stream(task="Brainstorm ways to reduce plastic waster."))
        generates = [msg for msg in result.messages if msg.source == "generator"]
        final_generate = generates[-1]
        summary = [msg for msg in result.messages if msg.source == "summary"][0]
        current_span.set_outputs({
            "generate": final_generate.content,
            "summary": summary.content,
        })
        current_span.set_attributes({
            "rounds": str(len(generates)),
            **model_client_config,
        })


if __name__ == "__main__":
    asyncio.run(main())
