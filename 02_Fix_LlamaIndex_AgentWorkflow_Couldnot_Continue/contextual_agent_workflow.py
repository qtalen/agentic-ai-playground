from typing import Optional, Union, List

from llama_index.core.memory import BaseMemory
from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import step, Context, StartEvent
from llama_index.core.agent.workflow import AgentWorkflow, AgentInput


class ContextualAgentWorkflow(AgentWorkflow):
    @step
    async def init_run(self, ctx: Context, ev: StartEvent) -> AgentInput:
        """Sets up the workflow and validates inputs"""
        await self._init_context(ctx, ev)

        user_msg: Optional[Union[str, ChatMessage]] = ev.get("user_msg")
        chat_history: Optional[List[ChatMessage]] = ev.get("chat_history", [])
        memory: BaseMemory = await ctx.get("memory")
        current_agent_name: str = await ctx.get("current_agent_name")

        if isinstance(user_msg, str):
            user_msg = ChatMessage(role="user", content=user_msg)

        if user_msg:
            await memory.aput(user_msg)
            await ctx.set("user_msg_str", user_msg.content)
        elif chat_history:
            last_msg = chat_history[-1].content or ""
            memory.set(chat_history)
            await ctx.set("user_msg_str", last_msg)
        else:
            raise ValueError("Must provide either user_msg or chat_history")

        input_messages = memory.get()
        return AgentInput(input=input_messages, current_agent_name=current_agent_name)

