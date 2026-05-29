本代码库是我的最新文章[Reflection SDD: Use a Reflection Harness to Level Up Your OpenSpec Workflow](https://www.dataleadsfuture.com/reflection-sdd-use-a-reflection-harness-to-level-up-your-openspec-workflow/)的源代码。

其中：

`openspec-reviewer.md`是本文涉及到的反思智能体的定义，请放到`~/.config/opencode/agents/`目录。

`openspec-workflow`技能定义了OpenSpec工作流程，用以配合进行提案制品文件的反思过程。请放到`~/.agents/skills/`目录。

取决于你使用的大模型，如果对技能的加载没有那么主动，你可以把以下prompt添加到你的项目或者全局`AGENTS.md`里去：

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