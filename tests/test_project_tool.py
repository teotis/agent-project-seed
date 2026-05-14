import importlib.util
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
        module.GitChange("??", ".env"),
        module.GitChange("??", "work/tmp/scratch.txt"),
        module.GitChange("??", "work/out/result.png"),
    ]

    allowed, rejected = module.classify_changes(changes)

    assert [change.path for change in allowed] == ["control/ledger.md"]
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
    assert (target / "control" / "contract.md").exists()
    assert (target / "work" / "in" / ".gitkeep").exists()


def test_init_updates_contract_state_and_ledger(tmp_path):
    target = _copy_and_init(tmp_path, name="My App", package="my_app")

    contract = (target / "control" / "contract.md").read_text(encoding="utf-8")
    assert "My App" in contract
    assert "Initialized, goals pending" in contract
    assert "After copying this scaffold" not in contract

    state = (target / "control" / "state.md").read_text(encoding="utf-8")
    assert "My App" in state
    assert "my_app" in state

    ledger = (target / "control" / "ledger.md").read_text(encoding="utf-8")
    assert "Project initialized from seed" in ledger
    assert "My App" in ledger


def test_no_legacy_directories_in_template():
    legacy_dirs = [
        "codex",
        "docs",
        "revision",
        "journal",
        "reports",
        "data",
        "source_material",
        "optional_packs",
        "scripts",
        "input",
        "output",
        ".tmp",
    ]
    for relative in legacy_dirs:
        assert not (ROOT / relative).exists(), f"legacy directory remains: {relative}"
