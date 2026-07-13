import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_panel():
    script = ROOT / "tools" / "panel.py"
    spec = importlib.util.spec_from_file_location("panel_tool", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["panel_tool"] = module
    spec.loader.exec_module(module)
    return module


def _copy_and_init(tmp_path, name="Demo Project", package="demo_project"):
    target = tmp_path / "copied_project"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.egg-info")
    shutil.copytree(ROOT, target, ignore=ignore)
    subprocess.run(
        [sys.executable, "tools/project.py", "init",
         "--name", name, "--package-name", package, "--no-git"],
        cwd=target, text=True, capture_output=True, check=True,
    )
    return target


def test_panel_detects_seed_status():
    """Current repo is a seed template; panel should show Seed Template status."""
    panel = load_panel()
    assert panel.detect_status() == "seed"


def test_panel_distinguishes_seed_pending_ready(tmp_path):
    """Three-level status detection: seed -> pending -> ready."""
    panel = load_panel()

    # seed
    assert panel.detect_status() == "seed"

    # after init it should be pending
    target = _copy_and_init(tmp_path)
    # Reload module so ROOT points to target
    import tools.panel as panel_mod
    original_root = panel_mod.ROOT
    try:
        panel_mod.ROOT = target
        assert panel_mod.detect_status() == "pending"

        # Manually edit AGENTS.md with explicit goals -> ready
        agents = target / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        text = text.replace("Initialized, goals pending", "Goal: Build a demo application")
        agents.write_text(text, encoding="utf-8")
        assert panel_mod.detect_status() == "ready"
    finally:
        panel_mod.ROOT = original_root


def test_panel_after_init_shows_project_name(tmp_path):
    """After init, panel should show project name instead of 'Agent Project Seed'."""
    target = _copy_and_init(tmp_path, name="My App", package="my_app")

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target, text=True, capture_output=True,
    )
    assert result.returncode == 0
    assert "My App" in result.stdout
    assert "种子模板" not in result.stdout
    assert "目标待定" in result.stdout


def test_panel_shows_package_and_records(tmp_path):
    """Panel should show package name and ledger record count."""
    target = _copy_and_init(tmp_path)

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target, text=True, capture_output=True,
    )
    assert result.returncode == 0
    assert "demo_project" in result.stdout
    assert "记录:" in result.stdout


def test_panel_prioritizes_delivery_receipt_over_git_details(tmp_path):
    target = _copy_and_init(tmp_path)
    receipt = target / "control" / "delivery_receipt.md"
    receipt.write_text(
        """# Delivery Receipt

## User Goal

Help researchers recover decision context quickly.

## Acceptance Criteria

- [x] A decision and its evidence appear together.
- [ ] The next research action is visible at handoff.

## Evidence

- Decision retrieval test passes.

## Remaining Gaps

- Verify handoff presentation with researchers.

## User Next Decision

- Decide whether to pilot the handoff view.
""",
        encoding="utf-8",
    )
    agents = target / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace("Initialized, goals pending", "Ready — goal defined"),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "tools/panel.py", "--mode", "handoff"],
        cwd=target,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "目标: Help researchers recover decision context quickly." in result.stdout
    assert "目标状态: 进行中" in result.stdout
    assert "验收: 1/2 已通过" in result.stdout
    assert "证据: Decision retrieval test passes." in result.stdout
    assert "缺口: Verify handoff presentation with researchers." in result.stdout
    assert "用户决策: Decide whether to pilot the handoff view." in result.stdout
    assert result.stdout.index("目标:") < result.stdout.index("Git:")


def test_panel_marks_goal_complete_only_with_evidence_and_no_gaps(tmp_path):
    target = _copy_and_init(tmp_path)
    (target / "control" / "delivery_receipt.md").write_text(
        """# Delivery Receipt

## User Goal

Ship a searchable research history.

## Acceptance Criteria

- [x] Search returns the matching decision.

## Evidence

- Search integration test passes.

## Remaining Gaps

## User Next Decision

- Start the next research task.
""",
        encoding="utf-8",
    )
    agents = target / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace("Initialized, goals pending", "Ready — goal defined"),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "目标状态: 验收完成" in result.stdout


def test_panel_shows_active_complex_task_breadcrumb_and_acceptance_gap(tmp_path):
    target = _copy_and_init(tmp_path, name="Workflow Lab", package="workflow_lab")
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=True)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Context Pilot"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )
    brief = target / "control" / "tasks" / "context-pilot" / "brief.md"
    brief.write_text(
        """# Context Pilot

## User Goal

- Keep complex-task context explicit.

## Acceptance Criteria

- [x] Work Packet exists.
- [ ] Panel shows the first evidence gap.

## Non-Goals

- No collaboration runtime.
""",
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "activate",
            "context-pilot",
            "--phase",
            "check",
            "--next",
            "Run the focused panel test",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "复杂任务: Context Pilot" in result.stdout
    assert "阶段: check" in result.stdout
    assert "任务下一步: Run the focused panel test" in result.stdout
    assert "任务缺口: Panel shows the first evidence gap." in result.stdout
    assert result.stdout.index("复杂任务:") < result.stdout.index("Git:")


def test_panel_falls_back_to_package_evidence_gap_after_acceptance_is_checked(tmp_path):
    target = _copy_and_init(tmp_path, name="Workflow Lab", package="workflow_lab")
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=True)
    subprocess.run(
        [sys.executable, "tools/project.py", "task", "init", "--name", "Evidence Pilot"],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )
    brief = target / "control" / "tasks" / "evidence-pilot" / "brief.md"
    brief.write_text(
        """# Evidence Pilot

## User Goal

- Keep completion evidence visible.

## Acceptance Criteria

- [x] The user-visible behavior is implemented.

## Non-Goals

- None.
""",
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "tools/project.py",
            "task",
            "activate",
            "evidence-pilot",
            "--phase",
            "check",
            "--next",
            "Close the remaining evidence gap",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=True,
    )

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "任务缺口: 01-main verification pending" in result.stdout


def test_panel_lists_open_records_in_chinese_and_limits_each_group(tmp_path):
    target = _copy_and_init(tmp_path, name="Demo Project", package="demo_project")
    ledger = target / "control" / "ledger.md"
    records = []
    for index in range(1, 7):
        records.append(f"""
## 2026-06-25T10:0{index}:00 - Open request {index}

type: request
status: open
tags: panel

summary:
- 未完成需求 {index}
""")
    records.append("""
## 2026-06-25T10:07:00 - Closed request

type: request
status: closed
tags: panel

summary:
- 已完成需求不显示
""")
    for index in range(1, 7):
        records.append(f"""
## 2026-06-25T11:0{index}:00 - Open risk {index}

type: risk
status: open
tags: panel

summary:
- 未收口风险 {index}
""")
    ledger.write_text(ledger.read_text(encoding="utf-8") + "\n".join(records), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "tools/panel.py", "--mode", "handoff"],
        cwd=target, text=True, capture_output=True,
    )

    assert result.returncode == 0
    assert "未完成:" in result.stdout
    assert "风险:" in result.stdout
    assert "未完成需求 1" in result.stdout
    assert "未完成需求 5" in result.stdout
    assert "未完成需求 6" not in result.stdout
    assert "已完成需求不显示" not in result.stdout
    assert "未收口风险 1" in result.stdout
    assert "未收口风险 5" in result.stdout
    assert "未收口风险 6" not in result.stdout


def test_claude_panel_hook_runs_only_for_first_prompt_or_handoff(tmp_path):
    target = _copy_and_init(tmp_path)
    hook = target / ".claude" / "hooks" / "panel_hook.py"
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True, text=True)

    second_prompt = subprocess.run(
        [sys.executable, str(hook)],
        cwd=target,
        input=json.dumps({"cwd": str(target), "prompt_index": 2}),
        text=True,
        capture_output=True,
    )
    assert second_prompt.returncode == 0
    assert second_prompt.stdout == ""

    first_prompt = subprocess.run(
        [sys.executable, str(hook)],
        cwd=target,
        input=json.dumps({"cwd": str(target), "prompt_index": 1}),
        text=True,
        capture_output=True,
    )
    assert first_prompt.returncode == 0
    assert "状态面板" in first_prompt.stdout
    assert list((target / ".git" / "clean-checkpoint-first").glob("*.json"))

    handoff = subprocess.run(
        [sys.executable, str(hook)],
        cwd=target,
        input=json.dumps({"cwd": str(target), "panel_mode": "handoff", "prompt_index": 9}),
        text=True,
        capture_output=True,
    )
    assert handoff.returncode == 0
    assert "--mode" not in handoff.stdout
    assert "状态面板" in handoff.stdout


def test_codex_panel_hook_runs_only_for_first_prompt_or_handoff(tmp_path):
    target = _copy_and_init(tmp_path)
    hook = target / ".codex" / "hooks" / "panel_hook.py"

    second_prompt = subprocess.run(
        [sys.executable, str(hook)],
        cwd=target,
        input=json.dumps({"cwd": str(target), "prompt_index": 2}),
        text=True,
        capture_output=True,
    )
    assert second_prompt.returncode == 0
    assert second_prompt.stdout == ""

    first_prompt = subprocess.run(
        [sys.executable, str(hook)],
        cwd=target,
        input=json.dumps({"cwd": str(target), "prompt_index": 1}),
        text=True,
        capture_output=True,
    )
    assert first_prompt.returncode == 0
    assert "状态面板" in first_prompt.stdout

    handoff = subprocess.run(
        [sys.executable, str(hook)],
        cwd=target,
        input=json.dumps({"cwd": str(target), "panel_mode": "handoff", "prompt_index": 9}),
        text=True,
        capture_output=True,
    )
    assert handoff.returncode == 0
    assert "状态面板" in handoff.stdout
