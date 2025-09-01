from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from agents import docker_executor, coder, exe_agent, reviewer

text_termination = TextMentionTermination("COOL")
team = RoundRobinGroupChat([coder, exe_agent, reviewer],
                           termination_condition=text_termination)


if __name__ == "__main__":
    import asyncio
    from autogen_agentchat.ui import Console

    async def main():
        task = "The bag has 4 black balls and 1 white ball. Every time, you pick one ball at random and swap it for a black ball. Keep going, and figure out the chance of pulling a black ball on the third try."

        async with docker_executor:
            await Console(team.run_stream(task=task))

    asyncio.run(main())
