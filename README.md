# Agent Project Seed

复制即用的多 Agent 协作项目底座。一条命令初始化，得到一个已命名、可检查、有面板、有规则、有安全提交的新项目。

- Python >= 3.9，零外部依赖
- 支持 Codex / Claude Code / Gemini CLI

## 适合什么

- 用 AI Agent 辅助开发，需要统一工程纪律
- 多 Agent 协作的代码库
- 需要结构化记录需求、决策、风险的轻量项目

## 5 分钟 Quick Start

**方式一：GitHub Template（推荐）**

1. 点击仓库页 "Use this template" 创建新仓库
2. Clone 新仓库到本地
3. 运行初始化：

```bash
python3 tools/project.py init --name "你的项目名"
python3 tools/project.py check
```

**方式二：本地复制**

```bash
cp -R agent_project_seed my_new_project
cd my_new_project
python3 tools/project.py init --name "你的项目名"
```

**方式三：直接 clone（不推荐）**

```bash
git clone <repo> my_new_project
cd my_new_project
rm -rf .git
python3 tools/project.py init --name "你的项目名"
```

> 直接 clone 不删除 `.git` 的话，remote 仍指向 seed 仓库。

## 初始化后你会得到什么

`init` 自动完成：

| 步骤 | 说明 |
|------|------|
| 文本替换 | 项目名、包名、slug 替换到所有文件 |
| 包重命名 | `src/base_scaffold/` → `src/你的包名/` |
| 更新 contract.md | Current Intent 写入项目名和待补全状态 |
| 更新 state.md | 记录项目名、包名、初始化时间 |
| 追加 ledger.md | 记录一条 `type: decision` 的初始化记录 |
| 激活 settings | 复制 `.claude/settings.example.json` → `settings.json` |
| Git 初始化 | 创建仓库并首次提交（`--no-git` 可跳过） |

## 面板

每次 Claude Code 对话开始时，自动注入项目状态面板。

```
【你的项目名】2026-05-14 (周四)
状态: 已初始化，目标待补全
Git: clean | Ledger: 2 条 | Package: your_pkg
目标: 项目目标
下一步: 编辑 control/contract.md 的 Current Intent
```

三档状态：
- **Seed 模板** — 尚未运行 `init`
- **已初始化，目标待补全** — `init` 已运行，但 `contract.md` 的目标未编辑
- **已就绪** — 目标已定制

手动验证面板：

```bash
python3 tools/panel.py
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `python3 tools/project.py init --name "名称"` | 初始化项目 |
| `python3 tools/project.py check` | 健康检查（文件、同步、面板、一致性） |
| `python3 tools/project.py sync-agents` | 从 contract.md 重新生成入口文件 |
| `python3 tools/project.py commit --message "type: msg"` | 安全提交 |
| `python3 tools/project.py commit --dry-run` | 预览哪些文件会被提交 |
| `python3 tools/panel.py` | 手动查看面板输出 |

## 安全提交机制

`commit` 命令只允许提交白名单文件（`control/`、`tools/`、`src/`、`tests/` 等），自动拒绝：

- `.env`、`work/tmp/`、`work/out/` 中的文件
- 不在白名单中的文件

Claude Code 的 Stop hook 会在每次对话结束时自动尝试安全提交。配置见 `.claude/settings.example.json`。

## 目录说明

```
├── control/                # 治理层
│   ├── contract.md         # 唯一共享规则源
│   ├── ledger.md           # 统一记录账本
│   └── state.md            # 当前态快照
├── work/                   # 工作层
│   ├── in/                 # 输入材料
│   ├── out/                # 正式产物（不提交）
│   └── tmp/                # 临时文件（不提交）
├── tools/
│   ├── project.py          # 初始化、预检、同步、安全提交
│   └── panel.py            # 面板生成器
├── src/
│   └── base_scaffold/      # Python 工具包
├── tests/                  # 测试
├── .claude/
│   ├── hooks/panel_hook.py # 面板注入 hook
│   └── settings.example.json
├── AGENTS.md               # Codex 入口
├── CLAUDE.md               # Claude Code 入口
└── GEMINI.md               # Gemini CLI 入口
```

## Python 工具包

`src/base_scaffold/` 提供可复用的基础能力：

- **core** — 路径管理、原子文件写入、环境变量加载、API 门控
- **records** — `Record` / `Ledger` 统一记录、`Manifest` 产物清单、`QCResult` 质量检查
- **review** — 生成 HTML Review 页面（图片/链接审阅）

测试依赖：`python3 -m pip install -e ".[test]"`

## 初始化后的必填项

运行 `init` 后，编辑 `control/contract.md` 的 `Current Intent` 部分，写清：

1. 项目目标
2. 非目标
3. 验收标准

完成后面板状态会从"目标待补全"变为"已就绪"。

## 故障排查

**面板显示 Seed 模板**
→ 运行 `python3 tools/project.py init --name "你的项目名"`

**面板显示"目标待补全"**
→ 编辑 `control/contract.md` 的 Current Intent，删除"已初始化，目标待补全"标记

**check 报告 agent entry files not synced**
→ 运行 `python3 tools/project.py sync-agents`

**check 报告 platform junk files tracked**
→ 运行 `git rm --cached ._文件名`，确认 `.gitignore` 包含 `._*`

**check 报告 missing .gitkeep**
→ 运行 `touch work/in/.gitkeep work/out/.gitkeep work/tmp/.gitkeep`

## Agent 使用规则

- 开始任务前按顺序读取：`contract.md` → `state.md` → `ledger.md` → 任务相关文件
- 需求、决策、风险等统一作为 `Record` 追加到 `ledger.md`
- 每个逻辑任务结束：运行 `check` → 提交 → 记录风险 → 给出下一步
- 外部 API 调用需同时满足环境变量启用 + 用户明确授权
- 冲突无法自动裁决时写入 `ledger.md`，等用户裁定
