#!/usr/bin/env python3
"""
UserPromptSubmit hook: injects a project status panel at controlled moments.

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
    mode = os.environ.get("PANEL_MODE", "entry")
    cmd = [
        sys.executable or "python3",
        str(project_root / "tools" / "panel.py"),
        "--mode",
        mode,
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
        log("Python executable not found")
        return -1, ""
    except Exception as exc:
        log(f"unexpected error: {exc}")
        return -1, ""


def record_clean_checkpoint_baseline(project_root: Path) -> None:
    command = [
        sys.executable or "python3",
        str(project_root / ".codex" / "hooks" / "clean_checkpoint_first.py"),
        "session-start",
    ]
    try:
        subprocess.run(command, cwd=str(project_root), capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        log(f"clean-checkpoint baseline unavailable: {exc}")


def panel_mode(payload: dict) -> str:
    value = payload.get("panel_mode") or payload.get("panelMode") or os.environ.get("PANEL_MODE", "")
    return value if value in {"entry", "handoff"} else "entry"


def is_first_prompt(payload: dict, project_root: Path) -> bool:
    if payload.get("is_first_prompt") is True or payload.get("isFirstPrompt") is True:
        return True
    prompt_index = payload.get("prompt_index") or payload.get("promptIndex")
    if isinstance(prompt_index, int):
        return prompt_index <= 1
    session_id = payload.get("session_id") or payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id:
        return False
    state_dir = project_root / ".tmp"
    state_path = state_dir / "panel_sessions.json"
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        seen = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
        if session_id in seen:
            return False
        seen.append(session_id)
        state_path.write_text(json.dumps(seen[-100:], ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as exc:
        log(f"session state unavailable: {exc}")
        return False


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
    mode = panel_mode(hook_input)
    first_prompt = is_first_prompt(hook_input, project_root)
    if first_prompt:
        record_clean_checkpoint_baseline(project_root)
    if mode != "handoff" and not first_prompt:
        return 0

    os.environ["PANEL_MODE"] = mode
    exit_code, panel_text = run_panel(project_root)
    if exit_code != 0 or not panel_text:
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "[System Instruction] 如果这是本次回复需要展示的状态面板，请先原样输出下面的中文状态面板；"
                "如果上下文里已有多个历史状态面板，只保留最新一次作为参考：\n\n"
                + panel_text
            ),
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
