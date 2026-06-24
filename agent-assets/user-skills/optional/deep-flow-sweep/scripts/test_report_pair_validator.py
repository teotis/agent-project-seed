#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("report_pair_validator.py")


class DeepFlowReportPairValidatorTest(unittest.TestCase):
    def test_accepts_matching_markdown_and_html_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dfs-report-pair-") as tmp:
            root = Path(tmp)
            md = root / "report.md"
            html = root / "report.html"
            md.write_text(
                "\n".join(
                    [
                        "### DFS-SKILL-01 [P1] Finding",
                        "### DFS-SKILL-02 [P2] Finding",
                        "### TP-01 [P1] Task",
                    ]
                ),
                encoding="utf-8",
            )
            html.write_text(
                "<html><body>DFS-SKILL-01 DFS-SKILL-02 TP-01</body></html>",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(md), str(html)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_rejects_missing_html_finding_id(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dfs-report-pair-") as tmp:
            root = Path(tmp)
            md = root / "report.md"
            html = root / "report.html"
            md.write_text(
                "\n".join(
                    [
                        "### DFS-SKILL-01 [P1] Finding",
                        "### DFS-SKILL-02 [P2] Finding",
                        "### TP-01 [P1] Task",
                    ]
                ),
                encoding="utf-8",
            )
            html.write_text(
                "<html><body>DFS-SKILL-01 TP-01</body></html>",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(md), str(html)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DFS-SKILL-02", result.stdout)


if __name__ == "__main__":
    unittest.main()
