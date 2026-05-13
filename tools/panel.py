#!/usr/bin/env python3
"""
项目状态面板生成器 — 每次对话自动注入。

三档状态:
  - Seed 模板: 尚未初始化
  - 已初始化，目标待补全: init 已运行，但 Current Intent 未编辑
  - 已就绪: Current Intent 已定制
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEED_PLACEHOLDER = "复制本底座后，先更新本节和"
PENDING_MARKER = "已初始化，目标待补全"


def read_project_name() -> str:
    """读取项目名，优先从 contract.md，回退到 pyproject.toml。"""
    contract = ROOT / "control" / "contract.md"
    if contract.exists():
        text = contract.read_text(encoding="utf-8")
        match = re.search(r"\*\*项目\*\*:\s*(.+)", text)
        if match:
            return match.group(1).strip()
    toml = ROOT / "pyproject.toml"
    if toml.exists():
        text = toml.read_text(encoding="utf-8")
        match = re.search(r'^name\s*=\s*"(.+?)"', text, re.MULTILINE)
        if match:
            return match.group(1)
    return ""


def read_package_name() -> str:
    """从 src/ 下的包目录推断包名。"""
    src = ROOT / "src"
    if not src.exists():
        return ""
    dirs = [d for d in src.iterdir() if d.is_dir() and not d.name.startswith("_")]
    return dirs[0].name if dirs else ""


def detect_status() -> str:
    """检测项目状态: seed / pending / ready。"""
    contract = ROOT / "control" / "contract.md"
    if not contract.exists():
        return "seed"
    text = contract.read_text(encoding="utf-8")
    if SEED_PLACEHOLDER in text:
        return "seed"
    if PENDING_MARKER in text:
        return "pending"
    return "ready"


def count_ledger_records() -> int:
    """统计 ledger.md 中的记录条数。"""
    ledger = ROOT / "control" / "ledger.md"
    if not ledger.exists():
        return 0
    text = ledger.read_text(encoding="utf-8")
    return len(re.findall(r"^## \d{4}-\d{2}-\d{2}T", text, re.MULTILINE))


def extract_intent_summary() -> str:
    """从 contract.md 提取 Current Intent 中的项目目标行。"""
    contract = ROOT / "control" / "contract.md"
    if not contract.exists():
        return ""
    text = contract.read_text(encoding="utf-8")
    match = re.search(r"## Current Intent\n\n(.+?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return ""
    body = match.group(1).strip()
    # 跳过元数据行（**项目**: / **状态**:），提取第一个 "- " 开头的行
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("- "):
            return line[2:]
    return ""


def extract_next_action() -> str:
    """从 state.md 提取下一步行动。"""
    state = ROOT / "control" / "state.md"
    if not state.exists():
        return ""
    text = state.read_text(encoding="utf-8")
    match = re.search(r"## Next Maintenance Action\n\n(.+?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return ""
    for line in match.group(1).strip().splitlines():
        line = line.strip()
        if line.startswith("- "):
            return line[2:]
    return ""


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


STATUS_LABELS = {
    "seed": "Seed 模板",
    "pending": "已初始化，目标待补全",
    "ready": "已就绪",
}


def generate_panel() -> str:
    today = date.today()
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]
    status = detect_status()
    project_name = read_project_name() or "Agent Project Seed"

    if status == "seed":
        return "\n".join([
            f"【{project_name}】{today.isoformat()} ({weekday})",
            f"状态: {STATUS_LABELS[status]}",
            "→ 运行 `python3 tools/project.py init --name \"你的项目名\"` 开始",
        ])

    package = read_package_name()
    records = count_ledger_records()
    git = git_status_summary()
    intent = extract_intent_summary()
    next_action = extract_next_action()

    lines = [
        f"【{project_name}】{today.isoformat()} ({weekday})",
        f"状态: {STATUS_LABELS[status]}",
        f"Git: {git} | Ledger: {records} 条 | Package: {package}",
    ]
    if intent:
        lines.append(f"目标: {intent}")
    if next_action:
        lines.append(f"下一步: {next_action}")
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
