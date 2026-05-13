# Project Contract

本文件是本仓库多 Agent 协作的唯一共享规则源。`AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 是平台入口，只指向本文件。

## Project Shape

这是一个复制即用的轻量项目底座。它只预装最小结构：

- `control/contract.md`：规则、目标、工作方式、可选能力清单。
- `control/ledger.md`：统一记录账本，保存需求、决策、会话、风险、问题、产物。
- `control/state.md`：当前态快照，方便下一轮接手。
- `work/in/`：输入材料。
- `work/out/`：正式产物和 manifest。
- `work/tmp/`：临时文件，不提交。
- `tools/project.py`：初始化、预检、同步入口、安全提交。
- `src/`：极薄通用工具。

## Current Intent

复制本底座后，先更新本节和 `control/state.md`，写清项目目标、非目标、验收标准。不要为了“完整”提前创建领域目录；当某类材料自然长大时，再让目录分裂。

## Reading Order

开始任务前读取：

1. `control/contract.md`
2. `control/state.md`
3. `control/ledger.md` 中与任务相关的最近记录
4. 当前任务直接涉及的文件

## Ledger Rule

需求、决策、风险、会话、冲突、产物都先写成 `Record`，追加到 `control/ledger.md`。统一格式：

```text
## YYYY-MM-DDTHH:MM:SS - short title

type: request | decision | session | risk | issue | artifact
tags: tag-a, tag-b

summary:
- ...

details:
- ...

links:
- path/or/url
```

只记录对项目未来有用的事实，不保存完整聊天流水，不记录密钥和隐私原文。

## Git Rule

默认使用 Git。每个逻辑任务结束前：

1. 运行 `python3 tools/project.py check` 或等价验证。
2. 查看改动，只提交本轮应提交文件。
3. 使用 `python3 tools/project.py commit --message "type: summary"` 辅助安全提交。
4. 不提交 `.env`、`work/tmp/`、`work/out/` 的正式输出、大体积缓存或密钥。
5. 不 push，除非用户明确要求。

## External Capability Gate

任何外部 API、成本调用、材料上传或大规模改写必须同时满足：

- 环境变量显式启用。
- CLI 参数或用户本轮明确授权。

API key 只能来自环境变量或 `.env`。

## Optional Capabilities

以下能力不预建目录；需要时再生成：

- data lifecycle：CSV/JSONL 状态主表、schema、同步脚本。
- content pipeline：draft/approved 分层、发布门控、冲突裁定。
- image generation：provider、队列、manifest、成本门控。
- html delivery：Markdown + self-contained HTML 双交付。

## Conflict Rule

冲突无法自动裁决时，追加 `type: issue` 到 `control/ledger.md`。用户或权威文件裁定后，追加 `type: decision`。不要靠静默重写制造“已经解决”的假象。

## Final Response Rule

每次任务结束必须包含：

- 本次结果
- 修改/新增文件
- 风险点
- 建议下一步

若无新增风险，明确写“未发现新增风险”。下一步必须是具体可执行动作。
