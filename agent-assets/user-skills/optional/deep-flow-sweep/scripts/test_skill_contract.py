#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
EVALS = json.loads((SKILL_DIR / "evals" / "evals.json").read_text(encoding="utf-8"))
PLAYBOOKS = {
    "balanced": SKILL_DIR / "references" / "profile-balanced.md",
    "main-flow": SKILL_DIR / "references" / "profile-main-flow.md",
    "reliability": SKILL_DIR / "references" / "profile-reliability.md",
    "performance": SKILL_DIR / "references" / "profile-performance.md",
    "security": SKILL_DIR / "references" / "profile-security.md",
    "observability": SKILL_DIR / "references" / "profile-observability.md",
    "test-effectiveness": SKILL_DIR / "references" / "profile-test-effectiveness.md",
    "project-governance": SKILL_DIR / "references" / "profile-project-governance.md",
}
DECISION_MODEL = SKILL_DIR / "references" / "evidence-decision-model.md"
REQUIRED_PLAYBOOK_SECTIONS = {
    "## Objective",
    "## Required Analysis Model",
    "## Mandatory Questions",
    "## Evidence Ladder",
    "## Method Selection",
    "## Severity Calibration",
    "## Completion Gate",
    "## Report Contract",
    "## Anti-Patterns",
}


class DeepFlowSweepContractTest(unittest.TestCase):
    def test_focus_profiles_are_explicit_and_composable(self) -> None:
        required_profiles = {
            "balanced",
            "main-flow",
            "reliability",
            "performance",
            "security",
            "observability",
            "test-effectiveness",
            "project-governance",
            "requirement-conformance",
        }
        lower = SKILL_TEXT.lower()

        self.assertIn("focus profiles", lower)
        for profile in required_profiles:
            self.assertIn(f"`{profile}`", lower)
        self.assertIn("focus does not remove baseline coverage", lower)

    def test_project_archetype_routing_uses_priors_not_conclusions(self) -> None:
        lower = SKILL_TEXT.lower()

        self.assertIn("project archetype routing", lower)
        self.assertIn("archetype signals are priors, not conclusions", lower)
        self.assertIn("project risk profile", lower)
        self.assertIn("applicability disposition", lower)
        for disposition in {
            "applicable",
            "possibly applicable",
            "not applicable",
            "deferred",
            "untriaged",
        }:
            self.assertIn(disposition, lower)
        for archetype in {
            "web / saas / api",
            "mobile / android / device",
            "agent / tooling / automation",
            "library / framework",
            "public release / split repository",
        }:
            self.assertIn(archetype, lower)

    def test_common_profiles_have_executable_playbooks(self) -> None:
        for profile, path in PLAYBOOKS.items():
            self.assertTrue(path.is_file(), f"missing playbook for {profile}")
            text = path.read_text(encoding="utf-8")
            for section in REQUIRED_PLAYBOOK_SECTIONS:
                self.assertIn(section, text, f"{profile} missing {section}")

    def test_playbooks_define_profile_specific_evidence(self) -> None:
        expected_terms = {
            "balanced": {
                "coverage matrix",
                "dimension trigger",
                "coverage debt",
                "critical flow",
            },
            "main-flow": {
                "goal-to-outcome",
                "flow graph",
                "success oracle",
                "broken chain",
            },
            "reliability": {
                "state model",
                "invariant",
                "fault injection",
                "recovery",
            },
            "performance": {
                "metric contract",
                "baseline",
                "warm-up",
                "tail latency",
                "profiler",
            },
            "test-effectiveness": {
                "risk-to-test matrix",
                "test topology map",
                "assertion quality",
                "mutation",
                "flaky",
                "coverage provenance",
                "prove-it",
                "lowest test level",
                "internal mocks",
                "shared mutable state",
            },
            "security": {
                "trust boundary",
                "exploitation scenario",
                "authentication",
                "authorization",
                "ai / llm",
                "proof of exploitability",
            },
            "observability": {
                "symptom",
                "cause",
                "recovery",
                "correlation",
                "sensitive data",
                "diagnostic drill",
            },
            "project-governance": {
                "governance matrix",
                "ci/release",
                "documentation drift",
                "artifact provenance",
                "agent parity",
            },
        }
        for profile, terms in expected_terms.items():
            lower = PLAYBOOKS[profile].read_text(encoding="utf-8").lower()
            for term in terms:
                self.assertIn(term, lower, f"{profile} missing term: {term}")

    def test_skill_routes_common_profiles_to_their_playbooks(self) -> None:
        lower = SKILL_TEXT.lower()
        for profile, path in PLAYBOOKS.items():
            self.assertIn(profile, lower)
            self.assertIn(f"`references/{path.name}`", lower)

    def test_analysis_only_mode_requires_new_authorization_to_edit(self) -> None:
        lower = SKILL_TEXT.lower()

        self.assertIn("analysis-only mode latch", lower)
        self.assertIn("new explicit user authorization", lower)
        self.assertIn("must not modify product source", lower)
        self.assertIn("analysis artifact root", lower)

    def test_severity_requires_direct_evidence(self) -> None:
        lower = SKILL_TEXT.lower()

        self.assertIn("severity and evidence gate", lower)
        self.assertIn("past severity is not inherited automatically", lower)
        self.assertIn("p0", lower)
        self.assertIn("p1", lower)
        self.assertIn("direct evidence", lower)

    def test_concurrent_artifacts_have_provenance_and_freshness(self) -> None:
        lower = SKILL_TEXT.lower()

        self.assertIn("run manifest", lower)
        for field in {
            "run_id",
            "git_sha",
            "dirty_state",
            "scope",
            "source_agent",
            "started_at",
            "finished_at",
            "artifact_path",
        }:
            self.assertIn(f"`{field}`", lower)
        self.assertIn("freshness", lower)

    def test_behavioral_evals_cover_the_new_guards(self) -> None:
        prompts = "\n".join(item["prompt"] for item in EVALS["evals"])

        self.assertIn("侧重性能", prompts)
        self.assertIn("默认模式", prompts)
        self.assertIn("功能链路", prompts)
        self.assertIn("侧重稳定性", prompts)
        self.assertIn("侧重测试覆盖", prompts)
        self.assertIn("项目治理", prompts)
        self.assertIn("只做分析", prompts)
        self.assertIn("历史报告", prompts)
        self.assertIn("并发 agent", prompts)
        self.assertIn("侧重安全", prompts)
        self.assertIn("侧重可观测性", prompts)
        self.assertIn("意图恢复", prompts)
        self.assertIn("测试拓扑", prompts)

    def test_budget_envelopes_are_observable_not_token_quotas(self) -> None:
        lower = SKILL_TEXT.lower()

        self.assertNotIn("50m+", lower)
        self.assertNotIn("1m-3m", lower)
        self.assertIn("evidence waves", lower)
        self.assertIn("stop condition", lower)

    def test_performance_requires_a_regression_guard(self) -> None:
        lower = PLAYBOOKS["performance"].read_text(encoding="utf-8").lower()

        self.assertIn("remeasure", lower)
        self.assertIn("regression guard", lower)

    def test_governance_routes_specialist_evidence_instead_of_duplicating_it(self) -> None:
        lower = PLAYBOOKS["project-governance"].read_text(encoding="utf-8").lower()

        self.assertIn("profile-security.md", lower)
        self.assertIn("profile-observability.md", lower)
        self.assertIn("profile-test-effectiveness.md", lower)
        self.assertNotIn("logging contract |", lower)
        self.assertNotIn("input boundary |", lower)

    def test_intent_recovery_and_finding_decisions_have_an_executable_model(self) -> None:
        self.assertTrue(DECISION_MODEL.is_file())
        lower = DECISION_MODEL.read_text(encoding="utf-8").lower()

        for term in {
            "intent recovery chain",
            "requirement or task source",
            "test oracle",
            "implementation",
            "runtime evidence",
            "severity",
            "confidence",
            "disposition",
            "block",
            "package",
            "investigate",
            "consider",
            "info",
            "drop",
        }:
            self.assertIn(term, lower)

        skill_lower = SKILL_TEXT.lower()
        self.assertIn("`references/evidence-decision-model.md`", skill_lower)
        self.assertIn("intent recovery", skill_lower)
        self.assertIn("severity, confidence, and disposition", skill_lower)


if __name__ == "__main__":
    unittest.main()
