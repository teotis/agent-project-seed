#!/usr/bin/env python3
"""
Lightweight Chinese project status panel.

The panel is intentionally cheap: it reads a few stable project files and runs
a handful of bounded git commands. It does not scan the source tree, inspect
large diffs, call networks, or invoke an LLM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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


@dataclass(frozen=True)
class DeliveryReceipt:
    goal: str = ""
    acceptance: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    gaps: tuple[str, ...] = field(default_factory=tuple)
    next_decision: tuple[str, ...] = field(default_factory=tuple)


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


def read_delivery_receipt() -> DeliveryReceipt | None:
    path = ROOT / "control" / "delivery_receipt.md"
    if not path.exists():
        return None
    section_names = {
        "user goal": "goal",
        "用户目标": "goal",
        "acceptance criteria": "acceptance",
        "验收标准": "acceptance",
        "evidence": "evidence",
        "证据": "evidence",
        "remaining gaps": "gaps",
        "剩余缺口": "gaps",
        "user next decision": "next_decision",
        "用户下一决策": "next_decision",
    }
    values: dict[str, list[str]] = {name: [] for name in section_names.values()}
    current: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", raw_line)
        if heading:
            current = section_names.get(heading.group(1).strip().casefold())
            continue
        if current is None:
            continue
        value = raw_line.strip()
        if not value:
            continue
        values[current].append(value[2:].strip() if value.startswith("- ") else value)
    return DeliveryReceipt(
        goal=" ".join(values["goal"]),
        acceptance=tuple(values["acceptance"]),
        evidence=tuple(values["evidence"]),
        gaps=tuple(values["gaps"]),
        next_decision=tuple(values["next_decision"]),
    )


def delivery_receipt_lines() -> list[str]:
    receipt = read_delivery_receipt()
    if receipt is None:
        return []
    lines: list[str] = []
    if receipt.goal:
        lines.append(f"目标: {receipt.goal}")
    if receipt.acceptance:
        passed = sum(1 for item in receipt.acceptance if item.casefold().startswith("[x]"))
        pending_evidence = not receipt.evidence or any("pending" in item.casefold() for item in receipt.evidence)
        if passed < len(receipt.acceptance):
            goal_status = "进行中"
        elif pending_evidence:
            goal_status = "验收已勾选，待补证据"
        elif receipt.gaps:
            goal_status = "验收已通过，仍有缺口"
        else:
            goal_status = "验收完成"
        lines.append(f"目标状态: {goal_status}")
        lines.append(f"验收: {passed}/{len(receipt.acceptance)} 已通过")
    if receipt.evidence:
        lines.append("证据: " + "；".join(receipt.evidence[:2]))
    if receipt.gaps:
        lines.append("缺口: " + "；".join(receipt.gaps[:2]))
    if receipt.next_decision:
        lines.append("用户决策: " + "；".join(receipt.next_decision[:2]))
    return lines


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


def active_task_state_file() -> Path | None:
    result = run_git(["rev-parse", "--git-common-dir"])
    if result is None or result.returncode != 0 or not result.stdout.strip():
        return None
    common_dir = Path(result.stdout.strip())
    if not common_dir.is_absolute():
        common_dir = ROOT / common_dir
    worktree_key = hashlib.sha256(str(ROOT.resolve()).encode("utf-8")).hexdigest()[:16]
    return common_dir.resolve() / "project-seed" / "active-task" / f"{worktree_key}.json"


def read_active_task_state() -> dict[str, str]:
    path = active_task_state_file()
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {key: value for key, value in data.items() if isinstance(key, str) and isinstance(value, str)}


def first_unchecked_acceptance(brief: Path) -> str:
    if not brief.is_file():
        return ""
    in_acceptance = False
    for raw_line in brief.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", raw_line)
        if heading:
            in_acceptance = heading.group(1).strip().casefold() in {
                "acceptance criteria",
                "验收标准",
                "验收条件",
            }
            continue
        if in_acceptance:
            match = re.match(r"^\s*-\s*\[\s\]\s+(.+?)\s*$", raw_line)
            if match:
                return match.group(1).strip()
    return ""


def first_pending_task_evidence(status: Path) -> str:
    if not status.is_file():
        return ""
    lines = status.read_text(encoding="utf-8").splitlines()
    if not lines:
        return ""
    header = lines[0].split("\t")
    indexes = {name: index for index, name in enumerate(header)}
    if "package_id" not in indexes:
        return ""
    complete_values = {"ok", "pass", "passed", "complete", "completed", "verified", "clean", "n/a"}
    for raw_line in lines[1:]:
        values = raw_line.split("\t")
        if len(values) <= indexes["package_id"]:
            continue
        package = values[indexes["package_id"]]
        for field in ("verification", "integration", "cleanup"):
            index = indexes.get(field)
            if index is None or index >= len(values):
                continue
            value = values[index].strip()
            if value.casefold() not in complete_values:
                return f"{package} {field} {value or 'missing'}"
    return ""


def active_task_lines() -> list[str]:
    state = read_active_task_state()
    slug = state.get("slug", "")
    task_root = ROOT / "control" / "tasks" / slug
    if not slug or not task_root.is_dir():
        return []
    title = slug
    brief = task_root / "brief.md"
    if brief.is_file():
        match = re.search(r"^#\s+(.+?)\s*$", brief.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            title = match.group(1).strip()
    lines = [f"复杂任务: {title} ({slug})"]
    if state.get("phase"):
        lines.append(f"阶段: {state['phase']}")
    if state.get("next"):
        lines.append(f"任务下一步: {state['next']}")
    gap = first_unchecked_acceptance(brief) or first_pending_task_evidence(task_root / "status.tsv")
    if gap:
        lines.append(f"任务缺口: {gap}")
    return lines


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
    receipt_lines = delivery_receipt_lines()
    task_lines = active_task_lines()

    lines = [
        f"[{project_name}] {mode_label}",
        *receipt_lines,
        *task_lines,
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
