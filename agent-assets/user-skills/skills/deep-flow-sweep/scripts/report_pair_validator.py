#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ID_RE = re.compile(r"\b(?:DFS-[A-Z0-9-]+|TP-\d+)\b")


def extract_ids(path: Path) -> set[str]:
    return set(ID_RE.findall(path.read_text(encoding="utf-8", errors="ignore")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that a deep-flow-sweep Markdown report and HTML review surface use the same structured finding/task IDs."
    )
    parser.add_argument("markdown", type=Path)
    parser.add_argument("html", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = [path for path in (args.markdown, args.html) if not path.is_file()]
    if missing:
        for path in missing:
            print(f"ERROR: missing file: {path}")
        return 2

    markdown_ids = extract_ids(args.markdown)
    html_ids = extract_ids(args.html)
    missing_in_html = sorted(markdown_ids - html_ids)
    extra_in_html = sorted(html_ids - markdown_ids)

    if missing_in_html or extra_in_html:
        if missing_in_html:
            print("ERROR: IDs missing from HTML: " + ", ".join(missing_in_html))
        if extra_in_html:
            print("ERROR: IDs present only in HTML: " + ", ".join(extra_in_html))
        return 1

    print(f"PASS: {len(markdown_ids)} structured IDs match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
