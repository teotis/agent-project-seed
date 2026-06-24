---
name: engineering-memory
description: >
  个人化工程记忆层。用于跨任务记录和召回项目决策、历史发现、用户偏好、分析产物、调用时间、后续行动和长期工程上下文；帮助分析技能从无状态工具升级为可审计的长期工程顾问。Use for Engineering Memory, artifact ledger, project decisions, user preferences, long-term engineering context, and recall before/after analysis runs.
---

# Engineering Memory

## Mission

为工程分析技能提供一个轻量、可审计、可撤销的长期记忆层。它记录事实日志，也沉淀长期有用的工程判断，让后续分析不必从零开始。

本技能不替代证据，不自动证明历史结论仍然正确。记忆只提供上下文、候选假设和待复核线索。

## Storage Model

默认写入当前项目内的本地 sidecar 目录：

```text
<project-root>/.memory/engineering/
  artifacts.jsonl
  projects/<project-id>.md
```

写入量通常很小：一次 `record` 是一行 JSONL，一次 `remember` 是一条 Markdown bullet。长期高频分析后可能增长，因此默认放在项目内 ignored 工作区，方便按项目清理、备份或整体迁移。

可用环境变量或 CLI 参数改写位置，优先级为 `--memory-root` > `ENGINEERING_MEMORY_ROOT` > `<project-root>/.memory/engineering/`：

```bash
ENGINEERING_MEMORY_ROOT=/path/to/memory
python3 <skill-dir>/scripts/engineering_memory.py --memory-root /path/to/memory recall --project <project-root>
```

不要把运行时记忆写进 `SKILL.md`、`agents/openai.yaml`、公开发布源、公开仓库或技能定义文件。技能定义描述能力；memory sidecar 保存个人历史。

## What To Record

优先记录高复用价值信息：

- artifact event：技能名、项目路径、任务、时间、报告/产物路径、摘要、关键发现、后续行动。
- decision：已经明确采用的项目决策、架构约束、发布规则。
- preference：用户明确表达过的稳定偏好，例如默认语言、报告格式、验证习惯。
- finding：跨会话反复出现或尚未关闭的重要发现。
- constraint：外部系统、设备、账号、公开发布、安全边界等长期约束。

避免记录：

- API key、token、凭证、私密账号内容、完整环境变量。
- 大段完整对话或无筛选工具输出。
- 一次性猜测、未经验证的严重性、情绪化评价。
- 可公开产物不应包含的私有路径、内部 prompt 或未发布案例。

## Workflow

### 1. Recall Before Analysis

在中高预算工程分析、架构审计、公开发布检查、复杂度扫描或项目治理任务开始前，读取当前项目的相关记忆：

```bash
python3 <skill-dir>/scripts/engineering_memory.py recall --project <project-root>
```

使用方式：

- 把历史决策作为上下文，不作为最终证据。
- 把历史发现作为候选检查点，重新验证后再写入报告。
- 把用户偏好用于输出形态，例如默认中文、HTML 报告、任务包格式。

### 2. Record Artifact Events

当分析或交付结束，记录本次产物和关键摘要：

```bash
python3 <skill-dir>/scripts/engineering_memory.py record \
  --skill deep-flow-sweep \
  --project <project-root> \
  --task "公开发布风险审计" \
  --summary "产出公开发布风险报告并列出后续修复包。" \
  --artifact reports/public-audit.html \
  --finding "公开版 SKILL.md 必须全英文" \
  --decision "公开发布源来自 references/public-en.SKILL.md" \
  --next-action "运行 rtk python3 control/project.py check"
```

### 3. Promote Long-Lived Notes Deliberately

只有当信息具备长期价值时，才写入项目 note：

```bash
python3 <skill-dir>/scripts/engineering_memory.py remember \
  --project <project-root> \
  --kind decision \
  --text "公开技能必须从 references/public-en.SKILL.md 同步。" \
  --source "AGENTS.md"
```

`kind` 只能是：

- `decision`
- `finding`
- `preference`
- `constraint`

重复文本会被去重，避免长期记忆膨胀成噪音。

## Interpretation Rules

- **事实和判断分离**：时间、路径、命令输出是事实；“这是长期决策”是判断。
- **记忆不是证据**：历史记录只能提示复核方向。报告中的结论仍需要当前代码、文档、命令、截图或用户确认支撑。
- **少写高信号**：默认记录 3-7 条关键事实，不记录每个工具调用。
- **用户可控**：如果用户要求不要记录本次任务，不写 memory；如果用户要求删除或更正记忆，优先执行。
- **公开发布隔离**：公开技能、公开 README、公开报告不得自动包含私有 memory 内容。

## Script API

脚本入口：

```bash
python3 <skill-dir>/scripts/engineering_memory.py --help
```

子命令：

- `recall`：输出项目记忆摘要和最近 artifact event。
- `record`：追加一条 JSONL artifact event。
- `remember`：写入或去重一条长期项目 note。

脚本默认只使用 Python 标准库，方便在 Codex、Claude Code 和普通 shell 中复用。
