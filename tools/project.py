#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTICE = "<!-- Generated from control/contract.md. Do not edit directly. -->"

REQUIRED_FILES = [
    "control/contract.md",
    "control/ledger.md",
    "control/state.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "pyproject.toml",
    ".gitignore",
    ".env.example",
]

REQUIRED_DIRS = ["control", "work/in", "work/out", "work/tmp", "tools", "src"]

ALLOWED_PREFIXES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "Makefile",
    "pyproject.toml",
    ".gitignore",
    ".env.example",
    ".claude/",
    "control/",
    "tools/",
    "src/",
    "tests/",
    "work/in/.gitkeep",
    "work/out/.gitkeep",
    "work/tmp/.gitkeep",
)

REJECT_PREFIXES = (".env", "work/tmp/", ".pytest_cache/", "__pycache__/")

TEXT_SUFFIXES = {".md", ".py", ".toml", ".txt", ".json", ".example", ".gitignore", ".yml", ".yaml"}


@dataclass
class Result:
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues


@dataclass(frozen=True)
class GitChange:
    status: str
    path: str


def slugify_project(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", name.strip()).strip("-").lower()
    return slug or "new-project"


def package_name_from_project(name: str) -> str:
    package = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip()).strip("_").lower()
    if not package:
        package = "new_project"
    if package[0].isdigit():
        package = f"p_{package}"
    return package


def render_agents() -> str:
    return f"""# Repository Instructions

{NOTICE}

共享工程规则来自：

`control/contract.md`

Codex 开始任务前应先读取该文件，再读取 `control/state.md`、`control/ledger.md` 以及任务相关文件。
"""


def render_claude() -> str:
    return f"""# Claude Code Entry

{NOTICE}

共享工程规则来自：

@./control/contract.md

## Claude Code Notes

- 修改共享规则后，运行 `python3 tools/project.py sync-agents`。
- 可配置 `.claude/settings.json` Stop hook 调用 `tools/project.py commit`。
- 不要在本文件复制共享主规则。
"""


def render_gemini() -> str:
    return f"""# Gemini CLI Entry

{NOTICE}

共享工程规则来自：

@./control/contract.md

## Gemini CLI Notes

- 修改共享规则后，运行 `python3 tools/project.py sync-agents`，并在 Gemini CLI 中重新加载上下文。
- 不要在本文件复制共享主规则。
"""


def expected_agent_files() -> dict[Path, str]:
    return {
        ROOT / "AGENTS.md": render_agents(),
        ROOT / "CLAUDE.md": render_claude(),
        ROOT / "GEMINI.md": render_gemini(),
    }


def sync_agents() -> int:
    if not (ROOT / "control" / "contract.md").exists():
        print("missing control/contract.md", file=sys.stderr)
        return 1
    for path, content in expected_agent_files().items():
        path.write_text(content, encoding="utf-8")
    print("Synced AGENTS.md, CLAUDE.md, and GEMINI.md.")
    return 0


def check_agent_sync(result: Result) -> None:
    if not (ROOT / "control" / "contract.md").exists():
        result.issues.append("missing control/contract.md")
        return
    for path, expected in expected_agent_files().items():
        if not path.exists():
            result.issues.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            result.issues.append(f"{path.relative_to(ROOT)} is not in sync with control/contract.md")
    if not any("sync" in issue for issue in result.issues):
        result.notices.append("agent entry files are synced")


def check_required(result: Result) -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            result.issues.append(f"missing required file: {relative}")
    for relative in REQUIRED_DIRS:
        if not (ROOT / relative).is_dir():
            result.issues.append(f"missing required dir: {relative}")


def check_package_import(result: Result) -> None:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        importlib.import_module("base_scaffold")
    except Exception as exc:
        result.issues.append(f"cannot import base_scaffold: {exc}")
    finally:
        try:
            sys.path.remove(str(ROOT / "src"))
        except ValueError:
            pass


def check_git(result: Result) -> None:
    if not (ROOT / ".git").exists():
        result.warnings.append("git repository is not initialized; run tools/project.py init after copying")
        return
    completed = run_git(["status", "--short"])
    if completed.returncode != 0:
        result.warnings.append("git status failed")


def print_result(result: Result, quiet: bool) -> None:
    if result.issues:
        print("[check] issues:")
        for issue in result.issues:
            print(f"- {issue}")
    if result.warnings:
        print("[check] warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.notices and not quiet:
        print("[check] notices:")
        for notice in result.notices:
            print(f"- {notice}")
    if result.ok and not result.warnings and not quiet:
        print("[check] OK")


def check(args: argparse.Namespace) -> int:
    result = Result()
    check_required(result)
    check_agent_sync(result)
    check_package_import(result)
    if not args.skip_git:
        check_git(result)
    print_result(result, args.quiet)
    return 1 if result.issues else 0


def is_text_file(path: Path) -> bool:
    if path.name in {".gitignore"}:
        return True
    return path.suffix in TEXT_SUFFIXES or path.name.endswith(".example")


def replace_text(project_name: str, package_name: str) -> None:
    project_slug = slugify_project(project_name)
    replacements = {
        "Base Project": project_name,
        "base-project": project_slug,
        "base_project": project_slug.replace("-", "_"),
        "base_scaffold": package_name,
        "BASE_SCAFFOLD": package_name.upper(),
    }
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file() or not is_text_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_text = text
        for old, new in replacements.items():
            new_text = new_text.replace(old, new)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")


def rename_package(package_name: str) -> None:
    src = ROOT / "src" / "base_scaffold"
    dst = ROOT / "src" / package_name
    if package_name == "base_scaffold" or not src.exists():
        return
    if dst.exists():
        raise FileExistsError(dst)
    src.rename(dst)


def tracked_initial_files() -> list[str]:
    paths: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == ".env" or rel.startswith("work/tmp/") and rel != "work/tmp/.gitkeep":
            continue
        if rel.startswith("work/out/") and rel != "work/out/.gitkeep":
            continue
        if "__pycache__" in rel or ".pytest_cache" in rel:
            continue
        paths.append(rel)
    return sorted(paths)


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def run_git_init(project_name: str) -> None:
    if (ROOT / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=ROOT, check=True)
    files = tracked_initial_files()
    if files:
        subprocess.run(["git", "add", "--", *files], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"chore: initialize {project_name}"], cwd=ROOT, check=True)


def init_project(args: argparse.Namespace) -> int:
    package_name = args.package_name or package_name_from_project(args.name)
    replace_text(args.name, package_name)
    rename_package(package_name)
    activate_settings()
    if not args.no_git:
        run_git_init(args.name)
    print(f"Initialized {args.name} with package {package_name}.")
    return 0


def activate_settings() -> None:
    """Copy settings.example.json to settings.json if settings.json does not exist."""
    example = ROOT / ".claude" / "settings.example.json"
    target = ROOT / ".claude" / "settings.json"
    if example.exists() and not target.exists():
        target.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")


def parse_status_line(line: str) -> GitChange:
    status = line[:2]
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return GitChange(status, path)


def git_changes() -> list[GitChange]:
    completed = run_git(["status", "--porcelain"])
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git status failed")
    return [parse_status_line(line) for line in completed.stdout.splitlines() if line.strip()]


def is_rejected(path: str) -> bool:
    if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in REJECT_PREFIXES):
        return True
    if path.startswith("work/out/") and path != "work/out/.gitkeep":
        return True
    return False


def is_allowed(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def classify_changes(changes: list[GitChange]) -> tuple[list[GitChange], list[GitChange]]:
    allowed: list[GitChange] = []
    rejected: list[GitChange] = []
    for change in changes:
        if "U" in change.status or is_rejected(change.path) or not is_allowed(change.path):
            rejected.append(change)
        else:
            allowed.append(change)
    return allowed, rejected


def commit(args: argparse.Namespace) -> int:
    if not (ROOT / ".git").exists():
        print("Not a git repository; run tools/project.py init first.", file=sys.stderr)
        return 1
    changes = git_changes()
    if not changes:
        print("No changes to commit.")
        return 0
    allowed, rejected = classify_changes(changes)
    if rejected:
        print("Refusing auto commit because some changes are unsafe or outside the allowlist:", file=sys.stderr)
        for change in rejected:
            print(f"- {change.status} {change.path}", file=sys.stderr)
        return 2
    if args.dry_run:
        print("Allowed changes:")
        for change in allowed:
            print(f"- {change.status} {change.path}")
        return 0
    add = run_git(["add", "--", *[change.path for change in allowed]])
    if add.returncode != 0:
        print(add.stderr.strip(), file=sys.stderr)
        return add.returncode
    completed = run_git(["commit", "-m", args.message])
    if completed.returncode != 0:
        print(completed.stdout.strip())
        print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode
    print(completed.stdout.strip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project scaffold command center.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a copied template")
    init.add_argument("--name", default=ROOT.name)
    init.add_argument("--package-name", default=None)
    init.add_argument("--no-git", action="store_true")

    check_cmd = sub.add_parser("check", help="check scaffold health")
    check_cmd.add_argument("--quiet", action="store_true")
    check_cmd.add_argument("--skip-git", action="store_true")

    sub.add_parser("sync-agents", help="sync thin agent entry files")

    commit_cmd = sub.add_parser("commit", help="safely commit allowed changes")
    commit_cmd.add_argument("--message", default="chore: auto commit agent task")
    commit_cmd.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    os.chdir(ROOT)
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        return init_project(args)
    if args.command == "check":
        return check(args)
    if args.command == "sync-agents":
        return sync_agents()
    if args.command == "commit":
        return commit(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
