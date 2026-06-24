#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("complexity_probe.py")


class ComplexityProbeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="complexity-probe-test-")
        self.repo = Path(self.temp_dir.name)
        self.run_command(["git", "init"])
        self.run_command(["git", "config", "user.email", "test@example.com"])
        self.run_command(["git", "config", "user.name", "Test User"])

        (self.repo / "src").mkdir()
        (self.repo / "src" / "service.py").write_text(
            "\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "",
                    "def process(items, enabled=True):",
                    "    # TODO: split responsibilities",
                    "    if enabled:",
                    "        for item in items:",
                    "            if item:",
                    "                print(item)",
                    "    return Path('.')",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.repo / "build").mkdir()
        (self.repo / "build" / "generated.py").write_text("if True:\n    pass\n", encoding="utf-8")
        (self.repo / ".tmp").mkdir()
        (self.repo / ".tmp" / "scratch.py").write_text("if True:\n    pass\n", encoding="utf-8")
        self.run_command(["git", "add", "src/service.py"])
        self.run_command(["git", "commit", "-m", "initial"])
        (self.repo / "src" / "service.py").write_text(
            (self.repo / "src" / "service.py").read_text(encoding="utf-8")
            + "\ndef second():\n    return True\n",
            encoding="utf-8",
        )
        self.run_command(["git", "add", "src/service.py"])
        self.run_command(["git", "commit", "-m", "touch hotspot"])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_command(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_reports_structural_facts_and_git_churn(self) -> None:
        result = self.run_command(["python3", str(SCRIPT), str(self.repo), "--pretty"])
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["probe"], "complexity")
        self.assertEqual(payload["summary"]["files_scanned"], 1)
        self.assertEqual(payload["summary"]["git_commits_scanned"], 2)

        file_fact = payload["files"][0]
        self.assertEqual(file_fact["path"], "src/service.py")
        self.assertGreaterEqual(file_fact["branch_tokens"], 3)
        self.assertGreaterEqual(file_fact["max_indent"], 3)
        self.assertEqual(file_fact["import_count"], 2)
        self.assertEqual(file_fact["todo_count"], 1)
        self.assertEqual(file_fact["git_change_count"], 2)

        scanned_paths = {item["path"] for item in payload["files"]}
        self.assertNotIn("build/generated.py", scanned_paths)
        self.assertNotIn(".tmp/scratch.py", scanned_paths)


if __name__ == "__main__":
    unittest.main()
