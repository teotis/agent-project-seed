# Private Identity Pattern Template

本模板提供 public-release-sweep 在 Dimension 1（Git History Identity）和 Dimension 4（Content Scanning）需要的**真实私有标识模式**。SKILL.md 主文件只举中性占位符（`<USER_CORP_DOMAIN>` / `<USER_NAME>` / `example.com` / `example_user`），实际审计时由调用方在本文件里填入私有上下文，避免私有种子嵌入 skill 自身。

> **使用约束**
>
> - 本文件只在私有仓库内被引用；不得复制到 `references/public-en.SKILL.md` 或公开发布产物。
> - 公开发布前若 sync 流程错误地把本文件带入 public 仓，必须当作 P0 finding。
> - 占位符可以多值，按 `|` 分隔，便于直接拼成 `git grep` / `git log` 的 ERE。

## 1. Identity Patterns（Dimension 1）

填写当前用户实际出现在 git author / committer 字段中的所有私有形态，包括历史机器、临时账号、企业邮箱、个人通讯邮箱和真实姓名。

```
USER_CORP_DOMAIN  = <例如：example.com|corp.example.com>
USER_PERSONAL_DOMAIN = <例如：qq.com|163.com|gmail.com>
USER_REAL_NAME    = <例如：example_user|Example User>
USER_LEGACY_HANDLE = <历史 handle、旧昵称、旧机器名>
```

引用方式（在 SKILL.md 工作流中调用）：

```bash
# Dimension 1 — Git History Identity（高置信度 P0/HIGH）
git log --format='%an <%ae>' | sort -u | grep -iE "@($USER_CORP_DOMAIN)|@($USER_PERSONAL_DOMAIN)|$USER_REAL_NAME|$USER_LEGACY_HANDLE"
git log --format='%cn <%ce>' | sort -u | grep -iE "@($USER_CORP_DOMAIN)|@($USER_PERSONAL_DOMAIN)|$USER_REAL_NAME|$USER_LEGACY_HANDLE"
```

## 2. Content Patterns（Dimension 4 高置信度组）

只放高置信度的私有标识、内部项目代号、真实竞品名、真实内部主机名。**不要**把通用英文词如 `internal`、`private`、`prod`、`dev` 放进这里——它们会在中大型代码库里产生大量误报，应放在 §3 低置信度组。

```
USER_PRIVATE_TOKENS = <例如：example_corp|example_user|<corp_codename>|<internal_hostname>>
USER_PRIVATE_TOOLS  = <例如：rtk|<internal_cli>>
```

引用方式：

```bash
# Dimension 4 高置信度：直接报 P0/HIGH
git grep -nIE "$USER_PRIVATE_TOKENS" -- .
git grep -nIE "(^|[^A-Za-z0-9_])($USER_PRIVATE_TOOLS)([^A-Za-z0-9_]|$)" -- .
```

## 3. Low-Confidence Trigger Words（仅触发人工复核）

以下词在通用代码库高频出现，不能直接判定 P0/HIGH，只用作**人工复核触发器**：命中后由审计者结合上下文判断是否是真泄露（例如 `internal_api_url`、`# private use only` 等需复核；`private static final`、`internal class` 等语言关键字直接忽略）。

```
LOW_CONFIDENCE_TRIGGERS = internal|private|confidential|do[-_ ]not[-_ ]share|company-only
```

引用方式：

```bash
# Dimension 4 低置信度：列出命中清单，人工逐条判定，不直接计入 severity
git grep -nIE "$LOW_CONFIDENCE_TRIGGERS" -- . > /tmp/public-release-sweep.low-confidence.txt
wc -l /tmp/public-release-sweep.low-confidence.txt
```

报告中应作为 `MEDIUM (needs review)` 列出，而不是 `P0/HIGH`。

## 4. Filling Workflow

1. 从用户私有 git config（`git config --global user.email`、`user.name`）和历史 commit 抽取 §1 字段。
2. 从用户私有项目代号、内部工具名、私有主机名补充 §2 字段。
3. §3 默认保留模板值；调用方一般不需要修改。
4. 把本模板的引用结果以 ERE 字符串注入 Dimension 1 / Dimension 4 命令；**绝不**把字面值写回 SKILL.md。
