from llama_index.core.agent.workflow import AgentStream


class ReasoningStreamAdapter:
    def __init__(self, event: AgentStream):
        self.event = event

    @property
    def delta(self) -> str:
        return self.event.delta

    @property
    def response(self) -> str:
        return self.event.response

    @property
    def tool_calls(self) -> list:
        return self.event.tool_calls

    @property
    def raw(self) -> dict:
        return self.event.raw

    @property
    def current_agent_name(self) -> str:
        return self.event.current_agent_name

    @property
    def reasoning_content(self) -> str | None:
        raw = self.event.raw
        if raw is None or (not raw['choices']):
            return None
        if (delta := raw['choices'][0]['delta']) is None:
            return None

        return delta.get("reasoning_content")