from typing import Optional

from llama_index.core.agent.workflow import AgentWorkflow, BaseWorkflowAgent
from llama_index.core.workflow import Context
from llama_index.core.tools import (
    AsyncBaseTool,
    FunctionTool
)
from llama_index.core.prompts.base import PromptTemplate


ENHANCED_HANDOFF_PROMPT = """Useful for handing off to another agent.
If you are currently not equipped to handle the user's request, or another agent is better suited to handle the request, please hand off to the appropriate agent.

Currently available agents:
{agent_info}
"""

ENHANCED_HANDOFF_OUTPUT_PROMPT = """
    Agent {to_agent} is now handling the request.
    Check the previous chat history and continue responding to the user's request: {user_request}.
"""


async def handoff(ctx: Context, to_agent: str, user_request: str):
    """Handoff control of that chat to the given agent."""
    agents: list[str] = await ctx.get('agents')
    current_agent_name: str = await ctx.get("current_agent_name")
    if to_agent not in agents:
        valid_agents = ", ".join([x for x in agents if x != current_agent_name])
        return f"Agent {to_agent} not found. Please select a valid agent to hand off to. Valid agents: {valid_agents}"

    await ctx.set("next_agent", to_agent)
    handoff_output_prompt = PromptTemplate(ENHANCED_HANDOFF_OUTPUT_PROMPT)
    return handoff_output_prompt.format(to_agent=to_agent, user_request=user_request)


class EnhancedAgentWorkflow(AgentWorkflow):
    def _get_handoff_tool(
        self, current_agent: BaseWorkflowAgent
    ) -> Optional[AsyncBaseTool]:
        """Creates a handoff tool for the given agent."""
        agent_info = {cfg.name: cfg.description for cfg in self.agents.values()}
        configs_to_remove = []
        for name in agent_info:
            if name == current_agent.name:
                configs_to_remove.append(name)
            elif (
                current_agent.can_handoff_to is not None
                and name not in current_agent.can_handoff_to
            ):
                configs_to_remove.append(name)

        for name in configs_to_remove:
            agent_info.pop(name)

        if not agent_info:
            return None

        handoff_prompt = PromptTemplate(ENHANCED_HANDOFF_PROMPT)
        fn_tool_prompt = handoff_prompt.format(agent_info=str(agent_info))
        return FunctionTool.from_defaults(
            async_fn=handoff, description=fn_tool_prompt, return_direct=True
        )