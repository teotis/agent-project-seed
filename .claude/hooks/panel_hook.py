#!/usr/bin/env python3
"""
UserPromptSubmit hook: injects a project status panel before every prompt.

Reads stdin JSON from Claude Code, runs the panel generator,
and outputs the panel as additionalContext.

Protocol:
  stdin:  {"session_id": "...", "prompt": "...", "cwd": "/path/to/project"}
  stdout: {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                   "additionalContext": "panel text"}}
  exit 0: success or silent skip (never blocks the user)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def log(msg: str) -> None:
    print(f"[panel_hook] {msg}", file=sys.stderr)


def find_project_root(cwd: str) -> Path | None:
    """Walk upward to find project root by checking for a marker file."""
    marker = os.environ.get("PANEL_PROJECT_MARKER", "tools/panel.py")
    candidate = Path(cwd).resolve()
    for _ in range(10):
        if (candidate / marker).exists():
            return candidate
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    return None


def run_panel(project_root: Path) -> tuple[int, str]:
    """Run the panel command and return (exit_code, stdout)."""
    cmd = [
        sys.executable or "python3",
        str(project_root / "tools" / "panel.py"),
    ]
    try:
        result = subprocess.run(
            cmd, cwd=str(project_root),
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        log("panel command timed out after 10s")
        return -1, ""
    except FileNotFoundError:
        log("python3 not found")
        return -1, ""
    except Exception as exc:
        log(f"unexpected error: {exc}")
        return -1, ""


def main() -> int:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        log("no valid stdin JSON, skipping")
        return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    cwd = hook_input.get("cwd", "")
    project_root = find_project_root(project_dir or cwd)
    if project_root is None:
        log("project root not found, skipping")
        return 0

    exit_code, panel_text = run_panel(project_root)
    if exit_code != 0 or not panel_text:
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "【系统指令】请在本轮回答开始前，先原样输出以下项目状态面板"
                "（如上下文中有多条历史面板，只展示最后一条）：\n\n"
                + panel_text
            ),
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
