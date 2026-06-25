#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


PACKAGE_HEADING = re.compile(r"^##\s+(PKG-[A-Z0-9-]+)\s+(.+)$", re.MULTILINE)
ISSUE_ID = re.compile(r"\bISSUE-\d+\b")
REQUIRED_PACKAGE_MARKERS = (
    "- **包含问题**:",
    "- **领域**:",
    "- **修复复杂度**:",
    "- **初查置信度**:",
    "### 问题表现",
    "### 初步分析",
    "### 证据与未知",
    "### 后续细化重点",
)


def package_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(PACKAGE_HEADING.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.start():end]))
    return blocks


def ownership_ids(block: str) -> list[str]:
    for line in block.splitlines():
        if line.startswith("- **包含问题**:"):
            return ISSUE_ID.findall(line)
    return []


def validate_report(
    report_path: Path,
    expected_issue_ids: set[str] | None = None,
) -> list[str]:
    text = report_path.read_text(encoding="utf-8")
    issues: list[str] = []

    if not text.startswith("# 批量问题初查与问题分包"):
        issues.append("缺少标准文档标题")
    if "## 输入覆盖" not in text:
        issues.append("缺少输入覆盖清单")
    if "## 推荐使用方法" not in text:
        issues.append("缺少推荐使用方法")
    if "/agent-orchestration-planner" not in text:
        issues.append("推荐使用方法未包含 agent-orchestration-planner 调用")

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
        description="Validate a bulk-issue-triage Markdown report."
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
    print(f"OK: {args.report} satisfies the bulk issue triage report contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
