#!/usr/bin/env python3
"""
项目状态面板生成器 — 每次对话自动注入。

检测项目初始化状态，显示简要情况。
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLACEHOLDER_TEXT = "复制本底座后，先更新本节和"


def is_initialized() -> bool:
    """检查项目是否已初始化（contract.md 的 Current Intent 是否被定制）。"""
    contract = ROOT / "control" / "contract.md"
    if not contract.exists():
        return False
    text = contract.read_text(encoding="utf-8")
    return PLACEHOLDER_TEXT not in text


def count_ledger_records() -> int:
    """统计 ledger.md 中的记录条数。"""
    ledger = ROOT / "control" / "ledger.md"
    if not ledger.exists():
        return 0
    text = ledger.read_text(encoding="utf-8")
    return len(re.findall(r"^## \d{4}-\d{2}-\d{2}T", text, re.MULTILINE))


def extract_intent() -> str:
    """从 contract.md 提取 Current Intent 的前两行。"""
    contract = ROOT / "control" / "contract.md"
    if not contract.exists():
        return ""
    text = contract.read_text(encoding="utf-8")
    match = re.search(r"## Current Intent\n\n(.+?)(?:\n\n|\Z)", text, re.DOTALL)
    if not match:
        return ""
    lines = [l.strip() for l in match.group(1).strip().splitlines() if l.strip()]
    return " | ".join(lines[:2])


def git_status_summary() -> str:
    """获取 git 状态摘要。"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT, capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return "unknown"
        changed = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
        return f"{changed} file{'s' if changed != 1 else ''}" if changed else "clean"
    except Exception:
        return "unknown"


def generate_panel() -> str:
    today = date.today()
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]

    if not is_initialized():
        return "\n".join([
            f"【Agent Project Seed】{today.isoformat()} ({weekday})",
            "状态: 尚未初始化",
            "→ 运行 `python3 tools/project.py init --name \"你的项目名\"` 开始",
        ])

    records = count_ledger_records()
    git = git_status_summary()
    intent = extract_intent()

    lines = [
        f"【Agent Project Seed】{today.isoformat()} ({weekday})",
        f"Git: {git} | Ledger 记录: {records} 条",
    ]
    if intent:
        lines.append(f"目标: {intent}")
    lines.append("→ 运行 `python3 tools/project.py check` 检查项目健康度")
    return "\n".join(lines)


def main() -> int:
    try:
        print(generate_panel())
    except Exception as exc:
        print(f"[panel] error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
