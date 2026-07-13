---
name: public-release-sweep
description: >
  公开发布安全核查扫雷。用于开源/公开仓库发布前的系统性安全审查，覆盖 Git 历史身份与密钥泄露、被追踪内部文件残留、内容中的硬编码路径与私有引用、二进制产物与 EXIF 元数据、LICENSE 与合规、公开/私有同步机制有效性，八大维度证据驱动，产出可审阅报告和修复任务包。
  Use for pre-release public safety auditing across 8 dimensions: git history identity & secrets, tracked internal files, hardcoded paths & private references, binary artifacts & EXIF metadata, LICENSE & legal compliance, and public/private sync mechanism verification. Evidence-backed reports with fix task packages.
---

# Public Release Sweep

## Mission

Systematically audit a project for public-release safety across 8 dimensions. Find everything that would leak unintended private identity, secrets, internal workflows, competitive intelligence, or unreleased features if the repository went public today. Produce an evidence-backed report with severity ratings and fix task packages.

This skill is the **public-safety counterpart** to `deep-flow-sweep`: it trades breadth of quality dimensions for depth on a single dimension — public exposure risk. Where deep-flow-sweep audits main flows, code quality, and architecture, public-release-sweep drills exclusively into what an external visitor could discover from the public repository (code, history, metadata, artifacts).

## 默认执行强度与询问门槛

### 调用入口契约

本 skill 是 sweep 类公开发布安全审计，允许两种入口：

- **用户显式启动**：用户点名本 skill、使用 `When To Use` 中列出的触发关键词，或明确要求做公开发布前安全核查 / 开源审查 / 公开仓库扫描 / 同步机制核查。
- **Agent active 启动**：当前任务已经需要判断仓库、同步脚本、public mirror、公开英文包、开源发布或公开前材料是否安全时，agent 可主动调用本 skill；尤其是发现疑似身份泄露、密钥、私有路径、内部文件残留、二进制元数据或 private/public sync 漂移时，应升级到本 skill，而不是只做普通代码审查。

Agent active 启动仍受授权边界限制：默认 **analysis-only**。不得在未获用户明确授权时执行历史重写、删除、提交、推送、发布、凭证操作或不可逆公开动作。若只是单个已知泄露的 surgical fix，且不需要完整 public-release verdict，可使用普通调试/修复流程；一旦问题关系到“是否可公开发布”的结论，就进入本 skill。

### 默认执行强度

一旦满足显式启动条件，调用即视为授权执行本 skill 在当前环境和既有安全边界内的完整原生工作流。默认全力执行：使用 **Deep** tier，覆盖全部适用维度，并在存在 private/public split 时深查实际 mirror 与同步机制；只有用户明确要求降级、缩小范围或聚焦时，才切换到 Quick、Normal 或有限维度。

目标仓库、公开模式、预算、预期 public identity 和可用工具应优先从当前 workspace、Git 配置、README、LICENSE、远端和同步脚本中推断，不要询问用户。信息不足但仍可开展有效审计时，继续执行，并把缺口记录为 `assumptions / unknowns / coverage debt`。

只有目标仓库完全无法识别、关键身份事实无法推断且会改变发布结论，或下一步涉及历史重写、删除、提交、推送、发布、凭证操作等既有授权边界外动作时，才中断询问。分析工具缺失、远端不可达或部分维度受阻不构成前置提问理由，应先完成其余审计并明确 coverage debt。

## Output Language

私有版默认使用中文交付。保留必要英文关键词、技能名、命令、文件名、代码标识、许可证名称、severity、public/private sync、public release 等专业术语。

私有版审计报告、修复任务包、最终回复和 HTML UI 文案默认使用中文。公开仓库内容、公开 README、公开英文 SKILL.md、对外发布说明或用户明确要求英文时，才使用英文；这种英文只适用于公开交付物本身，不应反向改变私有报告的默认语言。

## When To Use

Use this skill when the user asks for signals like:

- "公开前检查", "开源审查", "发布核查", "公开版本转化"
- "public release audit", "OSS readiness check", "open source scan"
- "公开仓库扫描", "暴露风险", "隐私泄露检查", "开源合规"
- "public repo safety", "release safety sweep", "pre-publish review"
- a request to verify that a project is safe to make public
- after a public repo is established, to verify sync mechanisms maintain safety

Do not use this skill for:

- fixing a single known leaked secret; use `systematic-debugging` to trace and remove it surgically;
- ordinary application security code review (OWASP, injection, auth); use the repo's security review workflow if available;
- code complexity or architecture cleanup; use `complexity-sweep` or `abstraction-architect`;
- licensing advice beyond the basic presence/correctness checks covered here.

## The 8 Check Dimensions

Normal and Deep sweeps must cover all 8 dimensions. Quick sweeps cover dimensions 1-3 and must explicitly state which dimensions were not checked. Each dimension has concrete detection patterns and severity criteria.

| # | Dimension | What it catches | P0/HIGH signals |
|---|-----------|----------------|-----------------|
| 1 | **Git History Identity** | Private names, corporate emails, personal contact emails in commit author/committer fields | `@<USER_CORP_DOMAIN>`, `@<USER_PERSONAL_DOMAIN>`, real names linked to corporate identity（具体 pattern 见 `references/private-identity-template.md`） |
| 2 | **Git History Secrets** | API keys, tokens, private keys, passwords in any historical commit or diff | `sk-*`, `ghp_*`, `-----BEGIN PRIVATE KEY-----`, `AKIA*` |
| 3 | **Tracked File Inventory** | Internal files that should not be public: AGENTS.md, CLAUDE.md, .codex/, control/, docs/plans/, reports/, specs/, tool/ | Agent instruction files, internal planning docs, unreleased specs |
| 4 | **Content Scanning** | Hardcoded local paths, private URLs, internal project names, competitor references, private tool commands in tracked files | `/Users/<name>/`, `/Volumes/<name>/`, `<USER_PRIVATE_TOOLS>` commands, internal hostnames（高置信度 token 见 `references/private-identity-template.md`；`internal`/`private`/`confidential` 仅作低置信度 trigger） |
| 5 | **Binary & Metadata** | Large binaries in history, APK/IPA/zip artifacts, EXIF data in images, PDF metadata | Debug APKs, EXIF with device model/firmware, >10MB binaries |
| 6 | **License & Legal** | Missing LICENSE file, placeholder copyright, real name in copyright, incorrect license for dependencies | `Copyright [yyyy] [name]`, copyright with real name |
| 7 | **Configuration & Env** | .env files tracked, private tool configs, internal API endpoints in config files | `.env` tracked, `settings.local.json` tracked, private URLs |
| 8 | **Sync Mechanism** | For split-repo projects: does the public-sync script/process correctly filter sensitive content? Are overlays clean? | Sync script copies sensitive files, overlays contain private info |

## Budget Tiers

| Tier | Trigger keywords | Dimensions covered | Output | Target scope |
|---|---|---|---|---|
| **Quick** | "快速公开检查", "quick public check" | Dimensions 1-3 only (highest risk) | Markdown source report + HTML review report | ~50K tokens |
| **Normal** | 用户明确要求常规、较快或有限深度审查 | All 8 dimensions, full depth | Markdown source report + HTML review report + fix plan | ~200K-500K tokens |
| **Deep** | 默认, "深度公开扫雷", "exhaustive public sweep" | Normal + cross-project comparison + sync mechanism deep audit + historical evolution | Markdown source report + full interactive HTML report + task packages + sync improvement plan | ~1M+ tokens |

If the user does not specify a budget limit, default to **Deep**. Downgrade only when the user explicitly asks for a faster, narrower, or lower-cost audit. For split-repo projects, always include Dimension 8 in Normal and Deep.

## Operating Principles

1. **Evidence before claims.** Every finding needs: exact location (file:line or commit hash), the exposed content type, a concrete visitor scenario ("anyone can `git clone` and run `git log --format='%ae'`"), and severity justification.
2. **History is the hardest to fix.** Prioritize git history issues highest because they require destructive `git filter-repo` operations. File-contents in the working tree are easy to fix; history rewrites are not.
3. **Assume public from day one.** If a repo will ever be public, treat its entire git history as eventually public. The cost of rewriting history now is far lower than after publication.
4. **Separate public/private by repo, not by ordinary directory.** A dedicated public repo, including a nested `public/` checkout with its own `.git`, is the preferred pattern. Verify it is truly independent.
5. **Analyze, do not repair without authorization.** Public-release fixes often involve destructive git operations (`filter-repo --force`, history deletion). Flag these as requiring explicit user authorization before execution.
6. **Verify what you claim.** Run the actual commands a visitor would run: `git log`, `git ls-files`, `git grep`. Do not rely on assumptions about what `.gitignore` excludes.
7. **Check the actual published state.** For projects with a public mirror, audit the actual public repo on GitHub, not just the local `public/` directory.
8. **Negative results are valuable.** A clean sweep with no findings is a strong signal that the project is ready for public release. Report it clearly.

## Model Adaptation Boundaries

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：analysis-only、8 维覆盖或 coverage debt、P0/HIGH 具体证据、visitor scenario、destructive Git 操作需新授权、actual published state、safe-to-publish verdict permission。这些是公开发布安全边界，不能因模型更强而放松。
- **Adaptive heuristics**：8 维顺序、扫描命令、工具选择、私有 token 模板、报告展开和 task package 粒度可按仓库形态调整。工具缺失时使用等价方法并降低证据等级，而不是阻塞全部审计或假装通过。
- **Creative extension lane**：当模型发现 8 维之外的 public exposure surface，例如 AI agent memory residue、generated artifacts、release automation provenance、package registry metadata 或 mirror policy drift，应临时命名该 dimension，记录 evidence command、visitor scenario、false-positive guard、coverage debt 和 verdict impact；安全 verdict 必须吸收该新增维度。

每次正式审计都做一次 **skill value check**：本 skill 是否比普通 grep 新增了 history/public-state 覆盖、visitor evidence、同步机制验证、破坏性修复边界或发布 verdict discipline。若没有，降级为 Quick/targeted scan 或 handoff。

## Workflow

### Investigation Kernel Adaptation

本 skill 参考项目级 Investigation Kernel，但本段是 standalone local adaptation：即使 single skill copied out，也必须能独立完成公开发布调查。

- **analysis artifact root**：正式审计优先写入 `reports/public-release-sweep/` 或用户指定的审计目录；只允许写审计报告、HTML review surface、evidence ledger、coverage debt、fix task packages 和 handoff notes。
- **analysis-only boundary**：默认不得修改产品代码、测试、配置、同步脚本、公开仓库内容、依赖锁或 Git 历史。删除跟踪文件、改同步策略、重写历史、提交或推送都需要报告后的 **new explicit user authorization**。
- **evidence map**：先建立 public exposure map，覆盖目标 repo、嵌套 public repo、远端状态、Git history、tracked file inventory、content scanning、binary/metadata、license/legal、configuration/env 和 sync mechanism。
- **coverage debt**：外部 GitHub 状态、远端权限、历史扫描工具、EXIF 工具、公开身份或 public mirror 不可用时，必须写入 coverage debt，不得声称 safe-to-publish。
- **claim permission**：只有所有适用维度已检查或明确 blocked/deferred，才可给出 ready/safe-to-publish verdict；P0/HIGH 必须有具体 file、commit、visitor scenario 或 exposed content evidence。
- **budget-aware stop review**：Quick 可在高风险前三维后停止并列 coverage debt；Normal 必须覆盖 8 维；Deep 根据 sync/history 风险和 low-information wave 的 marginal information gain 决定是否继续。不是固定两轮停止。

### 0. Establish Scope And Target

Infer the audit baseline from the repository when possible:

- target project(s) and whether each has its own `.git`;
- whether there is a public/private split, public mirror, or whole-repo publication plan;
- intended public identity from local repo config and README/LICENSE hints;
- budget tier (default: Deep).

Infer facts from repository evidence and record uncertain identity or publication assumptions in the report. Ask one minimal question only when the target cannot be identified or a fact cannot be inferred and would prevent any meaningful audit or materially invalidate the verdict.

### 1. Dimension 1 — Git History Identity

```bash
# For each target repo:
git log --format='%an <%ae>' | sort -u
git log --format='%cn <%ce>' | sort -u
```

Check each identity against（具体 pattern 由 `references/private-identity-template.md` §1 提供，主文件不嵌入真实私有标识）:
- Corporate email domains (`@<USER_CORP_DOMAIN>`，例如 `@example.com`)
- Personal contact emails (`@<USER_PERSONAL_DOMAIN>`，例如 `@example.org`)
- Real names linked to corporate identity (`<USER_REAL_NAME>`，例如 `example_user`)
- Inconsistent names across commits (suggests multiple machines/accounts)

加载模板后，引用其中的 `USER_CORP_DOMAIN` / `USER_PERSONAL_DOMAIN` / `USER_REAL_NAME` / `USER_LEGACY_HANDLE` 拼成 ERE，对上面两条 `git log` 输出再做 `grep -iE` 过滤，只把命中私有 pattern 的 identity 视为 P0/HIGH。如果模板未填写，记入 coverage debt 并提示用户补充，不得直接判定 clean。

### 2. Dimension 2 — Git History Secrets

```bash
git grep -nIE 'sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----|AKIA[A-Z0-9]{16}|api[_-]?key|secret[_-]?key|password|token' -- .
git log --all -G'sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----|AKIA[A-Z0-9]{16}|api[_-]?key|secret[_-]?key|password|token' --format='%H %s'
```

Also scan for:
- API key patterns: `api_key`, `apikey`, `secret_key`, `token`, `password`
- Internal service URLs: `<INTERNAL_SERVICE_HOST>`，internal hostnames（具体 host 由 `references/private-identity-template.md` §2 提供）
- AWS/GCP/Azure credential patterns

### 3. Dimension 3 — Tracked File Inventory

```bash
git ls-files | grep -iE '(AGENTS\.md|CLAUDE\.md|GEMINI\.md|\.codex/|control/|docs/plans/|reports/|specs/|tool/|\.env$|settings\.local\.json)'
```

Flag these categories:
- Agent instruction files (AGENTS.md, CLAUDE.md, GEMINI.md, .codex/)
- Internal governance (control/ledger.md, control/state.md)
- Planning documents (docs/plans/, specs/)
- Internal reports (reports/)
- Development tooling (tool/)
- Environment files (.env, settings.local.json)

### 4. Dimension 4 — Content Scanning

```bash
# 与具体用户无关的高置信度模式（直接计入 P0/HIGH）
git grep -nIE '/Users/|/Volumes/|/home/[^/[:space:]]+' -- .

# 私有 token / 私有工具：从 references/private-identity-template.md §2 加载 USER_PRIVATE_TOKENS / USER_PRIVATE_TOOLS
# 例：USER_PRIVATE_TOKENS='example_user|example_codename'  USER_PRIVATE_TOOLS='example_cli'
git grep -nIE "$USER_PRIVATE_TOKENS" -- .
git grep -nIE "(^|[^A-Za-z0-9_])($USER_PRIVATE_TOOLS)([^A-Za-z0-9_]|\$)" -- .

# 低置信度 trigger（仅触发人工复核，不直接判 P0/HIGH，参见模板 §3）
git grep -nIE 'internal|private|confidential|do[-_ ]not[-_ ]share|company-only' -- . > /tmp/public-release-sweep.low-confidence.txt
wc -l /tmp/public-release-sweep.low-confidence.txt
```

Patterns to detect:
- Local filesystem paths (`/Users/<name>/`, `/Volumes/<name>/`, `/home/<name>/`) — 高置信度
- Private tool references (`<USER_PRIVATE_TOOLS>`，例如 `example_cli`) — 高置信度，pattern 由模板 §2 注入
- Internal project names, code names, competitor references (`<USER_PRIVATE_TOKENS>`) — 高置信度，pattern 由模板 §2 注入
- Private git remote URLs in documentation — 高置信度
- 通用词 `internal` / `private` / `confidential` 等 — **低置信度 trigger**，需结合上下文判断（例如 `internal_api_url` 复核；`private static final`、`internal class` 等语言关键字应忽略），命中清单进入报告 `MEDIUM (needs review)` 段，不计入 P0/HIGH。

> Dimension 4 调用前应先读取 `references/private-identity-template.md`，把 §2 字段注入为 shell 变量；模板未填写时只跑高置信度通用模式 + 低置信度 trigger，并把"私有 token 列表缺失"记入 coverage debt。

### 5. Dimension 5 — Binary & Metadata

```bash
# Large files in git
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {size=$3; $1=$2=$3=""; sub(/^ +/, ""); print size, $0}' | sort -rn | head -20

# APK/IPA/zip/jar artifacts
git ls-files '*.apk' '*.ipa' '*.zip' '*.jar' '*.war'

# EXIF in images
find . -path ./.git -prune -o -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.pdf' \) -print | while IFS= read -r f; do
  exiftool "$f" 2>/dev/null | grep -iE 'make|model|software|gps|author|creator' && echo "  -> $f"
done
```

If `exiftool` is unavailable, record the tool gap instead of claiming metadata is clean.

### 6. Dimension 6 — License & Legal

- Does LICENSE file exist at repo root?
- Does copyright notice contain a real name instead of the public identity?
- Is the copyright year correct?
- For Apache 2.0: is the APPENDIX filled in?
- Are there NOTICE or AUTHORS files with private information?

### 7. Dimension 7 — Configuration & Env

- Is `.env` or `settings.local.json` tracked by git?
- Does `.env.example` or `settings.example.json` reference private tools or endpoints?
- Are there hardcoded internal URLs in config files?
- Does `.gitignore` exclude all sensitive local config patterns?

### 8. Dimension 8 — Sync Mechanism (split-repo projects only)

For projects using a `public/` subdirectory with independent git repo:

- Does the sync script use a whitelist (INCLUDE) or blacklist (EXCLUDE) approach? Whitelist is safer.
- Does the sync script have any content scanning before commit?
- Are overlay files (`docs/public_release_assets/`) themselves free of sensitive content?
- Does the public repo have local `user.name` and `user.email` configured correctly?
- Is there a verification script that runs before pushing to the public remote?

Use repo-local evidence:

```bash
git -C public/teotis-skills status --short
git -C public/teotis-skills config --get user.name
git -C public/teotis-skills config --get user.email
git -C public/teotis-skills ls-files | grep -iE '(AGENTS\.md|CLAUDE\.md|GEMINI\.md|\.codex/|control/|docs/plans/|reports/|specs/|tool/|\.env$|settings\.local\.json)'
```

### 9. Produce Report

Assemble all findings into paired reports by default, following `docs/contracts/output-modes.md`. The Markdown report is the source of truth for follow-up agents; the HTML report is the user-facing review surface using the format established by the `reviewable-html-report` capability. If that companion skill or report base is unavailable, use `references/fallback.html` for self-contained static HTML with TOC, stable section IDs, evidence appendix, Mermaid source fallback, and non-persistent feedback.

Report filenames for saved audits:

- `public_release_sweep_report_{YYYYMMDD}_{HHMM}.md`
- `public_release_sweep_report_{YYYYMMDD}_{HHMM}.html`

Quick audits still produce saved paired reports unless the user explicitly asks for `chat-only` / `no-files` output. HTML delivery provides a report path and clickable `file://` URL by default; active browser opening is optional preview behavior, not a completion standard.

```
sections:
  - overview: severity matrix + public-readiness verdict
  - per-project: dimension-by-dimension findings with evidence
  - common-issues: cross-project patterns
  - positive-findings: what's already done well
  - fix-plan: prioritized task packages with severity and estimated effort

severity levels:
  - P0 (blocking): API keys, real secrets → cannot publish
  - HIGH: identity leaks, internal files → must fix before publish
  - MEDIUM: confusable terms, internal docs → should fix
  - LOW: minor improvements → optional
```

HTML must use the same dimension IDs, finding IDs, severity labels, and fix task IDs as the Markdown report. It must include a clickable section index with stable section IDs. It may add filters, comparison views, expandable evidence, and feedback/export controls, but it must not introduce conclusions absent from Markdown. Provide the report path and clickable `file://` URL by default; active browser opening is optional preview behavior. If HTML cannot be generated, still deliver the Markdown report and state the limitation.

### 10. Fix Authorization Gate

In pure sweep mode, do not repair findings. If the user explicitly asks to implement fixes:

- Content edits (LICENSE, settings, README): safe to implement within the requested scope.
- `git rm --cached` operations: require confirmation because they change tracked public contents.
- `git filter-repo` operations: **require explicit user authorization** — these are irreversible history rewrites.
- API key rotation: flag as requiring external action (cannot be done from this repo)

## Positioning: Cross-Skill Integration

| Finding pattern | Escalate to | Handoff signal |
|---|---|---|
| API key or secret found in history | Manual key rotation on the external service | The key must be invalidated at its source; filter-repo alone is insufficient |
| Many independent fix tasks discovered | Claude Code Agent View / Dynamic Workflows, or `agent-orchestration-planner` | Use official Claude concurrency for independent tasks; use the planner only when execution needs a project-owned DAG, status ledger, worktree/branch policy, or final integration |
| Structural issue with public/private separation | `abstraction-architect` | The current split pattern has design flaws beyond simple cleanup |
| Sync mechanism needs redesign | `renewal-architect` | The existing sync script needs architectural changes, not just parameter tuning |
| Content issues reflect deeper naming/organization problems | `complexity-sweep` | Hardcoded paths and private references are symptoms of deeper coupling |

## The Iron Rule

**Never publish a repo whose git history contains real credentials or unintended private/corporate identity.** Rotate exposed credentials at the source, rewrite history before push, or keep the repo private.
