import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_project_tool():
    script = ROOT / "tools" / "project.py"
    spec = importlib.util.spec_from_file_location("project_tool", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["project_tool"] = module
    spec.loader.exec_module(module)
    return module


def test_commit_allowlist_rejects_env_tmp_and_outputs():
    module = load_project_tool()
    changes = [
        module.GitChange("??", "CONTEXT.md"),
        module.GitChange("??", "control/ledger.md"),
        module.GitChange("??", "docs/adr/0001-delivery-boundary.md"),
        module.GitChange("??", ".codex/config.example.toml"),
        module.GitChange(" M", "SETUP_NEW_MACHINE.md"),
        module.GitChange(" M", "README.zh.html"),
        module.GitChange("??", "reports/user-value-architect/report.html"),
        module.GitChange("??", ".env"),
        module.GitChange("??", "work/tmp/scratch.txt"),
        module.GitChange("??", "work/out/result.png"),
    ]

    allowed, rejected = module.classify_changes(changes)

    assert [change.path for change in allowed] == [
        "CONTEXT.md",
        "control/ledger.md",
        "docs/adr/0001-delivery-boundary.md",
        ".codex/config.example.toml",
        "SETUP_NEW_MACHINE.md",
        "README.zh.html",
        "reports/user-value-architect/report.html",
    ]
    assert [change.path for change in rejected] == [".env", "work/tmp/scratch.txt", "work/out/result.png"]


def test_commit_keeps_already_staged_deletions_out_of_git_add(tmp_path):
    target = tmp_path / "repo"
    (target / "tools").mkdir(parents=True)
    shutil.copy2(ROOT / "tools" / "project.py", target / "tools" / "project.py")
    (target / "AGENTS.md").write_text("# Test Rules\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "AGENTS.md", "tools/project.py"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "seed"],
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "rm", "AGENTS.md"], cwd=target, check=True, capture_output=True, text=True)

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "commit", "--message", "test: remove rules"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert not (target / "AGENTS.md").exists()


def test_safe_commit_rejects_high_confidence_secret_before_staging(tmp_path):
    target = tmp_path / "repo"
    (target / "tools").mkdir(parents=True)
    (target / "src").mkdir()
    shutil.copy2(ROOT / "tools" / "project.py", target / "tools" / "project.py")
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "tools/project.py"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "seed"],
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    secret_assignment = '"api_' + 'key": "latest-production-credential-value-1234567890"\n'
    (target / "src" / "leak.js").write_text("x" * 100_001 + "\n" + secret_assignment, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "commit", "--message", "test: reject secret"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "secret" in completed.stderr.lower()
    assert "src/leak.js" in completed.stderr
    assert subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=target,
        check=False,
    ).returncode == 0


def test_check_and_sync_agents_are_healthy():
    check = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr

    sync = subprocess.run(
        [sys.executable, "tools/project.py", "sync-agents"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert sync.returncode == 0, sync.stdout + sync.stderr
    assert "GEMINI" not in sync.stdout


def _copy_and_init(tmp_path, name="Demo Project", package="demo_project", platform="auto"):
    target = tmp_path / "copied_project"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.egg-info")
    shutil.copytree(ROOT, target, ignore=ignore)

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "init",
            "--name", name,
            "--package-name", package,
            "--no-git",
            "--platform", platform,
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return target


def test_init_project_copy_no_git(tmp_path):
    target = _copy_and_init(tmp_path)
    assert (target / "src" / "demo_project" / "__init__.py").exists()
    assert "demo-project" in (target / "pyproject.toml").read_text(encoding="utf-8")
    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    assert "Demo Project" in agents
    assert (target / ".codex" / "config.example.toml").exists()
    assert (target / ".codex" / "config.windows.example.toml").exists()
    assert (target / ".codex" / "hooks.json").exists()
    assert (target / ".codex" / "hooks.windows.json").exists()
    assert (target / ".codex" / "hooks" / "panel_hook.py").exists()
    assert (target / ".codex" / "hooks" / "clean_checkpoint_first.py").exists()
    assert (target / ".claude" / "settings.windows.example.json").exists()
    claude_settings = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert "UserPromptSubmit" in claude_settings["hooks"]
    assert "Stop" in claude_settings["hooks"]
    stop_command = claude_settings["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert ".codex/hooks/clean_checkpoint_first.py stop" in stop_command
    hooks = json.loads((target / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    assert "SessionStart" in hooks["hooks"]
    assert "PostToolUse" in hooks["hooks"]
    assert "Stop" in hooks["hooks"]
    assert (target / "work" / "in" / ".gitkeep").exists()
    assert (target / "reports" / ".gitkeep").exists()


def test_init_activates_windows_claude_and_codex_hooks(tmp_path):
    target = _copy_and_init(tmp_path, platform="windows")

    claude_settings = (target / ".claude" / "settings.json").read_text(encoding="utf-8")
    codex_hooks = (target / ".codex" / "hooks.json").read_text(encoding="utf-8")
    manifest = (target / "control" / "init_manifest.md").read_text(encoding="utf-8")

    assert "py -3 .claude/hooks/panel_hook.py" in claude_settings
    assert "py -3 .codex/hooks/clean_checkpoint_first.py stop" in claude_settings
    assert "py -3 .codex/hooks/panel_hook.py" in codex_hooks
    assert "py -3 .codex/hooks/clean_checkpoint_first.py stop" in codex_hooks
    assert "python3" not in claude_settings
    assert "python3" not in codex_hooks
    assert "Active platform config: windows" in manifest


def test_init_output_explains_project_level_and_optional_user_level_setup(tmp_path):
    target = tmp_path / "copied_project"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.egg-info")
    shutil.copytree(ROOT, target, ignore=ignore)

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "init",
            "--name",
            "Demo Project",
            "--package-name",
            "demo_project",
            "--no-git",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Project-level Claude Code settings are active" in completed.stdout
    assert ".claude/settings.json" in completed.stdout
    assert "Activated project hook/config files for platform:" in completed.stdout
    assert "User-level hook/config setup is optional" in completed.stdout
    assert "tools/project.py configure-claude" in completed.stdout
    assert "v2.1.140 or newer" in completed.stdout


def test_init_rewrites_project_facing_docs_and_resets_seed_history(tmp_path):
    target = _copy_and_init(tmp_path, name="Customer Portal", package="customer_portal")

    readme = (target / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# Customer Portal")
    assert "Agent Project Seed" not in readme
    assert "project_seed" not in readme
    assert "Initialize this repository" not in readme

    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    assert "**Project**: Customer Portal" in agents
    assert "A newly initialized agent-assisted project." in agents
    assert "copy this scaffold" not in agents

    ledger = (target / "control" / "ledger.md").read_text(encoding="utf-8")
    assert "Project initialized" in ledger
    assert "Record clean checkpoint design" not in ledger
    assert "Remove Gemini adapter" not in ledger
    assert "codex://threads/" not in ledger
    assert "Agent Project Seed" not in ledger

    manifest = (target / "control" / "init_manifest.md").read_text(encoding="utf-8")
    assert "Project name: Customer Portal" in manifest
    assert "Package name: customer_portal" in manifest
    assert "AGENTS.md" in manifest
    assert "README.md" in manifest
    assert "control/ledger.md" in manifest
    assert "Windows: `py -3 tools/project.py check`" in manifest
    assert "tools/project.py configure-claude" in manifest
    assert "Windows PowerShell" in readme
    assert "py -3 tools/project.py check" in readme
    assert "py -3 tools/project.py configure-claude" in readme
    assert "governance init --profile sustained" in readme
    assert "Run a Problem-Solving Round" in readme
    assert "reports/<topic>/" in readme
    assert "explicitly continues, resumes, or names it" in readme
    assert "Keep Verification Separate from Delivery" in readme
    assert "handoff artifact" in readme
    assert "Enter this mode only when the current user request explicitly continues" in agents
    html = (target / "README.zh.html").read_text(encoding="utf-8")
    assert "<title>Customer Portal</title>" in html
    assert "Agent Project Seed" not in html
    assert "Work Packet" in html
    assert "验证边界" in html
    assert not (target / "reports" / "user-value-architect").exists()


def test_init_chinese_html_escapes_project_name_and_updates_package_path(tmp_path):
    target = _copy_and_init(tmp_path, name="Research & Review <Lab>", package="research_review")

    html = (target / "README.zh.html").read_text(encoding="utf-8")

    assert "<title>Research &amp; Review &lt;Lab&gt;</title>" in html
    assert "<h1>Research &amp; Review &lt;Lab&gt;</h1>" in html
    assert ">research_review/</span>" in html
    assert ">base_scaffold/</span>" not in html


def test_seed_docs_include_windows_setup_commands():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    setup = (ROOT / "SETUP_NEW_MACHINE.md").read_text(encoding="utf-8")

    for text in (readme, setup):
        assert "Windows PowerShell" in text
        assert "py -3 tools/project.py init" in text
        assert "py -3 -m pytest" in text
        assert "tools/project.py configure-claude" in text
        assert "governance init --profile sustained" in text
        assert "Governance Lifecycle" in text
        assert "Run a Problem-Solving Round" in text
        assert "v2.1.140" in text
        assert "dontAsk" not in text
        assert "bypassPermissions" not in text
    assert "reports/<topic>/" in readme
    assert "authoritative adaptive contract" in readme
    assert "Keep Verification Separate from Delivery" in readme
    assert "Verification may create disposable local output" in setup
    assert "follow the adaptive contract in `AGENTS.md`" in setup
    assert "1. Put user-provided material" not in setup
    assert "Copy-Item" in readme
    assert "Copy-Item" in setup


def test_windows_agent_config_examples_avoid_unix_python_launcher():
    codex_hooks = (ROOT / ".codex" / "hooks.windows.json").read_text(encoding="utf-8")
    codex_config = (ROOT / ".codex" / "config.windows.example.toml").read_text(encoding="utf-8")
    claude_settings = (ROOT / ".claude" / "settings.windows.example.json").read_text(encoding="utf-8")

    assert "py -3 .codex/hooks/panel_hook.py" in codex_hooks
    assert '"py"' in codex_config
    assert '"-3"' in codex_config
    assert "py -3 .claude/hooks/panel_hook.py" in claude_settings
    assert "py -3 .codex/hooks/clean_checkpoint_first.py stop" in claude_settings
    assert "python3" not in codex_hooks
    assert "python3" not in codex_config
    assert "python3" not in claude_settings


def test_claude_permissions_keep_mutating_git_commands_out_of_default_allowlist():
    settings_paths = [
        ROOT / ".claude" / "settings.json",
        ROOT / ".claude" / "settings.example.json",
        ROOT / ".claude" / "settings.windows.example.json",
    ]
    forbidden = {
        "Bash(git add *)",
        "Bash(git commit *)",
        "Bash(git branch *)",
        "Bash(git stash *)",
        "Bash(git worktree *)",
        "Bash(git rm *)",
    }

    for path in settings_paths:
        allow = set(json.loads(path.read_text(encoding="utf-8"))["permissions"]["allow"])
        assert allow.isdisjoint(forbidden), path
        assert "Bash(git status *)" in allow
        assert any("tools/project.py commit" in entry for entry in allow)


def test_initialized_project_check_rejects_seed_residue(tmp_path):
    target = _copy_and_init(tmp_path)
    (target / "README.md").write_text("# Demo Project\n\nAgent Project Seed\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "seed residue" in completed.stdout
    assert "README.md" in completed.stdout


def test_initialized_project_check_allows_project_seed_substring_in_package_name(tmp_path):
    target = _copy_and_init(tmp_path, name="Test Project Seed", package="test_project_seed")

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "seed residue" not in completed.stdout


def test_codex_notify_hook_finds_project_root():
    hook = ROOT / "tools" / "hooks" / "codex_notify.py"
    spec = importlib.util.spec_from_file_location("codex_notify", hook)
    hook_module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["codex_notify"] = hook_module
    spec.loader.exec_module(hook_module)

    assert hook_module.find_project_root({"cwd": str(ROOT / "tools" / "hooks")}) == ROOT


def test_init_updates_contract_state_and_ledger(tmp_path):
    target = _copy_and_init(tmp_path, name="My App", package="my_app")

    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    assert "My App" in agents
    assert "Initialized, goals pending" in agents
    assert "Seed Template — copy this scaffold" not in agents

    state = (target / "control" / "state.md").read_text(encoding="utf-8")
    assert "My App" in state
    assert "my_app" in state

    ledger = (target / "control" / "ledger.md").read_text(encoding="utf-8")
    assert "Project initialized" in ledger
    assert "My App" in ledger
    assert "from seed" not in ledger
    assert (target / "control" / "init_manifest.md").exists()


def test_goal_driven_init_generates_project_intent_and_delivery_receipt(tmp_path):
    target = tmp_path / "copied_project"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.egg-info")
    shutil.copytree(ROOT, target, ignore=ignore)
    (target / "brief.md").write_text(
        """# Product Brief

## Target User

Independent researchers

## Core Problem

They lose the context behind decisions between research sessions.

## Project Goals

- Preserve decision context with each research artifact.
- Make the next research action obvious.

## Non-goals

- Replace a full research database.

## Acceptance Criteria

- A researcher can recover a decision and its evidence in one view.
- The next research action is recorded with every handoff.
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "init",
            "--name",
            "Research Memory",
            "--package-name",
            "research_memory",
            "--brief",
            "brief.md",
            "--no-git",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    assert "**Status**: Ready — goal defined" in agents
    assert "**Target user**: Independent researchers" in agents
    assert "Preserve decision context with each research artifact." in agents
    assert "Replace a full research database." in agents

    state = (target / "control" / "state.md").read_text(encoding="utf-8")
    assert "Core problem: They lose the context behind decisions" in state
    assert "Status: Ready — goal defined" in state

    receipt = (target / "control" / "delivery_receipt.md").read_text(encoding="utf-8")
    assert "## User Goal" in receipt
    assert "Independent researchers" in receipt
    assert "- [ ] A researcher can recover a decision and its evidence in one view." in receipt

    ledger = (target / "control" / "ledger.md").read_text(encoding="utf-8")
    assert "Target user: Independent researchers." in ledger
    assert "Core problem: They lose the context behind decisions between research sessions." in ledger

    panel = subprocess.run(
        [sys.executable, "tools/panel.py", "--mode", "entry"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert panel.returncode == 0, panel.stdout + panel.stderr
    assert "目标: Independent researchers: Preserve decision context with each research artifact." in panel.stdout
    assert panel.stdout.index("目标:") < panel.stdout.index("Git:")


def test_interactive_init_collects_missing_goal_fields(tmp_path):
    target = tmp_path / "copied_project"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.egg-info")
    shutil.copytree(ROOT, target, ignore=ignore)

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "init",
            "--name",
            "Learning Notes",
            "--package-name",
            "learning_notes",
            "--interactive",
            "--no-git",
        ],
        cwd=target,
        input="Students\nThey forget why notes matter.\nRecover study context quickly.\nA student can find the reason behind a note.\n",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    assert "**Target user**: Students" in agents
    assert "**Core problem**: They forget why notes matter." in agents
    assert "Recover study context quickly." in agents
    assert "A student can find the reason behind a note." in agents


def test_parse_brief_accepts_chinese_headings(tmp_path):
    module = load_project_tool()
    brief = tmp_path / "brief.md"
    brief.write_text(
        """## 目标用户
研究人员

## 核心问题
他们会遗失研究决策的上下文。

## 项目目标
- 保留每个决策的证据。

## 非目标
- 不替代研究数据库。

## 验收标准
- 可在一个视图中恢复决策与证据。
""",
        encoding="utf-8",
    )

    parsed = module.parse_brief(brief)

    assert parsed["target_user"] == ["研究人员"]
    assert parsed["core_problem"] == ["他们会遗失研究决策的上下文。"]
    assert parsed["goals"] == ["保留每个决策的证据。"]
    assert parsed["non_goals"] == ["不替代研究数据库。"]
    assert parsed["acceptance_criteria"] == ["可在一个视图中恢复决策与证据。"]


def test_no_legacy_directories_except_reports_in_template():
    legacy_dirs = [
        "codex",
        "revision",
        "journal",
        "data",
        "source_material",
        "optional_packs",
        "input",
        "output",
    ]
    for relative in legacy_dirs:
        assert not (ROOT / relative).exists(), f"legacy directory remains: {relative}"
    assert (ROOT / "reports").is_dir()


def test_gemini_adapter_is_not_part_of_template():
    module = load_project_tool()

    assert not (ROOT / "GEMINI.md").exists()
    assert all("GEMINI" not in str(path) for path in module.expected_agent_files())
    assert "GEMINI.md" not in module.ALLOWED_PREFIXES


def test_shared_agent_contract_uses_adaptive_rule_layers():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for heading in (
        "## Hard invariants",
        "## Mode contracts",
        "## User value priors",
        "## Adaptive heuristics",
        "## Examples and resources",
    ):
        assert heading in agents
    assert "Every task completion must include" not in agents
    assert "Read `control/state.md` when" in agents
    assert "Do not push unless the user explicitly requests it" in agents


def test_chinese_html_covers_current_public_capabilities():
    module = load_project_tool()
    result = module.Result()

    module.check_readme_zh_contract(result)

    assert result.issues == []
    html = (ROOT / "README.zh.html").read_text(encoding="utf-8")
    for marker in ("Clean Checkpoint", "Work Packet", "Governance Lifecycle", "Portable User Skills"):
        assert marker in html


def test_check_detects_chinese_html_public_capability_drift(tmp_path):
    target = _copy_and_init(tmp_path)
    html_path = target / "README.zh.html"
    html_path.write_text(
        html_path.read_text(encoding="utf-8").replace("仓库本地保留 38 个 Skill 快照", "仓库本地保留 37 个 Skill 快照"),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "README.zh.html public capability block drifted" in completed.stdout


def test_user_skill_manifest_assets_are_valid():
    module = load_project_tool()
    entries = module.user_skill_entries(["all"])

    assert len(entries) == 38
    assert (
        "recommended",
        "clean-checkpoint-first",
        ROOT / "agent-assets" / "user-skills" / "skills" / "clean-checkpoint-first",
    ) in entries
    assert (
        "recommended",
        "implement",
        ROOT / "agent-assets" / "user-skills" / "skills" / "implement",
    ) in entries
    assert (
        "all",
        "abstraction-architect",
        ROOT / "agent-assets" / "user-skills" / "skills" / "abstraction-architect",
    ) in entries
    assert (
        "all",
        "flow-realization-review",
        ROOT / "agent-assets" / "user-skills" / "skills" / "flow-realization-review",
    ) in entries

    result = module.Result()
    module.check_user_skill_assets(result)
    assert result.issues == []
    assert any("38 skills" in notice for notice in result.notices)


def test_agent_task_planner_contract_includes_exit_paths_and_lightweight_methods():
    skill = (ROOT / "agent-assets" / "user-skills" / "skills" / "agent-task-planner" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    contract = (
        ROOT
        / "agent-assets"
        / "user-skills"
        / "skills"
        / "agent-task-planner"
        / "references"
        / "task-plan-contract.md"
    ).read_text(encoding="utf-8")
    examples = (
        ROOT
        / "agent-assets"
        / "user-skills"
        / "skills"
        / "agent-task-planner"
        / "references"
        / "examples.md"
    ).read_text(encoding="utf-8")
    standalone_prompt = (
        ROOT
        / "agent-assets"
        / "user-skills"
        / "skills"
        / "agent-task-planner"
        / "references"
        / "standalone-prompt.md"
    ).read_text(encoding="utf-8")
    evals = json.loads(
        (
            ROOT
            / "agent-assets"
            / "user-skills"
            / "skills"
            / "agent-task-planner"
            / "evals"
            / "evals.json"
        ).read_text(encoding="utf-8")
    )

    assert "## Intake Gate" in skill
    assert "一次只问一个问题" in skill
    assert "默认带着合理假设继续推进" in skill
    assert "会改变拆包边界、验收标准、执行权限或风险等级" in skill
    assert "references/examples.md" in skill
    assert "`no-viable-plan`" in skill
    assert "`blocked-with-handoff`" in skill
    assert "## Lightweight Engineering Method" in skill
    assert "Simplicity first" in skill
    assert "Surgical changes" in skill
    assert "Root cause before repair" in skill
    assert "status.tsv" in contract
    assert "Exit outcome:" in contract
    assert "Complexity / boundary risk:" in contract
    assert "Example 1: Direct Bugfix" in examples
    assert "Example 2: Small Parallel Refactor" in examples
    assert "Example 3: Intake Or Exit" in examples
    assert "Example 4: Raw Claim Needs Validation" in examples
    assert "Example 5: Generated Translation Files Must Reach Target" in examples
    assert any("onboarding" in item["prompt"] for item in evals["evals"])
    assert any(
        "raw claim" in assertion["text"] or "exit" in assertion["text"].lower()
        for item in evals["evals"]
        for assertion in item["assertions"]
    )


def test_list_and_install_user_skills(tmp_path):
    list_result = subprocess.run(
        [sys.executable, "tools/project.py", "list-user-skills", "--profile", "recommended"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert list_result.returncode == 0, list_result.stdout + list_result.stderr
    assert "recommended\tclean-checkpoint-first\tok" in list_result.stdout
    assert "all\tflow-realization-review\tok" not in list_result.stdout

    install_root = tmp_path / "skills"
    dry_run = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "install-user-skills",
            "--install-root", str(install_root),
            "--dry-run",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert dry_run.returncode == 0, dry_run.stdout + dry_run.stderr
    assert "install custom:clean-checkpoint-first" in dry_run.stdout
    assert not install_root.exists()

    installed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "install-user-skills",
            "--profile", "all",
            "--install-root", str(install_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr
    assert (install_root / "implement" / "SKILL.md").exists()
    assert (install_root / "flow-realization-review" / "SKILL.md").exists()
    assert (install_root / "clean-checkpoint-first" / "SKILL.md").exists()


def test_audit_user_skills_detects_drift(tmp_path):
    install_root = tmp_path / "skills"
    install = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "install-user-skills",
            "--install-root",
            str(install_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert install.returncode == 0, install.stdout + install.stderr

    synced = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "audit-user-skills",
            "--install-root",
            str(install_root),
            "--strict",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert synced.returncode == 0, synced.stdout + synced.stderr
    assert "recommended\tclean-checkpoint-first\tsynced" in synced.stdout

    target = install_root / "implement" / "SKILL.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
    drifted = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "audit-user-skills",
            "--install-root",
            str(install_root),
            "--strict",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert drifted.returncode == 1
    assert "recommended\timplement\tdrifted" in drifted.stdout


def test_configure_claude_sets_user_default_mode(tmp_path):
    module = load_project_tool()
    assert module.parse_claude_version("Claude Code v2.1.140") == (2, 1, 140)

    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"permissions": {"allow": ["Bash(git status *)"]}}), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "configure-claude",
            "--settings-file",
            str(settings),
            "--claude-version-output",
            "Claude Code v2.1.140",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["permissions"]["defaultMode"] == "auto"
    assert data["permissions"]["allow"] == ["Bash(git status *)"]
    assert "current enough" in completed.stdout


def test_configure_claude_dry_run_does_not_write_settings(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "configure-claude",
            "--settings-file",
            str(settings),
            "--claude-version-output",
            "Claude Code v2.1.140",
            "--dry-run",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(settings.read_text(encoding="utf-8")) == {}
    assert "would set" in completed.stdout


def test_configure_claude_blocks_old_version_without_override(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "configure-claude",
            "--settings-file",
            str(settings),
            "--claude-version-output",
            "Claude Code v2.1.139",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "older than v2.1.140" in completed.stdout
    assert "--skip-version-check" in completed.stderr
    assert json.loads(settings.read_text(encoding="utf-8")) == {}


def test_configure_claude_blocks_unknown_version_without_override(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "configure-claude",
            "--settings-file",
            str(settings),
            "--claude-version-output",
            "Claude Code nightly",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "v2.1.140 or newer" in completed.stdout
    assert "--skip-version-check" in completed.stderr
    assert json.loads(settings.read_text(encoding="utf-8")) == {}


def test_task_init_creates_minimal_live_state_control_surface(tmp_path):
    target = _copy_and_init(tmp_path, name="Workflow Lab", package="workflow_lab")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "init",
            "--name",
            "Complex Refactor",
            "--package",
            "01-contract-characterization",
            "--package",
            "02-implementation",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    task_root = target / "control" / "tasks" / "complex-refactor"
    assert task_root.is_dir()
    assert "control/tasks/complex-refactor/status.tsv" in completed.stdout

    brief = (task_root / "brief.md").read_text(encoding="utf-8")
    assert "## User Goal" in brief
    assert "## Acceptance Criteria" in brief
    assert "- [ ]" in brief

    context = task_root / "context.jsonl"
    assert context.read_text(encoding="utf-8") == ""

    promotion = (task_root / "promotion.md").read_text(encoding="utf-8")
    assert "Knowledge Promotion Review" in promotion
    assert "Promote to test / hook / lint" in promotion
    assert "Keep task-local" in promotion
    assert "Discard as transient" in promotion

    index = (task_root / "INDEX.md").read_text(encoding="utf-8")
    assert "Complex Refactor" in index
    assert "`status.tsv` is the live source of truth" in index
    assert "chat transcripts, status panels, and final reports are secondary" in index

    status_lines = (task_root / "status.tsv").read_text(encoding="utf-8").splitlines()
    assert status_lines[0] == (
        "package_id\tstate\towner\tbranch\tworktree\tbase_commit\tcommit_hash\t"
        "verification\tintegration\tcleanup\tlast_error\tupdated_at"
    )
    assert status_lines[1].startswith("01-contract-characterization\tpending\t")
    assert status_lines[2].startswith("02-implementation\tpending\t")
    assert status_lines[3].startswith("99-finalize\tpending\t")

    events = (task_root / "events.jsonl").read_text(encoding="utf-8")
    assert '"event": "task_initialized"' in events
    assert '"task": "Complex Refactor"' in events

    package_doc = (task_root / "packages" / "01-contract-characterization.md").read_text(encoding="utf-8")
    assert "# 01-contract-characterization" in package_doc
    assert "Update `../status.tsv` when this package changes state." in package_doc


def test_task_context_add_lists_and_check_validates_manifest(tmp_path):
    target = _copy_and_init(tmp_path, name="Workflow Lab", package="workflow_lab")
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Context Pilot"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )

    added = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "context",
            "add",
            "context-pilot",
            "--file",
            "control/state.md",
            "--reason",
            "Current project state and next action",
            "--stage",
            "implement",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert added.returncode == 0, added.stdout + added.stderr
    planned = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "context",
            "add",
            "context-pilot",
            "--file",
            "AGENTS.md",
            "--reason",
            "Shared project contract",
            "--stage",
            "plan",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert planned.returncode == 0, planned.stdout + planned.stderr
    checked = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "context",
            "add",
            "context-pilot",
            "--file",
            "README.md",
            "--reason",
            "User-facing workflow contract",
            "--stage",
            "check",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr

    listed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "context",
            "list",
            "context-pilot",
            "--stage",
            "implement",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert listed.returncode == 0
    assert "implement\tcontrol/state.md\tCurrent project state and next action" in listed.stdout
    assert "AGENTS.md" not in listed.stdout

    handoff = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "context",
            "list",
            "context-pilot",
            "--stage",
            "handoff",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert handoff.returncode == 0
    assert "check\tREADME.md\tUser-facing workflow contract" in handoff.stdout
    assert "control/state.md" not in handoff.stdout

    manifest = target / "control" / "tasks" / "context-pilot" / "context.jsonl"
    first_entry = json.loads(manifest.read_text(encoding="utf-8").splitlines()[0])
    assert first_entry == {
        "file": "control/state.md",
        "reason": "Current project state and next action",
        "stage": "implement",
    }

    check = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr


def test_task_context_rejects_escape_duplicate_and_invalid_stage(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Safe Context"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )
    base = [sys.executable, "tools/project.py", "task", "context", "add", "safe-context"]

    escaped = subprocess.run(
        [*base, "--file", "../outside.md", "--reason", "escape", "--stage", "plan"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert escaped.returncode == 2
    assert "repo-relative" in escaped.stderr

    invalid_stage = subprocess.run(
        [*base, "--file", "control/state.md", "--reason", "state", "--stage", "deploy"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert invalid_stage.returncode == 2

    first = subprocess.run(
        [*base, "--file", "control/state.md", "--reason", "state", "--stage", "plan"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    duplicate = subprocess.run(
        [*base, "--file", "control/state.md", "--reason", "again", "--stage", "plan"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert first.returncode == 0
    assert duplicate.returncode == 2
    assert "duplicate context entry" in duplicate.stderr


def test_check_rejects_invalid_task_context_manifest(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Broken Context"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )
    manifest = target / "control" / "tasks" / "broken-context" / "context.jsonl"
    manifest.write_text(
        '{"file":"missing.md","reason":"required","stage":"implement"}\n',
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "context file does not exist" in completed.stdout


def test_check_rejects_missing_task_context_manifest(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Missing Context"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )
    (target / "control" / "tasks" / "missing-context" / "context.jsonl").unlink()

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "missing task context manifest" in completed.stdout


def test_check_preserves_legacy_live_state_task_without_work_packet_files(tmp_path):
    target = _copy_and_init(tmp_path)
    legacy = target / "control" / "tasks" / "legacy-task"
    legacy.mkdir(parents=True)
    (legacy / "INDEX.md").write_text("# Legacy Task\n", encoding="utf-8")
    (legacy / "status.tsv").write_text(
        "package_id\tstate\n01-main\tpending\n99-finalize\tpending\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_check_requires_promotion_classification_for_finalized_task(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Promotion Gate"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )
    task_root = target / "control" / "tasks" / "promotion-gate"
    status = task_root / "status.tsv"
    status.write_text(
        status.read_text(encoding="utf-8").replace(
            "99-finalize\tpending\t",
            "99-finalize\tfinalized\t",
        ),
        encoding="utf-8",
    )

    blocked = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert blocked.returncode == 1
    assert "finalized task requires a promotion classification" in blocked.stdout

    promotion = task_root / "promotion.md"
    promotion.write_text(
        promotion.read_text(encoding="utf-8").replace(
            "- [ ] Keep task-local",
            "- [x] Keep task-local",
        ),
        encoding="utf-8",
    )
    passed = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert passed.returncode == 0, passed.stdout + passed.stderr


def test_task_activate_current_and_deactivate_are_worktree_scoped(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=True)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Active Pilot"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )

    activated = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "activate",
            "active-pilot",
            "--phase",
            "implement",
            "--next",
            "Add the context validator",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert activated.returncode == 0, activated.stdout + activated.stderr

    current = subprocess.run(
        [sys.executable, "tools/project.py", "task", "current"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert current.returncode == 0
    assert "active-pilot\timplement\tAdd the context validator" in current.stdout
    assert list((target / ".git" / "project-seed" / "active-task").glob("*.json"))

    deactivated = subprocess.run(
        [sys.executable, "tools/project.py", "task", "deactivate"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert deactivated.returncode == 0

    missing = subprocess.run(
        [sys.executable, "tools/project.py", "task", "current"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode == 1
    assert "No active complex task" in missing.stdout


def test_task_init_refuses_to_overwrite_existing_task(tmp_path):
    target = _copy_and_init(tmp_path)
    command = [
        sys.executable,
        "tools/project.py",
        "task",
        "init",
        "--name",
        "Shared Migration",
    ]
    first = subprocess.run(command, cwd=target, text=True, capture_output=True, check=False)
    second = subprocess.run(command, cwd=target, text=True, capture_output=True, check=False)

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 2
    assert "already exists" in second.stderr


def test_governance_init_creates_optional_lifecycle_doc(tmp_path):
    target = _copy_and_init(tmp_path, name="Long App", package="long_app")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "governance",
            "init",
            "--profile",
            "sustained",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "control/governance.md" in completed.stdout
    assert "no hooks or stricter checks" in completed.stdout

    doc = (target / "control" / "governance.md").read_text(encoding="utf-8")
    assert "Project profile: `sustained`" in doc
    assert "`Protect`" in doc
    assert "`Pilot`" in doc
    assert "`Defer`" in doc
    assert "`Retire`" in doc
    assert "`CLAUDE.md`" in doc
    assert "`.codex/hooks.json`" in doc
    assert "`.claude/settings.json`" in doc
    assert "`agent-assets/user-skills/manifest.json`" in doc
    assert "This file is advisory" in doc

    check = subprocess.run(
        [sys.executable, "tools/project.py", "check", "--skip-git"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr


def test_governance_init_refuses_to_overwrite_existing_doc(tmp_path):
    target = _copy_and_init(tmp_path)
    command = [
        sys.executable,
        "tools/project.py",
        "governance",
        "init",
    ]
    first = subprocess.run(command, cwd=target, text=True, capture_output=True, check=False)
    second = subprocess.run(command, cwd=target, text=True, capture_output=True, check=False)

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 2
    assert "already exists" in second.stderr


def _git_commit_all(target: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=agent@example.invalid",
            "-c",
            "user.name=Agent",
            "commit",
            "-m",
            message,
        ],
        cwd=target,
        check=True,
        capture_output=True,
    )


def test_clean_checkpoint_hook_blocks_new_tracked_dirty(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
    _git_commit_all(target, "init")

    hook = [sys.executable, ".codex/hooks/clean_checkpoint_first.py"]
    start = subprocess.run([*hook, "session-start"], cwd=target, text=True, capture_output=True, check=False)
    assert start.returncode == 0, start.stdout + start.stderr

    readme = target / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\nnew tracked dirt\n", encoding="utf-8")

    stop = subprocess.run([*hook, "stop"], cwd=target, text=True, capture_output=True, check=False)
    assert stop.returncode == 1
    assert "Stop blocked" in stop.stderr
    assert "README.md" in stop.stderr


def test_clean_checkpoint_hook_allows_existing_dirty_baseline(tmp_path):
    target = _copy_and_init(tmp_path)
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
    _git_commit_all(target, "init")

    readme = target / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\npre-existing tracked dirt\n", encoding="utf-8")

    hook = [sys.executable, ".codex/hooks/clean_checkpoint_first.py"]
    start = subprocess.run([*hook, "session-start"], cwd=target, text=True, capture_output=True, check=False)
    assert start.returncode == 0, start.stdout + start.stderr

    stop = subprocess.run([*hook, "stop"], cwd=target, text=True, capture_output=True, check=False)
    assert stop.returncode == 0, stop.stdout + stop.stderr

    readme.write_text(readme.read_text(encoding="utf-8") + "\nadditional session dirt\n", encoding="utf-8")
    stop_after_new_edit = subprocess.run([*hook, "stop"], cwd=target, text=True, capture_output=True, check=False)
    assert stop_after_new_edit.returncode == 1
    assert "README.md" in stop_after_new_edit.stderr


def test_safety_check_detects_staged_env(tmp_path):
    target = tmp_path / "safety_project"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.egg-info")
    shutil.copytree(ROOT, target, ignore=ignore)
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=target, check=True, capture_output=True)

    env_file = target / ".env"
    env_file.write_text("SECRET_KEY=abc123\n", encoding="utf-8")
    subprocess.run(["git", "add", "-f", ".env"], cwd=target, check=True, capture_output=True)

    module = load_project_tool()
    result = module.Result()
    original_root = module.ROOT
    try:
        module.ROOT = target
        module.check_safety(result)
    finally:
        module.ROOT = original_root

    assert any("sensitive file" in issue for issue in result.issues)


def test_safety_check_reads_staged_blob_instead_of_working_tree(tmp_path):
    target = tmp_path / "staged_secret_project"
    (target / "src").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
    path = target / "src" / "config.js"
    staged_secret = '"api_' + 'key": "production-credential-value-1234567890"\n'
    path.write_text(staged_secret, encoding="utf-8")
    subprocess.run(["git", "add", "src/config.js"], cwd=target, check=True, capture_output=True)
    path.write_text('"api_key": "placeholder"\n', encoding="utf-8")

    module = load_project_tool()
    result = module.Result()
    original_root = module.ROOT
    try:
        module.ROOT = target
        module.check_safety(result)
    finally:
        module.ROOT = original_root

    assert any("src/config.js" in issue and "possible secret" in issue for issue in result.issues)
