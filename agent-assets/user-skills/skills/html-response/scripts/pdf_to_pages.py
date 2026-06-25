#!/usr/bin/env python3
"""PDF -> page PNG base64 data URL JSON.

Usage:
    python3 pdf_to_pages.py <pdf_path> [--dpi 144] [--output <output.json>]

Output JSON format:
    [{"page": 1, "data_url": "data:image/png;base64,..."}, ...]

Prefers pypdfium2, falls back to pdftoppm CLI.
"""
import argparse
import base64
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def render_with_pypdfium2(pdf_path: str, dpi: int) -> list[dict]:
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(pdf_path)
    scale = dpi / 72.0
    pages = []

    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        pages.append({"page": i + 1, "data_url": f"data:image/png;base64,{b64}"})

    doc.close()
    return pages


def render_with_pdftoppm(pdf_path: str, dpi: int) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = Path(tmpdir) / "page"
        result = subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), pdf_path, str(prefix)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {result.stderr}")

        pages = []
        for img_path in sorted(Path(tmpdir).glob("page-*.png")):
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            # Extract page number from filename like "page-01.png"
            num = int(img_path.stem.split("-")[-1])
            pages.append({"page": num, "data_url": f"data:image/png;base64,{b64}"})

        return pages


def main():
    parser = argparse.ArgumentParser(description="PDF -> page PNG data URL JSON")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--dpi", type=int, default=144, help="Render DPI (default 144)")
    parser.add_argument("--output", "-o", help="Output JSON file path (default stdout)")
    args = parser.parse_args()

    pdf_path = args.pdf_path
    if not Path(pdf_path).exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        pages = render_with_pypdfium2(pdf_path, args.dpi)
    except ImportError:
        print("pypdfium2 not available, falling back to pdftoppm...", file=sys.stderr)
        try:
            pages = render_with_pdftoppm(pdf_path, args.dpi)
        except (RuntimeError, FileNotFoundError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    output_json = json.dumps(pages, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"Output {len(pages)} pages to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
