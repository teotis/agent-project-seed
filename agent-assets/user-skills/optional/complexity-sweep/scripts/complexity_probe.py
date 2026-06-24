#!/usr/bin/env python3
"""Collect lightweight structural facts for complexity-sweep."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path


SCHEMA_VERSION = 1
CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".m",
    ".mm",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tmp",
    ".venv",
    ".worktrees",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "vendor",
}
BRANCH_RE = re.compile(
    r"\b(if|elif|else|for|while|case|catch|except|when)\b|&&|\|\||(?<!\?)\?(?!\?)"
)
IMPORT_RE = re.compile(
    r"^\s*(import\b|from\s+\S+\s+import\b|require\s*\(|use\s+\S+|#include\b)"
)
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect approximate structural and Git churn facts as JSON."
    )
    parser.add_argument("root", nargs="?", default=".", help="repository or directory to scan")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--no-git", action="store_true", help="skip Git history sampling")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def iter_code_files(root: Path, max_files: int, max_bytes: int) -> tuple[list[Path], int]:
    files: list[Path] = []
    skipped_large = 0
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in IGNORED_DIRS and not name.startswith("._")
        )
        for filename in sorted(filenames):
            path = Path(current) / filename
            if filename.startswith("._") or path.suffix.lower() not in CODE_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    skipped_large += 1
                    continue
            except OSError:
                continue
            files.append(path)
            if len(files) >= max_files:
                return files, skipped_large
    return files, skipped_large


def git_change_counts(root: Path) -> tuple[int, Counter[str]]:
    result = subprocess.run(
        ["git", "-C", str(root), "log", "--format=COMMIT:%H", "--name-only", "--", "."],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return 0, Counter()

    commit_count = 0
    changes: Counter[str] = Counter()
    seen_in_commit: set[str] = set()
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("COMMIT:"):
            for path in seen_in_commit:
                changes[path] += 1
            seen_in_commit.clear()
            commit_count += 1
        elif line:
            seen_in_commit.add(line)
    for path in seen_in_commit:
        changes[path] += 1
    return commit_count, changes


def indentation_level(line: str) -> int:
    prefix = line[: len(line) - len(line.lstrip(" \t"))]
    spaces = 0
    for char in prefix:
        spaces += 4 if char == "\t" else 1
    return spaces // 4


def file_facts(path: Path, root: Path, changes: Counter[str]) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    relative = path.relative_to(root).as_posix()
    branch_tokens = sum(len(BRANCH_RE.findall(line)) for line in lines)
    import_count = sum(bool(IMPORT_RE.search(line)) for line in lines)
    todo_count = len(TODO_RE.findall(text))
    max_indent = max((indentation_level(line) for line in lines if line.strip()), default=0)
    nonblank_lines = sum(bool(line.strip()) for line in lines)
    git_change_count = changes.get(relative, 0)
    hotspot_score = round(
        nonblank_lines / 50
        + branch_tokens
        + max_indent * 2
        + import_count / 2
        + git_change_count * 2
        + todo_count,
        2,
    )
    return {
        "path": relative,
        "lines": len(lines),
        "nonblank_lines": nonblank_lines,
        "branch_tokens": branch_tokens,
        "max_indent": max_indent,
        "import_count": import_count,
        "todo_count": todo_count,
        "git_change_count": git_change_count,
        "hotspot_score": hotspot_score,
    }


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    files, skipped_large = iter_code_files(root, args.max_files, args.max_bytes)
    commit_count, changes = (0, Counter()) if args.no_git else git_change_counts(root)
    facts = [file_facts(path, root, changes) for path in files]
    facts.sort(key=lambda item: str(item["path"]))
    hotspots = sorted(
        facts,
        key=lambda item: (-float(item["hotspot_score"]), str(item["path"])),
    )[:50]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "probe": "complexity",
        "root": str(root),
        "metric_note": (
            "branch_tokens, max_indent, and hotspot_score are language-agnostic "
            "heuristics for triage, not exact complexity measurements"
        ),
        "summary": {
            "files_scanned": len(facts),
            "files_skipped_large": skipped_large,
            "max_files_reached": len(files) >= args.max_files,
            "git_commits_scanned": commit_count,
        },
        "files": facts,
        "hotspots": hotspots,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
