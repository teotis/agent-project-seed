#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("flow_probe.py")


class FlowProbeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="flow-probe-test-")
        self.repo = Path(self.temp_dir.name)
        self.run_command(["git", "init"])
        self.run_command(["git", "config", "user.email", "test@example.com"])
        self.run_command(["git", "config", "user.name", "Test User"])

        (self.repo / ".github" / "workflows").mkdir(parents=True)
        (self.repo / ".pytest_cache").mkdir()
        (self.repo / "reports").mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "evals").mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "tests").mkdir()
        (self.repo / "vendor-copy" / ".git").mkdir(parents=True)
        (self.repo / "vendor-copy" / "src").mkdir()
        (self.repo / ".pytest_cache" / "README.md").write_text(
            "generated cache\n",
            encoding="utf-8",
        )
        (self.repo / "reports" / "old.md").write_text(
            "except Exception:\n    pass\n",
            encoding="utf-8",
        )
        (self.repo / "docs" / "example.md").write_text(
            "@app.route('/example')\nexcept Exception:\n    pass\n",
            encoding="utf-8",
        )
        (self.repo / "evals" / "evals.json").write_text(
            '{"prompt": "run a cron scheduler and catch Exception"}\n',
            encoding="utf-8",
        )
        (self.repo / "vendor-copy" / "src" / "copied.py").write_text(
            "import requests\nrequests.get('https://example.com')\n",
            encoding="utf-8",
        )
        (self.repo / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
        (self.repo / ".github" / "workflows" / "ci.yml").write_text(
            "on: [push]\njobs: {}\n",
            encoding="utf-8",
        )
        (self.repo / "src" / "app.py").write_text(
            "\n".join(
                [
                    "import os",
                    "import subprocess",
                    "import urllib.request",
                    "from flask import Flask",
                    "",
                    "app = Flask(__name__)",
                    "",
                    "@app.route('/health')",
                    "def health():",
                    "    try:",
                    "        urllib.request.urlopen(os.environ['UPSTREAM_URL'])",
                    "    except Exception:",
                    "        pass",
                    "    subprocess.run(['echo', 'ok'])",
                    "    return 'ok'",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.repo / "tests" / "test_app.py").write_text(
            "def test_health():\n    assert True\n",
            encoding="utf-8",
        )
        self.run_command(["git", "add", "."])
        self.run_command(["git", "commit", "-m", "initial"])

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

    def test_maps_flow_surfaces_and_risk_signals(self) -> None:
        result = self.run_command(["python3", str(SCRIPT), str(self.repo), "--pretty"])
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["probe"], "flow")
        self.assertEqual(payload["summary"]["git_commits_scanned"], 1)
        self.assertIn("pyproject.toml", payload["inventory"]["manifests"])
        self.assertIn(".github/workflows/ci.yml", payload["inventory"]["ci"])
        self.assertIn("tests/test_app.py", payload["inventory"]["tests"])
        self.assertNotIn(".pytest_cache/README.md", payload["inventory"]["docs"])
        self.assertNotIn("reports/old.md", payload["inventory"]["docs"])
        self.assertNotIn(
            "vendor-copy/src/copied.py",
            {item["path"] for item in payload["external_boundaries"]},
        )
        candidate_paths = {
            item["path"]
            for category in ("entry_points", "external_boundaries", "risk_signals")
            for item in payload[category]
        }
        self.assertNotIn("docs/example.md", candidate_paths)
        self.assertNotIn("evals/evals.json", candidate_paths)

        entry_kinds = {item["kind"] for item in payload["entry_points"]}
        self.assertIn("http_route", entry_kinds)

        boundary_kinds = {item["kind"] for item in payload["external_boundaries"]}
        self.assertTrue({"environment", "network", "process"}.issubset(boundary_kinds))

        risk_kinds = {item["kind"] for item in payload["risk_signals"]}
        self.assertIn("broad_exception", risk_kinds)
        self.assertIn("swallowed_exception", risk_kinds)
        self.assertTrue(
            all(
                item["source_kind"] == "source"
                for category in ("entry_points", "external_boundaries", "risk_signals")
                for item in payload[category]
                if item["path"] == "src/app.py"
            )
        )

        churn = {item["path"]: item["git_change_count"] for item in payload["git_hotspots"]}
        self.assertEqual(churn["src/app.py"], 1)

    def test_caps_candidate_lists_and_reports_total_match_counts(self) -> None:
        noisy = self.repo / "src" / "noisy.py"
        noisy.write_text(
            "\n".join("time.sleep(1)" for _ in range(20)),
            encoding="utf-8",
        )

        result = self.run_command(
            [
                "python3",
                str(SCRIPT),
                str(self.repo),
                "--no-git",
                "--max-matches-per-category",
                "3",
            ]
        )
        payload = json.loads(result.stdout)

        self.assertLessEqual(len(payload["risk_signals"]), 3)
        self.assertGreaterEqual(payload["summary"]["match_counts"]["risk_signals"], 20)
        self.assertTrue(payload["summary"]["matches_truncated"]["risk_signals"])


if __name__ == "__main__":
    unittest.main()
