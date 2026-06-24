#!/usr/bin/env python3
"""Cross-platform browser opener.

Usage:
    python3 open_browser.py <html_path>

Supports macOS (open), Linux (xdg-open), Windows (start).
"""
import os
import platform
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 open_browser.py <html_path>", file=sys.stderr)
        sys.exit(1)

    html_path = sys.argv[1]
    if not Path(html_path).exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    abs_path = str(Path(html_path).resolve())
    system = platform.system()

    if system == "Darwin":
        subprocess.Popen(["open", abs_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "Linux":
        subprocess.Popen(["xdg-open", abs_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "Windows":
        os.startfile(abs_path)  # type: ignore[attr-defined]
    else:
        print(f"Unsupported platform: {system}", file=sys.stderr)
        print(f"Please open manually: file://{abs_path}")
        sys.exit(1)

    print(f"Opened in browser: {abs_path}")


if __name__ == "__main__":
    main()
