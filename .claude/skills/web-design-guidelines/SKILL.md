---
name: web-design-guidelines
description: Review واضح's templates, CSS and JS against Vercel's Web Interface Guidelines (accessibility, focus, forms, animation, touch, layout) and report findings as file:line. Use when asked to "review my UI", "check accessibility", "audit the design", or after building or changing a page. Review only; never edits files.
argument-hint: <file-or-pattern>
---

# Web interface review (adapted for واضح)

Adapted from [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) (`web-design-guidelines`). The upstream skill downloads its rules from GitHub on every run; here they are a **pinned local copy** in [guidelines.md](guidelines.md) (vercel-labs/web-interface-guidelines, commit `434b7f9`, 2026-10-05, MIT, see [LICENSE](LICENSE)), so the rules can't change under us. To update: replace `guidelines.md` with the new `command.md`, read the diff, and note the commit here.

## How to run it

1. Read [guidelines.md](guidelines.md) and the files to review (if none were given, ask; usually `app/templates/<page>.html`, `app/static/style.css`, `app/static/*.js`).
2. Check them against the rules, **with the واضح overrides below**.
3. Report in the guidelines' terse `file:line` format, grouped by file. Do not edit anything; the main session decides what to fix.

## واضح overrides (these win over the guidelines)

`CLAUDE.md` and `.claude/rules/design.md` always beat this checklist. In particular:

- **Not React.** The site is FastAPI + Jinja templates + plain JS. Read React/Tailwind/Next rules (`onClick`, `useState`, `nuqs`, hydration, `priority`, `focus-visible:ring-*`) as their plain HTML/CSS equivalent, or skip them.
- **Language comes from the URL** (`/en/...`, decision 066), never from `Accept-Language`. Don't flag it.
- **No third-party requests** (self-hosted fonts, no CDN): never suggest `preconnect` to another domain or a CDN.
- **Arabic text is the source**: no "Title Case", no English curly-quote rules for Arabic. Arabic uses «» and the Arabic comma «، ». The copy rules apply to the English pages only, and never change wording that translates a fact (CLAUDE.md: translate exactly).
- **Colours, fonts and layout** come from `design.md` (decision 062/075). Report a problem (contrast, focus, size); don't propose a new palette or font.
- **RTL first**: also flag `left`/`right` where a logical property (`inline-start`/`inline-end`) is needed, and check at phone width.
