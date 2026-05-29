---
name: openspec-workflow
description: Mandatory prerequisite for ALL OpenSpec operations — load this BEFORE any openspec-* skill. Use when running /opsx-apply, /opsx-propose, /opsx-verify, /opsx-archive, /opsx-explore, /opsx-sync; running `openspec status`, `openspec list`, `openspec instructions`; reading files under `openspec/changes/`; or doing any OpenSpec stage (propose, apply, verify, archive, explore, sync).
license: MIT
compatibility: Requires openspec CLI.
metadata:
 author: Peng Qian
 version: "1.0"
---

## OpenSpec Workflow (Required)

**Every code change needs a proposal first. Code comes after.**

### The Flow
1. **Explore** - When the user says "let's think about it," "let's discuss," or "explore," just talk it through, no coding. Once the discussion feels solid and you're about to move into the propose stage, you need to write up a design brief first (`openspec/changes/<name>/explore-brief.md`, keep it to half a page). It should cover:
 - Alternatives that got rejected and why
 - The full labels/dimensions/mapping tables for the final approach (list everything out, no "e.g.")
 - Key cross-module data flows (who calls who, what params get passed)
 - A list of known open questions
This brief acts as a checklist when creating the proposal.
2. **Propose** - Create the proposal files under `openspec/changes/<change-name>/`. Before creating artifacts in batches, the main agent must read `explore-brief.md` first and go through each item to confirm whether all the design commitments (mapping tables, label sets, cross-module data flows, open questions) are covered in the artifacts being created in this batch. Use the brief as a checklist to avoid missing anything during transcription. **Create and review in batches, in this order:**
 - 2a. Create `proposal.md` → call `@openspec-reviewer` to review → fix issues → once it passes, `proposal.md` is frozen
 - 2b. Create `design.md` → call `@openspec-reviewer` to review (against the frozen proposal.md) → fix issues → once it passes, `design.md` is frozen
 - 2c. Create `specs/` → call `@openspec-reviewer` to review (against the frozen proposal.md + design.md) → fix issues → once it passes, specs are frozen
 - 2d. Create `tasks.md` → call `@openspec-reviewer` to review (against all previously frozen artifacts) → fix issues → done
 - **Never create all artifacts at once and then review them together.** Each round, only create one batch of freezable artifacts. When making edits, only touch the current batch. For already-frozen artifacts, only declarative additions are allowed (see freeze/unfreeze rules) — never touch decision-level content. If a review finds that a frozen artifact needs a decision-level change, unfreeze that artifact and all artifacts that came after it, then re-review from there.
3. **Apply** - Implement based on the proposal tasks. **No proposal means no file changes, period.**
4. **Verify** - Verify the implementation once it's done.
5. **Archive** - Archive the change.

### Hard Rules

- **Bug fixes don't need a proposal** — this hard rule only applies to feature changes or new features
- **No proposal, no changes**: If the user asks you to modify code, first confirm there's a matching proposal, or create one first
- **No proposal, no edits**: Before editing any file, check whether there's a matching change directory under `openspec/changes/`
- **No coding in Explore mode**: When the user is in explore mode, **do not** create proposals, **do not** edit files, **do not** write tests
- **After a change is done**: You must run the verify flow to check that the implementation matches the proposal

### What Every Proposal Needs

Every change must include:
- `proposal.md` - why the change is needed and what's in scope
- `design.md` - the design approach
- `tasks.md` - a concrete task checklist
- `.openspec.yaml` - change metadata

Extra requirements:
- **Task granularity**: Each task in `tasks.md` should take no more than 2 hours

### When Things Go Wrong

If any of the following happen, stop immediately and let the user know:
- Code is being modified without a proposal
- Files are being edited in explore mode
- Files outside the current proposal's scope are being modified

### OpenSpec Review Flow
1. When creating artifacts in batches, after each batch is created, you **must** call the `@openspec-reviewer` agent to review the **artifact files in that batch**. When calling, tell the reviewer which artifacts are already frozen and which ones are newly created in this round. You must attach `explore-brief.md` as the review baseline — the reviewer goes through each commitment in the brief and checks whether the artifacts fully capture it, with no gaps or contradictions. If there's no brief yet, attach the key context from the explore phase: what approaches were discussed, what got rejected, and why.
2. The main agent updates the **current batch's artifact files** based on feedback from `@openspec-reviewer`, without touching any frozen files.
3. Call `@openspec-reviewer` again to review the **current batch's artifact files** (still checking against previously frozen artifacts).
4. **What counts as passing:**

4a. **Single-round pass rule**: After the current review round, if the "### 🔴 Outstanding" section in `review-log.md` for that round doesn't exist or is empty, the batch is frozen and you move on to the next batch. No need for two consecutive clean rounds.

 Why: If there are no serious issues in the current round, the artifacts are in good shape. The latest review result is what counts — no need for an extra confirmation round.

4b. **Fix loop**: If there are still 🔴 issues in the current round, the main agent fixes them, the next review round happens, then back to 4a. Keep going until it passes or hits 4c.

4c. **Hard cap** (MAX_ROUNDS = 5): If the same batch has gone through 5 review rounds and still hasn't passed per 4a, stop the loop and hand it off to a human:

 > "Batch <batch> hasn't passed after 5 review rounds. Outstanding serious issues:
 > - <issue 1>
 > - <issue 2>
 > Please choose:
 > A. Force freeze, ignore outstanding issues and move to the next batch
 > B. Roll back the design and rethink this batch's approach
 > C. Add one more review round"

 Round counting rule: A round is only counted when `@openspec-reviewer` is called and a review-log entry is produced. Pure fix operations don't count.
5. After each review round, the main agent must **append** a summary of the review findings to `review-log.md` in the change directory. `<batch>` is one of: proposal / design / specs / tasks.

Format example:
## design Round 2 — 2026-05-26 14:00
### 🔴 Fixed
 - goal:* category mappings were missing → added all five categories with bilingual seed words
### 🟡 Addressed
 - fail:* mapping rules were missing → added the complete mapping table
### 🔴 Outstanding
 - updateEntry dedup path label merging (continuing to fix next round)

### Freeze and Unfreeze Rules
- **Freeze**: Once a batch of artifacts (like proposal.md) passes review, it's considered frozen. All subsequent artifact reviews must use the frozen artifacts as the baseline for consistency checks.
- **Soft freeze**: After freezing, you're allowed to append **declarative content** without triggering an unfreeze. Declarative content includes:
 - Adding missing mapping tables / keyword lists / complete enumerations
 - Fixing typos
 - Adding missing scenarios or examples
 - Adding boundary condition descriptions
 - The test: would this change cause an implementer to write different code? If no (just filling in details), it's declarative. If yes (changes algorithm, semantics, or responsibilities), it's decision-level and cannot be appended.
- **No decision-level changes to frozen artifacts**: Changing algorithms, label semantics, module responsibility boundaries, adding or removing capabilities — all of these are decision-level changes. Making a decision-level change to a frozen artifact requires a full-chain unfreeze.
- **Unfreeze**: If a later review finds that a frozen artifact needs a decision-level change, unfreeze that artifact and all artifacts that came after it, then re-review in batches starting from the unfreeze point.
- **Change isolation**: When fixing review issues, only modify the current batch and any unfrozen files. For frozen artifacts, only declarative additions are allowed — never touch decision-level content.
