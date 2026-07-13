#!/usr/bin/env python3
"""Lightweight lint checks for HTML produced by Adaptive HTML Response.

Usage:
    python3 validate_html.py <html_path>

This is a fast structural/safety check, not a conformance or security certification.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

REQUIRED_PATTERNS = {
    "doctype": r"<!doctype\s+html",
    "language": r"<html\b[^>]*\blang\s*=",
    "charset": r"<meta\b[^>]*charset\s*=",
    "viewport": r"<meta\b[^>]*name\s*=\s*[\"']viewport[\"']",
    "title": r"<title>\s*[^<\s][^<]*</title>",
    "main landmark": r"<main\b",
}
WARNING_PATTERNS = {
    "external dependency": r"(?:src|href)\s*=\s*[\"']https?://",
    "inline event handler": r"\son[a-z]+\s*=",
    "javascript URL": r"javascript\s*:",
    "eval usage": r"\beval\s*\(",
    "new Function usage": r"\bnew\s+Function\s*\(",
}
VISUAL_OPEN_TAG_PATTERN = re.compile(
    r'<(?P<tag>[a-z][\w:-]*)\b(?P<attrs>[^>]*)\bdata-visual-purpose\s*=\s*'
    r'["\'](?P<purpose>[^"\']+)["\'][^>]*>',
    flags=re.I | re.S,
)
RELATIONSHIP_VISUAL_PURPOSES = {
    "system-map",
    "concept-map",
    "architecture-map",
    "dependency-map",
}


def text_content(html_fragment: str) -> str:
    without_scripts = re.sub(
        r"<(?:script|style)\b.*?</(?:script|style)>",
        " ",
        html_fragment,
        flags=re.I | re.S,
    )
    without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
    return " ".join(unescape(without_tags).split())


def normalized_phrase(value: str) -> str:
    return re.sub(r"\W+", "", value, flags=re.I).lower()


def iter_coverage_items(value: object):
    if isinstance(value, dict):
        if "disposition" in value or "importance" in value or "id" in value:
            yield value
        for child in value.values():
            yield from iter_coverage_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_coverage_items(child)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_path")
    parser.add_argument(
        "--profile",
        choices=("base", "comprehension", "architecture"),
        default="base",
        help="Apply additional checks for a comprehension-first explanation.",
    )
    args = parser.parse_args()
    path = Path(args.html_path)
    if not path.exists():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()

    errors: list[str] = []
    warnings: list[str] = []
    for label, pattern in REQUIRED_PATTERNS.items():
        if not re.search(pattern, lower, flags=re.I | re.S):
            errors.append(f"missing {label}")
    if "content-security-policy" not in lower:
        warnings.append("missing Content Security Policy meta tag")
    if "prefers-reduced-motion" not in lower:
        warnings.append("no reduced-motion handling detected")
    if "skip-link" not in lower and "skip to" not in lower:
        warnings.append("no skip link detected")
    for label, pattern in WARNING_PATTERNS.items():
        if re.search(pattern, text, flags=re.I | re.S):
            warnings.append(f"detected {label}; review intent and safety")

    if args.profile in {"comprehension", "architecture"}:
        comprehension_patterns = {
            "thesis": r'data-comprehension-role\s*=\s*["\']thesis["\']',
            "section index": (
                r'<nav\b[^>]*(?:data-comprehension-role\s*=\s*["\']section-index["\']'
                r'|class\s*=\s*["\'][^"\']*(?:toc|lens-nav)[^"\']*["\'])'
            ),
            "semantic overview visual": (
                r'data-visual-purpose\s*=\s*["\']'
                r'(?:system-map|concept-map|architecture-map|dependency-map)["\']'
            ),
            "coverage ledger": r'id\s*=\s*["\']coverage-ledger["\']',
            "evidence appendix": (
                r'data-comprehension-role\s*=\s*["\']evidence-appendix["\']'
            ),
            "source reference": r'data-source-ref\s*=\s*["\'][^"\']+["\']',
        }
        for label, pattern in comprehension_patterns.items():
            if not re.search(pattern, text, flags=re.I | re.S):
                errors.append(f"missing {label}")

        thesis_match = re.search(
            r'<[a-z][\w:-]*\b[^>]*data-comprehension-role\s*=\s*["\']thesis["\'][^>]*>',
            text,
            flags=re.I | re.S,
        )
        main_match = re.search(r"<main\b", text, flags=re.I)
        if thesis_match and main_match and thesis_match.start() > main_match.start():
            errors.append("thesis is not in the opening viewport")
        if thesis_match and not re.search(
            r'data-source-ref\s*=\s*["\'][^"\']+["\']',
            thesis_match.group(0),
            flags=re.I,
        ):
            errors.append("thesis lacks source reference")
        if thesis_match:
            thesis_tag = re.match(r"<([a-z][\w:-]*)\b", thesis_match.group(0), flags=re.I)
            thesis_text = ""
            if thesis_tag:
                thesis_block = re.search(
                    re.escape(thesis_match.group(0)) + r"(.*?)</" + thesis_tag.group(1) + r"\s*>",
                    text,
                    flags=re.I | re.S,
                )
                if thesis_block:
                    thesis_text = text_content(thesis_block.group(1))
            title_match = re.search(r"<title\b[^>]*>(.*?)</title>", text, flags=re.I | re.S)
            title_text = text_content(title_match.group(1)) if title_match else ""
            thesis_words = re.findall(r"[\w'-]+", thesis_text)
            looks_like_title = (
                title_text
                and normalized_phrase(thesis_text)
                and normalized_phrase(thesis_text) == normalized_phrase(title_text)
            )
            if looks_like_title or (len(thesis_text) < 60 and len(thesis_words) < 8):
                errors.append("thesis looks decorative instead of a conclusion")

        ledger_match = re.search(
            r'<script\b[^>]*id\s*=\s*["\']coverage-ledger["\'][^>]*>(.*?)</script>',
            text,
            flags=re.I | re.S,
        )
        if ledger_match:
            ledger_text = text_content(ledger_match.group(1))
            try:
                ledger = json.loads(ledger_text)
            except json.JSONDecodeError as exc:
                errors.append(f"coverage ledger is not valid JSON: {exc.msg}")
            else:
                for item in iter_coverage_items(ledger):
                    item_id = str(item.get("id") or "<unknown>")
                    disposition = str(item.get("disposition") or "").strip().lower()
                    importance = str(item.get("importance") or "").strip().lower()
                    if not disposition:
                        errors.append(f"coverage item lacks disposition: {item_id}")
                    if disposition == "omitted" and not str(item.get("reason") or "").strip():
                        errors.append(f"omitted coverage item lacks reason: {item_id}")
                    if importance == "primary" and disposition == "omitted":
                        errors.append(f"primary coverage item is omitted: {item_id}")

        index_match = re.search(
            r'<nav\b[^>]*(?:data-comprehension-role\s*=\s*["\']section-index["\']'
            r'|class\s*=\s*["\'][^"\']*(?:toc|lens-nav)[^"\']*["\'])[^>]*>'
            r'(.*?)</nav>',
            text,
            flags=re.I | re.S,
        )
        if index_match:
            targets = re.findall(r'href\s*=\s*["\']#([^"\']+)["\']', index_match.group(1), flags=re.I)
            if len(set(targets)) < 3:
                errors.append("section index has fewer than three anchor links")
            for target in set(targets):
                if not re.search(r'id\s*=\s*["\']' + re.escape(target) + r'["\']', text, flags=re.I):
                    errors.append(f"section index target not found: {target}")

        for visual in VISUAL_OPEN_TAG_PATTERN.finditer(text):
            visual_tag = visual.group(0)
            purpose = visual.group("purpose").strip().lower()
            if not re.search(r'data-visual-question\s*=\s*["\'][^"\']+["\']', visual_tag, flags=re.I):
                errors.append(f"visual lacks reader question: {purpose}")
            if purpose in RELATIONSHIP_VISUAL_PURPOSES and not re.search(
                r'data-visual-relationships\s*=\s*["\'][^"\']+["\']',
                visual_tag,
                flags=re.I,
            ):
                errors.append(f"relationship visual lacks relationship explanation: {purpose}")

        svg_blocks = re.findall(r"<svg\b.*?</svg>", text, flags=re.I | re.S)
        if svg_blocks and not all(
            re.search(r"<title\b", block, flags=re.I)
            and re.search(r"<desc\b", block, flags=re.I)
            for block in svg_blocks
        ):
            errors.append("inline SVG missing title or description")

        visible_feedback = re.search(
            r'<(?:section|aside|div)\b[^>]*class\s*=\s*["\'][^"\']*'
            r'(?:feedback-controls|review-panel)[^"\']*["\']',
            text,
            flags=re.I | re.S,
        )
        collapsed_review = re.search(
            r'<details\b[^>]*class\s*=\s*["\'][^"\']*review-drawer',
            text,
            flags=re.I | re.S,
        )
        if visible_feedback and not collapsed_review:
            errors.append("feedback controls are primary instead of collapsed")

        has_complex_interaction = re.search(r'data-interaction\s*=\s*["\'][^"\']+["\']', text, flags=re.I)
        has_static_fallback = (
            re.search(r'data-static-fallback\s*=\s*["\'][^"\']+["\']', text, flags=re.I)
            or re.search(r'class\s*=\s*["\'][^"\']*static-fallback[^"\']*["\']', text, flags=re.I)
            or re.search(r"<noscript\b", text, flags=re.I)
        )
        if has_complex_interaction and not has_static_fallback:
            errors.append("complex interaction lacks static fallback")

    if args.profile == "architecture":
        architecture_patterns = {
            "dynamic flow": r'data-visual-purpose\s*=\s*["\']dynamic-flow["\']',
            "comparison matrix": (
                r'data-visual-purpose\s*=\s*["\']'
                r'(?:comparison-matrix|small-multiples)["\']'
            ),
        }
        for label, pattern in architecture_patterns.items():
            if not re.search(pattern, text, flags=re.I | re.S):
                errors.append(f"missing {label}")

    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        return 1
    print("PASS: required structural checks found")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
