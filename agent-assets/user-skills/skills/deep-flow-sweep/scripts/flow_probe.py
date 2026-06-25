#!/usr/bin/env python3
"""Collect lightweight flow-surface facts for deep-flow-sweep."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path


SCHEMA_VERSION = 1
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".gradle",
    ".h",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".m",
    ".md",
    ".php",
    ".properties",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
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
    "reports",
    "runs",
    "target",
    "vendor",
}
MANIFEST_NAMES = {
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "composer.json",
    "gemfile",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "settings.gradle",
    "settings.gradle.kts",
}
ENTRY_PATTERNS = {
    "http_route": re.compile(
        r"@[\w.]*(route|get|post|put|patch|delete)\s*\(|\b(app|router)\.(get|post|put|patch|delete)\s*\(",
        re.IGNORECASE,
    ),
    "cli": re.compile(
        r"\b(argparse|click\.command|typer\.Typer|cobra\.Command|commander\.)\b|if\s+__name__\s*==\s*['\"]__main__['\"]"
    ),
    "background_job": re.compile(
        r"@\w*(task|job)\b|\b(cron|scheduler|scheduleAtFixedRate|WorkManager)\b",
        re.IGNORECASE,
    ),
    "ui_entry": re.compile(
        r"@Composable\b|\b(Activity|Fragment)\b|\b(createRoot|ReactDOM\.render)\s*\("
    ),
}
BOUNDARY_PATTERNS = {
    "environment": re.compile(r"\b(os\.environ|os\.getenv|process\.env|System\.getenv)\b"),
    "network": re.compile(
        r"\b(urllib|requests\.|httpx\.|fetch\s*\(|URLSession|HttpClient|OkHttpClient)\b"
    ),
    "process": re.compile(
        r"\b(subprocess\.|child_process|Runtime\.getRuntime|ProcessBuilder|execFile\s*\()"
    ),
    "filesystem": re.compile(
        r"\b(open\s*\(|Path\s*\(|read_text\s*\(|write_text\s*\(|FileInputStream|FileOutputStream)\b"
    ),
    "database": re.compile(
        r"\b(sqlalchemy|sqlite3|psycopg|jdbc:|SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET)\b",
        re.IGNORECASE,
    ),
}
RISK_PATTERNS = {
    "broad_exception": re.compile(
        r"\bexcept\s+(Exception|BaseException)\b|\bcatch\s*\(\s*(Exception|Throwable)\b"
    ),
    "fixed_sleep": re.compile(r"\b(time\.sleep|Thread\.sleep|setTimeout)\s*\("),
    "todo_marker": re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE),
}
SWALLOWED_EXCEPTION_RE = re.compile(
    r"(except[^\n]*:\s*\n\s*(pass|return\s+None)|catch\s*\([^)]*\)\s*\{\s*\})",
    re.MULTILINE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect flow entry, boundary, automation, risk, and Git churn facts as JSON."
    )
    parser.add_argument("root", nargs="?", default=".", help="repository or directory to scan")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--max-matches-per-category", type=int, default=500)
    parser.add_argument("--no-git", action="store_true", help="skip Git history sampling")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def iter_text_files(root: Path, max_files: int, max_bytes: int) -> tuple[list[Path], int]:
    files: list[Path] = []
    skipped_large = 0
    script_path = Path(__file__).resolve()
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in IGNORED_DIRS
            and not name.startswith("._")
            and not (current_path / name / ".git").is_dir()
        )
        for filename in sorted(filenames):
            path = current_path / filename
            if filename.startswith("._"):
                continue
            try:
                if path.resolve() == script_path:
                    continue
            except OSError:
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS and filename.lower() not in MANIFEST_NAMES:
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


def classify_inventory(relative: str) -> list[str]:
    lower = relative.lower()
    name = Path(lower).name
    kinds: list[str] = []
    if name in MANIFEST_NAMES:
        kinds.append("manifests")
    if (
        lower.startswith(".github/workflows/")
        or name in {".gitlab-ci.yml", "jenkinsfile", "azure-pipelines.yml"}
    ):
        kinds.append("ci")
    if (
        "/test" in f"/{lower}"
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.js", ".test.ts", "test.kt", "tests.java"))
    ):
        kinds.append("tests")
    if lower.startswith(("docs/", "doc/")) or Path(lower).suffix == ".md":
        kinds.append("docs")
    if lower.startswith(("scripts/", "script/", "tools/", "tool/")):
        kinds.append("scripts")
    if (
        "config" in name
        or name.startswith(".env")
        or Path(lower).suffix in {".properties", ".toml", ".yaml", ".yml"}
    ):
        kinds.append("config")
    return kinds


def classify_source_kind(relative: str) -> str:
    lower = relative.lower()
    name = Path(lower).name
    if "/fixtures/" in f"/{lower}":
        return "fixture"
    if (
        "/test" in f"/{lower}"
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.js", ".test.ts", "test.kt", "tests.java"))
    ):
        return "test"
    if lower.startswith(("docs/", "doc/")) or Path(lower).suffix == ".md":
        return "documentation"
    if lower.startswith(("scripts/", "script/", "tools/", "tool/")):
        return "script"
    if (
        lower.startswith(".github/workflows/")
        or name in {".gitlab-ci.yml", "jenkinsfile", "azure-pipelines.yml"}
    ):
        return "ci"
    if name in MANIFEST_NAMES:
        return "manifest"
    if name.endswith("_probe.py"):
        return "tooling"
    if (
        "config" in name
        or name.startswith(".env")
        or Path(lower).suffix in {".json", ".properties", ".toml", ".xml", ".yaml", ".yml"}
    ):
        return "config"
    return "source"


def matches_for_file(
    relative: str,
    text: str,
    patterns: dict[str, re.Pattern[str]],
    source_kind: str,
) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    for kind, pattern in patterns.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            matches.append(
                {
                    "kind": kind,
                    "path": relative,
                    "line": line,
                    "source_kind": source_kind,
                }
            )
    return matches


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    files, skipped_large = iter_text_files(root, args.max_files, args.max_bytes)
    inventory: dict[str, list[str]] = {
        "manifests": [],
        "ci": [],
        "tests": [],
        "config": [],
        "docs": [],
        "scripts": [],
    }
    entry_points: list[dict[str, object]] = []
    boundaries: list[dict[str, object]] = []
    risks: list[dict[str, object]] = []

    for path in files:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for kind in classify_inventory(relative):
            inventory[kind].append(relative)
        source_kind = classify_source_kind(relative)
        if source_kind in {"source", "script"}:
            entry_points.extend(
                matches_for_file(relative, text, ENTRY_PATTERNS, source_kind)
            )
            boundaries.extend(
                matches_for_file(relative, text, BOUNDARY_PATTERNS, source_kind)
            )
            risks.extend(matches_for_file(relative, text, RISK_PATTERNS, source_kind))
            for match in SWALLOWED_EXCEPTION_RE.finditer(text):
                risks.append(
                    {
                        "kind": "swallowed_exception",
                        "path": relative,
                        "line": text.count("\n", 0, match.start()) + 1,
                        "source_kind": source_kind,
                    }
                )

    for values in inventory.values():
        values.sort()
    ordering = lambda item: (str(item["path"]), int(item["line"]), str(item["kind"]))
    entry_points.sort(key=ordering)
    boundaries.sort(key=ordering)
    risks.sort(key=ordering)

    commit_count, changes = (0, Counter()) if args.no_git else git_change_counts(root)
    scanned_paths = {path.relative_to(root).as_posix() for path in files}
    git_hotspots = [
        {"path": path, "git_change_count": count}
        for path, count in sorted(changes.items(), key=lambda item: (-item[1], item[0]))
        if path in scanned_paths
    ]
    git_hotspots = git_hotspots[:50]
    match_counts = {
        "entry_points": len(entry_points),
        "external_boundaries": len(boundaries),
        "risk_signals": len(risks),
    }
    max_matches = max(0, args.max_matches_per_category)
    matches_truncated = {
        key: count > max_matches for key, count in match_counts.items()
    }
    entry_points = entry_points[:max_matches]
    boundaries = boundaries[:max_matches]
    risks = risks[:max_matches]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "probe": "flow",
        "root": str(root),
        "metric_note": (
            "pattern matches are reconnaissance candidates; confirm relevance in project context "
            "before creating findings"
        ),
        "summary": {
            "files_scanned": len(files),
            "files_skipped_large": skipped_large,
            "max_files_reached": len(files) >= args.max_files,
            "git_commits_scanned": commit_count,
            "match_counts": match_counts,
            "matches_truncated": matches_truncated,
        },
        "inventory": inventory,
        "entry_points": entry_points,
        "external_boundaries": boundaries,
        "risk_signals": risks,
        "git_hotspots": git_hotspots,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
