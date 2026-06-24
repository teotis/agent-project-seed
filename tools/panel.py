#!/usr/bin/env python3
"""
Lightweight Chinese project status panel.

The panel is intentionally cheap: it reads a few stable project files and runs
a handful of bounded git commands. It does not scan the source tree, inspect
large diffs, call networks, or invoke an LLM.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEED_PLACEHOLDER = "Seed Template — copy this scaffold to start a new project."
PENDING_MARKER = "Initialized, goals pending"
MAX_ITEMS_PER_GROUP = 5


@dataclass(frozen=True)
class LedgerRecord:
    title: str
    type: str = ""
    status: str = ""
    summary: tuple[str, ...] = field(default_factory=tuple)


def read_agents_text() -> str:
    agents = ROOT / "AGENTS.md"
    if not agents.exists():
        return ""
    return agents.read_text(encoding="utf-8")


def read_project_name() -> str:
    text = read_agents_text()
    match = re.search(r"\*\*Project\*\*:\s*(.+)", text)
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
    src = ROOT / "src"
    if not src.exists():
        return ""
    dirs = [d for d in src.iterdir() if d.is_dir() and not d.name.startswith("_")]
    return dirs[0].name if dirs else ""


def detect_status() -> str:
    text = read_agents_text()
    if not text:
        return "seed"
    if SEED_PLACEHOLDER in text:
        return "seed"
    if PENDING_MARKER in text:
        return "pending"
    return "ready"


def count_ledger_records() -> int:
    ledger = ROOT / "control" / "ledger.md"
    if not ledger.exists():
        return 0
    text = ledger.read_text(encoding="utf-8")
    return len(re.findall(r"^## \d{4}-\d{2}-\d{2}T", text, re.MULTILINE))


def read_ledger_records() -> list[LedgerRecord]:
    ledger = ROOT / "control" / "ledger.md"
    if not ledger.exists():
        return []
    text = ledger.read_text(encoding="utf-8")
    chunks = re.split(r"(?=^## \d{4}-\d{2}-\d{2}T)", text, flags=re.MULTILINE)
    records: list[LedgerRecord] = []
    for chunk in chunks:
        lines = chunk.strip().splitlines()
        if not lines or not lines[0].startswith("## "):
            continue
        title = lines[0].split(" - ", 1)[1].strip() if " - " in lines[0] else lines[0][3:].strip()
        record_type = ""
        status = ""
        summary: list[str] = []
        in_summary = False
        for raw_line in lines[1:]:
            line = raw_line.strip()
            if line.startswith("type:"):
                record_type = line.split(":", 1)[1].strip()
                in_summary = False
            elif line.startswith("status:"):
                status = line.split(":", 1)[1].strip()
                in_summary = False
            elif line == "summary:":
                in_summary = True
            elif re.match(r"^[a-zA-Z_-]+:", line):
                in_summary = False
            elif in_summary and line.startswith("- "):
                summary.append(line[2:].strip())
        records.append(LedgerRecord(title=title, type=record_type, status=status, summary=tuple(summary)))
    return records


def item_text(record: LedgerRecord) -> str:
    return record.summary[0] if record.summary else record.title


def dedupe_limited(values: list[str], *, seen: set[str] | None = None, limit: int = MAX_ITEMS_PER_GROUP) -> list[str]:
    seen_values = seen if seen is not None else set()
    result: list[str] = []
    for value in values:
        text = value.strip()
        key = re.sub(r"\s+", " ", text).lower()
        if not text or key in seen_values:
            continue
        result.append(text)
        seen_values.add(key)
        if len(result) >= limit:
            break
    return result


def open_items_by_type(*record_types: str, seen: set[str] | None = None) -> list[str]:
    records = [
        record for record in read_ledger_records()
        if record.status == "open" and record.type in record_types
    ]
    return dedupe_limited([item_text(record) for record in records], seen=seen)


def extract_next_actions(limit: int = 3, *, seen: set[str] | None = None) -> list[str]:
    state = ROOT / "control" / "state.md"
    if not state.exists():
        return []
    text = state.read_text(encoding="utf-8")
    match = re.search(r"## Next Maintenance Action\n\n(.+?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return []
    values = [
        line.strip()[2:].strip()
        for line in match.group(1).strip().splitlines()
        if line.strip().startswith("- ")
    ]
    return dedupe_limited(values, seen=seen, limit=limit)


def run_git(args: list[str], timeout: int = 5) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception:
        return None


def git_status_summary() -> str:
    result = run_git(["status", "--porcelain"])
    if result is None or result.returncode != 0:
        return "工作区未知"
    changed = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
    return "工作区干净" if changed == 0 else f"工作区 {changed} 个改动"


def current_branch() -> str:
    result = run_git(["branch", "--show-current"])
    if result is None or result.returncode != 0:
        return "分支未知"
    return result.stdout.strip() or "detached"


def last_commit() -> str:
    result = run_git(["log", "-1", "--oneline"])
    if result is None or result.returncode != 0:
        return "无提交信息"
    text = result.stdout.strip()
    return text if text else "无提交信息"


def worktree_summary() -> str:
    result = run_git(["worktree", "list", "--porcelain"])
    if result is None or result.returncode != 0:
        return "worktree 未知"
    total = sum(1 for line in result.stdout.splitlines() if line.startswith("worktree "))
    extras = max(total - 1, 0)
    return "worktree 无额外项" if extras == 0 else f"worktree 另有 {extras} 个"


def branch_summary() -> str:
    result = run_git(["branch", "--format=%(refname:short)", "--sort=-committerdate"])
    if result is None or result.returncode != 0:
        return "分支未知"
    current = current_branch()
    branches = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    others = [branch for branch in branches if branch != current]
    if not others:
        return f"当前 {current}"
    recent = ", ".join(others[:3])
    return f"当前 {current}; 另有 {len(others)} 个，最近: {recent}"


STATUS_LABELS = {
    "seed": "种子模板",
    "pending": "目标待定",
    "ready": "就绪",
}


def generate_panel(mode: str = "entry") -> str:
    today = date.today()
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][today.weekday()]
    status = detect_status()
    project_name = read_project_name() or "Agent Project Seed"
    mode_label = "交接" if mode == "handoff" else "进入"

    if status == "seed":
        return "\n".join([
            f"[{project_name}] {mode_label} | {current_branch()} | {git_status_summary()}",
            f"状态: {STATUS_LABELS[status]} | 记录: {count_ledger_records()} | {today.isoformat()} ({weekday})",
            f"Git: {worktree_summary()} | {branch_summary()} | 最近: {last_commit()}",
            "未完成: 无标记 open 需求",
            "风险: 无标记 open 风险",
            "下一步: 运行 `python3 tools/project.py init --name \"your-project-name\"` 初始化项目",
        ])

    package = read_package_name()
    records = count_ledger_records()
    seen: set[str] = set()
    requests = open_items_by_type("request", seen=seen)
    risks = open_items_by_type("risk", "issue", seen=seen)
    next_actions = extract_next_actions(seen=seen)

    lines = [
        f"[{project_name}] {mode_label} | {current_branch()} | {git_status_summary()}",
        f"状态: {STATUS_LABELS[status]} | 记录: {records} | 包: {package}",
        f"Git: {worktree_summary()} | {branch_summary()} | 最近: {last_commit()}",
        "未完成: " + ("；".join(requests) if requests else "无标记 open 需求"),
        "风险: " + ("；".join(risks) if risks else "无标记 open 风险"),
    ]
    if next_actions:
        lines.append("下一步: " + "；".join(next_actions))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a lightweight project status panel.")
    parser.add_argument("--mode", choices=["entry", "handoff"], default="entry")
    args = parser.parse_args()
    try:
        print(generate_panel(args.mode))
    except Exception as exc:
        print(f"[panel] error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
