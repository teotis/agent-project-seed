# html-response Script Dependencies

## External Dependencies

The scripts in `scripts/` may require external tools and Python packages beyond the standard library.

### System-Level Dependencies

| Tool | Script | Purpose | Install (macOS) |
|---|---|---|---|
| LibreOffice (`soffice`) | `doc_to_pdf.py` | Convert DOCX/DOC/PPT/PPTX to PDF | `brew install --cask libreoffice` |
| `pdftoppm` (poppler-utils) | `pdf_to_pages.py` (fallback) | Render PDF pages as images | `brew install poppler` |

### Python Package Dependencies

| Package | Script | Required | Install |
|---|---|---|---|
| `pypdfium2` | `pdf_to_pages.py` | Optional (preferred) | `pip install pypdfium2` |

### stdlib-Only Scripts (no external dependencies)

- `validate_html.py` — structural and safety checks
- `open_browser.py` — cross-platform browser launcher

## Fallback Behavior

If a dependency is missing, the script exits with a descriptive error message. The agent should:
1. Report the missing dependency
2. Offer to install it (if allowed by the execution environment)
3. Fall back to an alternative approach (e.g., link to the file instead of rendering pages)

## Platform Notes

- **macOS**: LibreOffice is typically installed via Homebrew or direct download. `poppler` provides `pdftoppm`.
- **Linux**: `apt install libreoffice-core poppler-utils` or equivalent.
- **Windows**: LibreOffice installer from libreoffice.org; poppler via MSYS2 or WSL.
