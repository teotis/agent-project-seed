#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


HOOK_NAME = "clean-checkpoint-first"
ALLOW_DIRTY_ENV = "CLEAN_CHECKPOINT_FIRST_ALLOW_DIRTY"
ALLOW_DIRTY_FILE = ".codex/clean-checkpoint-first.allow-dirty"


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def find_project_root(start: Path) -> Path:
    completed = run_git(start, ["rev-parse", "--show-toplevel"])
    if completed.returncode == 0 and completed.stdout.strip():
        return Path(completed.stdout.strip()).resolve()
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / "AGENTS.md").is_file() and (parent / "tools" / "project.py").is_file():
            return parent
    return current


def git_common_dir(root: Path) -> Path | None:
    completed = run_git(root, ["rev-parse", "--git-common-dir"])
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    path = Path(completed.stdout.strip())
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def state_file(root: Path) -> Path:
    common_dir = git_common_dir(root)
    if common_dir is not None:
        safe_root = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
        return common_dir / HOOK_NAME / f"{safe_root}.json"
    return root / ".tmp" / HOOK_NAME / "state.json"


def diff_digest(root: Path, path: str, status: str) -> str:
    chunks = [status]
    for args in (["diff", "--binary", "--", path], ["diff", "--cached", "--binary", "--", path]):
        completed = run_git(root, args)
        if completed.returncode == 0:
            chunks.append(completed.stdout)
    return hashlib.sha256("\0".join(chunks).encode("utf-8")).hexdigest()


def tracked_dirty(root: Path) -> dict[str, dict[str, str]]:
    completed = run_git(root, ["status", "--porcelain=v1", "--untracked-files=no"])
    if completed.returncode != 0:
        return {}
    dirty: dict[str, dict[str, str]] = {}
    for line in completed.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            dirty[path] = {
                "status": status,
                "digest": diff_digest(root, path, status),
            }
    return dirty


def read_state(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_state(path: Path, root: Path, dirty: dict[str, dict[str, str]], *, reset_baseline: bool) -> None:
    prior = read_state(path)
    baseline = dirty if reset_baseline else prior.get("baseline", dirty)
    data = {
        "root": str(root),
        "baseline": baseline,
        "latest": dirty,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def allow_dirty(root: Path) -> bool:
    return os.environ.get(ALLOW_DIRTY_ENV) == "1" or (root / ALLOW_DIRTY_FILE).exists()


def stop(root: Path) -> int:
    if allow_dirty(root):
        return 0

    path = state_file(root)
    state = read_state(path)
    baseline = state.get("baseline", {})
    if not isinstance(baseline, dict):
        baseline = {}

    dirty = tracked_dirty(root)
    write_state(path, root, dirty, reset_baseline=False)
    new_dirty = {name: entry for name, entry in dirty.items() if baseline.get(name) != entry}
    if not new_dirty:
        return 0

    print(
        "Stop blocked by clean-checkpoint-first: this session left new tracked dirty changes.",
        file=sys.stderr,
    )
    print(
        "Create a local checkpoint commit, revert only your own changes, or explain the blocker.",
        file=sys.stderr,
    )
    print(
        f"To bypass intentionally for this session, set {ALLOW_DIRTY_ENV}=1.",
        file=sys.stderr,
    )
    print("New tracked dirty paths:", file=sys.stderr)
    for name in sorted(new_dirty):
        status = new_dirty[name].get("status", "??")
        print(f"- {status} {name}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Project-local clean checkpoint hook")
    parser.add_argument("event", choices=["session-start", "post-tool-use", "stop"])
    args = parser.parse_args()

    root = find_project_root(Path.cwd())
    if not (root / ".git").exists():
        return 0

    path = state_file(root)
    dirty = tracked_dirty(root)
    if args.event == "session-start":
        write_state(path, root, dirty, reset_baseline=True)
        return 0
    if args.event == "post-tool-use":
        write_state(path, root, dirty, reset_baseline=False)
        return 0
    return stop(root)


if __name__ == "__main__":
    raise SystemExit(main())
