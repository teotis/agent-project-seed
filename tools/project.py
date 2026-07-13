#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "control/ledger.md",
    "control/state.md",
    "AGENTS.md",
    "CLAUDE.md",
    "README.zh.html",
    ".codex/config.example.toml",
    ".codex/config.windows.example.toml",
    ".codex/hooks.json",
    ".codex/hooks.windows.json",
    ".codex/hooks/clean_checkpoint_first.py",
    ".claude/settings.json",
    ".claude/settings.example.json",
    ".claude/settings.windows.example.json",
    "agent-assets/user-skills/manifest.json",
    "pyproject.toml",
    ".gitignore",
]

REQUIRED_DIRS = ["control", "reports", "work/in", "work/out", "work/tmp", "tools", "src"]
PROJECT_FACING_FILES = [
    "README.md",
    "README.zh.html",
    "AGENTS.md",
    "control/state.md",
    "control/ledger.md",
    "control/init_manifest.md",
    "control/delivery_receipt.md",
]
SEED_RESIDUE_PATTERNS = [
    "Agent Project Seed",
    "project_seed",
    "Seed Template",
    "codex://threads/",
    "Record clean checkpoint design",
    "Remove Gemini adapter",
    "Define lightweight status panel contract",
]
CLAUDE_DEFAULT_MODES = ("auto",)
RECOMMENDED_CLAUDE_DEFAULT_MODE = "auto"
MIN_CLAUDE_CODE_VERSION = (2, 1, 140)
MIN_CLAUDE_CODE_VERSION_TEXT = "v2.1.140"

ALLOWED_PREFIXES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "README.zh.html",
    "SETUP_NEW_MACHINE.md",
    "Makefile",
    "pyproject.toml",
    ".gitignore",
    ".env.example",
    ".codex/",
    ".claude/",
    "agent-assets/",
    "control/",
    "reports/",
    "tools/",
    "src/",
    "tests/",
    "work/in/.gitkeep",
    "work/out/.gitkeep",
    "work/tmp/.gitkeep",
)

REJECT_PREFIXES = (".env", "work/tmp/", ".pytest_cache/", "__pycache__/")

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".json",
    ".jsonl",
    ".tsv",
    ".csv",
    ".example",
    ".gitignore",
    ".yml",
    ".yaml",
}
USER_SKILLS_ROOT = ROOT / "agent-assets" / "user-skills"
USER_SKILLS_DIR = USER_SKILLS_ROOT / "skills"
USER_SKILL_PROFILES = ("recommended", "all")
GOVERNANCE_PROFILES = ("one-off", "lightweight", "sustained")
TASK_CONTEXT_STAGES = ("plan", "implement", "check")
TASK_PHASES = ("plan", "implement", "check", "handoff")
README_ZH_CAPABILITY_ROWS = (
    '<tr><td>状态面板</td><td>中文展示进入/交接快照：优先呈现用户目标、验收进度、证据、缺口与下一决策；随后才是 Git、open 记录和风险</td></tr>',
    '<tr><td>安全提交</td><td>基于路径白名单和高置信 secret 扫描的提交命令，在 staging 前拒绝敏感内容</td></tr>',
    '<tr><td>Clean Checkpoint</td><td>只针对当前会话新增的 tracked 改动执行 Stop gate，保留用户已有脏改动并支持明确 blocked handoff</td></tr>',
    '<tr><td>统一账本</td><td>请求、决策、会话、风险、问题和产物共用一种结构化记录格式</td></tr>',
    '<tr><td>健康检查</td><td>验证必需文件、入口文件同步、hooks、gitkeep、包导入和平台垃圾文件</td></tr>',
    '<tr><td>Agent 同步</td><td>从共享规则重新生成 <code>CLAUDE.md</code></td></tr>',
    '<tr><td>Work Packet</td><td>仅在跨包、worktree、Agent 或交接会话的复杂任务中启用 curated context、live state 和知识提升复核</td></tr>',
    '<tr><td>Governance Lifecycle</td><td>面向长期项目的可选规则生命周期评审面，不会默认增加 hook 或强制流程</td></tr>',
    '<tr><td>Portable User Skills</td><td>仓库本地保留 38 个 Skill 快照；默认推荐小型工程核心，专家能力显式启用</td></tr>',
    '<tr><td>工具包</td><td>Python 辅助模块：路径管理、原子写入、环境变量加载、API 门控、Record/Ledger/Manifest/QC、Review 页面</td></tr>',
    '<tr><td>多 Agent 入口</td><td>各工具专属文件统一指向同一份共享合约</td></tr>',
)
README_ZH_CAPABILITIES_BEGIN = "<!-- BEGIN MANAGED CAPABILITIES -->"
README_ZH_CAPABILITIES_END = "<!-- END MANAGED CAPABILITIES -->"


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


@dataclass(frozen=True)
class ProjectIntent:
    target_user: str = ""
    core_problem: str = ""
    goals: tuple[str, ...] = ()
    non_goals: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()

    @property
    def goal_defined(self) -> bool:
        return bool(self.target_user and self.core_problem and self.goals)


BRIEF_SECTION_FIELDS = {
    "target user": "target_user",
    "目标用户": "target_user",
    "core problem": "core_problem",
    "核心问题": "core_problem",
    "project goals": "goals",
    "goals": "goals",
    "项目目标": "goals",
    "non-goals": "non_goals",
    "non goals": "non_goals",
    "非目标": "non_goals",
    "acceptance criteria": "acceptance_criteria",
    "验收标准": "acceptance_criteria",
    "验收条件": "acceptance_criteria",
}


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


def task_slug_from_name(name: str) -> str:
    return slugify_project(name).replace("_", "-")


def clean_intent_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lstrip("- ").strip())


def parse_brief(path: Path) -> dict[str, list[str]]:
    """Read a small Markdown brief without adding a parser dependency."""
    values: dict[str, list[str]] = {
        "target_user": [],
        "core_problem": [],
        "goals": [],
        "non_goals": [],
        "acceptance_criteria": [],
    }
    current_field: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", raw_line)
        if heading:
            current_field = BRIEF_SECTION_FIELDS.get(heading.group(1).strip().casefold())
            continue
        if current_field is None:
            continue
        value = clean_intent_value(raw_line)
        if value:
            values[current_field].append(value)
    return values


def prompt_for_missing_intent(intent: ProjectIntent) -> ProjectIntent:
    """Collect the four smallest pieces of information for a useful first task."""
    target_user = intent.target_user or input("Target user: ").strip()
    core_problem = intent.core_problem or input("Core problem: ").strip()
    goals = intent.goals or tuple(filter(None, [input("Primary project goal: ").strip()]))
    acceptance = intent.acceptance_criteria or tuple(
        filter(None, [input("First acceptance criterion: ").strip()])
    )
    return ProjectIntent(
        target_user=target_user,
        core_problem=core_problem,
        goals=goals,
        non_goals=intent.non_goals,
        acceptance_criteria=acceptance,
    )


def resolve_project_intent(args: argparse.Namespace) -> ProjectIntent:
    brief: dict[str, list[str]] = {
        "target_user": [],
        "core_problem": [],
        "goals": [],
        "non_goals": [],
        "acceptance_criteria": [],
    }
    if args.brief:
        path = Path(args.brief)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            raise FileNotFoundError(f"brief file not found: {args.brief}")
        brief = parse_brief(path)

    def cli_or_brief(value: str | None, key: str) -> str:
        return clean_intent_value(value) if value else " ".join(brief[key])

    def list_cli_or_brief(value: list[str] | None, key: str) -> tuple[str, ...]:
        source = value if value else brief[key]
        return tuple(clean_intent_value(item) for item in source if clean_intent_value(item))

    intent = ProjectIntent(
        target_user=cli_or_brief(args.target_user, "target_user"),
        core_problem=cli_or_brief(args.core_problem, "core_problem"),
        goals=list_cli_or_brief(args.goal, "goals"),
        non_goals=list_cli_or_brief(args.non_goal, "non_goals"),
        acceptance_criteria=list_cli_or_brief(args.acceptance_criterion, "acceptance_criteria"),
    )
    return prompt_for_missing_intent(intent) if args.interactive else intent


def markdown_bullets(values: tuple[str, ...], fallback: str) -> str:
    return "\n".join(f"- {value}" for value in values) if values else f"- {fallback}"


def render_claude() -> str:
    return f"""@AGENTS.md

# Claude Code adapter

This repository uses `AGENTS.md` as the shared source of truth for AI coding agents.

Claude Code-specific notes:

- Follow `AGENTS.md` first.
- Keep this file short and Claude-specific.
- Do not duplicate shared project rules here.
- When a repeated mistake is discovered, suggest whether it should become a hook, test, lint rule, or CI check instead of adding another reminder here.
- The project-level Claude Stop hook uses the same baseline-aware clean-checkpoint gate as Codex; agents create the local commit deliberately after review.
"""


def expected_agent_files() -> dict[Path, str]:
    return {
        ROOT / "CLAUDE.md": render_claude(),
    }


def sync_agents() -> int:
    if not (ROOT / "AGENTS.md").exists():
        print("missing AGENTS.md", file=sys.stderr)
        return 1
    for path, content in expected_agent_files().items():
        path.write_text(content, encoding="utf-8")
    print("Synced CLAUDE.md from AGENTS.md.")
    return 0


def check_agent_sync(result: Result) -> None:
    if not (ROOT / "AGENTS.md").exists():
        result.issues.append("missing AGENTS.md")
        return
    for path, expected in expected_agent_files().items():
        if not path.exists():
            result.issues.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            result.issues.append(f"{path.relative_to(ROOT)} is not in sync with AGENTS.md")
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


def check_panel_runs(result: Result) -> None:
    """Check that tools/panel.py can execute without errors."""
    panel = ROOT / "tools" / "panel.py"
    if not panel.exists():
        result.issues.append("missing tools/panel.py")
        return
    try:
        completed = subprocess.run(
            [sys.executable, str(panel)],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        if completed.returncode != 0:
            result.issues.append(f"tools/panel.py failed: {completed.stderr.strip()}")
        elif not completed.stdout.strip():
            result.warnings.append("tools/panel.py produced no output")
        else:
            result.notices.append("panel hook is functional")
    except subprocess.TimeoutExpired:
        result.warnings.append("tools/panel.py timed out after 10s")
    except Exception as exc:
        result.warnings.append(f"tools/panel.py error: {exc}")


def render_readme_zh_capability_rows() -> str:
    return "\n".join(f"    {row}" for row in README_ZH_CAPABILITY_ROWS)


def check_readme_zh_contract(result: Result) -> None:
    path = ROOT / "README.zh.html"
    if not path.is_file():
        result.issues.append("missing README.zh.html")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        re.escape(README_ZH_CAPABILITIES_BEGIN) + r"\n(?P<body>.*?)\n\s*" + re.escape(README_ZH_CAPABILITIES_END),
        re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        result.issues.append("README.zh.html is missing the managed public capability block")
        return
    if match.group("body").strip() != render_readme_zh_capability_rows().strip():
        result.issues.append("README.zh.html public capability block drifted from tools/project.py")
        return
    result.notices.append("Chinese HTML public capability block is synced")


def check_init_status_consistency(result: Result) -> None:
    """Check that AGENTS.md/state are consistent with each other."""
    agents = ROOT / "AGENTS.md"
    state = ROOT / "control" / "state.md"
    if not agents.exists() or not state.exists():
        return
    agents_text = agents.read_text(encoding="utf-8")
    state_text = state.read_text(encoding="utf-8")
    seed_status = "Seed Template — copy this scaffold to start a new project."
    agents_is_seed = seed_status in agents_text
    state_initialized = "Initialized at:" in state_text
    if agents_is_seed == state_initialized:
        result.warnings.append(
            "init status mismatch: AGENTS.md and state.md disagree on initialization state"
        )
    elif not agents_is_seed:
        result.notices.append("init status is consistent across AGENTS.md/state")


def is_initialized_project() -> bool:
    agents = ROOT / "AGENTS.md"
    state = ROOT / "control" / "state.md"
    if state.exists() and "Initialized at:" in state.read_text(encoding="utf-8"):
        return True
    if agents.exists() and "Seed Template — copy this scaffold to start a new project." not in agents.read_text(encoding="utf-8"):
        return True
    return False


def check_seed_residue(result: Result) -> None:
    if not is_initialized_project():
        return
    for relative in PROJECT_FACING_FILES:
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SEED_RESIDUE_PATTERNS:
            if seed_residue_found(text, pattern):
                result.issues.append(f"seed residue in initialized project: {relative} contains {pattern!r}")
                break


def seed_residue_found(text: str, pattern: str) -> bool:
    if pattern == "project_seed":
        return re.search(r"(?<![A-Za-z0-9_])project_seed(?![A-Za-z0-9_])", text) is not None
    return pattern in text


def check_claude_hook_files(result: Result) -> None:
    """Check that Claude hook files exist if settings.example.json references them."""
    example = ROOT / ".claude" / "settings.example.json"
    if not example.exists():
        return
    hook_script = ROOT / ".claude" / "hooks" / "panel_hook.py"
    if not hook_script.exists():
        result.warnings.append("missing .claude/hooks/panel_hook.py (referenced by settings)")
    else:
        result.notices.append("Claude hook files present")


def check_codex_hook_files(result: Result) -> None:
    """Check that Codex helper files exist."""
    example = ROOT / ".codex" / "config.example.toml"
    windows_example = ROOT / ".codex" / "config.windows.example.toml"
    hooks = ROOT / ".codex" / "hooks.json"
    windows_hooks = ROOT / ".codex" / "hooks.windows.json"
    panel_hook = ROOT / ".codex" / "hooks" / "panel_hook.py"
    checkpoint_hook = ROOT / ".codex" / "hooks" / "clean_checkpoint_first.py"
    notify = ROOT / "tools" / "hooks" / "codex_notify.py"
    panel = ROOT / "tools" / "hooks" / "panel_print.py"
    if not example.exists():
        result.warnings.append("missing .codex/config.example.toml")
    elif not windows_example.exists():
        result.warnings.append("missing .codex/config.windows.example.toml")
    elif not hooks.exists():
        result.warnings.append("missing .codex/hooks.json")
    elif not windows_hooks.exists():
        result.warnings.append("missing .codex/hooks.windows.json")
    elif not panel_hook.exists():
        result.warnings.append("missing .codex/hooks/panel_hook.py")
    elif not checkpoint_hook.exists():
        result.warnings.append("missing .codex/hooks/clean_checkpoint_first.py")
    elif not notify.exists():
        result.warnings.append("missing tools/hooks/codex_notify.py (referenced by Codex config example)")
    elif not panel.exists():
        result.warnings.append("missing tools/hooks/panel_print.py")
    else:
        result.notices.append("Codex hook helper files present")


def load_user_skill_manifest() -> dict:
    path = USER_SKILLS_ROOT / "manifest.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid user skill manifest: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("invalid user skill manifest: expected object")
    return data


def user_skill_entries(selected_profiles: list[str] | None = None) -> list[tuple[str, str, Path]]:
    manifest = load_user_skill_manifest()
    skills = manifest.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("invalid user skill manifest: skills must be a list")
    selected = selected_profiles or ["all"]
    unknown = [profile for profile in selected if profile not in USER_SKILL_PROFILES]
    if unknown:
        raise ValueError(f"unknown user skill profile: {', '.join(unknown)}")
    include_all = "all" in selected
    entries: list[tuple[str, str, Path]] = []
    for item in skills:
        if not isinstance(item, dict):
            raise ValueError("invalid user skill manifest: each skill must be an object")
        name = item.get("name")
        profile = item.get("profile")
        if not isinstance(name, str) or not name:
            raise ValueError("invalid user skill name in manifest")
        if profile not in USER_SKILL_PROFILES:
            raise ValueError(f"invalid user skill profile for {name}: {profile}")
        if include_all or profile in selected:
            entries.append((profile, name, USER_SKILLS_DIR / name))
    return entries


def check_user_skill_assets(result: Result) -> None:
    try:
        entries = user_skill_entries(["all"])
    except ValueError as exc:
        result.issues.append(str(exc))
        return
    seen: dict[str, str] = {}
    missing: list[str] = []
    duplicates: list[str] = []
    for profile, name, path in entries:
        prior = seen.get(name)
        if prior is not None:
            duplicates.append(f"{name} ({prior}, {profile})")
        seen[name] = profile
        if not (path / "SKILL.md").is_file():
            missing.append(f"skills/{name}/SKILL.md")
    if duplicates:
        result.issues.append(f"duplicate portable user skills: {', '.join(duplicates)}")
    if missing:
        result.issues.append(f"missing portable user skill files: {', '.join(missing[:10])}")
    expected_names = set(seen)
    actual_names = {
        path.name
        for path in USER_SKILLS_DIR.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    unlisted = sorted(actual_names - expected_names)
    if unlisted:
        result.issues.append(f"unlisted portable user skills: {', '.join(unlisted)}")
    if entries and not duplicates and not missing and not unlisted:
        result.notices.append(f"portable user skill assets present ({len(entries)} skills)")


def check_work_dirs_have_gitkeep(result: Result) -> None:
    """Check that work subdirectories have .gitkeep files."""
    for subdir in ["work/in", "work/out", "work/tmp"]:
        gitkeep = ROOT / subdir / ".gitkeep"
        if not gitkeep.exists():
            result.warnings.append(f"missing {subdir}/.gitkeep (dir may not survive git clone)")


def task_root_for_slug(slug: str) -> Path:
    return ROOT / "control" / "tasks" / slug


def validate_context_file_path(value: object) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value.strip():
        return None, "context file must be a non-empty repo-relative path"
    relative = Path(value.strip())
    if relative.is_absolute() or ".." in relative.parts:
        return None, f"context file must be repo-relative without '..': {value}"
    target = (ROOT / relative).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return None, f"context file escapes repository root: {value}"
    if not target.is_file():
        return None, f"context file does not exist: {relative.as_posix()}"
    if not is_text_file(target):
        return None, f"context file must be a supported text file: {relative.as_posix()}"
    return target, None


def load_task_context_entries(task_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    manifest = task_root / "context.jsonl"
    if not manifest.is_file():
        return [], [f"missing task context manifest: {manifest.relative_to(ROOT)}"]
    entries: list[dict[str, str]] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for line_number, raw_line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        location = f"{manifest.relative_to(ROOT)}:{line_number}"
        try:
            item = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"{location}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(item, dict):
            errors.append(f"{location}: context entry must be a JSON object")
            continue
        file_value = item.get("file")
        reason = item.get("reason")
        stage = item.get("stage")
        _, path_error = validate_context_file_path(file_value)
        if path_error:
            errors.append(f"{location}: {path_error}")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{location}: reason must be a non-empty string")
        if stage not in TASK_CONTEXT_STAGES:
            errors.append(
                f"{location}: stage must be one of {', '.join(TASK_CONTEXT_STAGES)}"
            )
        if isinstance(file_value, str) and isinstance(stage, str):
            key = (Path(file_value).as_posix(), stage)
            if key in seen:
                errors.append(f"{location}: duplicate context entry for {key[0]} at stage {stage}")
            seen.add(key)
        if not path_error and isinstance(reason, str) and reason.strip() and stage in TASK_CONTEXT_STAGES:
            entries.append(
                {
                    "file": Path(str(file_value)).as_posix(),
                    "reason": reason.strip(),
                    "stage": str(stage),
                }
            )
    return entries, errors


def task_packet_dirs() -> list[Path]:
    tasks_root = ROOT / "control" / "tasks"
    if not tasks_root.is_dir():
        return []
    return sorted(
        path
        for path in tasks_root.iterdir()
        if path.is_dir()
        and any(
            (path / marker).is_file()
            for marker in ("brief.md", "context.jsonl", "promotion.md")
        )
    )


def check_task_contexts(result: Result) -> None:
    packets = task_packet_dirs()
    for task_root in packets:
        _, errors = load_task_context_entries(task_root)
        result.issues.extend(errors)
    if packets and not any("context" in issue for issue in result.issues):
        result.notices.append(f"complex task context manifests valid ({len(packets)})")


def task_finalize_state(task_root: Path) -> str:
    status = task_root / "status.tsv"
    if not status.is_file():
        return ""
    lines = status.read_text(encoding="utf-8").splitlines()
    if not lines:
        return ""
    header = lines[0].split("\t")
    try:
        package_index = header.index("package_id")
        state_index = header.index("state")
    except ValueError:
        return ""
    for line in lines[1:]:
        values = line.split("\t")
        if len(values) > max(package_index, state_index) and values[package_index] == "99-finalize":
            return values[state_index].strip()
    return ""


def promotion_is_classified(path: Path) -> bool:
    if not path.is_file():
        return False
    in_classification = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", raw_line)
        if heading:
            in_classification = heading.group(1).strip().casefold() == "classification"
            continue
        if in_classification and re.match(r"^\s*-\s*\[[xX]\]\s+", raw_line):
            return True
    return False


def check_task_promotions(result: Result) -> None:
    for task_root in task_packet_dirs():
        if task_finalize_state(task_root) != "finalized":
            continue
        if not promotion_is_classified(task_root / "promotion.md"):
            result.issues.append(
                f"finalized task requires a promotion classification: {task_root.relative_to(ROOT)}/promotion.md"
            )


def check_no_platform_junk_tracked(result: Result) -> None:
    """Check that no platform junk files (._*, .DS_Store) are tracked."""
    if not (ROOT / ".git").exists():
        return
    completed = run_git(["ls-files"])
    if completed.returncode != 0:
        return
    junk = []
    for line in completed.stdout.splitlines():
        name = line.strip()
        if name.startswith("._") or name == ".DS_Store":
            junk.append(name)
    if junk:
        result.warnings.append(f"platform junk files tracked in git: {', '.join(junk)}")


SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    (
        "credential assignment",
        re.compile(
            r"['\"]?\b(?:api[_-]?key|secret|password|token)\b['\"]?\s*[:=]\s*['\"](?P<value>[^'\"\r\n]{8,})['\"]",
            re.IGNORECASE,
        ),
    ),
    ("OpenAI-style token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
]
SECRET_PLACEHOLDER_VALUES = {
    "placeholder",
    "example",
    "dummy",
    "test",
    "replace_me",
    "replace-me",
    "changeme",
    "change_me",
    "change-me",
    "your_api_key",
    "your-api-key",
    "insert_key_here",
    "test_api_key_placeholder",
}
SECRET_SCAN_CHUNK_SIZE = 64 * 1024
SECRET_SCAN_OVERLAP = 4096


def is_explicit_secret_placeholder(value: str) -> bool:
    normalized = value.strip().casefold()
    return (
        normalized in SECRET_PLACEHOLDER_VALUES
        or normalized.startswith("${") and normalized.endswith("}")
        or normalized.startswith("<") and normalized.endswith(">")
    )


def secret_finding_from_chunks(path: str, chunks) -> str | None:
    overlap = b""
    first_chunk = True
    for chunk in chunks:
        if first_chunk:
            first_chunk = False
            if b"\x00" in chunk[:8192]:
                return None
        sample = overlap + chunk
        text = sample.decode("utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                value = match.groupdict().get("value", "")
                if value and is_explicit_secret_placeholder(value):
                    continue
                return f"possible secret ({label}) in selected file: {path}"
        overlap = sample[-SECRET_SCAN_OVERLAP:]
    return None


def secret_findings(paths: list[str]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        if path == ".env" or path.endswith("/.env"):
            findings.append(f"sensitive file selected for commit: {path}")
            continue
        target = ROOT / path
        if not target.is_file():
            continue
        try:
            with target.open("rb") as handle:
                finding = secret_finding_from_chunks(
                    path,
                    iter(lambda: handle.read(SECRET_SCAN_CHUNK_SIZE), b""),
                )
        except OSError:
            continue
        if finding:
            findings.append(finding)
    return findings


def staged_secret_findings(paths: list[str]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        exists = run_git(["cat-file", "-e", f":{path}"])
        if exists.returncode != 0:
            continue
        if path == ".env" or path.endswith("/.env"):
            findings.append(f"sensitive file staged for commit: {path}")
            continue
        process = subprocess.Popen(
            ["git", "show", f":{path}"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        assert process.stdout is not None
        finding = secret_finding_from_chunks(
            path,
            iter(lambda: process.stdout.read(SECRET_SCAN_CHUNK_SIZE), b""),
        )
        if process.poll() is None:
            process.terminate()
        process.stdout.close()
        process.wait()
        if finding:
            findings.append(finding)
    return findings


def check_safety(result: Result) -> None:
    """Check staged files for secrets and sensitive patterns."""
    if not (ROOT / ".git").exists():
        return
    completed = run_git(["diff", "--cached", "--name-only"])
    if completed.returncode != 0:
        return
    staged = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    result.issues.extend(staged_secret_findings(staged))


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
    check_panel_runs(result)
    check_readme_zh_contract(result)
    check_init_status_consistency(result)
    check_seed_residue(result)
    check_claude_hook_files(result)
    check_codex_hook_files(result)
    check_user_skill_assets(result)
    check_work_dirs_have_gitkeep(result)
    check_task_contexts(result)
    check_task_promotions(result)
    if not args.skip_git:
        check_git(result)
        check_no_platform_junk_tracked(result)
        check_safety(result)
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
    try:
        intent = resolve_project_intent(args)
    except (FileNotFoundError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    package_name = args.package_name or package_name_from_project(args.name)
    platform_name = active_platform(args.platform)
    replace_text(args.name, package_name)
    rename_package(package_name)
    update_contract(args.name, intent)
    update_state(args.name, package_name, intent)
    update_readme(args.name, package_name, intent)
    update_readme_zh(args.name, package_name)
    reset_init_ledger(args.name, package_name, intent)
    reset_reports_dir()
    write_delivery_receipt(intent)
    write_init_manifest(args.name, package_name, platform_name, intent)
    activate_platform_configs(platform_name)
    if not args.no_git:
        run_git_init(args.name)
    print(f"Initialized {args.name} with package {package_name}.")
    if intent.goal_defined:
        print("Project goal, user, and acceptance criteria were written to control/delivery_receipt.md.")
    elif args.brief or args.interactive or args.target_user or args.core_problem or args.goal:
        print("Project intent is incomplete; add a target user, core problem, and at least one project goal.")
    print(
        "Project-level Claude Code settings are active in .claude/settings.json "
        "(status panel + clean-checkpoint Stop gate)."
    )
    print(f"Activated project hook/config files for platform: {platform_name}.")
    print(
        "User-level hook/config setup is optional; use it only when you want the "
        "same behavior outside this project-level Claude Code config."
    )
    print(
        "For smoother new Claude Code sessions, run "
        "`python3 tools/project.py configure-claude` "
        "or on Windows `py -3 tools/project.py configure-claude` after updating Claude Code to v2.1.140 or newer."
    )
    return 0


def active_platform(value: str) -> str:
    if value != "auto":
        return value
    return "windows" if os.name == "nt" else "posix"


def platform_template(target: Path, platform_name: str) -> Path:
    if platform_name == "windows":
        for windows in [
            target.with_name(f"{target.stem}.windows{target.suffix}"),
            target.with_name(f"{target.stem}.windows.example{target.suffix}"),
        ]:
            if windows.exists():
                return windows
    example = target.with_name(f"{target.stem}.example{target.suffix}")
    return example if example.exists() else target


def activate_platform_configs(platform_name: str) -> None:
    """Write active project hook/config files from the platform-specific examples."""
    active_files = [
        ROOT / ".claude" / "settings.json",
        ROOT / ".codex" / "hooks.json",
    ]
    for target in active_files:
        source = platform_template(target, platform_name)
        if source.exists():
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def update_contract(project_name: str, intent: ProjectIntent) -> None:
    """Update AGENTS.md with initialized project-facing template."""
    path = ROOT / "AGENTS.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if intent.goal_defined:
        new_intent = (
            f"**Project**: {project_name}\n"
            f"**Status**: Ready — goal defined\n"
            f"**Target user**: {intent.target_user}\n"
            f"**Core problem**: {intent.core_problem}\n"
            f"\n"
            f"### Project Goals\n\n{markdown_bullets(intent.goals, 'No project goal recorded.')}\n"
            f"\n### Non-goals\n\n{markdown_bullets(intent.non_goals, 'No non-goals recorded.')}\n"
            f"\n### Acceptance Criteria\n\n{markdown_bullets(intent.acceptance_criteria, 'No acceptance criteria recorded.')}\n"
        )
    else:
        new_intent = (
            f"**Project**: {project_name}\n"
            f"**Status**: Initialized, goals pending\n"
            f"\n"
            f"Edit this section to specify:\n"
            f"- Project goals\n"
            f"- Non-goals\n"
            f"- Acceptance criteria\n"
        )
    if "## Current Intent" in text:
        text = re.sub(
            r"## Current Intent\n\n.*?(?=\n## |\Z)",
            "## Current Intent\n\n" + new_intent.rstrip() + "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        # No Current Intent block exists; insert before first ## heading
        text = re.sub(
            r"(## )",
            f"## Current Intent\n\n{new_intent}\n\\1",
            text, count=1,
        )
    overview_text = (
        f"An agent-assisted project for {intent.target_user}. It exists because {intent.core_problem}"
        if intent.goal_defined
        else "A newly initialized agent-assisted project. Replace this section with the project's real purpose, audience, non-goals, and acceptance criteria after initialization."
    )
    overview = f"## Project overview\n\n{overview_text}\n"
    if "## Project overview" in text:
        text = re.sub(
            r"## Project overview\n\n.*?(?=\n## )",
            overview + "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        text = text.replace("## How to work in this repository", overview + "\n## How to work in this repository")
    path.write_text(text, encoding="utf-8")


def update_state(project_name: str, package_name: str, intent: ProjectIntent) -> None:
    """Replace state.md with initialized content."""
    path = ROOT / "control" / "state.md"
    status = "Ready — goal defined" if intent.goal_defined else "Initialized, goals pending"
    intent_lines = (
        f"- Target user: {intent.target_user}\n"
        f"- Core problem: {intent.core_problem}\n"
        f"- Project goals:\n{markdown_bullets(intent.goals, 'No project goal recorded.')}\n"
        f"- Acceptance criteria:\n{markdown_bullets(intent.acceptance_criteria, 'No acceptance criteria recorded.')}\n"
        if intent.goal_defined
        else ""
    )
    next_action = (
        "- Start the first task against `control/delivery_receipt.md` and update its evidence as work progresses.\n"
        if intent.goal_defined
        else "- Edit Current Intent in `AGENTS.md` to specify project goals, non-goals, and acceptance criteria.\n"
    )
    content = (
        f"# State\n"
        f"\n"
        f"## Current State\n"
        f"\n"
        f"- Project name: {project_name}\n"
        f"- Package name: {package_name}\n"
        f"- Initialized at: {now_iso()}\n"
        f"- Status: {status}\n"
        f"{intent_lines}"
        f"\n"
        f"## Next Maintenance Action\n"
        f"\n"
        f"{next_action}"
    )
    path.write_text(content, encoding="utf-8")


def update_readme(project_name: str, package_name: str, intent: ProjectIntent) -> None:
    path = ROOT / "README.md"
    goal_section = ""
    if intent.goal_defined:
        goal_section = f"""## Project Intent

- Target user: {intent.target_user}
- Core problem: {intent.core_problem}

### Goals

{markdown_bullets(intent.goals, 'No project goal recorded.')}

### Acceptance Criteria

{markdown_bullets(intent.acceptance_criteria, 'No acceptance criteria recorded.')}

The current delivery status lives in `control/delivery_receipt.md`.

"""
    if intent.goal_defined:
        first_actions = (
            "1. Start the first task against the acceptance criteria in `control/delivery_receipt.md`.\n"
            "2. Update the receipt with verification evidence, remaining gaps, and the user's next decision.\n"
            "3. Run the health check and task-specific tests before handing off.\n"
        )
    else:
        first_actions = (
            "1. Edit `AGENTS.md` to define the real project goals, non-goals, and acceptance criteria.\n"
            "2. Update this README with the product, library, or workflow this repository will actually provide.\n"
            "3. Run the health check for your platform.\n"
            "4. Run the tests for your platform.\n"
            "5. Optional: run `python3 tools/project.py list-user-skills`, install the deliberately small portable skill profile for Codex or Claude, then use `python3 tools/project.py audit-user-skills` before any forced replacement.\n"
            "6. Optional for Claude Code: run `python3 tools/project.py configure-claude` to make new sessions use auto permission review after updating Claude Code to v2.1.140 or newer.\n"
            "7. Optional: install user-level hooks/config only if you want similar behavior outside this project-level Claude Code setup.\n"
            "8. Optional for long-lived projects: run `python3 tools/project.py governance init --profile sustained` to track the lifecycle of durable rules, scripts, reports, and agent workflows.\n"
        )
    content = f"""# {project_name}

A newly initialized agent-assisted project.

## Current Setup

- Project name: {project_name}
- Python package: `{package_name}`
- Shared agent rules: `AGENTS.md`
- Current state snapshot: `control/state.md`
- Long-term project ledger: `control/ledger.md`
- Durable analysis reports: `reports/`
- Project-level Claude Code hooks: `.claude/settings.json` enables the status panel and a clean-checkpoint Stop gate

{goal_section}
## First Actions

{first_actions}

## Run a Problem-Solving Round

`AGENTS.md` contains the authoritative adaptive contract. Read it plus the files directly involved. Consult `control/state.md` and relevant ledger records only when current state or prior decisions constrain the task.

Use `reports/<topic>/` for reusable analysis. When tracked files change, run the project check and proportional tests, then close with a guarded local checkpoint or an explicit blocked handoff. Create a Work Packet only for work that crosses dependent packages, worktrees, agents, or handoff sessions.

## Useful Commands

macOS/Linux:

```bash
python3 tools/panel.py --mode entry
python3 tools/project.py check
python3 tools/project.py list-user-skills
python3 tools/project.py install-user-skills --target codex
python3 tools/project.py audit-user-skills --target codex
python3 tools/project.py configure-claude
python3 tools/project.py governance init --profile sustained
python3 -m pytest
```

Windows PowerShell:

```powershell
py -3 tools/panel.py --mode entry
py -3 tools/project.py check
py -3 tools/project.py list-user-skills
py -3 tools/project.py install-user-skills --target codex
py -3 tools/project.py audit-user-skills --target codex
py -3 tools/project.py configure-claude
py -3 tools/project.py governance init --profile sustained
py -3 -m pytest
```
"""
    path.write_text(content, encoding="utf-8")


def update_readme_zh(project_name: str, package_name: str) -> None:
    """Retain the Chinese HTML overview as a project-facing scaffold page."""
    path = ROOT / "README.zh.html"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    safe_project_name = escape(project_name)
    safe_package_name = escape(package_name)
    text = text.replace("<title>Agent Project Seed</title>", f"<title>{safe_project_name}</title>")
    text = text.replace("<h1>Agent Project Seed</h1>", f"<h1>{safe_project_name}</h1>")
    text = text.replace(
        "<p>极简的项目种子，clone 即用，可以方便地按你自己的习惯进行后续开发。</p>",
        "<p>使用项目本地 Agent 规则、状态面、安全提交和可选复杂任务能力的工作区。</p>",
    )
    text = text.replace(
        "Agent Project Seed &mdash; 多 Agent 协作底座",
        f"{safe_project_name} &mdash; Agent 协作工作区",
    )
    text = text.replace("base_scaffold/", f"{safe_package_name}/")
    pattern = re.compile(
        re.escape(README_ZH_CAPABILITIES_BEGIN) + r"\n.*?\n\s*" + re.escape(README_ZH_CAPABILITIES_END),
        re.DOTALL,
    )
    managed_block = (
        README_ZH_CAPABILITIES_BEGIN
        + "\n"
        + render_readme_zh_capability_rows()
        + "\n    "
        + README_ZH_CAPABILITIES_END
    )
    text = pattern.sub(managed_block, text, count=1)
    path.write_text(text, encoding="utf-8")


def reset_init_ledger(project_name: str, package_name: str, intent: ProjectIntent) -> None:
    """Reset ledger.md to the initialized project's first durable record."""
    path = ROOT / "control" / "ledger.md"
    intent_details = (
        f"- Target user: {intent.target_user}.\n"
        f"- Core problem: {intent.core_problem}\n"
        f"- Project goals: {'; '.join(intent.goals)}\n"
        if intent.goal_defined
        else ""
    )
    next_detail = (
        "- Next: start the first task against `control/delivery_receipt.md` and record evidence there.\n"
        if intent.goal_defined
        else "- Next: edit `AGENTS.md` and `README.md` to specify the real project goals and usage.\n"
    )
    receipt_link = "- control/delivery_receipt.md\n" if intent.goal_defined else ""
    content = (
        "# Ledger\n"
        "\n"
        "Unified record ledger. Requirements, decisions, sessions, risks, issues, and artifacts are all appended here as Records.\n"
        "\n"
        f"## {now_iso()} - Project initialized\n"
        "\n"
        "type: decision\n"
        "status: closed\n"
        "tags: init, project-setup\n"
        "\n"
        "summary:\n"
        f"- Initialized `{project_name}` as a new project workspace.\n"
        f"- Package name: `{package_name}`.\n"
        "\n"
        "details:\n"
        "- Completed: project-facing README rewrite, package rename, settings activation, contract/state update, initialization manifest.\n"
        f"{intent_details}"
        f"{next_detail}"
        "\n"
        "links:\n"
        "- AGENTS.md\n"
        "- README.md\n"
        "- control/state.md\n"
        "- control/init_manifest.md\n"
        f"{receipt_link}"
    )
    path.write_text(content, encoding="utf-8")


def reset_reports_dir() -> None:
    """Clear seed analysis reports from a newly initialized project."""
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    for child in reports.iterdir():
        if child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    (reports / ".gitkeep").write_text("", encoding="utf-8")


def write_delivery_receipt(intent: ProjectIntent) -> None:
    path = ROOT / "control" / "delivery_receipt.md"
    if not intent.goal_defined:
        path.unlink(missing_ok=True)
        return
    goal = f"{intent.target_user}: {intent.goals[0]}"
    acceptance = "\n".join(f"- [ ] {criterion}" for criterion in intent.acceptance_criteria)
    if not acceptance:
        acceptance = "- [ ] Add the first verifiable acceptance criterion."
    content = f"""# Delivery Receipt

Update this file as work progresses. It is the user-facing evidence summary shown first in the status panel.

## User Goal

{goal}

## Context

- Core problem: {intent.core_problem}

## Acceptance Criteria

{acceptance}

## Evidence

- Pending verification.

## Remaining Gaps

- Work has not started.

## User Next Decision

- Start the first task against the acceptance criteria.
"""
    path.write_text(content, encoding="utf-8")


def write_init_manifest(project_name: str, package_name: str, platform_name: str, intent: ProjectIntent) -> None:
    path = ROOT / "control" / "init_manifest.md"
    receipt_updated = "- control/delivery_receipt.md\n" if intent.goal_defined else ""
    review_next = (
        "- Review the goal, acceptance criteria, and first delivery receipt before starting work.\n"
        if intent.goal_defined
        else "- Replace placeholder goals in AGENTS.md.\n- Replace placeholder project description in README.md.\n"
    )
    content = f"""# Initialization Manifest

- Project name: {project_name}
- Package name: {package_name}
- Active platform config: {platform_name}
- Initialized at: {now_iso()}

## Automatically Updated

- AGENTS.md
- README.md
- pyproject.toml
- control/state.md
- control/ledger.md
{receipt_updated}- control/init_manifest.md
- reports/.gitkeep
- src/{package_name}/
- .claude/settings.json
- .codex/hooks.json

## Review Next

{review_next}- Project-level Claude Code hooks are active in `.claude/settings.json`; user-level hook/config setup remains optional.
- Project hook/config files were activated for `{platform_name}`.
- Optional: run `python3 tools/project.py configure-claude` or Windows `py -3 tools/project.py configure-claude` for smoother new Claude Code sessions after updating Claude Code to v2.1.140 or newer.
- Add project-specific source code and tests.
- macOS/Linux: `python3 tools/project.py check`
- Windows: `py -3 tools/project.py check`
- macOS/Linux: `python3 -m pytest`
- Windows: `py -3 -m pytest`
"""
    path.write_text(content, encoding="utf-8")


def parse_status_line(line: str) -> GitChange:
    status = line[:2]
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return GitChange(status, path)


def git_changes() -> list[GitChange]:
    completed = run_git(["status", "--porcelain", "--untracked-files=all"])
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
    safety_findings = secret_findings([change.path for change in allowed])
    if safety_findings:
        print("Refusing safe commit because selected changes may contain sensitive data:", file=sys.stderr)
        for finding in safety_findings:
            print(f"- {finding}", file=sys.stderr)
        return 2
    if args.dry_run:
        print("Allowed changes:")
        for change in allowed:
            print(f"- {change.status} {change.path}")
        return 0
    already_staged_deletions = [change for change in allowed if change.status[0] == "D"]
    deletions_to_stage = [change for change in allowed if change.status[0] != "D" and change.status[1] == "D"]
    additions_or_updates = [change for change in allowed if change not in already_staged_deletions and change not in deletions_to_stage]
    if additions_or_updates:
        add = run_git(["add", "--", *[change.path for change in additions_or_updates]])
        if add.returncode != 0:
            print(add.stderr.strip(), file=sys.stderr)
            return add.returncode
    if deletions_to_stage:
        add_deletions = run_git(["add", "-u", "--", *[change.path for change in deletions_to_stage]])
        if add_deletions.returncode != 0:
            print(add_deletions.stderr.strip(), file=sys.stderr)
            return add_deletions.returncode
    completed = run_git(["commit", "-m", args.message])
    if completed.returncode != 0:
        print(completed.stdout.strip())
        print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode
    print(completed.stdout.strip())
    return 0


TASK_STATE_HEADER = (
    "package_id\tstate\towner\tbranch\tworktree\tbase_commit\tcommit_hash\t"
    "verification\tintegration\tcleanup\tlast_error\tupdated_at"
)


def tsv_field(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def git_head_or_pending() -> str:
    if not (ROOT / ".git").exists():
        return "pending"
    completed = run_git(["rev-parse", "HEAD"])
    if completed.returncode != 0:
        return "pending"
    return completed.stdout.strip() or "pending"


def default_task_packages(packages: list[str] | None) -> list[str]:
    values = [tsv_field(value) for value in (packages or []) if tsv_field(value)]
    if not values:
        values = ["01-main"]
    if "99-finalize" not in values:
        values.append("99-finalize")
    return values


def render_task_index(task_name: str, task_slug: str, packages: list[str]) -> str:
    package_lines = "\n".join(f"- `{package}`" for package in packages)
    return f"""# {task_name}

## Purpose

Use this Work Packet only for complex work that spans multiple packages,
branches, worktrees, agents, or handoff sessions. Routine single-session work
should stay in `control/state.md`, `control/ledger.md`, and normal checkpoint
commits.

## Live State Contract

- `status.tsv` is the live source of truth for package execution state.
- `events.jsonl` is append-only history for important state transitions.
- Package Markdown files hold human-readable evidence, verification, risks, and
  blocker notes.
- `brief.md` holds the user goal, acceptance criteria, and non-goals.
- `context.jsonl` is the curated, stage-scoped list of project files an agent
  must read before acting.
- `promotion.md` is the one-time finish review for deciding which learnings
  deserve a durable home.
- `control/ledger.md` records durable project decisions and risks; it should not
  duplicate every package update.
- chat transcripts, status panels, and final reports are secondary. If they
  disagree with `status.tsv`, refresh them from the live state before deciding
  whether the task is complete.

## Packages

{package_lines}

## State Vocabulary

Suggested states: `pending`, `in_progress`, `blocked`, `completed`,
`integrated`, `finalized`, `canceled`.

`99-finalize` should be marked `finalized` only after integration verification
and cleanup evidence are recorded. Before finalizing, complete the knowledge
promotion review in `promotion.md`.

## Work Packet Commands

```bash
python3 tools/project.py task context add {task_slug} --file <path> --reason <why> --stage plan
python3 tools/project.py task activate {task_slug} --phase plan --next "<required action>"
python3 tools/project.py task current
python3 tools/project.py task deactivate
```
"""


def render_task_brief(task_name: str) -> str:
    return f"""# {task_name}

## User Goal

- Define the user-visible outcome before implementation.

## Acceptance Criteria

- [ ] Replace this placeholder with a verifiable outcome.

## Non-Goals

- Record explicit exclusions when they matter.
"""


def render_promotion_review() -> str:
    return """# Knowledge Promotion Review

Complete this once during finalization. Select only the destinations that have
real future value; transient implementation details should not become project
rules.

## Classification

- [ ] Promote to test / hook / lint
- [ ] Promote to module README / spec
- [ ] Record as ledger decision / risk
- [ ] Keep task-local
- [ ] Discard as transient

## Candidates

- None recorded yet.

## Applied Updates

- None.
"""


def render_package_doc(package_id: str) -> str:
    return f"""# {package_id}

## Scope

- Define the package goal before starting work.

## Evidence

- Branch: pending
- Worktree: pending
- Base commit: pending
- Commit hash: pending
- Changed files: pending

## Verification

- pending

## Risks

- none identified yet

## Blocker Notes

- Last error: n/a
- Recovery hint: n/a

Update `../status.tsv` when this package changes state.
"""


def status_row(package_id: str, base_commit: str, timestamp: str) -> str:
    values = [
        package_id,
        "pending",
        "unassigned",
        "pending",
        "pending",
        base_commit,
        "pending",
        "pending",
        "pending",
        "pending",
        "",
        timestamp,
    ]
    return "\t".join(tsv_field(value) for value in values)


def task_init(args: argparse.Namespace) -> int:
    task_name = tsv_field(args.name)
    if not task_name:
        print("task name cannot be empty", file=sys.stderr)
        return 2
    slug = args.slug or task_slug_from_name(task_name)
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", slug):
        print(f"invalid task slug: {slug}", file=sys.stderr)
        return 2
    task_root = ROOT / "control" / "tasks" / slug
    if task_root.exists():
        print(f"task Work Packet already exists: {task_root.relative_to(ROOT)}", file=sys.stderr)
        return 2

    packages = default_task_packages(args.package)
    timestamp = now_iso()
    base_commit = git_head_or_pending()

    (task_root / "packages").mkdir(parents=True, exist_ok=False)
    (task_root / "INDEX.md").write_text(render_task_index(task_name, slug, packages), encoding="utf-8")
    (task_root / "brief.md").write_text(render_task_brief(task_name), encoding="utf-8")
    (task_root / "context.jsonl").write_text("", encoding="utf-8")
    (task_root / "promotion.md").write_text(render_promotion_review(), encoding="utf-8")
    (task_root / "status.tsv").write_text(
        TASK_STATE_HEADER + "\n" + "\n".join(status_row(package, base_commit, timestamp) for package in packages) + "\n",
        encoding="utf-8",
    )
    event = {
        "ts": timestamp,
        "event": "task_initialized",
        "task": task_name,
        "slug": slug,
        "packages": packages,
        "base_commit": base_commit,
    }
    (task_root / "events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    for package in packages:
        (task_root / "packages" / f"{package}.md").write_text(render_package_doc(package), encoding="utf-8")

    print(f"Created complex task Work Packet: {task_root.relative_to(ROOT)}")
    print(f"Live state: {(task_root / 'status.tsv').relative_to(ROOT)}")
    return 0


def task_context_add(args: argparse.Namespace) -> int:
    task_root = task_root_for_slug(args.slug)
    if not task_root.is_dir():
        print(f"task does not exist: control/tasks/{args.slug}", file=sys.stderr)
        return 2
    target, error = validate_context_file_path(args.file)
    if error:
        print(error, file=sys.stderr)
        return 2
    reason = args.reason.strip()
    if not reason:
        print("reason must be non-empty", file=sys.stderr)
        return 2
    entries, errors = load_task_context_entries(task_root)
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 2
    relative = target.relative_to(ROOT.resolve()).as_posix() if target else args.file
    if any(entry["file"] == relative and entry["stage"] == args.stage for entry in entries):
        print(f"duplicate context entry for {relative} at stage {args.stage}", file=sys.stderr)
        return 2
    entry = {"file": relative, "reason": reason, "stage": args.stage}
    manifest = task_root / "context.jsonl"
    with manifest.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Added {args.stage} context: {relative}")
    return 0


def task_context_list(args: argparse.Namespace) -> int:
    task_root = task_root_for_slug(args.slug)
    if not task_root.is_dir():
        print(f"task does not exist: control/tasks/{args.slug}", file=sys.stderr)
        return 2
    entries, errors = load_task_context_entries(task_root)
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 2
    requested_stage = "check" if args.stage == "handoff" else args.stage
    for entry in entries:
        if requested_stage and entry["stage"] != requested_stage:
            continue
        print(f"{entry['stage']}\t{entry['file']}\t{entry['reason']}")
    return 0


def git_private_root() -> Path | None:
    completed = run_git(["rev-parse", "--git-common-dir"])
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    path = Path(completed.stdout.strip())
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def active_task_state_file() -> Path | None:
    private_root = git_private_root()
    if private_root is None:
        return None
    worktree_key = hashlib.sha256(str(ROOT.resolve()).encode("utf-8")).hexdigest()[:16]
    return private_root / "project-seed" / "active-task" / f"{worktree_key}.json"


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


def task_activate(args: argparse.Namespace) -> int:
    task_root = task_root_for_slug(args.slug)
    if not task_root.is_dir():
        print(f"task does not exist: control/tasks/{args.slug}", file=sys.stderr)
        return 2
    state_path = active_task_state_file()
    if state_path is None:
        print("git repository is required for worktree-scoped active task state", file=sys.stderr)
        return 2
    next_action = args.next_action.strip()
    if not next_action:
        print("next action must be non-empty", file=sys.stderr)
        return 2
    state = {
        "slug": args.slug,
        "phase": args.phase,
        "next": next_action,
        "updated_at": now_iso(),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Activated complex task: {args.slug} ({args.phase})")
    return 0


def task_current(_args: argparse.Namespace) -> int:
    state = read_active_task_state()
    slug = state.get("slug", "")
    if not slug or not task_root_for_slug(slug).is_dir():
        print("No active complex task.")
        return 1
    print(f"{slug}\t{state.get('phase', '')}\t{state.get('next', '')}")
    return 0


def task_deactivate(_args: argparse.Namespace) -> int:
    state_path = active_task_state_file()
    if state_path is None:
        print("git repository is required for worktree-scoped active task state", file=sys.stderr)
        return 2
    if state_path.exists():
        state_path.unlink()
    print("Deactivated complex task.")
    return 0


def render_governance_doc(profile: str) -> str:
    profile_notes = {
        "one-off": (
            "Use this file sparingly. For a one-off project, prefer deleting or "
            "archiving temporary rules, scripts, and reports during handoff."
        ),
        "lightweight": (
            "Track only the few rules, scripts, reports, or workflows that need "
            "future recall. Most decisions should still live in `control/ledger.md`."
        ),
        "sustained": (
            "Use this as a small review surface for durable project governance. "
            "Review items when they become noisy, obsolete, duplicated, or replaced."
        ),
    }
    return f"""# Governance Lifecycle

Project profile: `{profile}`

{profile_notes[profile]}

## Purpose

Use this optional file when project rules, verification scripts, reports, or
agent workflows are likely to live beyond one task. It exists to prevent
governance from only accumulating. Every durable item should have a reason to
exist and a way to be downgraded, merged, or retired.

One-off projects usually do not need this file. Small projects can keep these
decisions in `control/ledger.md`. Long-lived projects can use the table below as
a compact lifecycle review surface.

## State Vocabulary

- `Protect`: keep; it protects a current invariant or user-visible promise.
- `Pilot`: try in a limited scope; promote or retire after evidence.
- `Defer`: valid concern, but not worth adding to the active workflow yet.
- `Retire`: remove, archive, or downgrade because the cost now exceeds value.

## Review Table

| Item | Type | State | Protects / value | Trigger | Cost | Owner | Review when | Retire or downgrade when | Replacement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `AGENTS.md` | rule | Protect | Shared project invariants for agents | Every agent session | Rule churn if overused | project owner | A rule is added or contradicted | A rule is better enforced by a test, hook, or script | n/a |
| `CLAUDE.md` | adapter | Protect | Claude Code points back to shared rules | Claude Code sessions | Duplicate-rule drift | project owner | `AGENTS.md` changes | Adapter can be generated or is no longer used | `tools/project.py sync-agents` |
| `.codex/hooks.json` | hook | Protect | Codex status and clean-checkpoint gates | Codex sessions | Hook noise or stale paths | project owner | Hook behavior changes | The invariant is covered by another hook or test | `.codex/hooks/*.py` |
| `.claude/settings.json` | hook | Protect | Claude status and checkpoint helpers | Claude Code sessions | Tool-specific config drift | project owner | Claude hook behavior changes | Claude support is removed or generated elsewhere | `.claude/settings.example.json` |
| `agent-assets/user-skills/manifest.json` | skill bundle | Pilot | Portable skills for new environments | Environment bootstrap | Bundle bloat and overlapping skills | project owner | Skills are added, overlap, or go stale | A skill is unused, duplicated, or superseded | `tools/project.py list-user-skills` |

## Review Prompts

- Which rules or scripts are protecting a live invariant?
- Which reports or issue packages are stale enough to archive?
- Which checks are duplicating each other?
- Which agent instructions should become a test, hook, script, or skill?
- Which pilots have enough evidence to promote or retire?

## Operating Rule

This file is advisory. It should not block normal work by itself. If an item
needs enforcement, add the narrowest matching mechanism: a test, a lint rule, a
hook, a safe-commit guard, or a project-specific verification script.
"""


def governance_init(args: argparse.Namespace) -> int:
    profile = args.profile
    if profile not in GOVERNANCE_PROFILES:
        print(f"invalid governance profile: {profile}", file=sys.stderr)
        return 2
    path = ROOT / "control" / "governance.md"
    if path.exists() and not args.force:
        print(f"governance lifecycle already exists: {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    path.write_text(render_governance_doc(profile), encoding="utf-8")
    print(f"Created governance lifecycle: {path.relative_to(ROOT)}")
    print("This is opt-in documentation only; no hooks or stricter checks were enabled.")
    return 0


def user_skill_target_root(target: str) -> Path:
    home = Path.home()
    if target == "codex":
        return home / ".codex" / "skills"
    if target == "claude":
        return home / ".claude" / "skills"
    raise ValueError(f"unknown target: {target}")


def install_targets(target: str) -> list[tuple[str, Path]]:
    if target == "all":
        return [("codex", user_skill_target_root("codex")), ("claude", user_skill_target_root("claude"))]
    return [(target, user_skill_target_root(target))]


def skill_copy_ignore(_: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name.startswith("._")}
    ignored.update({".DS_Store", "__pycache__", ".pytest_cache"})
    return ignored


def skill_tree_digest(root: Path) -> str:
    """Return a stable content digest for a portable skill directory."""
    digest = hashlib.sha256()
    if not root.is_dir():
        return ""
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == ".DS_Store" or any(part.startswith("._") for part in path.relative_to(root).parts):
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def list_user_skills(args: argparse.Namespace) -> int:
    for profile, name, path in user_skill_entries(args.profile or ["all"]):
        status = "ok" if (path / "SKILL.md").is_file() else "missing"
        print(f"{profile}\t{name}\t{status}\t{path.relative_to(ROOT)}")
    return 0


def install_user_skills(args: argparse.Namespace) -> int:
    entries = user_skill_entries(args.profile or ["recommended"])
    actions: list[tuple[str, Path, Path]] = []
    for _profile, name, source in entries:
        if not (source / "SKILL.md").is_file():
            print(f"missing source skill: {source}", file=sys.stderr)
            return 1
        targets = [("custom", Path(args.install_root))] if args.install_root else install_targets(args.target)
        for target_name, target_root in targets:
            actions.append((target_name, source, target_root / name))

    for target_name, source, destination in actions:
        label = f"{target_name}:{destination.name}"
        if destination.exists() and not args.force:
            print(f"skip existing {label} (use --force to replace)")
            continue
        if args.dry_run:
            action = "replace" if destination.exists() else "install"
            print(f"{action} {label} <- {source.relative_to(ROOT)}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination, ignore=skill_copy_ignore)
        print(f"installed {label}")
    return 0


def audit_user_skills(args: argparse.Namespace) -> int:
    """Report whether installed skills match this seed's portable snapshot."""
    entries = user_skill_entries(args.profile or ["recommended"])
    targets = [("custom", Path(args.install_root))] if args.install_root else install_targets(args.target)
    drift_found = False
    for target_name, target_root in targets:
        for profile, name, source in entries:
            destination = target_root / name
            if not destination.is_dir():
                status = "missing"
            elif skill_tree_digest(source) == skill_tree_digest(destination):
                status = "synced"
            else:
                status = "drifted"
            if status != "synced":
                drift_found = True
            print(f"{target_name}\t{profile}\t{name}\t{status}\t{destination}")
    if args.strict and drift_found:
        return 1
    return 0


def parse_claude_version(version_output: str) -> tuple[int, int, int] | None:
    match = re.search(r"\bv?(\d+)\.(\d+)\.(\d+)\b", version_output)
    if match:
        return tuple(int(value) for value in match.groups())
    return None


def claude_version_status(version_output: str) -> tuple[str, str]:
    if not version_output.strip():
        return "unknown", "Claude Code version could not be checked; install or update Claude Code before configuring defaults."
    version = parse_claude_version(version_output)
    if version is None:
        return (
            "unknown",
            f"Claude Code version output did not include a parseable version; update to {MIN_CLAUDE_CODE_VERSION_TEXT} or newer, then rerun.",
        )
    minimum = MIN_CLAUDE_CODE_VERSION
    if version < minimum:
        return (
            "outdated",
            f"Claude Code appears older than {MIN_CLAUDE_CODE_VERSION_TEXT}; update before relying on auto permission mode.",
        )
    return "ok", f"Claude Code version is current enough: v{version[0]}.{version[1]}.{version[2]}"


def read_claude_version_output(args: argparse.Namespace) -> str:
    if args.claude_version_output is not None:
        return args.claude_version_output
    try:
        completed = subprocess.run(
            ["claude", "--version"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return (completed.stdout + "\n" + completed.stderr).strip()


def load_json_object(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def configure_claude(args: argparse.Namespace) -> int:
    settings_path = Path(args.settings_file).expanduser() if args.settings_file else Path.home() / ".claude" / "settings.json"
    try:
        settings = load_json_object(settings_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"cannot read Claude settings: {exc}", file=sys.stderr)
        return 1

    permissions = settings.get("permissions")
    if not isinstance(permissions, dict):
        permissions = {}
        settings["permissions"] = permissions
    permissions["defaultMode"] = args.default_mode

    version_output = read_claude_version_output(args)
    version_state, version_message = claude_version_status(version_output)

    if version_state in {"outdated", "unknown"} and not args.skip_version_check:
        print(version_message)
        print(f"Use --skip-version-check only if you have separately verified Claude Code is {MIN_CLAUDE_CODE_VERSION_TEXT} or newer.", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"would set {settings_path} permissions.defaultMode = {args.default_mode}")
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"set {settings_path} permissions.defaultMode = {args.default_mode}")

    print(version_message)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project scaffold command center.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a copied template")
    init.add_argument("--name", default=ROOT.name)
    init.add_argument("--package-name", default=None)
    init.add_argument("--brief", help="Markdown brief with target user, core problem, goals, and acceptance criteria")
    init.add_argument("--target-user", help="primary user for this project")
    init.add_argument("--core-problem", help="user problem this project should solve")
    init.add_argument("--goal", action="append", help="project goal; repeat for multiple goals")
    init.add_argument("--non-goal", action="append", help="explicit non-goal; repeat as needed")
    init.add_argument(
        "--acceptance-criterion",
        action="append",
        help="verifiable acceptance criterion; repeat as needed",
    )
    init.add_argument(
        "--interactive",
        action="store_true",
        help="prompt only for missing target user, core problem, goal, and first acceptance criterion",
    )
    init.add_argument("--no-git", action="store_true")
    init.add_argument(
        "--platform",
        choices=["auto", "posix", "windows"],
        default="auto",
        help="active hook/config platform to write during init; default detects the current OS",
    )

    check_cmd = sub.add_parser("check", help="check scaffold health")
    check_cmd.add_argument("--quiet", action="store_true")
    check_cmd.add_argument("--skip-git", action="store_true")

    sub.add_parser("sync-agents", help="sync thin agent entry files")

    list_skills = sub.add_parser("list-user-skills", help="list bundled portable user skills")
    list_skills.add_argument(
        "--profile",
        action="append",
        choices=USER_SKILL_PROFILES,
        help="skill profile to list; repeatable",
    )

    install_skills = sub.add_parser("install-user-skills", help="install bundled user skills")
    install_skills.add_argument("--target", choices=["codex", "claude", "all"], default="codex")
    install_skills.add_argument("--install-root", help="install into an explicit skills directory")
    install_skills.add_argument(
        "--profile",
        action="append",
        choices=USER_SKILL_PROFILES,
        help="skill profile to install; repeatable",
    )
    install_skills.add_argument("--force", action="store_true", help="replace existing target skills")
    install_skills.add_argument("--dry-run", action="store_true")

    audit_skills = sub.add_parser(
        "audit-user-skills",
        help="compare installed skills with this seed's portable snapshot",
    )
    audit_skills.add_argument("--target", choices=["codex", "claude", "all"], default="codex")
    audit_skills.add_argument("--install-root", help="compare against an explicit skills directory")
    audit_skills.add_argument(
        "--profile",
        action="append",
        choices=USER_SKILL_PROFILES,
        help="skill profile to audit; repeatable",
    )
    audit_skills.add_argument("--strict", action="store_true", help="return non-zero if any skill is missing or drifted")

    configure_claude_cmd = sub.add_parser(
        "configure-claude",
        help="configure user-level Claude Code defaults for smoother new sessions",
    )
    configure_claude_cmd.add_argument(
        "--default-mode",
        choices=CLAUDE_DEFAULT_MODES,
        default=RECOMMENDED_CLAUDE_DEFAULT_MODE,
        help="permissions.defaultMode to write into the user Claude settings file",
    )
    configure_claude_cmd.add_argument("--settings-file", help="explicit Claude settings JSON file")
    configure_claude_cmd.add_argument(
        "--claude-version-output",
        help="test hook: provide claude --version output instead of invoking claude",
    )
    configure_claude_cmd.add_argument(
        "--skip-version-check",
        action="store_true",
        help=f"write settings after a separate manual check confirmed Claude Code is {MIN_CLAUDE_CODE_VERSION_TEXT} or newer",
    )
    configure_claude_cmd.add_argument("--dry-run", action="store_true")

    task = sub.add_parser("task", help="manage optional complex task Work Packets")
    task_sub = task.add_subparsers(dest="task_command", required=True)
    task_init_cmd = task_sub.add_parser("init", help="create a minimal complex-task Work Packet")
    task_init_cmd.add_argument("--name", required=True, help="human-readable task name")
    task_init_cmd.add_argument("--slug", help="directory slug under control/tasks/")
    task_init_cmd.add_argument(
        "--package",
        action="append",
        help="package id to seed in status.tsv; repeatable. Defaults to 01-main plus 99-finalize.",
    )
    task_context_cmd = task_sub.add_parser("context", help="manage curated task context")
    task_context_sub = task_context_cmd.add_subparsers(dest="context_command", required=True)
    task_context_add_cmd = task_context_sub.add_parser("add", help="add a stage-scoped context file")
    task_context_add_cmd.add_argument("slug", help="task directory slug")
    task_context_add_cmd.add_argument("--file", required=True, help="repo-relative text file")
    task_context_add_cmd.add_argument("--reason", required=True, help="why the agent must read this file")
    task_context_add_cmd.add_argument("--stage", required=True, choices=TASK_CONTEXT_STAGES)
    task_context_list_cmd = task_context_sub.add_parser("list", help="list curated task context")
    task_context_list_cmd.add_argument("slug", help="task directory slug")
    task_context_list_cmd.add_argument(
        "--stage",
        choices=TASK_PHASES,
        help="show one stage only; handoff reuses check context",
    )
    task_activate_cmd = task_sub.add_parser("activate", help="set the active task for this worktree")
    task_activate_cmd.add_argument("slug", help="task directory slug")
    task_activate_cmd.add_argument("--phase", required=True, choices=TASK_PHASES)
    task_activate_cmd.add_argument("--next", dest="next_action", required=True, help="next required action")
    task_sub.add_parser("current", help="show the active task for this worktree")
    task_sub.add_parser("deactivate", help="clear the active task for this worktree")

    governance = sub.add_parser("governance", help="manage optional governance lifecycle controls")
    governance_sub = governance.add_subparsers(dest="governance_command", required=True)
    governance_init_cmd = governance_sub.add_parser(
        "init",
        help="create a small optional lifecycle review surface for rules, scripts, reports, and workflows",
    )
    governance_init_cmd.add_argument(
        "--profile",
        choices=GOVERNANCE_PROFILES,
        default="lightweight",
        help="project profile to describe in control/governance.md",
    )
    governance_init_cmd.add_argument("--force", action="store_true", help="overwrite an existing lifecycle file")

    commit_cmd = sub.add_parser("commit", help="safely commit allowed changes")
    commit_cmd.add_argument("--message", default="chore: checkpoint agent work")
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
    if args.command == "list-user-skills":
        return list_user_skills(args)
    if args.command == "install-user-skills":
        return install_user_skills(args)
    if args.command == "audit-user-skills":
        return audit_user_skills(args)
    if args.command == "configure-claude":
        return configure_claude(args)
    if args.command == "task":
        if args.task_command == "init":
            return task_init(args)
        if args.task_command == "context":
            if args.context_command == "add":
                return task_context_add(args)
            if args.context_command == "list":
                return task_context_list(args)
            parser.error(f"unknown context command {args.context_command}")
        if args.task_command == "activate":
            return task_activate(args)
        if args.task_command == "current":
            return task_current(args)
        if args.task_command == "deactivate":
            return task_deactivate(args)
        parser.error(f"unknown task command {args.task_command}")
    if args.command == "governance":
        if args.governance_command == "init":
            return governance_init(args)
        parser.error(f"unknown governance command {args.governance_command}")
    if args.command == "commit":
        return commit(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
