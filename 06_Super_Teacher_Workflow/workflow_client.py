from typing import Sequence, AsyncGenerator

from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import (
    BaseChatMessage, BaseAgentEvent
)
from autogen_agentchat.base import TaskResult
from autogen_core import CancellationToken

from agents import (
    docker_executor, thinker, coder, exe_agent,
    filtered_reviewer, filtered_writer
)


class SuperTeacherFlow:
    def __init__(self):
        self._build_workflow()

    async def run(
        self,
        *,
        task: str | BaseChatMessage | Sequence[BaseChatMessage] | None = None,
        cancellation_token: CancellationToken | None = None,
        output_task_messages: bool = True,
    ) -> TaskResult:
        result: TaskResult | None = None
        async for message in self.run_stream(
            task=task,
            cancellation_token=cancellation_token,
            output_task_messages=output_task_messages,
        ):
            if isinstance(message, TaskResult):
                result = message
        if result is not None:
            return result
        raise AssertionError("The stream should have returned the final result.")

    @staticmethod
    async def start():
        await docker_executor.start()

    @staticmethod
    async def stop():
        await docker_executor.stop()

    async def run_stream(
        self,
            *,
            task: str | BaseChatMessage | Sequence[BaseChatMessage] | None = None,
            cancellation_token: CancellationToken | None = None,
            output_task_messages: bool = True,
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | TaskResult, None]:
        async for event in self._flow.run_stream(
                task=task,
                cancellation_token=cancellation_token,
                output_task_messages=output_task_messages
        ):
            yield event

    def _build_workflow(self):
        terminator = MaxMessageTermination(20)

        builder = DiGraphBuilder()
        builder.add_node(thinker)
        builder.add_node(coder).add_node(exe_agent)
        builder.add_node(filtered_reviewer).add_node(filtered_writer)

        builder.set_entry_point(thinker)

        builder.add_edge(thinker, coder,
                         activation_group="gen_code", activation_condition="any")
        builder.add_edge(coder, exe_agent)
        builder.add_edge(exe_agent, filtered_reviewer)
        builder.add_edge(filtered_reviewer, filtered_writer,
                         condition="COOL")
        builder.add_edge(filtered_reviewer, coder,
                         condition="REJECT",
                         activation_group="gen_code", activation_condition="any")
        graph = builder.build()
        self._flow = GraphFlow(builder.get_participants(), graph=graph,
                               termination_condition=terminator)


if __name__ == "__main__":
    import asyncio
    from autogen_agentchat.ui import Console
    import mlflow

    mlflow.set_experiment("Super Teacher Workflow")
    mlflow.autogen.autolog()
    async def main():
        task = "One day, Julia went to her cousin's house, which is 4,000 meters from her home. At 7:20 in the morning, Julia started walking from her house at a speed of 60 meters per minute. At the same time, her cousin started riding his bike to pick her up. When the cousin reached Julia's house, he found she had already left, so he turned around and rode after her at 260 meters per minute. Once he caught up with her, he carried her back to his house on the bike at a speed of 175 meters per minute. How many minutes were left until 8:00 when they arrived at the cousin's house?"
        # task = """
        # A road construction team took on the task of building a highway.
        # The original plan was to build 720 meters per day, but in reality, they built 80 meters more each day.
        # This way, they were able to finish 1200 meters short of the full length 3 days ahead of schedule. How long is the entire highway?
        # """
        # task = """
        # The school organized two extracurricular interest groups to go on an outing.
        # The first group walks 4.5 kilometers per hour, and the second group goes 3.5 kilometers per hour.
        # After both groups set off at the same time for 1 hour, the first group stopped to visit an orchard for 1 hour before going to catch up with the second group.
        # How long will it take for the first group to catch up with the second group?
        # """
        with mlflow.start_span(name="root_span"):
            async with docker_executor:
                await Console(SuperTeacherFlow().run_stream(task=task))

    asyncio.run(main())
