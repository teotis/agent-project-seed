#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import engineering_memory


class EngineeringMemoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="engineering-memory-")
        self.memory_root = Path(self.tmp.name)
        self.project_path = "/work/example-app"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_default_memory_root_is_project_local(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            root = engineering_memory.resolve_memory_root(None, self.project_path)

        self.assertEqual(root, Path(self.project_path) / ".memory" / "engineering")

    def test_explicit_memory_root_overrides_environment_and_project_default(self) -> None:
        with patch.dict("os.environ", {"ENGINEERING_MEMORY_ROOT": "/env/memory"}, clear=True):
            root = engineering_memory.resolve_memory_root(Path("/explicit/memory"), self.project_path)

        self.assertEqual(root, Path("/explicit/memory"))

    def test_environment_memory_root_overrides_project_default(self) -> None:
        with patch.dict("os.environ", {"ENGINEERING_MEMORY_ROOT": "/env/memory"}, clear=True):
            root = engineering_memory.resolve_memory_root(None, self.project_path)

        self.assertEqual(root, Path("/env/memory"))

    def test_record_appends_artifact_event_with_stable_project_id(self) -> None:
        event = engineering_memory.record_event(
            self.memory_root,
            skill="deep-flow-sweep",
            project_path=self.project_path,
            task="审计主流程",
            summary="发现发布路径缺少隐私门禁。",
            artifacts=["reports/audit.html"],
            key_findings=["公开发布前必须运行 privacy gate"],
            decisions=["公开仓库只同步英文 SKILL.md"],
            user_preferences=["私有报告默认中文"],
            next_actions=["运行 control/project.py check"],
            timestamp="2026-06-17T12:00:00Z",
        )

        events_path = self.memory_root / "artifacts.jsonl"
        lines = events_path.read_text(encoding="utf-8").splitlines()
        stored = json.loads(lines[0])

        self.assertEqual(event["project_id"], "example-app-aceeab15")
        self.assertEqual(stored["skill"], "deep-flow-sweep")
        self.assertEqual(stored["timestamp"], "2026-06-17T12:00:00Z")
        self.assertEqual(stored["artifacts"], ["reports/audit.html"])
        self.assertEqual(stored["decisions"], ["公开仓库只同步英文 SKILL.md"])

    def test_remember_upserts_project_note_without_duplicates(self) -> None:
        first = engineering_memory.remember_note(
            self.memory_root,
            project_path=self.project_path,
            kind="decision",
            text="公开技能必须从 references/public-en.SKILL.md 同步。",
            source="manual",
            timestamp="2026-06-17T12:00:00Z",
        )
        second = engineering_memory.remember_note(
            self.memory_root,
            project_path=self.project_path,
            kind="decision",
            text="公开技能必须从 references/public-en.SKILL.md 同步。",
            source="manual",
            timestamp="2026-06-17T12:05:00Z",
        )

        note_path = self.memory_root / "projects" / "example-app-aceeab15.md"
        text = note_path.read_text(encoding="utf-8")

        self.assertEqual(first["status"], "created")
        self.assertEqual(second["status"], "existing")
        self.assertEqual(text.count("references/public-en.SKILL.md"), 1)
        self.assertIn(
            "references/public-en.SKILL.md 同步。 _(source: manual; recorded: 2026-06-17T12:00:00Z)_\n\n## Findings",
            text,
        )

    def test_recall_project_summary_combines_notes_and_recent_events(self) -> None:
        engineering_memory.remember_note(
            self.memory_root,
            project_path=self.project_path,
            kind="preference",
            text="私有技能交付默认中文主叙述。",
            source="AGENTS.md",
            timestamp="2026-06-17T12:00:00Z",
        )
        engineering_memory.record_event(
            self.memory_root,
            skill="product-sense-refiner",
            project_path=self.project_path,
            task="设计 engineering memory MVP",
            summary="采用 sidecar memory 而不是修改 SKILL.md。",
            artifacts=["docs/engineering-memory.md"],
            timestamp="2026-06-17T12:10:00Z",
        )

        summary = engineering_memory.recall_project(
            self.memory_root,
            project_path=self.project_path,
            limit=3,
        )

        self.assertIn("# Engineering Memory: example-app", summary)
        self.assertIn("私有技能交付默认中文主叙述。", summary)
        self.assertIn("product-sense-refiner", summary)
        self.assertIn("docs/engineering-memory.md", summary)


if __name__ == "__main__":
    unittest.main()
