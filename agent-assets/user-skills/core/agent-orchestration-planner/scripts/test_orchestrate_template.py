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
TEMPLATE = SCRIPT_DIR / "orchestrate-template.sh"


class OrchestrateTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="orchestrate-template-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.run_cmd(["git", "init"], cwd=self.repo)
        self.run_cmd(["git", "config", "user.email", "test@example.com"], cwd=self.repo)
        self.run_cmd(["git", "config", "user.name", "Test User"], cwd=self.repo)
        (self.repo / ".gitignore").write_text(".worktrees/\n._*\n", encoding="utf-8")
        (self.repo / "README.md").write_text("test repo\n", encoding="utf-8")
        self.run_cmd(["git", "add", ".gitignore", "README.md"], cwd=self.repo)
        self.run_cmd(["git", "commit", "-m", "init"], cwd=self.repo)
        self.mainline = self.run_cmd(
            ["git", "branch", "--show-current"],
            cwd=self.repo,
        ).stdout.strip()

        self.plan = self.repo / "docs" / "plans" / "sample-orchestration"
        (self.plan / "launchers").mkdir(parents=True)
        (self.plan / "packages").mkdir()
        (self.plan / "status").mkdir()
        shutil.copy2(TEMPLATE, self.plan / "launchers" / "orchestrate.sh")
        self.make_kit()

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

    def make_kit(self) -> None:
        (self.plan / "INDEX.md").write_text("# Sample\n", encoding="utf-8")
        (self.plan / "packages" / "01-alpha.md").write_text("# Alpha\n", encoding="utf-8")
        (self.plan / "packages" / "02-beta.md").write_text("# Beta\n", encoding="utf-8")
        (self.plan / "packages" / "99-finalize.md").write_text("# Finalize\n", encoding="utf-8")
        for package_id in ("01-alpha", "02-beta", "99-finalize"):
            (self.plan / "status" / f"{package_id}.md").write_text(
                f"# {package_id} Status\n\n## State\n\n`pending`\n",
                encoding="utf-8",
            )
        worktree_base = self.repo / ".worktrees" / "sample-orchestration"
        (self.plan / "launchers" / "package-graph.tsv").write_text(
            "\n".join(
                [
                    "package_id\tpackage_doc\tstatus_file\tdependencies\tdependency_type\twave\tbranch\tworktree\tmanual\tfinalize",
                    f"01-alpha\tpackages/01-alpha.md\tstatus/01-alpha.md\t\tstatus\t1\tagent/sample/01-alpha\t{worktree_base / '01-alpha'}\t0\t0",
                    f"02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t01-alpha\tstatus\t2\tagent/sample/02-beta\t{worktree_base / '02-beta'}\t0\t0",
                    f"99-finalize\tpackages/99-finalize.md\tstatus/99-finalize.md\t01-alpha,02-beta\tstatus+code\tfinal\tagent/sample/99-finalize\t{worktree_base / '99-finalize'}\t0\t1",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.plan / "status" / "state.tsv").write_text(
            "\n".join(
                [
                    "package_id\tstate\tlaunched_at\tcompleted_at\tagent\tbranch\tworktree\tbase_commit\tcommit_hash\tverification\tintegration\tcleanup\tlast_error\tfailed_command\tconflict_files\tlog_summary\trecovery_hint",
                    f"01-alpha\tpending\t\t\t\tagent/sample/01-alpha\t{worktree_base / '01-alpha'}\t\t\tpending\tpending\tpending\t\t\t\t\t",
                    f"02-beta\tpending\t\t\t\tagent/sample/02-beta\t{worktree_base / '02-beta'}\t\t\tpending\tpending\tpending\t\t\t\t\t",
                    f"99-finalize\tpending\t\t\t\tagent/sample/99-finalize\t{worktree_base / '99-finalize'}\t\t\tpending\tpending\tpending\t\t\t\t\t",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.plan / "launchers" / "agent-prompts.md").write_text(
            textwrap.dedent(
                f"""
                # Agent Prompts

                ## Package: 01-alpha - Alpha

                Run alpha.

                ## Package: 02-beta - Beta

                Run beta.

                ## Package: 99-finalize - Finalize

                Run finalize.
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

    def fake_claude(
        self,
        *,
        logs_ok: bool = True,
        omit_session: bool = False,
        output_style: str = "plain",
        agents_help_ok: bool = True,
        drain_stdin_on_bg: bool = False,
        drain_stdin_on_logs: bool = False,
    ) -> dict[str, str]:
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir(exist_ok=True)
        script = bin_dir / "claude"
        script.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env bash
                set -euo pipefail
                case "${{1:-}}" in
                  --version)
                    echo "2.1.142 (fake)"
                    ;;
                  logs)
                    if [ "{'1' if drain_stdin_on_logs else '0'}" = "1" ]; then
                      cat >/dev/null || true
                    fi
                    if [ "{'1' if logs_ok else '0'}" = "1" ]; then
                      echo "fake logs for $2"
                    else
                      echo "job not found" >&2
                      exit 1
                    fi
                    ;;
                  agents)
                    if [ "${{2:-}}" = "--help" ] && [ "{'1' if agents_help_ok else '0'}" = "1" ]; then
                      echo "Usage: claude agents"
                    else
                      echo "'claude agents' is not available in this environment." >&2
                      exit 1
                    fi
                    ;;
                  --bg)
                    if [ "{'1' if drain_stdin_on_bg else '0'}" = "1" ]; then
                      {{
                        printf 'ARGS:%s\\n' "$*"
                        cat || true
                        printf '\\n---END---\\n'
                      }} >> "{self.tmp / 'claude-bg-input.log'}"
                    fi
                    if [ "{'1' if omit_session else '0'}" = "1" ]; then
                      echo "backgrounded"
                    elif [ "{output_style}" = "bullet" ]; then
                      echo "backgrounded · fake-session-123"
                    elif [ "{output_style}" = "ansi_bullet" ]; then
                      printf 'backgrounded · \\033[36mfake-session-123\\033[39m\\n'
                    else
                      echo "backgrounded fake-session-123"
                    fi
                    ;;
                  *)
                    echo "unexpected claude args: $*" >&2
                    exit 2
                    ;;
                esac
                """
            ),
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        return {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}

    def fake_codex(self) -> dict[str, str]:
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir(exist_ok=True)
        script = bin_dir / "codex"
        script.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -euo pipefail
                if [ "${1:-}" = "--version" ]; then
                  echo "codex 9.9.9 (fake)"
                  exit 0
                fi
                if [ "${1:-}" != "exec" ]; then
                  echo "unexpected codex args: $*" >&2
                  exit 2
                fi
                for arg in "$@"; do
                  if [ "$arg" = "--ask-for-approval" ]; then
                    echo "unexpected codex args: $*" >&2
                    exit 2
                  fi
                done
                prompt="$(cat)"
                if printf '%s' "$prompt" | grep -q "Package: 99-finalize"; then
                  id="99-finalize"
                elif printf '%s' "$prompt" | grep -q "Package: 02-beta"; then
                  id="02-beta"
                else
                  id="01-alpha"
                fi
                echo "{\\"type\\":\\"thread.started\\",\\"thread_id\\":\\"thread-${id}\\"}"
                echo "{\\"type\\":\\"turn.completed\\"}"
                """
            ),
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        codex_home = self.tmp / "codex-home"
        codex_home.mkdir(exist_ok=True)
        return {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "ORCHESTRATION_RUNNER": "codex",
            "CODEX_HOME": str(codex_home),
        }

    def orchestrate(self, *args: str, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
        return self.run_cmd(
            ["bash", str(self.plan / "launchers" / "orchestrate.sh"), *args],
            cwd=self.repo,
            env=env,
            check=check,
        )

    def make_worktree_paths_relative(self) -> None:
        absolute_base = str(self.repo / ".worktrees" / "sample-orchestration")
        relative_base = ".worktrees/sample-orchestration"
        for path in (
            self.plan / "launchers" / "package-graph.tsv",
            self.plan / "status" / "state.tsv",
        ):
            path.write_text(
                path.read_text(encoding="utf-8").replace(absolute_base, relative_base),
                encoding="utf-8",
            )

    def make_package_dependency_type(self, package_id: str, dependency_type: str) -> None:
        graph = self.plan / "launchers" / "package-graph.tsv"
        lines = graph.read_text(encoding="utf-8").splitlines()
        updated: list[str] = []
        for line in lines:
            fields = line.split("\t")
            if fields and fields[0] == package_id:
                fields[4] = dependency_type
                line = "\t".join(fields)
            updated.append(line)
        graph.write_text("\n".join(updated) + "\n", encoding="utf-8")

    def commit_in_package_worktree(self, package_id: str, filename: str, content: str) -> str:
        worktree = self.repo / ".worktrees" / "sample-orchestration" / package_id
        branch = f"agent/sample/{package_id}"
        self.run_cmd(["git", "worktree", "add", "-B", branch, str(worktree), "HEAD"], cwd=self.repo)
        (worktree / filename).write_text(content, encoding="utf-8")
        self.run_cmd(["git", "add", filename], cwd=worktree)
        self.run_cmd(["git", "commit", "-m", f"{package_id} change"], cwd=worktree)
        return self.run_cmd(["git", "rev-parse", "HEAD"], cwd=worktree).stdout.strip()

    def prepare_cleanup_package(
        self,
        package_id: str,
        *,
        merge_to_mainline: bool = True,
        state: str = "completed",
    ) -> tuple[Path, str]:
        commit = self.commit_in_package_worktree(
            package_id,
            f"{package_id}.txt",
            f"{package_id}\n",
        )
        if merge_to_mainline:
            self.run_cmd(["git", "merge", "--ff-only", commit], cwd=self.repo)
        self.orchestrate(
            "mark-state",
            package_id,
            state,
            "--commit",
            commit,
            "--verification",
            "unit: pass",
            "--integration",
            "merged to mainline" if merge_to_mainline else "not merged",
        )
        return (
            self.repo / ".worktrees" / "sample-orchestration" / package_id,
            commit,
        )

    def test_status_rejects_malformed_state(self) -> None:
        (self.plan / "status" / "state.tsv").write_text(
            "package_id\tstate\n01-alpha\tpending\n",
            encoding="utf-8",
        )
        result = self.orchestrate("status", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid state header", result.stderr)

    def test_status_rejects_prompt_heading_that_runtime_cannot_parse(self) -> None:
        prompts = self.plan / "launchers" / "agent-prompts.md"
        prompts.write_text(
            prompts.read_text(encoding="utf-8").replace(
                "## Package: 01-alpha - Alpha",
                "## 01-alpha",
            ),
            encoding="utf-8",
        )

        result = self.orchestrate("status", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "prompt missing canonical heading: ## Package: 01-alpha - <title>",
            result.stderr,
        )
        self.assertIn("prompt validation failed", result.stderr)

    def test_start_rejects_duplicate_prompt_heading_before_mutating_state(self) -> None:
        prompts = self.plan / "launchers" / "agent-prompts.md"
        prompts.write_text(
            prompts.read_text(encoding="utf-8")
            + "\n## Package: 01-alpha - Duplicate\n\nDo not launch.\n",
            encoding="utf-8",
        )
        state_before = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")

        result = self.orchestrate("start", env=self.fake_claude(), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate prompt heading for package: 01-alpha", result.stderr)
        self.assertEqual(
            state_before,
            (self.plan / "status" / "state.tsv").read_text(encoding="utf-8"),
        )
        self.assertFalse(
            (self.repo / ".worktrees" / "sample-orchestration" / "01-alpha").exists()
        )

    def test_mark_state_writes_plain_signature_line(self) -> None:
        self.orchestrate("mark-state", "01-alpha", "blocked", "--error", "test blocker")

        state_lines = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8").splitlines()
        signature_lines = [line for line in state_lines if line.startswith("# signature:")]
        self.assertEqual(1, len(signature_lines))
        self.assertFalse(any(line.startswith(("'", '"')) for line in state_lines))

        result = self.orchestrate("status")
        self.assertEqual(result.returncode, 0)

    def test_start_records_session_id_and_creates_worktree(self) -> None:
        result = self.orchestrate("start", env=self.fake_claude())
        self.assertEqual(result.returncode, 0)
        self.assertIn("fake-session-123", (self.plan / "status" / "state.tsv").read_text())
        self.assertEqual(
            "claude",
            (self.plan / "status" / "runner").read_text(encoding="utf-8").strip(),
        )
        self.assertIn("claude agents", result.stdout)
        self.assertTrue((self.repo / ".worktrees" / "sample-orchestration" / "01-alpha").exists())
        self.assertTrue((self.plan / "status" / "launch-01-alpha.log").exists())
        logs = self.plan / "status" / "logs" / "01-alpha.log"
        self.assertTrue(logs.exists())
        self.assertIn("fake logs for fake-session-123", logs.read_text(encoding="utf-8"))

    def test_start_from_outside_repo_resolves_relative_worktree_to_repo_root(self) -> None:
        self.make_worktree_paths_relative()

        result = self.run_cmd(
            ["bash", str(self.plan / "launchers" / "orchestrate.sh"), "start"],
            cwd=self.tmp,
            env=self.fake_claude(),
        )

        self.assertEqual(result.returncode, 0)
        worktree = self.repo / ".worktrees" / "sample-orchestration" / "01-alpha"
        self.assertTrue(worktree.exists())
        self.assertFalse((self.tmp / ".worktrees" / "sample-orchestration" / "01-alpha").exists())
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn(f"agent/sample/01-alpha\t{worktree.resolve()}", state)

    def test_start_parses_bullet_backgrounded_session_id(self) -> None:
        result = self.orchestrate("start", env=self.fake_claude(output_style="bullet"))
        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("fake-session-123", state)
        self.assertNotIn("\t·\t", state)

    def test_start_parses_ansi_colored_backgrounded_session_id(self) -> None:
        result = self.orchestrate("start", env=self.fake_claude(output_style="ansi_bullet"))
        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("fake-session-123", state)
        self.assertNotIn("\x1b[36m", state)

    def test_start_launches_ready_wave_when_claude_reads_stdin(self) -> None:
        graph = self.plan / "launchers" / "package-graph.tsv"
        graph.write_text(
            graph.read_text(encoding="utf-8").replace(
                "02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t01-alpha\tstatus\t2",
                "02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t\tstatus\t1",
            ),
            encoding="utf-8",
        )

        result = self.orchestrate("start", env=self.fake_claude(drain_stdin_on_bg=True))

        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tlaunched\t", state)
        self.assertIn("02-beta\tlaunched\t", state)
        self.assertTrue((self.plan / "status" / "launch-01-alpha.log").exists())
        self.assertTrue((self.plan / "status" / "launch-02-beta.log").exists())
        stdin_log = (self.tmp / "claude-bg-input.log").read_text(encoding="utf-8")
        self.assertIn("Run alpha.", stdin_log)
        self.assertIn("Run beta.", stdin_log)
        self.assertNotIn("ARGS:--bg Run alpha.", stdin_log)

    def test_start_keeps_ready_queue_isolated_from_claude_log_stdin(self) -> None:
        graph = self.plan / "launchers" / "package-graph.tsv"
        graph.write_text(
            graph.read_text(encoding="utf-8").replace(
                "02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t01-alpha\tstatus\t2",
                "02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t\tstatus\t1",
            ),
            encoding="utf-8",
        )

        result = self.orchestrate(
            "start",
            env=self.fake_claude(drain_stdin_on_logs=True),
        )

        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tlaunched\t", state)
        self.assertIn("02-beta\tlaunched\t", state)

    def test_codex_runner_records_thread_id_and_creates_worktree(self) -> None:
        result = self.orchestrate("start", env=self.fake_codex())

        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("codex-thread:thread-01-alpha", state)
        self.assertTrue((self.repo / ".worktrees" / "sample-orchestration" / "01-alpha").exists())
        self.assertTrue((self.plan / "status" / "launch-01-alpha.log").exists())
        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn('"runner":"codex"', events)
        self.assertEqual(
            "codex",
            (self.plan / "status" / "runner").read_text(encoding="utf-8").strip(),
        )

    def test_advance_reuses_persisted_codex_runner_without_environment_variable(self) -> None:
        env = self.fake_codex()
        self.orchestrate("start", env=env)
        self.orchestrate(
            "mark-state",
            "01-alpha",
            "completed",
            "--commit",
            "abc123",
            "--verification",
            "unit: pass",
        )
        inherited_env = env.copy()
        inherited_env.pop("ORCHESTRATION_RUNNER")

        result = self.orchestrate("advance", "--from", "01-alpha", env=inherited_env)

        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("02-beta\tlaunched\t", state)
        self.assertIn("codex-thread:thread-02-beta", state)
        self.assertIn("Codex runner output", result.stdout)
        self.assertIn("codex exec resume <thread-id>", result.stdout)
        self.assertNotIn("codex resume <thread-id>", result.stdout)

    def test_codex_runner_rejects_unsupported_approval_policy(self) -> None:
        env = self.fake_codex()
        env["ORCHESTRATION_CODEX_APPROVAL_POLICY"] = "sometimes"

        result = self.orchestrate("start", env=env, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported ORCHESTRATION_CODEX_APPROVAL_POLICY", result.stderr)

    def test_codex_runner_rejects_unwritable_home_before_creating_worktree(self) -> None:
        env = self.fake_codex()
        invalid_home = self.tmp / "codex-home-file"
        invalid_home.write_text("not a directory\n", encoding="utf-8")
        env["CODEX_HOME"] = str(invalid_home)

        result = self.orchestrate("start", env=env, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Codex home is not writable", result.stderr)
        self.assertFalse((self.repo / ".worktrees" / "sample-orchestration" / "01-alpha").exists())

    def test_doctor_marks_exited_codex_process_stale(self) -> None:
        env = self.fake_codex()
        self.orchestrate("start", env=env)

        result = self.orchestrate("doctor", env=env, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reconciled 1 stale Codex process", result.stdout)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tstale\t", state)
        self.assertIn("completed without recording final package state", state)

    def test_auto_permission_mode_requires_explicit_opt_in(self) -> None:
        env = self.fake_claude()
        env["CLAUDE_PERMISSION_MODE"] = "auto"
        result = self.orchestrate("start", env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CLAUDE_PERMISSION_MODE=auto requires", result.stderr)

    def test_bypass_permission_mode_requires_explicit_opt_in(self) -> None:
        env = self.fake_claude()
        env["CLAUDE_PERMISSION_MODE"] = "bypassPermissions"
        result = self.orchestrate("start", env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CLAUDE_PERMISSION_MODE=bypassPermissions requires", result.stderr)

    def test_unreadable_logs_mark_package_stale(self) -> None:
        result = self.orchestrate("start", env=self.fake_claude(logs_ok=False), check=False)
        self.assertNotEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tstale\t", state)
        self.assertIn("logs are not readable", state)
        self.assertTrue((self.plan / "status" / "logs" / "01-alpha.log").exists())

    def test_missing_session_id_marks_package_invalid(self) -> None:
        result = self.orchestrate("start", env=self.fake_claude(omit_session=True), check=False)
        self.assertNotEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tinvalid\t", state)
        self.assertIn("missing background session id", state)

    def test_launched_state_does_not_unlock_downstream(self) -> None:
        self.orchestrate("start", env=self.fake_claude())

        result = self.orchestrate("advance", env=self.fake_claude())

        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tlaunched\t", state)
        self.assertIn("02-beta\tpending\t", state)
        self.assertNotIn("02-beta\tlaunched\t", state)
        self.assertIn("No ready packages to launch", result.stdout)

    def test_mark_state_unlocks_downstream_only_after_completed(self) -> None:
        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", "abc123", "--verification", "unit: pass")
        result = self.orchestrate("advance", env=self.fake_claude())
        self.assertEqual(result.returncode, 0)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("02-beta\tlaunched\t", state)

    def test_code_dependency_launches_from_integration_baseline(self) -> None:
        self.make_package_dependency_type("02-beta", "code")
        alpha_commit = self.commit_in_package_worktree("01-alpha", "alpha.txt", "alpha\n")
        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", alpha_commit, "--verification", "unit: pass")

        result = self.orchestrate("advance", env=self.fake_claude())

        self.assertEqual(result.returncode, 0)
        beta_worktree = self.repo / ".worktrees" / "sample-orchestration" / "02-beta"
        self.assertTrue(beta_worktree.exists())
        self.run_cmd(["git", "merge-base", "--is-ancestor", alpha_commit, "HEAD"], cwd=beta_worktree)
        base_commit = self.run_cmd(["git", "rev-parse", "HEAD"], cwd=beta_worktree).stdout.strip()
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn(f"02-beta\tlaunched\t", state)
        self.assertIn(f"\t{base_commit}\t\tpending\t", state)
        self.assertIn('"event":"code_dependency_merged"', (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8"))

    def test_retry_only_accepts_bad_terminal_states(self) -> None:
        result = self.orchestrate("retry", "01-alpha", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("retry only supports", result.stderr)
        self.orchestrate("mark-state", "01-alpha", "blocked", "--error", "test blocker")
        result = self.orchestrate("retry", "01-alpha", env=self.fake_claude())
        self.assertEqual(result.returncode, 0)

    def test_retry_breaker_stops_repeated_same_failure(self) -> None:
        env = self.fake_claude(omit_session=True)
        self.orchestrate("start", env=env, check=False)
        self.orchestrate("retry", "01-alpha", env=env, check=False)
        self.orchestrate("retry", "01-alpha", env=env, check=False)

        result = self.orchestrate("retry", "01-alpha", env=env, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("retry breaker open for 01-alpha", result.stderr)
        self.assertIn("missing background session id", result.stderr)

    def test_failure_recovery_context_survives_retry_until_completion(self) -> None:
        self.orchestrate(
            "mark-state",
            "01-alpha",
            "blocked",
            "--error",
            "merge failed",
            "--failed-command",
            "git merge agent/sample/01-alpha",
            "--conflict-files",
            "app/A.kt,app/B.kt",
            "--log-summary",
            "both branches edited constructor",
            "--recovery-hint",
            "resolve A before B",
        )

        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn("merge failed\tgit merge agent/sample/01-alpha\tapp/A.kt,app/B.kt", state)
        self.assertIn('"event":"terminal_failure"', events)
        self.assertIn('"failed_command":"git merge agent/sample/01-alpha"', events)
        self.assertIn('"recovery_hint":"resolve A before B"', events)

        result = self.orchestrate("retry", "01-alpha", env=self.fake_claude())
        self.assertEqual(result.returncode, 0)
        self.assertIn("prior failure context", result.stderr)
        self.assertIn("resolve A before B", result.stderr)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tlaunched\t", state)
        self.assertIn("merge failed\tgit merge agent/sample/01-alpha\tapp/A.kt,app/B.kt", state)

        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", "abc123", "--verification", "unit: pass")
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertNotIn("merge failed", state)
        self.assertNotIn("resolve A before B", state)

    def test_duplicate_terminal_failure_is_not_counted_twice(self) -> None:
        self.orchestrate("mark-state", "01-alpha", "blocked", "--error", "same blocker")
        self.orchestrate("mark-state", "01-alpha", "blocked", "--error", "same blocker")

        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")

        self.assertEqual(events.count('"event":"terminal_failure"'), 1)
        self.assertIn('"event":"terminal_failure_duplicate"', events)

    def test_collect_logs_writes_session_log_snapshot(self) -> None:
        self.orchestrate("start", env=self.fake_claude())

        result = self.orchestrate("collect-logs", "01-alpha", env=self.fake_claude())

        self.assertEqual(result.returncode, 0)
        self.assertIn("status/logs/01-alpha.log", result.stdout)
        logs = self.plan / "status" / "logs" / "01-alpha.log"
        self.assertIn("fake logs for fake-session-123", logs.read_text(encoding="utf-8"))
        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event":"agent_logs_collected"', events)
        self.assertIn('"reason":"manual"', events)

    def test_doctor_reconciles_unreadable_active_session_as_stale(self) -> None:
        self.orchestrate("start", env=self.fake_claude())

        result = self.orchestrate("doctor", env=self.fake_claude(logs_ok=False), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reconciled 1 stale agent session", result.stdout)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tstale\t", state)
        self.assertIn("doctor reconcile", state)
        logs = self.plan / "status" / "logs" / "01-alpha.log"
        self.assertIn("job not found", logs.read_text(encoding="utf-8"))
        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event":"agent_lost"', events)
        self.assertIn('"event":"agent_logs_unreadable"', events)

    def test_events_log_records_launch_and_state_changes(self) -> None:
        self.orchestrate("start", env=self.fake_claude())
        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", "abc123", "--verification", "unit: pass")

        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")

        self.assertIn('"event":"launch_succeeded"', events)
        self.assertIn('"package_id":"01-alpha"', events)
        self.assertIn('"session_id":"fake-session-123"', events)
        self.assertIn('"event":"state_changed"', events)
        self.assertIn('"new_state":"completed"', events)

    def test_scratch_path_creates_gitignored_package_workspace(self) -> None:
        result = self.orchestrate("scratch-path", "01-alpha")

        scratch_path = Path(result.stdout.strip())
        self.assertEqual(scratch_path, self.plan / "scratch" / "01-alpha")
        self.assertTrue(scratch_path.is_dir())
        gitignore = (self.plan / "scratch" / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*", gitignore)
        self.assertIn("!.gitignore", gitignore)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("01-alpha\tpending\t", state)
        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event":"scratch_path_requested"', events)
        self.assertIn('"package_id":"01-alpha"', events)

    def test_scratch_path_rejects_unknown_package(self) -> None:
        result = self.orchestrate("scratch-path", "nope", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown package: nope", result.stderr)

    def test_manual_packages_are_not_auto_launched(self) -> None:
        graph = self.plan / "launchers" / "package-graph.tsv"
        graph.write_text(
            graph.read_text(encoding="utf-8").replace(
                "02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t01-alpha\tstatus\t2\tagent/sample/02-beta",
                "02-beta\tpackages/02-beta.md\tstatus/02-beta.md\t01-alpha\tstatus\t2\tagent/sample/02-beta",
            ).replace(
                "\t0\t0\n99-finalize",
                "\t1\t0\n99-finalize",
                1,
            ),
            encoding="utf-8",
        )
        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", "abc123", "--verification", "unit: pass")
        result = self.orchestrate("advance", env=self.fake_claude())
        self.assertEqual(result.returncode, 0)
        self.assertIn("manual package ready: 02-beta", result.stderr)
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("02-beta\tmanual_required\t", state)
        self.assertFalse((self.repo / ".worktrees" / "sample-orchestration" / "02-beta").exists())

    def test_doctor_environment_reports_claude_capabilities(self) -> None:
        env = self.fake_claude(agents_help_ok=False)
        env["ORCHESTRATION_TEMPLATE_PATH"] = str(TEMPLATE)
        result = self.orchestrate("doctor", "--environment", env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("runner=claude", result.stdout)
        self.assertIn("claude_version=2.1.142 (fake)", result.stdout)
        self.assertIn("claude_agents_help=unavailable", result.stdout)
        self.assertIn("template_generated_version=1.1.1", result.stdout)
        self.assertIn("template_current_version=1.1.1", result.stdout)
        self.assertIn("template_version_status=ok", result.stdout)

    def test_doctor_environment_reports_codex_capabilities(self) -> None:
        result = self.orchestrate("doctor", "--environment", env=self.fake_codex())
        self.assertEqual(result.returncode, 0)
        self.assertIn("runner=codex", result.stdout)
        self.assertIn("codex_version=codex 9.9.9 (fake)", result.stdout)
        self.assertIn("codex_exec_approval_policy_flag=unavailable", result.stdout)
        self.assertIn("codex_sandbox=workspace-write", result.stdout)
        self.assertIn("codex_approval_policy=never", result.stdout)
        self.assertIn("codex_home=", result.stdout)
        self.assertIn("codex_home_writable=", result.stdout)

    def test_verify_finalize_blocks_missing_package_evidence(self) -> None:
        self.orchestrate("mark-state", "01-alpha", "completed", "--verification", "unit: pass")
        result = self.orchestrate("verify-finalize", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("01-alpha missing commit_hash", result.stderr)

    def test_verify_package_blocks_dirty_git_worktree(self) -> None:
        worktree = self.repo / ".worktrees" / "sample-orchestration" / "01-alpha"
        self.run_cmd(
            ["git", "worktree", "add", "-B", "agent/sample/01-alpha", str(worktree), "HEAD"],
            cwd=self.repo,
        )
        (worktree / "DIRTY.txt").write_text("uncommitted\n", encoding="utf-8")
        commit = self.run_cmd(["git", "rev-parse", "HEAD"], cwd=self.repo).stdout.strip()
        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", commit, "--verification", "unit: pass")

        result = self.orchestrate("verify-package", "01-alpha", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("01-alpha worktree is dirty", result.stderr)

    def test_verify_package_blocks_missing_code_dependency_ancestor(self) -> None:
        self.make_package_dependency_type("02-beta", "code")
        alpha_commit = self.commit_in_package_worktree("01-alpha", "alpha.txt", "alpha\n")
        beta_commit = self.commit_in_package_worktree("02-beta", "beta.txt", "beta\n")
        self.orchestrate("mark-state", "01-alpha", "completed", "--commit", alpha_commit, "--verification", "unit: pass")
        self.orchestrate("mark-state", "02-beta", "completed", "--commit", beta_commit, "--verification", "unit: pass")

        result = self.orchestrate("verify-package", "02-beta", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("02-beta does not contain code dependency 01-alpha", result.stderr)

    def test_cleanup_removes_only_recorded_merged_resources_and_records_events(self) -> None:
        alpha_worktree, _ = self.prepare_cleanup_package("01-alpha")
        beta_worktree, _ = self.prepare_cleanup_package("02-beta")
        finalize_worktree, _ = self.prepare_cleanup_package(
            "99-finalize",
            state="finalizing",
        )
        unrelated_worktree = self.repo / ".worktrees" / "unrelated"
        self.run_cmd(
            [
                "git",
                "worktree",
                "add",
                "-b",
                "unrelated/local-work",
                str(unrelated_worktree),
                "HEAD",
            ],
            cwd=self.repo,
        )

        result = self.orchestrate("cleanup", "--mainline", self.mainline)

        self.assertEqual(result.returncode, 0)
        self.assertFalse(alpha_worktree.exists())
        self.assertFalse(beta_worktree.exists())
        self.assertFalse(finalize_worktree.exists())
        self.assertTrue(unrelated_worktree.exists())
        for branch in (
            "agent/sample/01-alpha",
            "agent/sample/02-beta",
            "agent/sample/99-finalize",
        ):
            branch_result = self.run_cmd(
                ["git", "rev-parse", "--verify", branch],
                cwd=self.repo,
                check=False,
            )
            self.assertNotEqual(branch_result.returncode, 0)
        self.run_cmd(
            ["git", "rev-parse", "--verify", "unrelated/local-work"],
            cwd=self.repo,
        )
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertEqual(state.count("\tremoved\t"), 3)
        events = (self.plan / "status" / "events.jsonl").read_text(encoding="utf-8")
        self.assertEqual(events.count('"event":"cleanup_succeeded"'), 3)

    def test_cleanup_blocks_dirty_worktree_before_removing_any_resource(self) -> None:
        alpha_worktree, _ = self.prepare_cleanup_package("01-alpha")
        beta_worktree, _ = self.prepare_cleanup_package("02-beta")
        finalize_worktree, _ = self.prepare_cleanup_package(
            "99-finalize",
            state="finalizing",
        )
        (beta_worktree / "DIRTY.txt").write_text("dirty\n", encoding="utf-8")

        result = self.orchestrate(
            "cleanup",
            "--mainline",
            self.mainline,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("02-beta worktree is dirty", result.stderr)
        self.assertTrue(alpha_worktree.exists())
        self.assertTrue(beta_worktree.exists())
        self.assertTrue(finalize_worktree.exists())
        state = (self.plan / "status" / "state.tsv").read_text(encoding="utf-8")
        self.assertIn("99-finalize\tblocked\t", state)

    def test_cleanup_blocks_commit_not_merged_to_mainline(self) -> None:
        alpha_worktree, _ = self.prepare_cleanup_package("01-alpha")
        beta_worktree, _ = self.prepare_cleanup_package(
            "02-beta",
            merge_to_mainline=False,
        )
        finalize_worktree, _ = self.prepare_cleanup_package(
            "99-finalize",
            state="finalizing",
        )

        result = self.orchestrate(
            "cleanup",
            "--mainline",
            self.mainline,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            f"02-beta commit is not merged into mainline {self.mainline}",
            result.stderr,
        )
        self.assertTrue(alpha_worktree.exists())
        self.assertTrue(beta_worktree.exists())
        self.assertTrue(finalize_worktree.exists())

    def test_cleanup_is_idempotent_after_success(self) -> None:
        self.prepare_cleanup_package("01-alpha")
        self.prepare_cleanup_package("02-beta")
        self.prepare_cleanup_package("99-finalize", state="finalizing")
        self.orchestrate("cleanup", "--mainline", self.mainline)

        result = self.orchestrate("cleanup", "--mainline", self.mainline)

        self.assertEqual(result.returncode, 0)
        self.assertIn("cleanup: already complete", result.stdout)

    def test_mark_state_rejects_finalized_until_cleanup_completes(self) -> None:
        self.prepare_cleanup_package("01-alpha")
        self.prepare_cleanup_package("02-beta")
        _, finalize_commit = self.prepare_cleanup_package(
            "99-finalize",
            state="finalizing",
        )

        result = self.orchestrate(
            "mark-state",
            "99-finalize",
            "finalized",
            "--commit",
            finalize_commit,
            "--verification",
            "all pass",
            "--integration",
            f"merged to {self.mainline}",
            "--cleanup",
            "deferred",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot mark 99-finalize finalized before cleanup completes", result.stderr)


if __name__ == "__main__":
    unittest.main()
