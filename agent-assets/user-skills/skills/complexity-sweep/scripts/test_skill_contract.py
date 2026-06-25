#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


class ComplexitySweepContractTest(unittest.TestCase):
    def test_project_shape_lens_routes_complexity_without_hardcoding(self) -> None:
        lower = SKILL_TEXT.lower()

        self.assertIn("project shape lens", lower)
        self.assertIn("shape signals are priors, not conclusions", lower)
        self.assertIn("complexity risk profile", lower)
        self.assertIn("low metric complexity does not equal low comprehension cost", lower)
        for shape in {
            "web / saas / api",
            "mobile / android / device",
            "agent / tooling / automation",
            "library / framework",
            "split public/private repository",
        }:
            self.assertIn(shape, lower)


if __name__ == "__main__":
    unittest.main()
