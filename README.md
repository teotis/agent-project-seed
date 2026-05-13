# Agent Project Seed

复制即用的多 Agent 协作项目底座，为 Codex、Claude Code、Gemini CLI 等 AI 辅助开发工作流设计。

## 核心理念

**一份规则，多个 Agent。** 所有协作规则集中在 `control/contract.md`，各平台入口文件（`AGENTS.md`、`CLAUDE.md`、`GEMINI.md`）只做指向，不做复制。修改一处，全局生效。

## 目录结构

```
├── control/                # 治理层
│   ├── contract.md         # 唯一共享规则源
│   ├── ledger.md           # 统一记录账本（需求/决策/风险/会话/问题/产物）
│   └── state.md            # 当前态快照
├── work/                   # 工作层
│   ├── in/                 # 输入材料
│   ├── out/                # 正式产物（不提交）
│   └── tmp/                # 临时文件（不提交）
├── tools/
│   └── project.py          # 初始化、预检、同步、安全提交
├── src/
│   └── base_scaffold/      # Python 工具包（记录、路径、文件操作、QC、Review）
├── tests/                  # 测试
├── AGENTS.md               # Codex 入口
├── CLAUDE.md               # Claude Code 入口
└── GEMINI.md               # Gemini CLI 入口
```

## Quick Start

```bash
cp -R seed my_new_project
cd my_new_project
python3 tools/project.py init --name "My New Project"
python3 tools/project.py check
```

`init` 默认初始化 Git 仓库并创建初始提交。嵌入已有仓库时使用 `--no-git`。

## 工具命令

| 命令 | 说明 |
|------|------|
| `python3 tools/project.py init --name "名称"` | 初始化项目，替换占位符，重命名包 |
| `python3 tools/project.py check` | 预检：文件完整性、Agent 同步状态、包可导入性 |
| `python3 tools/project.py sync-agents` | 从 `contract.md` 重新生成各平台入口文件 |
| `python3 tools/project.py commit --message "type: msg"` | 安全提交（只允许白名单文件，拒绝 `.env`/`work/tmp/`/`work/out/`） |

## Python 工具包

`src/base_scaffold/` 提供可复用的基础能力：

- **core** — 路径管理、原子文件写入、环境变量加载、API 门控
- **records** — `Record` / `Ledger` 统一记录、`Manifest` 产物清单、`QCResult` 质量检查
- **review** — 生成 HTML Review 页面（图片/链接审阅）

## 协作规则摘要

- 开始任务前按顺序读取：`contract.md` → `state.md` → `ledger.md` → 任务相关文件
- 需求、决策、风险等统一作为 `Record` 追加到 `ledger.md`
- 每个逻辑任务结束：运行 `check` → 提交 → 记录风险 → 给出下一步
- 外部 API 调用需同时满足环境变量启用 + 用户明确授权
- 冲突无法自动裁决时写入 `ledger.md`，等用户裁定

## 适用场景

- 用 AI Agent 辅助开发的项目，需要统一工程纪律
- 多 Agent（Codex / Claude / Gemini）协作的代码库
- 需要结构化记录需求、决策、风险的轻量项目
