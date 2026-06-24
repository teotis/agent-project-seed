#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_html.py")


def run_validator(html: str, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "report.html"
        path.write_text(html, encoding="utf-8")
        return subprocess.run(
            ["python3", str(SCRIPT), str(path), *args],
            check=False,
            capture_output=True,
            text=True,
        )


BASE_HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
  <title>Architecture explainer</title>
  <style>@media (prefers-reduced-motion: reduce) { * { animation: none; } }</style>
</head>
"""


class ComprehensionProfileTest(unittest.TestCase):
    def test_rejects_thesis_below_main_content(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <nav class="toc" data-comprehension-role="section-index">
            <a href="#overview">Overview</a>
            <a href="#model">Model</a>
            <a href="#evidence">Evidence</a>
          </nav>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="concept-map" data-source-ref="claim-1" data-visual-question="How do the ideas relate?" data-visual-relationships="A enables B; B constrains C">
                <svg role="img"><title>Concept map</title><desc>Three related ideas.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
            </section>
            <section id="model" data-comprehension-role="thesis" data-source-ref="claim-1">
              <h1>Core idea appears too late</h1>
            </section>
            <section id="evidence">
              <script type="application/json" id="coverage-ledger">{"claims":["claim-1"]}</script>
              <details data-comprehension-role="evidence-appendix">
                <summary>Evidence appendix</summary><p>Source details.</p>
              </details>
            </section>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "comprehension")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("thesis is not in the opening viewport", result.stdout)

    def test_rejects_thesis_without_source_reference(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <header data-comprehension-role="thesis"><h1>Concept explainer</h1></header>
          <nav class="toc" data-comprehension-role="section-index">
            <a href="#overview">Overview</a>
            <a href="#model">Model</a>
            <a href="#evidence">Evidence</a>
          </nav>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="concept-map" data-source-ref="claim-1" data-visual-question="How do the ideas relate?" data-visual-relationships="A enables B; B constrains C">
                <svg role="img"><title>Concept map</title><desc>Three related ideas.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
            </section>
            <section id="model"><h2>Model</h2></section>
            <section id="evidence">
              <script type="application/json" id="coverage-ledger">{"claims":["claim-1"]}</script>
              <details data-comprehension-role="evidence-appendix">
                <summary>Evidence appendix</summary><p>Source details.</p>
              </details>
            </section>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "comprehension")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("thesis lacks source reference", result.stdout)

    def test_rejects_visual_without_reader_question(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <header data-comprehension-role="thesis" data-source-ref="claim-1"><h1>Concept explainer</h1></header>
          <nav class="toc" data-comprehension-role="section-index">
            <a href="#overview">Overview</a>
            <a href="#model">Model</a>
            <a href="#evidence">Evidence</a>
          </nav>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="concept-map" data-source-ref="claim-1" data-visual-relationships="A enables B; B constrains C">
                <svg role="img"><title>Concept map</title><desc>Three related ideas.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
            </section>
            <section id="model"><h2>Model</h2></section>
            <section id="evidence">
              <script type="application/json" id="coverage-ledger">{"claims":["claim-1"]}</script>
              <details data-comprehension-role="evidence-appendix">
                <summary>Evidence appendix</summary><p>Source details.</p>
              </details>
            </section>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "comprehension")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("visual lacks reader question", result.stdout)

    def test_rejects_complex_interaction_without_static_fallback(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <header data-comprehension-role="thesis" data-source-ref="claim-1"><h1>Concept explainer</h1></header>
          <nav class="toc" data-comprehension-role="section-index">
            <a href="#overview">Overview</a>
            <a href="#model">Model</a>
            <a href="#evidence">Evidence</a>
          </nav>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="concept-map" data-source-ref="claim-1" data-visual-question="How do the ideas relate?" data-visual-relationships="A enables B; B constrains C">
                <svg role="img"><title>Concept map</title><desc>Three related ideas.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
              <section data-interaction="lens-switcher">
                <button>Runtime lens</button>
              </section>
            </section>
            <section id="model"><h2>Model</h2></section>
            <section id="evidence">
              <script type="application/json" id="coverage-ledger">{"claims":["claim-1"]}</script>
              <details data-comprehension-role="evidence-appendix">
                <summary>Evidence appendix</summary><p>Source details.</p>
              </details>
            </section>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "comprehension")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complex interaction lacks static fallback", result.stdout)

    def test_rejects_comprehension_page_without_section_index(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <header data-comprehension-role="thesis"><h1>Concept explainer</h1></header>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="concept-map" data-source-ref="claim-1">
                <svg role="img"><title>Concept map</title><desc>Three related ideas.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
            </section>
            <script type="application/json" id="coverage-ledger">
              {"claims":["claim-1"]}
            </script>
            <details data-comprehension-role="evidence-appendix">
              <summary>Evidence appendix</summary><p>Source details.</p>
            </details>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "comprehension")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing section index", result.stdout)

    def test_rejects_cardified_article_without_semantic_visuals(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <main id="main">
            <section class="card"><h1>Summary</h1><p>Layered architecture.</p></section>
            <section class="card"><h2>Layer one</h2><p>Details.</p></section>
            <div class="feedback-controls"><textarea></textarea></div>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "architecture")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing semantic overview visual", result.stdout)
        self.assertIn("missing coverage ledger", result.stdout)

    def test_accepts_traceable_visual_explainer(self) -> None:
        html = BASE_HEAD + """
        <body data-document-id="architecture-v2">
          <a class="skip-link" href="#main">Skip</a>
          <header data-comprehension-role="thesis" data-source-ref="claim-1"><h1>Architecture explainer</h1></header>
          <nav class="lens-nav" data-comprehension-role="section-index">
            <a href="#overview">Overview</a>
            <a href="#runtime">Runtime path</a>
            <a href="#comparison">Feature comparison</a>
            <a href="#evidence">Evidence</a>
          </nav>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="system-map" data-source-ref="claim-1" data-visual-question="Which components own the important relationships?" data-visual-relationships="UI calls API; API persists state">
                <svg role="img"><title>System map</title><desc>Labeled module relationships.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
            </section>
            <section data-visual-purpose="dynamic-flow" data-source-ref="flow-1" data-visual-question="What happens during the representative request?">
              <h2 id="runtime">Runtime path</h2>
            </section>
            <section data-visual-purpose="comparison-matrix" data-source-ref="comparison-1" data-visual-question="How do the important variants differ?">
              <h2 id="comparison">Feature comparison</h2>
            </section>
            <section id="evidence">
            <script type="application/json" id="coverage-ledger">
              {"claims":["claim-1"],"relationships":["flow-1"]}
            </script>
            <details data-comprehension-role="evidence-appendix">
              <summary>Evidence appendix</summary><p>Source details.</p>
            </details>
            </section>
            <details class="review-drawer"><summary>Review this report</summary></details>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "architecture")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_general_comprehension_does_not_force_runtime_or_comparison(self) -> None:
        html = BASE_HEAD + """
        <body>
          <a class="skip-link" href="#main">Skip</a>
          <header data-comprehension-role="thesis" data-source-ref="claim-1"><h1>Concept explainer</h1></header>
          <nav class="toc" data-comprehension-role="section-index">
            <a href="#overview">Overview</a>
            <a href="#model">Model</a>
            <a href="#evidence">Evidence</a>
          </nav>
          <main id="main">
            <section id="overview">
              <figure data-visual-purpose="concept-map" data-source-ref="claim-1" data-visual-question="How do the ideas relate?" data-visual-relationships="A enables B; B constrains C">
                <svg role="img"><title>Concept map</title><desc>Three related ideas.</desc></svg>
                <figcaption>Overview</figcaption>
              </figure>
            </section>
            <section id="model"><h2>Model</h2></section>
            <section id="evidence">
            <script type="application/json" id="coverage-ledger">
              {"claims":["claim-1"]}
            </script>
            <details data-comprehension-role="evidence-appendix">
              <summary>Evidence appendix</summary><p>Source details.</p>
            </details>
            </section>
          </main>
        </body></html>
        """
        result = run_validator(html, "--profile", "comprehension")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
