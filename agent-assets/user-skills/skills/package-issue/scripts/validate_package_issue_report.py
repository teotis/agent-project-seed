#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


PACKAGE_HEADING = re.compile(r"^##\s+(PKG-[A-Z0-9-]+)\s+(.+)$", re.MULTILINE)
EVIDENCE_LINE = re.compile(r"^-\s+(EV-[A-Z0-9-]+)\s+\|", re.MULTILINE)
EVIDENCE_ID = re.compile(r"\bEV-[A-Z0-9-]+\b")
VALID_ROUTES = {
    "diagnosing-bugs",
    "handoff",
    "orchestration",
    "external-assist",
    "deferred",
}
REQUIRED_SUMMARY_MARKERS = (
    "- 输入问题数：",
    "- 问题包数：",
    "- 待补证据：",
    "- 修复价值分布：",
    "- 路由分布：",
    "- 推荐顺序：",
)
REQUIRED_PACKAGE_MARKERS = (
    "- **包含问题**:",
    "- **领域**:",
    "- **修复复杂度**:",
    "- **初查置信度**:",
    "- **当前判断**:",
    "- **修复价值**:",
    "- **next_route**:",
    "- **证据引用**:",
    "- **依赖**:",
    "- **明确排除**:",
    "### 问题表现",
    "### 用户影响",
    "### 初步分析",
    "### 证据与未知",
    "### 修复价值核查",
    "### 分包依据与依赖闭包",
    "### 范围与依赖",
    "### 后续细化重点",
)


def package_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(PACKAGE_HEADING.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.start():end]))
    return blocks


def field_value(block: str, label: str) -> str | None:
    prefix = f"- **{label}**:"
    for line in block.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return None


def comma_separated_values(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def ownership_ids(block: str) -> list[str]:
    return comma_separated_values(field_value(block, "包含问题"))


def evidence_ids(text: str) -> list[str]:
    return EVIDENCE_LINE.findall(text)


def evidence_references(block: str) -> list[str]:
    value = field_value(block, "证据引用")
    if not value:
        return []
    return EVIDENCE_ID.findall(value)


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:next_heading if next_heading >= 0 else len(text)]


def has_nonempty_field(block: str, label: str) -> bool:
    value = field_value(block, label)
    return bool(value and value.lower() != "none")


def validate_summary(text: str, issues: list[str]) -> None:
    summary = section(text, "## 决策摘要")
    if not summary:
        issues.append("缺少决策摘要")
        return
    for marker in REQUIRED_SUMMARY_MARKERS:
        if marker not in summary:
            issues.append(f"决策摘要缺少字段：{marker}")


def validate_evidence_ledger(text: str, issues: list[str]) -> set[str]:
    if "## Evidence Ledger" not in text:
        issues.append("缺少 Evidence Ledger")
        return set()
    ids = evidence_ids(section(text, "## Evidence Ledger"))
    counts = Counter(ids)
    duplicates = sorted(evidence_id for evidence_id, count in counts.items() if count > 1)
    if duplicates:
        issues.append(f"Evidence ID 重复：{', '.join(duplicates)}")
    if not ids:
        issues.append("Evidence Ledger 未声明任何 EV-* 证据")
    return set(ids)


def validate_report(
    report_path: Path,
    expected_issue_ids: set[str] | None = None,
) -> list[str]:
    text = report_path.read_text(encoding="utf-8")
    issues: list[str] = []

    if not text.startswith("# 问题初查与打包"):
        issues.append("缺少标准文档标题")
    validate_summary(text, issues)
    if "## 输入覆盖" not in text:
        issues.append("缺少输入覆盖清单")
    ledger_ids = validate_evidence_ledger(text, issues)

    blocks = package_blocks(text)
    if not blocks:
        issues.append("未找到任何 PKG-* 问题包")
        return issues

    owners: list[str] = []
    for package_id, block in blocks:
        for marker in REQUIRED_PACKAGE_MARKERS:
            if marker not in block:
                issues.append(f"{package_id} 缺少必填结构：{marker}")
        ids = ownership_ids(block)
        if not ids:
            issues.append(f"{package_id} 未声明包含问题")
        owners.extend(ids)

        route = field_value(block, "next_route")
        if route and route not in VALID_ROUTES:
            issues.append(f"{package_id} next_route 无效：{route}")
        if route == "orchestration" and not has_nonempty_field(block, "编排理由"):
            issues.append(f"{package_id} 使用 orchestration 时必须声明编排理由")

        references = evidence_references(block)
        if not references:
            issues.append(f"{package_id} 未引用任何 Evidence ID")
        unknown_evidence = sorted(set(references) - ledger_ids)
        if unknown_evidence:
            issues.append(
                f"{package_id} 引用了未声明的 Evidence ID：{', '.join(unknown_evidence)}"
            )

    counts = Counter(owners)
    duplicates = sorted(issue_id for issue_id, count in counts.items() if count > 1)
    if duplicates:
        issues.append(f"问题重复归属：{', '.join(duplicates)}")

    if expected_issue_ids is not None:
        missing = sorted(expected_issue_ids - set(owners))
        unexpected = sorted(set(owners) - expected_issue_ids)
        if missing:
            issues.append(f"问题未分配到主包：{', '.join(missing)}")
        if unexpected:
            issues.append(f"出现未声明的问题 ID：{', '.join(unexpected)}")

    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a package-issue Markdown report."
    )
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--issue-ids",
        default="",
        help="Comma-separated expected IDs, for example ISSUE-001,ISSUE-002.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected = {
        value.strip()
        for value in args.issue_ids.split(",")
        if value.strip()
    }
    issues = validate_report(args.report, expected or None)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1
    print(f"OK: {args.report} satisfies the package issue report contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
