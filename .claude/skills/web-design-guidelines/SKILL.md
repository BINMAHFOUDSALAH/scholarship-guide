---
name: web-design-guidelines
description: Review Wadih's web interface for accessibility, usability, and responsive behavior. Use for a requested UI audit or to verify a substantial page change.
argument-hint: "<file-or-pattern>"
---

# Wadih interface review

Use the pinned local [Vercel Web Interface Guidelines](guidelines.md) and its accompanying [license](LICENSE). When refreshing the checklist, review the upstream diff and record the source commit.

1. Read the files or page named in the task. For a review of recent work, start with the relevant diff.
2. Apply `CLAUDE.md` and `.claude/rules/design.md`. Adapt the checklist to FastAPI, Jinja, CSS, and vanilla JavaScript. Use the site's `/en/` routing and apply copy guidance in the page's own language.
3. Check keyboard access, visible focus, forms, touch targets, contrast, reduced motion, and mobile layout. For Arabic pages, check RTL alignment and mixed Arabic and English text. Flag unexpected third-party requests on public pages.
4. When browser tools are available, verify findings in the rendered interface and state what you checked.

Report findings by severity with `file:line`, the student impact, and a suggested fix. Flag concrete issues in the current design, including typography, color, or layout when they affect usability. This skill is review-only. Return findings to the main session for implementation.