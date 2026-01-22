from typing import Sequence, MutableMapping, Any
from uuid import uuid4

from pydantic import BaseModel
from agent_framework import ChatMessage, ChatMessageStoreProtocol
from redisvl.extensions.message_history import MessageHistory

class RedisVLStoreState(BaseModel):
    thread_id: str | None
    top_k: int = 6
    session_tag: str | None
    redis_url: str | None

class RedisVLMessageStore(ChatMessageStoreProtocol):
    def __init__(
        self,
        thread_id: str = "common_thread",
        top_k: int = 6,
        session_tag: str | None = None,
        redis_url: str | None = "redis://localhost:6379",
    ):
        self._thread_id = thread_id
        self._top_k = top_k
        self._session_tag = session_tag or f"session_{uuid4()}"
        self._redis_url = redis_url

        self._init_message_history()

    async def list_messages(self) -> list[ChatMessage]:
        messages: list[dict[str, str]] = self._message_history.get_recent(
            top_k=self._top_k,
            session_tag=self._session_tag,
        )
        return [self._back_to_chat_message(message)
                for message in messages]

    async def add_messages(self, messages: Sequence[ChatMessage]):
        messages = [self._to_redis_message(message)
                    for message in messages]
        self._message_history.add_messages(
            messages,
            session_tag=self._session_tag
        )

    @classmethod
    async def deserialize(
        cls, serialized_store_state: MutableMapping[str, Any], **kwargs: Any
    ) -> "RedisVLMessageStore":
        if not serialized_store_state:
            raise ValueError("serialized_store_state is required for deserialization")

        state = RedisVLStoreState.model_validate(serialized_store_state)
        return cls(
            thread_id=state.thread_id,
            top_k=state.top_k,
            session_tag=state.session_tag,
            redis_url=state.redis_url
        )

    async def update_from_state(
        self, serialized_store_state: MutableMapping[str, Any], **kwargs: Any
    ) -> None:
        if not serialized_store_state:
            raise ValueError("serialized_store_state is required for ")

        state = RedisVLStoreState.model_validate(serialized_store_state)
        self._thread_id = state.thread_id
        self._redis_url = state.redis_url
        self._top_k = state.top_k
        self._session_tag = state.session_tag
        self._init_message_history()

    async def serialize(self, **kwargs: Any) -> dict[str, Any]:
        state = RedisVLStoreState(
            thread_id=self._thread_id,
            redis_url=self._redis_url,
            top_k=self._top_k,
            session_tag=self._session_tag,
        )
        return state.model_dump()

    def clear(self) -> None:
        self._message_history.clear()
        self._message_history.delete()

    def _init_message_history(self):
        self._message_history = MessageHistory(
            name=self._thread_id,
            redis_url=self._redis_url,
        )

    @staticmethod
    def _back_to_chat_message(message: dict[str, str]) -> ChatMessage:
        return ChatMessage(
            role="assistant" if message["role"]=="llm" else message["role"],
            text=message['content']
        )

    @staticmethod
    def _to_redis_message(message: ChatMessage) -> dict[str, str]:
        return {
            "role": "llm" if str(message.role)=="assistant" else str(message.role),
            "content": message.text
        }