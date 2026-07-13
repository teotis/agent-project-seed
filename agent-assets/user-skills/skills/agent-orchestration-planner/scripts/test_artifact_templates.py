#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "references" / "artifact_templates.md"


class ArtifactTemplateTest(unittest.TestCase):
    def test_script_output_requires_primary_and_cross_runner_blocks(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")

        required = [
            "When Codex is primary, include a separate Claude Code alternative block",
            "When Claude Code is primary, include a separate Codex App / Codex runner alternative block",
            "**Primary script path (Codex App / Codex runner)**",
            "**Alternative runner (Claude Code)**",
            "**Primary script path (Claude Code)**",
            "**Alternative runner (Codex App / Codex runner)**",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
