from typing import List, Sequence, Optional, override
from pprint import pprint

from llama_index.core import PromptTemplate
from pydantic import Field
from llama_index.core.memory import BaseMemory
from llama_index.core.tools import AsyncBaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.prompts import BasePromptTemplate
from llama_index.core.workflow import Context
from llama_index.core.agent.workflow import (
    FunctionAgent,
    AgentOutput,
    ToolCallResult
)

STATE_STR_PROMPT = """

Current state：
{state_str}
"""


class ContextualFunctionAgent(FunctionAgent):
    """The Function Agent contains a system_prompt with state strings."""
    state_str_prompt: Optional[str] = Field(
        default=STATE_STR_PROMPT,
        description="Adding state information to the system_prompt."
    )

    @override
    async def take_step(
        self,
        ctx: Context,
        llm_input: List[ChatMessage],
        tools: Sequence[AsyncBaseTool],
        memory: BaseMemory
    ) -> AgentOutput:
        if '{state_str}' not in self.state_str_prompt:
            raise ValueError("{state_str} not found in provided state_str_prompt")
        current_state = await ctx.get("state")

        state_str_template = PromptTemplate(self.state_str_prompt)
        state_prompt = state_str_template.format(
            state_str=current_state
        )

        if llm_input[0].role == "system":
            llm_input[0].content = llm_input[0].content + state_prompt
        else:
            llm_input = [ChatMessage(role="system", content=state_prompt)] + llm_input

        output = await super().take_step(
            ctx, llm_input, tools, memory
        )
        await ctx.set(self.scratchpad_key, [])
        return output

    @override
    async def handle_tool_call_results(
        self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
    ) -> None:
        current_state = await ctx.get("state", {})

        for tool_call_result in results:

            if (
                tool_call_result.return_direct
                and tool_call_result.tool_name != "handoff"
            ):
                await memory.aput(
                    ChatMessage(
                        role="assistant",
                        content=str(tool_call_result.tool_output.content),
                        additional_kwargs={"tool_call_id": tool_call_result.tool_call_id}
                    )
                )
                break
            current_state[tool_call_result.tool_name] = {
                'params': str(tool_call_result.tool_kwargs),
                'output': str(tool_call_result.tool_output.content)
            }
        await ctx.set("state", current_state)
