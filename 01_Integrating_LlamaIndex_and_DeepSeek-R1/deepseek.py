from typing import (
    Sequence,
    Any,
    Optional
)

from llama_index.llms.openai_like import OpenAILike
from llama_index.llms.openai.base import llm_retry_decorator
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponseAsyncGen,
    ChatResponseGen,
    ChatResponse
)


class ReasoningChatResponse(ChatResponse):
    reasoning_content: Optional[str] = None


class DeepSeek(OpenAILike):
    @llm_retry_decorator
    def _stream_chat(
            self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        responses = super()._stream_chat(messages, **kwargs)

        def gen() -> ChatResponseGen:
            for response in responses:
                if processed := self._build_reasoning_response(response):
                    yield processed
        return gen()

    @llm_retry_decorator
    async def _astream_chat(
            self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        responses = await super()._astream_chat(messages, **kwargs)

        async def gen() -> ChatResponseAsyncGen:
            async for response in responses:
                if processed := self._build_reasoning_response(response):
                    yield processed
        return gen()

    @staticmethod
    def _build_reasoning_response(response: ChatResponse) \
            -> ReasoningChatResponse | None:
        if not (raw := response.raw).choices:
            return None
        if (delta := raw.choices[0].delta) is None:
            return None

        return ReasoningChatResponse(
            message=response.message,
            delta=response.delta,
            raw=response.raw,
            reasoning_content=getattr(delta, "reasoning_content", None),
            additional_kwargs=response.additional_kwargs
        )






