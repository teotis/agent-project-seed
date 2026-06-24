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
        module.GitChange("??", "control/ledger.md"),
        module.GitChange("??", ".codex/config.example.toml"),
        module.GitChange(" M", "SETUP_NEW_MACHINE.md"),
        module.GitChange("??", ".env"),
        module.GitChange("??", "work/tmp/scratch.txt"),
        module.GitChange("??", "work/out/result.png"),
    ]

    allowed, rejected = module.classify_changes(changes)

    assert [change.path for change in allowed] == [
        "control/ledger.md",
        ".codex/config.example.toml",
        "SETUP_NEW_MACHINE.md",
    ]
    assert [change.path for change in rejected] == [".env", "work/tmp/scratch.txt", "work/out/result.png"]


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


def _copy_and_init(tmp_path, name="Demo Project", package="demo_project"):
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
    hooks = json.loads((target / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    assert "SessionStart" in hooks["hooks"]
    assert "PostToolUse" in hooks["hooks"]
    assert "Stop" in hooks["hooks"]
    assert (target / "work" / "in" / ".gitkeep").exists()


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
    assert "Windows PowerShell" in readme
    assert "py -3 tools/project.py check" in readme
    assert "governance init --profile sustained" in readme


def test_seed_docs_include_windows_setup_commands():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    setup = (ROOT / "SETUP_NEW_MACHINE.md").read_text(encoding="utf-8")

    for text in (readme, setup):
        assert "Windows PowerShell" in text
        assert "py -3 tools/project.py init" in text
        assert "py -3 -m pytest" in text
        assert "governance init --profile sustained" in text
        assert "Governance Lifecycle" in text
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
    assert "python3" not in codex_hooks
    assert "python3" not in codex_config
    assert "python3" not in claude_settings


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


def test_no_legacy_directories_in_template():
    legacy_dirs = [
        "codex",
        "revision",
        "journal",
        "reports",
        "data",
        "source_material",
        "optional_packs",
        "input",
        "output",
    ]
    for relative in legacy_dirs:
        assert not (ROOT / relative).exists(), f"legacy directory remains: {relative}"


def test_gemini_adapter_is_not_part_of_template():
    module = load_project_tool()

    assert not (ROOT / "GEMINI.md").exists()
    assert all("GEMINI" not in str(path) for path in module.expected_agent_files())
    assert "GEMINI.md" not in module.ALLOWED_PREFIXES


def test_user_skill_manifest_assets_are_valid():
    module = load_project_tool()
    entries = module.user_skill_entries(["all"])

    assert len(entries) == 44
    assert ("core", "clean-checkpoint-first", ROOT / "agent-assets" / "user-skills" / "core" / "clean-checkpoint-first") in entries
    assert ("core", "agent-task-planner", ROOT / "agent-assets" / "user-skills" / "core" / "agent-task-planner") in entries
    assert ("optional", "abstraction-architect", ROOT / "agent-assets" / "user-skills" / "optional" / "abstraction-architect") in entries
    assert ("superpowers", "brainstorming", ROOT / "agent-assets" / "user-skills" / "superpowers" / "brainstorming") in entries

    result = module.Result()
    module.check_user_skill_assets(result)
    assert result.issues == []
    assert any("44 skills" in notice for notice in result.notices)


def test_agent_task_planner_contract_includes_exit_paths_and_lightweight_methods():
    skill = (ROOT / "agent-assets" / "user-skills" / "core" / "agent-task-planner" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    contract = (
        ROOT
        / "agent-assets"
        / "user-skills"
        / "core"
        / "agent-task-planner"
        / "references"
        / "task-plan-contract.md"
    ).read_text(encoding="utf-8")
    examples = (
        ROOT
        / "agent-assets"
        / "user-skills"
        / "core"
        / "agent-task-planner"
        / "references"
        / "examples.md"
    ).read_text(encoding="utf-8")
    evals = json.loads(
        (
            ROOT
            / "agent-assets"
            / "user-skills"
            / "core"
            / "agent-task-planner"
            / "evals"
            / "evals.json"
        ).read_text(encoding="utf-8")
    )

    assert "## Intake Gate" in skill
    assert "ask exactly one question" in skill
    assert "references/examples.md" in skill
    assert "## Exit Paths" in skill
    assert "`no-viable-plan`" in skill
    assert "`blocked-with-handoff`" in skill
    assert "## Lightweight Engineering Method" in skill
    assert "Simplicity first" in skill
    assert "Surgical changes" in skill
    assert "Root cause before repair" in skill
    assert "## Exit Path" in contract
    assert "Exit outcome:" in contract
    assert "Example 1: Direct Bugfix" in examples
    assert "Example 2: Small Parallel Refactor" in examples
    assert "Example 3: Intake Or Exit" in examples
    assert any("onboarding" in item["prompt"] for item in evals["evals"])


def test_list_and_install_user_skills(tmp_path):
    list_result = subprocess.run(
        [sys.executable, "tools/project.py", "list-user-skills", "--group", "superpowers"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert list_result.returncode == 0, list_result.stdout + list_result.stderr
    assert "superpowers\tbrainstorming\tok" in list_result.stdout
    assert "core\tclean-checkpoint-first" not in list_result.stdout

    install_root = tmp_path / "skills"
    dry_run = subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "install-user-skills",
            "--group", "core",
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
            "--group", "superpowers",
            "--install-root", str(install_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr
    assert (install_root / "brainstorming" / "SKILL.md").exists()
    assert (install_root / "writing-skills" / "SKILL.md").exists()
    assert not (install_root / "clean-checkpoint-first").exists()


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
