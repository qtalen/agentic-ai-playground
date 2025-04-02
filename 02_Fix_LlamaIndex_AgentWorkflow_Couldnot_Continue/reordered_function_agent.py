from typing import override, Sequence, List

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.workflow import Context
from llama_index.core.memory import BaseMemory
from llama_index.core.tools import AsyncBaseTool
from llama_index.core.agent.workflow.workflow_events import (
    AgentOutput,
)


class ReorderedFunctionAgent(FunctionAgent):
    @override
    async def take_step(
            self,
            ctx: Context,
            llm_input: List[ChatMessage],
            tools: Sequence[AsyncBaseTool],
            memory: BaseMemory,
    ) -> AgentOutput:
        last_msg = llm_input[-1] and llm_input[-1].content
        state = await ctx.get("state", None)

        if "handoff_result" in last_msg:
            for message in llm_input[::-1]:
                if message.role == MessageRole.USER:
                    last_user_msg = message
                    llm_input.append(last_user_msg)
                    break

        return await super().take_step(ctx, llm_input, tools, memory)
