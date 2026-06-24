#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


NOTE_HEADINGS = {
    "decision": "Decisions",
    "finding": "Findings",
    "preference": "Preferences",
    "constraint": "Constraints",
}


def legacy_user_memory_root() -> Path:
    return Path.home() / ".codex" / "memory" / "engineering"


def default_memory_root(project_path: str) -> Path:
    return Path(project_path).expanduser() / ".memory" / "engineering"


def resolve_memory_root(memory_root: Path | None, project_path: str) -> Path:
    if memory_root is not None:
        return memory_root.expanduser()
    configured = os.environ.get("ENGINEERING_MEMORY_ROOT")
    if configured:
        return Path(configured).expanduser()
    return default_memory_root(project_path)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_project_path(project_path: str) -> str:
    return str(Path(project_path).expanduser())


def project_id(project_path: str) -> str:
    normalized = normalize_project_path(project_path).rstrip("/")
    name = Path(normalized).name or "project"
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:8]
    return f"{slugify(name)}-{digest}"


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    chars = []
    previous_hyphen = False
    for char in lowered:
        if char.isalnum():
            chars.append(char)
            previous_hyphen = False
        elif not previous_hyphen:
            chars.append("-")
            previous_hyphen = True
    slug = "".join(chars).strip("-")
    return slug or "item"


def ensure_memory_root(memory_root: Path) -> None:
    (memory_root / "projects").mkdir(parents=True, exist_ok=True)


def as_list(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    return [value.strip() for value in values if value and value.strip()]


def record_event(
    memory_root: Path,
    *,
    skill: str,
    project_path: str,
    task: str,
    summary: str = "",
    artifacts: Iterable[str] | None = None,
    key_findings: Iterable[str] | None = None,
    decisions: Iterable[str] | None = None,
    user_preferences: Iterable[str] | None = None,
    next_actions: Iterable[str] | None = None,
    timestamp: str | None = None,
) -> dict[str, object]:
    ensure_memory_root(memory_root)
    normalized_project = normalize_project_path(project_path)
    event = {
        "timestamp": timestamp or utc_now(),
        "skill": skill,
        "project_id": project_id(normalized_project),
        "project_path": normalized_project,
        "task": task,
        "summary": summary,
        "artifacts": as_list(artifacts),
        "key_findings": as_list(key_findings),
        "decisions": as_list(decisions),
        "user_preferences": as_list(user_preferences),
        "next_actions": as_list(next_actions),
    }
    events_path = memory_root / "artifacts.jsonl"
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def project_note_path(memory_root: Path, project_path: str) -> Path:
    return memory_root / "projects" / f"{project_id(project_path)}.md"


def read_project_notes(path: Path, project_path: str) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        f"# Engineering Memory: {Path(project_path).name or 'project'}\n\n"
        f"Project path: `{normalize_project_path(project_path)}`\n\n"
        "## Decisions\n\n"
        "## Findings\n\n"
        "## Preferences\n\n"
        "## Constraints\n"
    )


def remember_note(
    memory_root: Path,
    *,
    project_path: str,
    kind: str,
    text: str,
    source: str,
    timestamp: str | None = None,
) -> dict[str, str]:
    if kind not in NOTE_HEADINGS:
        raise ValueError(f"kind must be one of: {', '.join(sorted(NOTE_HEADINGS))}")
    ensure_memory_root(memory_root)
    path = project_note_path(memory_root, project_path)
    content = read_project_notes(path, project_path)
    clean_text = " ".join(text.strip().split())
    if clean_text in content:
        return {"status": "existing", "path": str(path)}

    heading = f"## {NOTE_HEADINGS[kind]}"
    bullet = f"- {clean_text} _(source: {source}; recorded: {timestamp or utc_now()})_"
    lines = content.splitlines()
    try:
        heading_index = lines.index(heading)
    except ValueError:
        lines.extend(["", heading, ""])
        heading_index = len(lines) - 2

    insert_at = heading_index + 1
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1
    lines.insert(insert_at, bullet)
    if insert_at + 1 < len(lines) and lines[insert_at + 1].startswith("## "):
        lines.insert(insert_at + 1, "")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"status": "created", "path": str(path)}


def load_recent_events(memory_root: Path, project_path: str, limit: int) -> list[dict[str, object]]:
    events_path = memory_root / "artifacts.jsonl"
    if not events_path.is_file():
        return []
    pid = project_id(project_path)
    matches: list[dict[str, object]] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("project_id") == pid:
            matches.append(event)
    return matches[-limit:]


def recall_project(memory_root: Path, *, project_path: str, limit: int = 5) -> str:
    ensure_memory_root(memory_root)
    notes_path = project_note_path(memory_root, project_path)
    notes = read_project_notes(notes_path, project_path).rstrip()
    events = load_recent_events(memory_root, project_path, limit)
    output = [notes, "", "## Recent Artifacts", ""]
    if not events:
        output.append("- No recorded artifact events yet.")
    for event in reversed(events):
        artifacts = event.get("artifacts") or []
        artifact_text = ", ".join(f"`{item}`" for item in artifacts) if artifacts else "no artifacts"
        output.append(
            f"- {event.get('timestamp')} `{event.get('skill')}`: "
            f"{event.get('task')} — {event.get('summary') or 'no summary'} ({artifact_text})"
        )
    return "\n".join(output).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and recall engineering memory.")
    parser.add_argument("--memory-root", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record", help="Append an artifact event.")
    record.add_argument("--skill", required=True)
    record.add_argument("--project", required=True)
    record.add_argument("--task", required=True)
    record.add_argument("--summary", default="")
    record.add_argument("--artifact", action="append", default=[])
    record.add_argument("--finding", action="append", default=[])
    record.add_argument("--decision", action="append", default=[])
    record.add_argument("--preference", action="append", default=[])
    record.add_argument("--next-action", action="append", default=[])
    record.add_argument("--timestamp")

    remember = subparsers.add_parser("remember", help="Upsert a long-lived project note.")
    remember.add_argument("--project", required=True)
    remember.add_argument("--kind", required=True, choices=sorted(NOTE_HEADINGS))
    remember.add_argument("--text", required=True)
    remember.add_argument("--source", required=True)
    remember.add_argument("--timestamp")

    recall = subparsers.add_parser("recall", help="Print project engineering memory.")
    recall.add_argument("--project", required=True)
    recall.add_argument("--limit", type=int, default=5)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_path = args.project
    memory_root = resolve_memory_root(args.memory_root, project_path)
    if args.command == "record":
        event = record_event(
            memory_root,
            skill=args.skill,
            project_path=args.project,
            task=args.task,
            summary=args.summary,
            artifacts=args.artifact,
            key_findings=args.finding,
            decisions=args.decision,
            user_preferences=args.preference,
            next_actions=args.next_action,
            timestamp=args.timestamp,
        )
        print(json.dumps(event, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "remember":
        result = remember_note(
            memory_root,
            project_path=args.project,
            kind=args.kind,
            text=args.text,
            source=args.source,
            timestamp=args.timestamp,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "recall":
        print(recall_project(memory_root, project_path=args.project, limit=args.limit), end="")
        return 0
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
