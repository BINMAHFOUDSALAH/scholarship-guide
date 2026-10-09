# Project Files Guide

A reference for the "special" files a project like this can have: what each one does, whether we use it yet, and when it's worth adding.

**Golden rule:** every file should have **one job**. Two files doing the same job means one of them will quietly go out of date and mislead you (or the next AI session).

Legend: ✅ we have it · ⏳ add later (stage noted) · ❌ not needed for us

---

## Instructions for AI assistants

| File | What it does | Status | When to use it |
|---|---|---|---|
| `CLAUDE.md` | Claude Code reads it automatically at the start of every session in this folder: rules, working style, commands, architecture, and pointers to other docs. | ✅ | Always. Keep it short: rules and pointers, not a diary. Update it when a rule or the architecture changes. |
| `AGENTS.md` | The same idea as `CLAUDE.md`, but read by *other* AI coding tools (OpenAI Codex, Cursor, etc.). | ❌ | Only if you start using another AI tool on this repo. Then it can point to `CLAUDE.md` instead of repeating it. |
| `.claude/skills/<name>/SKILL.md` | A reusable recipe Claude follows for a **repeated** task, e.g. "add a new path: create the JSON, check every source, add tests." You can trigger it by name. | ⏳ Stage 2 / 5 | When we've done the same multi-step task at least once or twice and want it done the same way every time. Don't write one before doing the task. |
| `.claude/agents/<name>.md` | A specialized Claude helper (subagent) with its own instructions and tools, e.g. a "content checker" that reviews pages for missing sources. | ⏳ Stage 3+ | When there's enough content that a dedicated reviewer saves time. Not the same as the AI agents in Stage 8, which are website features for students. |
| `.claude/settings.json` | Project settings for Claude Code: allowed commands (permissions) and hooks (actions that run automatically, e.g. after every edit). Shared via git. | ⏳ when needed | When you keep approving the same safe command, or want something automated (e.g. "run tests after each change"). |
| `.claude/settings.local.json` | The same, but personal to your machine. Not committed (already in `.gitignore`). | as needed | Personal preferences you don't want in the repo. |
| `.claude/launch.json` | Tells the Claude desktop app how to start the dev server in its browser pane. | ✅ | Already set up. Update it if the start command changes. |
| Claude's memory | Notes Claude keeps about you and the project, stored on **your computer**, outside the repo. | automatic | It helps across sessions, but it isn't in git. Anything important for the project belongs in `CLAUDE.md` or `docs/`. |

## Planning and documentation

| File | What it does | Status | When to use it |
|---|---|---|---|
| `docs/roadmap.md` | The living plan: stages, steps, and checkboxes showing where we are. | ✅ | Tick boxes at the end of every step. A new session reads this to know "what's next." |
| `progress.md` | Commonly used for "what's done, what's next." | ❌ | Same job as `docs/roadmap.md`, so we don't add it. If you ever want a **session log** (a dated diary of what happened each session), that's a different job and could be `docs/log.md`. |
| `docs/decisions.md` | Every design choice: what we chose, the alternatives, and why. | ✅ | Add an entry whenever we make a choice someone might later question. Never delete old entries; mark them "Superseded." |
| `spec.md` / `docs/specs/<feature>.md` | A **specification**: a short document describing exactly what a feature must do *before* building it (goal, inputs, outputs, rules, edge cases, how we'll test it). | ⏳ Stage 2+ | Before any feature bigger than a page: the paths data model (Stage 2), the compare-paths table, the chatbot (Stage 7), each agent (Stage 8). One spec per feature in `docs/specs/`, not one giant `spec.md`. Specs are also great input for AI: "build what this spec says." |
| `docs/project-files-guide.md` | This file. | ✅ | Look things up here. |
| `README.md` | The front page of the repo on GitHub: what the project is, how to run it, the live link. | ✅ | Update it when how to run the project changes, and at launch (add the live URL + screenshots). |
| `CHANGELOG.md` | A list of what changed in each release, written for users. | ❌ for now | Useful once the site is live and you ship updates people care about. |
| `CONTRIBUTING.md` | How other people can contribute (style rules, how to submit changes). | ❌ | Only if others start contributing. |
| `LICENSE` | Says what others may legally do with your code. Without one, nobody may reuse it. | ⏳ before launch | Decide before making the repo public: open source (e.g. MIT) or "all rights reserved." Content and code can have different licenses. |

## Code and configuration

| File | What it does | Status | When to use it |
|---|---|---|---|
| `requirements.txt` | The list of Python packages + exact versions. `pip install -r requirements.txt` rebuilds the environment anywhere. | ✅ | Update it whenever we install a package. |
| `pyproject.toml` | The modern, all-in-one Python project config (dependencies, tool settings for pytest, linters…). | ❌ for now | If we adopt tools like `uv` or `ruff`, or the config grows. `requirements.txt` is enough for now. |
| `.gitignore` | Files git should never track (`.venv/`, `.env`, caches). | ✅ | Add to it whenever a generated or secret file appears. |
| `.env` | Secrets (API keys) for your machine only. **Never committed, never shared.** Claude never reads it. | ⏳ Stage 7 | When we use a paid AI API. |
| `.env.example` | A copy of `.env` with the **names** of the settings but **no real values**, so others know what to set. | ⏳ Stage 7 | Created together with `.env`. Safe to commit. |
| `data/*.json` | Settings and facts (site name, paths, resources, the quote). | ✅ | Edit content here, never in templates. |
| `content/**/*.md` | Page text in Markdown, with a frontmatter header (`title`, `status`, `sources`, `last_checked`). | ⏳ Step 5 | Every guide page. |
| `tests/` | Automated tests (pytest). | ⏳ Step 6 | Every feature gets tests. CI runs them automatically. |
| `.github/workflows/*.yml` | GitHub Actions (CI): runs tests on every push. | ⏳ Stage 4 | When we want automatic checks so a broken change can't slip through. |
| `render.yaml` | Render's deployment config as a file ("infrastructure as code"). | ⏳ Step 7 (optional) | When the deploy settings should live in git instead of only in Render's dashboard. |
