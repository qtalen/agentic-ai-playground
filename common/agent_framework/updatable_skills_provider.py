import logging
from typing import override

from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path

from agent_framework._skills import (
    SkillsProvider,
    Skill,
    SkillScriptRunner,
    _create_instructions,
)

logger = logging.getLogger(__name__)


class UpdatableSkillsProvider(SkillsProvider):
    """SkillsProvider that supports dynamic skill updates via async skills_updater.

    This provider allows you to pass an optional async ``skills_updater`` callable
    that returns new skills to be merged into the provider's skill set before each
    agent run.

    Examples:
        Using an async skills_updater function:

        .. code-block:: python

            async def get_latest_skills():
                # Can perform async operations like API calls, database queries, etc.
                await asyncio.sleep(0.1)
                return [
                    Skill(
                        name="dynamic-skill",
                        description="A dynamically loaded skill",
                        content="Use this for ...",
                    ),
                ]

            provider = UpdatableSkillsProvider(
                skill_paths="./skills",
                skills_updater=get_latest_skills,
            )
    """

    def __init__(
        self,
        skill_paths: str | Path | Sequence[str | Path] | None = None,
        *,
        skills: Sequence[Skill] | None = None,
        script_runner: SkillScriptRunner | None = None,
        instruction_template: str | None = None,
        resource_extensions: tuple[str, ...] | None = None,
        script_extensions: tuple[str, ...] | None = None,
        require_script_approval: bool = False,
        source_id: str | None = None,
        skills_updater: Callable[[], Awaitable[Sequence[Skill]]] | None = None,
    ):
        super().__init__(
            skill_paths=skill_paths,
            skills=skills,
            script_runner=script_runner,
            instruction_template=instruction_template,
            resource_extensions=resource_extensions,
            script_extensions=script_extensions,
            require_script_approval=require_script_approval,
            source_id=source_id,
        )
        self._skills_updater = skills_updater
        self._instruction_template = instruction_template
        self._script_runner = script_runner
        self._require_script_approval = require_script_approval

    async def _update(self) -> None:
        """Call the async skills_updater function to fetch and merge new skills.

        If the skills_updater raises an exception, logs the error and continues
        execution without blocking before_run.
        """
        if self._skills_updater is None:
            return

        try:
            new_skills = await self._skills_updater()

            for skill in new_skills:
                self._skills[skill.name] = skill

            has_scripts = any(s.scripts for s in self._skills.values())

            self._instructions = _create_instructions(
                prompt_template=self._instruction_template,
                skills=self._skills,
                include_script_runner_instructions=has_scripts,
            )

            self._tools = self._create_tools(
                include_script_runner_tool=has_scripts,
                require_script_approval=self._require_script_approval,
            )

        except Exception as exc:
            logger.exception("Failed to update skills: %s", exc)

    @override
    async def before_run(
        self,
        *,
        agent,
        session,
        context,
        state,
    ) -> None:
        await self._update()
        await super().before_run(
            agent=agent,
            session=session,
            context=context,
            state=state,
        )
