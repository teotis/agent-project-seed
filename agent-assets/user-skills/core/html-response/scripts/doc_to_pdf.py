#!/usr/bin/env python3
"""DOCX/DOC/PPT/PPTX -> PDF (via LibreOffice soffice).

Usage:
    python3 doc_to_pdf.py <input_path> [--output <output.pdf>]

Requires LibreOffice soffice. Errors out if not available.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_soffice() -> str:
    """Find the soffice executable."""
    # Check PATH first
    soffice = shutil.which("soffice")
    if soffice:
        return soffice

    # macOS default install paths
    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for p in mac_paths:
        if Path(p).exists():
            return p

    return ""


def convert_to_pdf(input_path: str, output_dir: str) -> str:
    """Convert file to PDF using soffice, return the resulting PDF path."""
    soffice = find_soffice()
    if not soffice:
        print("Error: LibreOffice soffice not found. Please install LibreOffice.", file=sys.stderr)
        sys.exit(1)

    # Use isolated profile to avoid lock conflicts
    with tempfile.TemporaryDirectory() as profile_dir:
        cmd = [
            soffice,
            "-env:UserInstallation=file://" + profile_dir,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"soffice conversion failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

    # Locate the output PDF
    input_stem = Path(input_path).stem
    pdf_path = Path(output_dir) / f"{input_stem}.pdf"
    if not pdf_path.exists():
        # Try to find any generated PDF
        pdfs = list(Path(output_dir).glob("*.pdf"))
        if pdfs:
            pdf_path = pdfs[0]
        else:
            print("Error: soffice did not produce a PDF file", file=sys.stderr)
            sys.exit(1)

    return str(pdf_path)


def main():
    parser = argparse.ArgumentParser(description="DOCX/DOC/PPT/PPTX -> PDF")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("--output", "-o", help="Output PDF path (default: same directory as input)")
    args = parser.parse_args()

    input_path = args.input_path
    if not Path(input_path).exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = str(Path(args.output).parent) if args.output else str(Path(input_path).parent)
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = convert_to_pdf(input_path, output_dir)

    if args.output and pdf_path != args.output:
        shutil.move(pdf_path, args.output)
        pdf_path = args.output

    print(pdf_path)


if __name__ == "__main__":
    main()
