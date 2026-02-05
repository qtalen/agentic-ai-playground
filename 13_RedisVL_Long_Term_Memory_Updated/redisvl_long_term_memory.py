import asyncio
import os
import time
from typing import Any, MutableSequence, cast

from pydantic import BaseModel, Field
from agent_framework import (
    ContextProvider, Context,
    Role, ChatMessage
)
from rich.console import Console
from redisvl.extensions.message_history import SemanticMessageHistory
from redisvl.utils.vectorize import HFTextVectorizer

from common.models import Qwen3
from common.agent_framework.openai_like import OpenAILikeChatClient


console = Console()

class ExtractResult(BaseModel):
    should_write_memory: bool = Field(..., description="Is there any memory worth saving?")
    memory_to_write: str = Field(..., description="Use one short, clear sentence in natural language to describe the single fact you want to store as a memory.")
    reason: str = Field(..., description="The reason why it is or isn’t worth saving as a memory.")


class LongTermMemory(ContextProvider):
    def __init__(
        self,
        thread_id: str | None = None,
        session_tag: str | None = None,
        distance_threshold: float = 0.3,
        context_prompt: str = ContextProvider.DEFAULT_CONTEXT_PROMPT,
        redis_url: str = "redis://localhost:6379",
        embedding_model: str = "BAAI/bge-m3",
        llm_model: str = Qwen3.NEXT,
        llm_api_key: str | None = None,
        llm_base_url: str | None = None,
    ):
        self._thread_id = thread_id or "semantic_thread"
        self._session_tag = session_tag or f"session_common_user"
        self._distance_threshold = distance_threshold
        self._context_prompt = context_prompt
        self._redis_url = redis_url
        self._embedding_model = embedding_model
        self._llm_model = llm_model
        self._llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self._llm_base_url = llm_base_url or os.getenv("OPENAI_API_URL")

        self._init_sematic_store()
        self._init_extractor()

    async def invoking(
        self,
        messages: ChatMessage | MutableSequence[ChatMessage],
        **kwargs: Any
    ) -> Context:
        if isinstance(messages, ChatMessage):
            messages = [messages]
        prompt = "\n".join([m.text for m in messages])

        line_sep_memories = self._get_line_sep_memories(prompt)

        start = time.monotonic()
        asyncio.create_task(self._save_memory(messages, line_sep_memories))
        console.print(f"[bright_cyan]It took {time.monotonic() - start} seconds to retrieve the memory.\n")
        return Context(messages=[
            ChatMessage(role="user", text=f"{self._context_prompt}\n{line_sep_memories}")
        ] if len(line_sep_memories)>0 else None)

    async def _save_memory(
        self,
        messages: ChatMessage | MutableSequence[ChatMessage],
        relevant_memory: str | None = None,
    ) -> None:
        detect_messages = (
            [
            ChatMessage(role=Role.USER, text=f"Existing related memories：\n\n{relevant_memory}"),
            ] + list(messages)
            if relevant_memory.strip()
            else list(messages)
        )
        response = await self._extractor.run(detect_messages)

        extract_result: ExtractResult = cast(ExtractResult, response.value)
        console.print(f"[bright_green]{response}")
        if extract_result.should_write_memory:
            self._semantic_store.add_messages(
                messages=[
                    {"role": "user", "content": extract_result.memory_to_write}
                ],
                session_tag=self._session_tag,
            )

    def _get_line_sep_memories(self, prompt: str) -> str:
        context = self._semantic_store.get_relevant(prompt, role="user", session_tag=self._session_tag)
        line_sep_memories = "\n".join([f"* {str(m.get("content", ""))}" for m in context])
        console.print("[bright_yellow]===============>line sep memories:<===========")
        console.print(f"[bright_yellow]{line_sep_memories}\n\n")
        return line_sep_memories

    def _init_sematic_store(self) -> None:
        self._semantic_store = SemanticMessageHistory(
            name=self._thread_id,
            session_tag=self._session_tag,
            distance_threshold=self._distance_threshold,
            redis_url=self._redis_url,
            vectorizer=HFTextVectorizer(
                model=self._embedding_model,
            )
        )

    def _init_extractor(self):
        with open("prompt.md", "r", encoding="utf-8") as f:
                system_prompt = f.read()

        self._extractor = OpenAILikeChatClient(
            model_id=self._llm_model,
        ).as_agent(
            name="extractor",
            instructions=system_prompt,
            default_options={
                "response_format": ExtractResult,
                "extra_body": {"enable_thinking": False}
            },
        )