#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CODEX_TEMPLATE = SCRIPT_DIR / "start-codex-app-template.sh"
CLAUDE_TEMPLATE = SCRIPT_DIR / "start-claude-code-template.sh"


class RunnerLauncherTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="runner-launcher-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.run_cmd(["git", "init"], cwd=self.repo)
        self.run_cmd(["git", "config", "user.email", "test@example.com"], cwd=self.repo)
        self.run_cmd(["git", "config", "user.name", "Test User"], cwd=self.repo)
        (self.repo / "README.md").write_text("test\n", encoding="utf-8")
        self.run_cmd(["git", "add", "README.md"], cwd=self.repo)
        self.run_cmd(["git", "commit", "-m", "init"], cwd=self.repo)

        self.plan = self.repo / "docs" / "plans" / "sample"
        self.launchers = self.plan / "launchers"
        (self.plan / "status").mkdir(parents=True)
        self.launchers.mkdir(parents=True)

        shutil.copy2(CODEX_TEMPLATE, self.launchers / "start-codex-app.sh")
        shutil.copy2(CLAUDE_TEMPLATE, self.launchers / "start-claude-code.sh")
        for launcher in ("start-codex-app.sh", "start-claude-code.sh"):
            path = self.launchers / launcher
            path.chmod(path.stat().st_mode | stat.S_IEXEC)

        self.write_fake_orchestrate()
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        self.write_fake_codex()
        self.write_fake_claude()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cmd(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        result = subprocess.run(
            args,
            cwd=cwd,
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check and result.returncode != 0:
            self.fail(
                f"command failed: {args}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def env(self) -> dict[str, str]:
        return {"PATH": f"{self.fake_bin}{os.pathsep}{os.environ['PATH']}"}

    def write_fake_orchestrate(self) -> None:
        script = self.launchers / "orchestrate.sh"
        script.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -euo pipefail
                SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
                PLAN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
                mkdir -p "$PLAN_ROOT/status"
                printf '%s\t%s\n' "${ORCHESTRATION_RUNNER:-missing}" "$*" >> "$PLAN_ROOT/status/calls.log"
                case "${1:-}" in
                  doctor)
                    echo "runner=${ORCHESTRATION_RUNNER:-missing}"
                    ;;
                  start)
                    echo "started ${ORCHESTRATION_RUNNER:-missing}"
                    ;;
                  status)
                    echo "PACKAGE STATE"
                    ;;
                  *)
                    echo "$*"
                    ;;
                esac
                """
            ),
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

    def write_fake_codex(self) -> None:
        script = self.fake_bin / "codex"
        script.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env bash
                printf '%s\\n' "$*" >> "{self.tmp / 'codex.log'}"
                """
            ),
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

    def write_fake_claude(self) -> None:
        script = self.fake_bin / "claude"
        script.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env bash
                printf '%s\\n' "$*" >> "{self.tmp / 'claude.log'}"
                echo "claude $*"
                """
            ),
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

    def calls(self) -> list[str]:
        return (self.plan / "status" / "calls.log").read_text(encoding="utf-8").splitlines()

    def test_codex_launcher_runs_doctor_start_status_with_codex_runner(self) -> None:
        result = self.run_cmd(
            ["bash", str(self.launchers / "start-codex-app.sh")],
            cwd=self.repo,
            env=self.env(),
        )

        self.assertEqual(
            [
                "codex\tdoctor --environment",
                "codex\tstart",
                "codex\tstatus",
            ],
            self.calls(),
        )
        self.assertIn("Codex runner evidence", result.stdout)
        self.assertIn("start-codex-app.sh resume <thread-id>", result.stdout)

    def test_claude_launcher_runs_doctor_start_status_with_claude_runner(self) -> None:
        result = self.run_cmd(
            ["bash", str(self.launchers / "start-claude-code.sh")],
            cwd=self.repo,
            env=self.env(),
        )

        self.assertEqual(
            [
                "claude\tdoctor --environment",
                "claude\tstart",
                "claude\tstatus",
            ],
            self.calls(),
        )
        self.assertIn("claude agents --cwd", result.stdout)
        self.assertIn("start-claude-code.sh\" agents", result.stdout)

    def test_codex_resume_strips_coordinator_prefix(self) -> None:
        self.run_cmd(
            ["bash", str(self.launchers / "start-codex-app.sh"), "resume", "codex-thread:abc123"],
            cwd=self.repo,
            env=self.env(),
        )

        self.assertEqual(
            "exec resume abc123",
            (self.tmp / "codex.log").read_text(encoding="utf-8").strip(),
        )


if __name__ == "__main__":
    unittest.main()
