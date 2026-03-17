import os
from typing import Any
import logging
import json

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http import Compression
from opentelemetry import trace
from agent_framework import observability
from agent_framework._types import AgentRunInputs, FinishReason, prepend_instructions_to_messages
from agent_framework.observability import (
    configure_otel_providers,
    _to_otel_message,
    OtelAttr,
    ROLE_EVENT_MAP,
    FINISH_REASON_MAP,
    MessageListTimestampFilter,
    logger,
)

def list_to_str(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for index, message in enumerate(messages, start=1):
        block: list[str] = [f'### *-{index:02d}-* [{message.get("role", "")}]:']
        for part in message["parts"]:
            if part["type"] == "text":
                block.append(str(part["content"]))
            else:
                block.append(json.dumps(part, ensure_ascii=False))
        parts.append("\n".join(block))
    return "\n\n--------\n\n".join(parts)

def _capture_messages_utf8(
    span: trace.Span,
    provider_name: str,
    messages: AgentRunInputs,
    system_instructions: str | list[str] | None = None,
    output: bool = False,
    finish_reason: FinishReason | None = None,
) -> None:
    """Log messages with extra information."""
    from agent_framework._types import normalize_messages, prepend_instructions_to_messages

    # prepped = prepend_instructions_to_messages(normalize_messages(messages), system_instructions)
    prepped = normalize_messages(messages)
    otel_messages: list[dict[str, Any]] = []
    for index, message in enumerate(prepped):
        # Reuse the otel message representation for logging instead of calling to_dict()
        # to avoid expensive Pydantic serialization overhead
        otel_message = _to_otel_message(message)
        otel_messages.append(otel_message)
        logger.info(
            otel_message,
            extra={
                OtelAttr.EVENT_NAME: OtelAttr.CHOICE if output else ROLE_EVENT_MAP.get(message.role),
                OtelAttr.PROVIDER_NAME: provider_name,
                MessageListTimestampFilter.INDEX_KEY: index,
            },
        )
    if finish_reason:
        otel_messages[-1]["finish_reason"] = FINISH_REASON_MAP[finish_reason]

    # message_text = ""
    # for index, message in enumerate(otel_messages, start=1):
    #     message_text += f"### *-{index:02d}-* [{message["role"]}]:\n"
    #     for part in message["parts"]:
    #         if part["type"] == "text":
    #             message_text += f"{part["content"]}\n"
    #         else:
    #             message_text += f"{json.dumps(part, ensure_ascii=False)}\n"
    #     message_text += f"\n---\n"

    message_text = list_to_str(otel_messages)

    # span.set_attribute(OtelAttr.OUTPUT_MESSAGES if output else OtelAttr.INPUT_MESSAGES, json.dumps(otel_messages, ensure_ascii=False))
    span.set_attribute(OtelAttr.OUTPUT_MESSAGES if output else OtelAttr.INPUT_MESSAGES,
                       message_text)
    if system_instructions:
        if not isinstance(system_instructions, list):
            system_instructions = [system_instructions]
        otel_sys_instructions = [{
            "role": "system",
            "parts": [{"type": "text", "content": instruction} for instruction in system_instructions]
        }]
        instructions_str = list_to_str(otel_sys_instructions)
        # span.set_attribute(OtelAttr.SYSTEM_INSTRUCTIONS, json.dumps(otel_sys_instructions, ensure_ascii=False))
        span.set_attribute(OtelAttr.SYSTEM_INSTRUCTIONS, instructions_str)

observability._capture_messages = _capture_messages_utf8

def mlflow_log(experiment_id: str = "0"):
    endpoint = os.environ.get("MLFLOW_TRACKING_URI")
    exporters = [
        OTLPSpanExporter(
            endpoint=f"{endpoint}/v1/traces",
            headers={
                "x-mlflow-experiment-id": experiment_id
            },
            compression=Compression.Gzip
        ),
    ]
    configure_otel_providers(exporters=exporters, enable_sensitive_data=True)