---
name: openspec-workflow
description: Mandatory prerequisite for ALL OpenSpec operations — load this BEFORE any openspec-* skill. Use when running /opsx-apply, /opsx-propose, /opsx-verify, /opsx-archive, /opsx-explore, /opsx-sync; running `openspec status`, `openspec list`, `openspec instructions`; reading files under `openspec/changes/`; or doing any OpenSpec stage (propose, apply, verify, archive, explore, sync).
license: MIT
compatibility: Requires openspec CLI.
metadata:
    author: Peng Qian
    version: "1.0"
---

## OpenSpec Workflow（强制）

**所有代码变更必须先有提案，后写代码。**

### 流程
1. **Explore** - 用户说"想想"、"讨论"、"explore"时，只讨论不编码。若讨论已充分、即将进入 propose 阶段，必须先创建一份设计概要（`openspec/changes/<name>/explore-brief.md`，半页纸），包含：
   - 被否决的备选方案及否决原因
   - 最终方案的完整标签/维度/映射表（完整列出，不写"例如"）
   - 关键跨模块数据流（谁调谁、传什么参数）
   - 已知待解决问题列表
   设计概要作为 proposal 创建的 checklist 对照使用
2. **Propose** - 创建 `openspec/changes/<change-name>/` 下的提案文件。在分批创建制品之前，主智能体必须先阅读 `explore-brief.md`，逐项确认所有设计承诺（映射表、标签集合、跨模块数据流、待解决问题）是否已在此批次将创建的制品中得到覆盖。brief 作为 checklist 使用，避免转录遗漏。**按以下顺序分批创建、分批审查**：
   - 2a. 创建 `proposal.md` → 调用 `@openspec-reviewer` 审查 → 修复 → 通过后 `proposal.md` 冻结
   - 2b. 创建 `design.md` → 调用 `@openspec-reviewer` 审查（对照已冻结的 proposal.md） → 修复 → 通过后 `design.md` 冻结
   - 2c. 创建 `specs/` → 调用 `@openspec-reviewer` 审查（对照已冻结的 proposal.md + design.md） → 修复 → 通过后 specs 冻结
   - 2d. 创建 `tasks.md` → 调用 `@openspec-reviewer` 审查（对照所有已冻结的前序制品） → 修复 → 通过
   - **严禁一次性创建所有制品再审查。** 每轮只创建一批可冻结的制品，修改时也只改当前批次。对已冻结的制品只允许声明性追加（见冻结与解冻规则），不碰决策性内容。如果审查发现已冻结的制品需要做决策性修改 → 解冻该制品及其所有后序制品，重新审查。
3. **Apply** - 按提案任务实施，**没有提案不得修改任何文件**
4. **Verify** - 实现完成后验证
5. **Archive** - 归档变更

### 硬性规则

- **bug修复无需编辑或创建提案**，此硬性规则只对功能变更或新增功能时有效
- **无提案不变更**：如果用户要求修改代码，必须先确认已有对应提案，或先创建提案
- **无提案不编辑**：编辑文件前，检查当前是否在 `openspec/changes/` 下有匹配的变更目录
- **Explore 模式不编码**：当用户在 explore 模式下，**禁止**创建提案、**禁止**编辑文件、**禁止**写测试
- **变更完成后**：必须执行 verify 流程，检查实现与提案的一致性

### 提案创建要求

每次创建变更必须包含：
- `proposal.md` - 变更原因和范围
- `design.md` - 设计方案
- `tasks.md` - 具体任务清单
- `.openspec.yaml` - 变更元数据

附加要求：
- **任务粒度**：`tasks.md` 中每个任务不超过 2 小时

### 违规处理

如果检测到以下情况，立即停止并提醒用户：
- 没有提案就开始修改代码
- 在 explore 模式下编辑文件
- 修改了不属于当前提案范围的文件

### OpenSpec反思流程
1. 分批创建制品时，**每批制品创建后**都**必须**调用`@openspec-reviewer`智能体对该**批次内的制品文件**进行审核。调用时必须告知审查者哪些制品已冻结、哪些是本次新创建的。必须附上 `explore-brief.md` 作为审查基线，审查者逐项对照 brief 中的承诺检查制品是否完整转录、有无遗漏或矛盾。若暂无 brief 文件，须附上 explore 阶段的关键背景：讨论了哪些方案、否决了哪些、为什么。
2. 主智能体根据`@openspec-reviewer`反馈的审核结果修改**当前批次的制品文件**，不碰已冻结的文件
3. 再次调用`@openspec-reviewer`智能体对**当前批次的制品文件**进行审核（仍然对照已冻结的前序制品）
4. **审查通过标准**：

   4a. **单轮通过原则**：当前轮次审查后，若 `review-log.md` 中该轮次的 "### 🔴 遗留" 不存在或为空 → 该批次冻结，进入下一批次。不再要求连续两轮 clean。

       理由：如果本轮已无严重问题，说明当前制品状态合格，无需重复审查。修复后的版本以最新审查结果为准，不需要额外一轮确认。

   4b. **修复循环**：若当前轮仍有 🔴 问题 → 主智能体修复 → 下一轮审查 → 回到 4a。重复直至通过或触发 4c。

   4c. **硬上界保护**（MAX_ROUNDS = 5）：同一批次累计审查轮次达到 5 轮仍未按 4a 通过 → 停止循环，交由人工决策：

       > "批次 <batch> 经过 5 轮审查仍未通过。遗留严重问题：
       >   - <issue 1>
       >   - <issue 2>
       > 请选择：
       >   A. 强制冻结，忽略遗留问题继续下一批次
       >   B. 回退设计，重新思考该批次方案
       >   C. 追加一轮审查"

       轮次计数规则：仅当调用了 @openspec-reviewer 并产出了 review-log 条目时计为一轮。纯修复操作不计数。
5. 每轮审查完成后，主智能体必须将审查报告的发现摘要**追加**到 change 目录下的 `review-log.md`。<batch> 取值为 proposal / design / specs / tasks 之一。

   格式示例：
   ## design Round 2 — 2026-05-26 14:00
   ### 🔴 已修复
   - goal:* 类别映射缺失 → 已补充五大类别及中英双语种子词
   ### 🟡 已处理
   - fail:* 映射规则缺失 → 已补充完整映射表
   ### 🔴 遗留
   - updateEntry 去重路径标签合并（下轮继续修复）

### 冻结与解冻规则
- **冻结**：某批次制品（如 proposal.md）通过审查后即视为冻结。后续制品的审查必须以冻结制品为基准做一致性检查。
- **软冻结**：冻结后的制品允许追加**声明性内容**而不触发解冻。声明性内容包括：
  - 补充缺失的映射表/关键词表/完整列表
  - 修正拼写错误
  - 添加遗漏的场景/示例
  - 补充边界条件描述
  判断标准：该修改是否会导致实现者写出不同的代码？若不会（仅补充细节），为声明性；若会（改变算法/语义/职责），为决策性，不可追加。
- **决策性修改禁止追加**：改变算法、标签语义、模块职责划分、新增/删除 capability 等属于决策性修改。对冻结制品做决策性修改必须启动全链解冻。
- **解冻**：如果后续审查发现已冻结的制品需要做决策性修改，解冻该制品及其所有后序制品，从解冻点重新分批审查。
- **修改隔离**：修复审查问题时修改当前批次和已解冻的文件，对已冻结的制品只允许声明性追加，绝不动手修改决策性内容。