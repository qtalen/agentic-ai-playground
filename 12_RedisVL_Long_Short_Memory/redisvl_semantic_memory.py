import os
from typing import Sequence, Any, MutableSequence
from types import TracebackType
from uuid import uuid4

from agent_framework import ContextProvider, Context, ChatMessage

from redisvl.extensions.message_history import SemanticMessageHistory
from redisvl.utils.vectorize import OpenAITextVectorizer, HFTextVectorizer


class RedisVLSemanticMemory(ContextProvider):
    def __init__(
        self,
        thread_id: str | None = None,
        session_tag: str | None = None,
        distance_threshold: float = 0.3,
        redis_url: str = "redis://localhost:6379",
        embedding_model: str = "BAAI/bge-m3",
        embedding_api_key: str | None = None,
        embedding_endpoint: str | None = None,
    ):
        self._thread_id = thread_id or "semantic_thread"
        self._session_tag = session_tag or f"session_{uuid4()}"
        self._distance_threshold = distance_threshold
        self._redis_url = redis_url
        self._embedding_model = embedding_model
        self._embedding_api_key = embedding_api_key or os.getenv("EMBEDDING_API_KEY")
        self._embedding_endpoint = embedding_endpoint or os.getenv("EMBEDDING_ENDPOINT")

        self._init_semantic_store()

    async def invoked(
        self,
        request_messages: ChatMessage | Sequence[ChatMessage],
        response_messages: ChatMessage | Sequence[ChatMessage] | None = None,
        invoke_exception: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        if isinstance(request_messages, ChatMessage):
            request_messages = [request_messages]
        if isinstance(response_messages, ChatMessage):
            response_messages = [response_messages]
        chat_messages = request_messages + response_messages
        messages = [self._to_redis_message(message)
                    for message in chat_messages]
        self._semantic_store.add_messages(
            messages=messages,
            session_tag=self._session_tag,
        )

    async def invoking(
        self,
        messages: ChatMessage | MutableSequence[ChatMessage],
        **kwargs: Any
    ) -> Context:
        if isinstance(messages, ChatMessage):
            messages = [messages]
        prompt = "\n".join([message.text
                            for message in messages])
        context = self._semantic_store.get_relevant(
            prompt=prompt,
            raw=True,
            session_tag=self._session_tag,
        )
        context = sorted(context, key=lambda m: m['timestamp'])
        relevant_messages = [self._back_to_chat_message(message)
                             for message in context]
        print("=====>The retrieved messages: ")
        print([m.text for m in relevant_messages])

        return Context(messages=relevant_messages)

    def clear(self):
        self._semantic_store.clear()
        self._semantic_store.delete()

    async def __aenter__(self) -> "Self":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.clear()

    @staticmethod
    def _back_to_chat_message(message: dict[str, str]) -> ChatMessage:
        return ChatMessage(
            role="assistant" if message["role"]=="llm" else message["role"],
            text=message['content']
        )

    @staticmethod
    def _to_redis_message(message: ChatMessage) -> dict[str, str]:
        return {
            "role": "llm" if message.role.value=="assistant" else message.role.value,
            "content": message.text
        }

    def _init_semantic_store(self) -> None:
        if not self._embedding_api_key:
            vectorizer = HFTextVectorizer(
                model=self._embedding_model,
            )
        else:
            vectorizer = OpenAITextVectorizer(
                model=self._embedding_model,
                api_config={
                    "api_key": self._embedding_api_key,
                    "base_url": self._embedding_endpoint
                }
            )

        self._semantic_store = SemanticMessageHistory(
            name=self._thread_id,
            session_tag=self._session_tag,
            distance_threshold=self._distance_threshold,
            redis_url=self._redis_url,
            vectorizer=vectorizer,
        )