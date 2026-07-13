# Reviewable HTML Report Base

Common report mechanics for skills that generate interactive HTML analysis reports.

Resolve this file relative to the `reviewable-html-report` skill directory:
`references/report_base.md`. Calling skills should reference the
`reviewable-html-report` capability first. Any sibling-relative lookup used
inside this repository is a local convenience, not a standalone portability
requirement.

---

## 1. Mermaid Initialization

Place in `<head>`. Each calling skill should customize `themeVariables` colors to
match its design tokens.

```html
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  themeVariables: {
    fontSize: '16px',
    primaryColor: 'var(--mermaid-primary, #334155)',
    primaryTextColor: 'var(--mermaid-text, #e2e8f0)',
    primaryBorderColor: 'var(--mermaid-border, #64748b)',
    lineColor: 'var(--mermaid-line, #94a3b8)',
    secondaryColor: 'var(--mermaid-secondary, #1e293b)',
    tertiaryColor: 'var(--mermaid-tertiary, #334155)',
    nodeBorder: 'var(--mermaid-node-border, #64748b)',
    clusterBkg: 'var(--mermaid-cluster-bg, #1e293b)',
    clusterBorder: 'var(--mermaid-cluster-border, #475569)',
    titleColor: 'var(--mermaid-title, #e2e8f0)',
    edgeLabelBackground: 'var(--mermaid-edge-label-bg, #1e293b)'
  }
});
</script>
```

### Compatibility Rules

- Use `flowchart TB`, `flowchart LR`, or `flowchart TD`; avoid legacy `graph`.
- Do not use emoji inside Mermaid code.
- Node labels should be ASCII or plain text.
- Do not use `linkStyle` directives.
- Use `subgraph id["Display Label"]` formatting.
- Avoid complex punctuation and path symbols inside node text.
- Do not add `%%{init:...}%%` blocks in individual diagrams.
- `.topology-diagram .mermaid` must have `min-height: 380px; width: 100%;`.
- If Mermaid CDN cannot load, display readable Mermaid source in `<pre>` blocks and disclose that rendering is unavailable.

---

## 2. Topology Comparison CSS Skeleton

Each calling skill defines its own color variables and semantic variants. Keep the
layout skeleton shared:

```css
.topology-compare {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 24px;
}
.topology-diagram {
  flex: 1;
  min-width: 340px;
  cursor: pointer;
}
.topology-diagram .mermaid {
  min-height: 380px;
  width: 100%;
  background: var(--topo-bg);
}
.topology-diagram .label {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  padding: 4px 12px;
  border-radius: 4px;
  display: inline-block;
}
```

The calling skill should define `.topology-diagram.current`,
`.topology-diagram.proposed`, or equivalent variants with its own semantics.

---

## 3. Lightbox

### CSS

```css
.lightbox {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: var(--lb-backdrop, rgba(0, 0, 0, 0.78));
  cursor: pointer;
}
.lightbox.active {
  display: flex;
  align-items: center;
  justify-content: center;
}
.lightbox .diagram-wrapper {
  min-width: 700px;
  min-height: 500px;
  max-width: 94vw;
  max-height: 92vh;
  overflow: auto;
  background: var(--lb-content-bg, #111827);
  border-radius: 8px;
  padding: 24px;
}
```

### JavaScript

```javascript
document.querySelectorAll('.topology-diagram').forEach(diagram => {
  diagram.style.cursor = 'pointer';
  diagram.addEventListener('click', () => {
    const sourceSvg = diagram.querySelector('.mermaid svg');
    if (!sourceSvg) return;
    const svg = sourceSvg.cloneNode(true);
    const lb = document.createElement('div');
    lb.className = 'lightbox active';
    const wrapper = document.createElement('div');
    wrapper.className = 'diagram-wrapper';
    wrapper.appendChild(svg);
    lb.appendChild(wrapper);
    document.body.appendChild(lb);
    const close = () => lb.remove();
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', function onEsc(e) {
      if (e.key === 'Escape') {
        close();
        document.removeEventListener('keydown', onEsc);
      }
    });
  });
});
```

---

## 4. Interactive Review Controls

Each reviewable card gets one stable ID. The calling skill owns the status labels.

```html
<div class="review-controls" data-card-id="<stable-id>">
  <textarea class="review-text" placeholder="Review notes..."></textarea>
  <div class="review-actions">
    <select class="review-status">
      <!-- skill-specific options -->
    </select>
    <div class="star-rating" aria-label="Rating">
      <button type="button" data-value="1">1</button>
      <button type="button" data-value="2">2</button>
      <button type="button" data-value="3">3</button>
      <button type="button" data-value="4">4</button>
      <button type="button" data-value="5">5</button>
    </div>
  </div>
</div>
```

### localStorage Persistence

```javascript
(function() {
  const STORAGE_KEY = '<skill-specific-report-key>';
  const memoryFallback = {};

  function readAll() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch (e) {
      return memoryFallback;
    }
  }

  function writeAll(data) {
    Object.assign(memoryFallback, data);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      // Keep memoryFallback for this page session.
    }
  }

  function saveReview(cardId, data) {
    const all = readAll();
    all[cardId] = data;
    writeAll(all);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const saved = readAll();
    document.querySelectorAll('.review-controls').forEach(ctrl => {
      const cardId = ctrl.dataset.cardId;
      const text = ctrl.querySelector('.review-text');
      const status = ctrl.querySelector('.review-status');
      const current = saved[cardId] || {};
      if (text && current.text) text.value = current.text;
      if (status && current.status) status.value = current.status;

      const persist = () => saveReview(cardId, {
        text: text?.value || '',
        status: status?.value || ''
      });
      text?.addEventListener('input', persist);
      status?.addEventListener('change', persist);
    });
  });
})();
```

---

## 5. Feedback Export Pattern

```javascript
function exportReview() {
  const parts = [];
  document.querySelectorAll('.review-controls').forEach(ctrl => {
    const cardId = ctrl.dataset.cardId;
    const title = ctrl.closest('.card')?.querySelector('.card-title')?.textContent || cardId;
    const text = ctrl.querySelector('.review-text')?.value || '';
    const status = ctrl.querySelector('.review-status')?.value || '';
    const rating = ctrl.querySelector('.star-rating .active')?.dataset?.value || '';
    if (text || status || rating) {
      parts.push(`## ${title}\n- ID: ${cardId}\n- Rating: ${rating}/5\n- Status: ${status}\n- Notes: ${text}\n`);
    }
  });

  const markdown = parts.join('\n---\n') + '\n\n' + EXPORT_DIRECTIVE;
  navigator.clipboard.writeText(markdown).then(() => {
    showToast('Review copied');
  }).catch(() => {
    const fallback = document.createElement('textarea');
    fallback.value = markdown;
    fallback.style.width = '100%';
    fallback.style.minHeight = '180px';
    document.body.appendChild(fallback);
    fallback.focus();
    fallback.select();
  });
}
```

The calling skill must define `EXPORT_DIRECTIVE` so the exported notes are useful
for the next round without granting unapproved implementation authority.

---

## 6. Required Section Index

Every interactive HTML report must include a clickable section index. Use stable,
human-readable IDs so links survive copy/paste and exported review notes.

Use either a sidebar or a compact top bar. A sticky top TOC must not occupy more
than 60% of the opening viewport or freeze a large title box over the first
screen. If the TOC needs more than two rows, prefer a collapsible control,
sidebar mode, or a non-sticky fallback on narrow screens.

```html
<nav class="toc" aria-label="Section index">
  <a href="#executive-summary">Executive Summary</a>
  <a href="#evidence-ledger">Evidence Ledger</a>
  <a href="#recommendations">Recommendations</a>
  <a href="#review-notes">Review Notes</a>
</nav>

<main>
  <section id="executive-summary">
    <h2>Executive Summary</h2>
  </section>
  <section id="evidence-ledger">
    <h2>Evidence Ledger</h2>
  </section>
</main>
```

```css
.toc {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--toc-bg, #0f172a);
  padding: 10px 0;
  max-height: min(28vh, 180px);
  overflow-y: auto;
  overscroll-behavior: contain;
}
.toc a {
  border-radius: 4px;
  padding: 6px 10px;
  color: var(--toc-link, #cbd5e1);
  text-decoration: none;
}
.toc a:hover,
.toc a.active {
  background: var(--toc-active-bg, #1e293b);
  color: var(--toc-active, #ffffff);
}
section[id] {
  scroll-margin-top: 72px;
}
@media (max-width: 720px) {
  .toc {
    position: static;
    max-height: none;
  }
}
```

### TOC Scroll Linkage

```javascript
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      document.querySelectorAll('.toc a').forEach(a => a.classList.remove('active'));
      const link = document.querySelector(`.toc a[href="#${entry.target.id}"]`);
      if (link) link.classList.add('active');
    }
  });
}, { rootMargin: '-10% 0px -80% 0px' });

document.querySelectorAll('section[id]').forEach(s => observer.observe(s));
```
