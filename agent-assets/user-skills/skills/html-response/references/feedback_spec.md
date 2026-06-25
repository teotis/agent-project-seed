# Feedback and Continuation Specification

## Purpose

Feedback should let a user react to the exact unit they reviewed without rewriting context. In `html-response`, feedback is an optional secondary layer for comprehension-first pages: the HTML is readable and useful even if no feedback is provided. Formal review controls, local persistence, approval state, ratings, and exportable review notes should use `reviewable-html-report` mechanics.

## 1. Stable Review Units

Each reviewable unit uses stable attributes:

```html
<section class="review-unit" data-item-id="finding-auth-boundary" data-item-type="finding">
  <h3>Authentication boundary mixes policy and transport</h3>
  ...
  <div class="feedback-controls" data-for="finding-auth-boundary">...</div>
</section>
```

Item IDs are meaningful, unique within the document, and preserved in exported feedback.

## 2. Feedback Components

Use only components relevant to the mode:

- `status`: selectable review disposition, e.g. `Agree`, `Need evidence`, `Defer`, `Incorrect`.
- `rating`: optional 1–5 score only when relative acceptance/confidence is useful.
- `comment`: textarea attached to one review unit.
- `priority`: optional ranking for options/findings/planned actions.
- `annotation`: for pages/images; stores position plus text and category.
- `global_note`: overall review comment or desired next focus.

Avoid rating widgets for factual explanations unless the user benefits from evaluating clarity or confidence.

## 3. Local Persistence

Use local persistence only when lightweight feedback is genuinely useful and `reviewable-html-report` is not the better owner. Required behavior:

```javascript
const storageKey = `adaptive-html-feedback:${location.pathname}:${document.body.dataset.documentId || 'default'}`;
function saveFeedback(state) {
  try { localStorage.setItem(storageKey, JSON.stringify(state)); }
  catch (_) { window.__feedbackFallback = state; }
}
function loadFeedback() {
  try { return JSON.parse(localStorage.getItem(storageKey) || 'null'); }
  catch (_) { return window.__feedbackFallback || null; }
}
```

Provide a visible `Clear feedback` button and do not store document content beyond what the user actively enters or selects.

## 4. Export Contract

A single export action produces:

1. readable Markdown for the next conversation turn;
2. a compact machine-readable block with IDs and values.

Example:

```markdown
# Review Feedback: Authentication Refactoring Options

## finding-auth-boundary — Need evidence
Priority: High
Comment: Show the call paths proving this boundary is responsible for duplicated checks.

## option-adapter — Prefer
Comment: Proceed to a migration plan, but retain current API compatibility.

## Overall note
Please focus the next iteration on measured production risk and rollback design.

---ADAPTIVE_HTML_FEEDBACK_JSON---
{"document_id":"auth-review-v1","items":[{"id":"finding-auth-boundary","status":"need_evidence","priority":"high","comment":"..."}]}
---END_ADAPTIVE_HTML_FEEDBACK_JSON---

[Continuation Directive] Use the feedback above to revise the analysis or propose the next reviewable plan. Do not execute destructive actions, modify production systems, change user files, or send communications unless I explicitly authorize that action.
```

The continuation directive is safe by default and must be adjusted only to the user's explicit authorized intention.

## 5. Clipboard and Export Fallback

`navigator.clipboard.writeText` may not be available in all local-file or permission contexts. Export behavior must:

1. attempt clipboard write only from a user-triggered button;
2. show success only after the promise resolves;
3. on failure, open a modal or `<textarea>` containing the export text, select it, and instruct manual copy;
4. allow saving as `.md` or `.json` when convenient.

## 6. Interaction Accessibility

- All status groups use labeled radio buttons or toggle buttons with state announced to assistive technology.
- Rating stars, when used, must have keyboard-operable radio equivalents and accessible labels.
- Toasts use `role="status"` / `aria-live="polite"`.
- Annotation drawers are reachable by keyboard and provide an ordered list of comments.
- Region-selection interactions also provide “Add page comment” without drawing.
