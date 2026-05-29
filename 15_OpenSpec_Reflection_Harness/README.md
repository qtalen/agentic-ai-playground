This repository is the source code for my latest article [Reflection SDD: Use a Reflection Harness to Level Up Your OpenSpec Workflow](https://www.dataleadsfuture.com/reflection-sdd-use-a-reflection-harness-to-level-up-your-openspec-workflow/).

In this repo:

`openspec-reviewer.md` is the reflection agent definition covered in the article. Please place it in the `~/.config/opencode/agents/` directory.

`openspec-workflow` defines the OpenSpec workflow skill, which works alongside the reflection process for proposal artifact files. Please place it in the `~/.agents/skills/` directory.

Depending on the LLM you're using, if it doesn't load skills very proactively, you can add the following prompt to your project or global `AGENTS.md`:

```markdown
### CRITICAL: Skill loading

**Before invoking ANY OpenSpec stage or /opsx command, you MUST load TWO skills:**

1. Load `openspec-workflow` — the standard workflow framework
2. Load the stage-specific skill (e.g. `openspec-apply-change`, `openspec-propose`, etc.)

**Concrete triggers — load both skills when you see:**
- User says `/opsx-apply`, `/opsx-propose`, `/opsx-verify`, `/opsx-archive`, `/opsx-explore`, `/opsx-sync`
- User says "implement tasks from an OpenSpec change", "apply this change", "propose a change", etc.
- You are about to run `openspec instructions apply`, `openspec status`, `openspec list`, etc.
- You are reading files under `openspec/changes/<name>/`

Failure to load `openspec-workflow` will result in missing critical workflow context.
```