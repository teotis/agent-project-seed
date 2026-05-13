import importlib.util
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
    """当前仓库是 seed 模板，面板应显示 Seed 模板状态。"""
    panel = load_panel()
    assert panel.detect_status() == "seed"


def test_panel_distinguishes_seed_pending_ready(tmp_path):
    """三档状态检测：seed → pending → ready。"""
    panel = load_panel()

    # seed
    assert panel.detect_status() == "seed"

    # init 后是 pending
    target = _copy_and_init(tmp_path)
    # 重载模块让 ROOT 指向 target
    import tools.panel as panel_mod
    original_root = panel_mod.ROOT
    try:
        panel_mod.ROOT = target
        assert panel_mod.detect_status() == "pending"

        # 手动编辑 contract.md 写入明确目标 → ready
        contract = target / "control" / "contract.md"
        text = contract.read_text(encoding="utf-8")
        text = text.replace("已初始化，目标待补全", "目标：构建一个演示应用")
        contract.write_text(text, encoding="utf-8")
        assert panel_mod.detect_status() == "ready"
    finally:
        panel_mod.ROOT = original_root


def test_panel_after_init_shows_project_name(tmp_path):
    """init 后面板应显示项目名而非 'Agent Project Seed'。"""
    target = _copy_and_init(tmp_path, name="My App", package="my_app")

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target, text=True, capture_output=True,
    )
    assert result.returncode == 0
    assert "My App" in result.stdout
    assert "Seed 模板" not in result.stdout
    assert "已初始化" in result.stdout


def test_panel_shows_package_and_records(tmp_path):
    """面板应显示包名和 ledger 记录数。"""
    target = _copy_and_init(tmp_path)

    result = subprocess.run(
        [sys.executable, "tools/panel.py"],
        cwd=target, text=True, capture_output=True,
    )
    assert result.returncode == 0
    assert "demo_project" in result.stdout
    assert "Ledger:" in result.stdout
