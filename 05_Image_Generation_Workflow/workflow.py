import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.workflow import (
    Context,
    StartEvent,
    StopEvent,
    Workflow,
    step
)

import ctx_manager as ctx_mgr
from prompts_en import (
    PROMPT_GENERATE_SYSTEM, PROMPT_TRANSLATE_SYSTEM,
    PROMPT_REWRITE_SYSTEM
)
from events import (
    GenPromptEvent, PromptGeneratedEvent,
    StreamEvent, GenImageEvent, RewriteQueryEvent
)

load_dotenv("../.env_deepseek")


class ImageGeneration(Workflow):
    def __init__(self, *args, **kwargs):
        self.deepseek_client = OpenAILike(
            model="deepseek-chat",
            is_chat_model=True,
            is_function_calling_model=True
        )
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("REAL_OPENAI_API_KEY"),
            base_url=os.getenv("REAL_OPENAI_BASE_URL"),
        )

        super().__init__(*args, **kwargs)

    @step
    async def on_start(self, ctx: Context, ev: StartEvent) -> GenImageEvent | GenPromptEvent:
        query = ev.query
        if len(query) > 0 and ("APPROVE" in query.upper()):
            return GenImageEvent(content=query)
        else:
            return GenPromptEvent(content=ev.query)

    @step
    async def prompt_generator(self, ctx: Context, ev: GenPromptEvent) \
            -> PromptGeneratedEvent | RewriteQueryEvent | None:
        user_query = ev.content
        hist_query = await ctx_mgr.get_rewritten_hist(ctx)
        hist_prompt = await ctx_mgr.get_image_prompt(ctx)
        system_prompt = PROMPT_GENERATE_SYSTEM.format(
            hist_query=hist_query,
            hist_prompt=hist_prompt
        )
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_query)
        ]
        image_prompt = ""
        events = await self.deepseek_client.astream_chat(messages)
        async for event in events:
            ctx.write_event_to_stream(StreamEvent(target="prompt", delta=event.delta))
            image_prompt += event.delta

        await ctx_mgr.add_query_hist(ctx, user_query)
        await ctx_mgr.set_image_prompt(ctx, image_prompt)
        ctx.send_event(PromptGeneratedEvent(content=image_prompt))
        ctx.send_event(RewriteQueryEvent())

    @step
    async def translate_prompt(self, ctx: Context, ev: PromptGeneratedEvent) -> StopEvent:
        image_prompt = ev.content
        messages = [
            ChatMessage(role="system", content=PROMPT_TRANSLATE_SYSTEM),
            ChatMessage(role="user", content=image_prompt)
        ]
        events = await self.deepseek_client.astream_chat(messages)
        translate_result = ""
        async for event in events:
            ctx.write_event_to_stream(StreamEvent(target="translate", delta=event.delta))
            translate_result += event.delta
        return StopEvent(target="prompt", result=translate_result)

    @step
    async def generate_image(self, ctx: Context, ev: GenImageEvent) -> StopEvent:
        prompt = await ctx_mgr.get_image_prompt(ctx)
        image_url, revised_prompt = await self._image_generate(prompt=prompt)
        return StopEvent(target="image",
                         result={
                             "image_url": image_url,
                             "revised_prompt": revised_prompt
                         }
                         )

    @step
    async def rewrite_query(self, ctx: Context, ev: RewriteQueryEvent) -> None:
        query_hist_str = await ctx_mgr.get_query_hist(ctx)
        messages = [
            ChatMessage(role="system", content=PROMPT_REWRITE_SYSTEM),
            ChatMessage(role="user", content=query_hist_str)
        ]
        response = await self.deepseek_client.achat(messages)
        rewritten_prompt = response.message.content
        await ctx_mgr.set_rewritten_hist(ctx, rewritten_prompt)

    async def _image_generate(self, prompt: str) -> tuple[str, str]:
        ## Stop DALL-E 3 from rewriting incoming prompts
        final_prompt = f"""
        I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:
        {prompt}
        """
        response = await self.openai_client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            n=1,
            size="1792x1024",
            quality="hd",
            style="vivid",
        )
        return response.data[0].url, response.data[0].revised_prompt
