# Artifact Explanation And Lightweight Review Specification

## 1. Goal

This reference supports visual or formatted deliverables without losing context. Use it inside `html-response` when rendered documents,
slides, images, page layouts, and outputs need explanation, comparison, or lightweight optional comments attached to visible regions.

If the user's primary job is formal page-by-page review, persistent comments, approval status, ratings, or feedback export for follow-up agents, use `reviewable-html-report` mechanics instead. `html-response` may still provide the comprehension layer around the artifact.

## 2. Packaging Profiles

### Single-File Portable

Use when the payload remains practical: small image sets or documents of roughly up to 12 rendered pages / 20 MB embedded data.
Embed preview assets as data URLs and inline CSS/JS.

### Local Review Bundle

Use for larger outputs. Produce:

```text
<topic>_review/
  index.html
  assets/pages/page-0001.png
  assets/pages/page-0002.png
  data/document.json
```

The HTML remains locally usable without internet, but it is distributed with sibling assets. State clearly that the directory must
remain intact when shared.

## 3. File Preprocessing

- PDF: render page previews using `scripts/pdf_to_pages.py`; for large outputs, adapt or extend the script to write page assets rather
  than one massive base64 JSON file.
- Office document or slides: use `scripts/doc_to_pdf.py` to create a preview PDF; preserve the original file unchanged.
- Images: render original local image or embedded copy according to packaging profile.
- Markdown: prefer semantic HTML and section comments; use pixel/region annotation only for layout review.

## 4. Viewer Layout

Viewer structure:

- Header: filename, page count, review or explanation purpose, zoom, and optional lightweight export.
- Main stage: page thumbnails/nav plus active page or vertical page stream.
- Review panel: annotations ordered by page and position, edit/delete/clear controls.
- Status banner: what has been rendered, whether the view is complete, and any fallback limitations.

## 5. Annotation Model

```javascript
{
  id: "ann-...",
  itemType: "artifact-annotation",
  artifactId: "proposal-v2",
  page: 3,
  kind: "point" | "region" | "page-comment",
  x: 0.42,
  y: 0.31,
  width: 0.18,
  height: 0.06,
  category: "change" | "question" | "approve" | "issue",
  text: "Increase spacing above this heading.",
  createdAt: "ISO timestamp"
}
```

Use normalized coordinates (`0` to `1`) rather than pixels so annotations survive zooming.

## 6. Input Alternatives

Pointer selection is useful, but never the only path:

- Click/tap to add a point annotation.
- Drag to mark a region when pointer operation is available.
- Provide `Add page comment` for keyboard-only or non-precise feedback.
- Allow annotation editing from the ordered list without manipulating the page surface.

## 7. Fallbacks

- Conversion failure: provide a textual explanation and, when possible, a semantic/text preview or original artifact link.
- Rendering failure: show available pages/assets and declare which precise annotations are unavailable.
- Very large source: provide a navigable index or partial preview; do not falsely claim full visual review coverage.
- Missing clipboard permission: reveal export text for manual copy/download.
