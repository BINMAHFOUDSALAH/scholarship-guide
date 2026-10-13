# Project Files Guide

A reference for the "special" files a project like this can have: what each one does, whether we use it yet, and when it's worth adding. Checked against Anthropic's [.claude directory reference](https://code.claude.com/docs/en/claude-directory) on 2026-10-13 (decision 059).

**Golden rule:** every file should have **one job**. Two files doing the same job means one of them will quietly go out of date and mislead you (or the next AI session).

Legend: ✅ we have it · ⏳ add later (stage noted) · ❌ not needed for us

---

## Instructions for AI assistants

| File | What it does | Status | When to use it |
|---|---|---|---|
| `CLAUDE.md` | Claude Code reads it automatically at the start of every session in this folder: rules, working style, commands, architecture, and pointers to other docs. | ✅ | Always. Keep it short: rules and pointers, not a diary. Update it when a rule or the architecture changes. |
| `AGENTS.md` | The same idea as `CLAUDE.md`, but read by *other* AI coding tools (OpenAI Codex, Cursor, etc.). | ❌ | Only if you start using another AI tool on this repo. Then it can point to `CLAUDE.md` instead of repeating it. |
| `.claude/skills/<name>/SKILL.md` | A reusable recipe Claude follows for a **repeated** task. You can trigger it by name. | ✅ | `research-wave` (university requirements, decision 054). Write one only after doing the task once or twice by hand. |
| `.claude/agents/<name>.md` | A specialized Claude helper (subagent) with its own instructions and tools, e.g. a "content checker" that reviews pages for missing sources. | ✅ | `source-researcher`, `fact-checker`, `reviewer` (decision 037), all read-only, on Haiku 5.5. Add one only for a job we repeat. Not the same as the AI agents in Stage 8, which are website features for students. |
| `.claude/rules/<topic>.md` | Instructions that load only when Claude works on matching files (`paths:` in the frontmatter), so CLAUDE.md stays short. | ✅ | `design.md` (decision 035's design rules, loads for `app/templates/` and `app/static/`). Add one when a CLAUDE.md rule only matters for part of the code. |
| `.claude/settings.json` | Project settings for Claude Code: allowed/blocked actions (permissions) and hooks (actions that run automatically). Shared via git. Unlike CLAUDE.md (advice), these are enforced. | ✅ | Today it blocks Claude from reading `.env` and forces every subagent onto Haiku 5.5 (`CLAUDE_CODE_SUBAGENT_MODEL` + `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`; without FORCE the built-in Explore and Plan agents ignore it). Add to it when you keep approving the same safe command, or want something automated. No hooks yet: a hook must work in your Windows setup too. |
| `.claude/settings.local.json` | The same, but personal to your machine. Not committed (already in `.gitignore`). | as needed | Personal preferences you don't want in the repo. |
| `.claude/launch.json` | Tells the Claude desktop app how to start the dev server in its browser pane. | ✅ | Already set up. Update it if the start command changes. |
| `.claude/commands/<name>.md` | Older form of a `/name` shortcut. | ❌ | Skills replaced it (same `/name`, plus supporting files). Use a skill. |
| `.claude/workflows/`, `.claude/agent-memory/`, `.claude/output-styles/` | Saved multi-agent workflow scripts; memory for subagents that set `memory:`; shared response styles. | ❌ | Created only when you use those features. None needed now. |
| `.mcp.json` (repo root) | MCP servers shared with everyone who opens the project (databases, APIs, browsers). | ❌ for now | When the project needs an external tool that has no CLI, or in the AI stages when we build an MCP server for واضح's verified data. Personal servers go in `~/.claude.json`, not here. |
| `/goal` | Not a file: a command that keeps Claude working until a condition you state is true (e.g. `/goal all tests pass and the Oxford file has no draft flag`). | as needed | Long tasks with a checkable end. Lasts one session; the plan itself stays in `docs/roadmap.md`. |
| `CLAUDE.local.md` | Personal notes Claude reads only on your machine. | ❌ | Only for private preferences; project rules belong in `CLAUDE.md`. |
| Claude's memory | Notes Claude keeps about you and the project, stored on **your computer**, outside the repo. | automatic | It helps across sessions, but it isn't in git. Anything important for the project belongs in `CLAUDE.md` or `docs/`. |

## Planning and documentation

| File | What it does | Status | When to use it |
|---|---|---|---|
| `docs/roadmap.md` | The living plan: stages, steps, and checkboxes showing where we are. | ✅ | Tick boxes at the end of every step. A new session reads this to know "what's next." |
| `progress.md` | Commonly used for "what's done, what's next." | ❌ | Same job as `docs/roadmap.md`, so we don't add it. If you ever want a **session log** (a dated diary of what happened each session), that's a different job and could be `docs/log.md`. |
| `docs/decisions.md` | Every design choice: what we chose, the alternatives, and why. | ✅ | Add an entry whenever we make a choice someone might later question. Never delete old entries; mark them "Superseded." |
| `spec.md` / `docs/specs/<feature>.md` | A **specification**: a short document describing exactly what a feature must do *before* building it (goal, inputs, outputs, rules, edge cases, how we'll test it). | ⏳ Stage 2+ | Before any feature bigger than a page: the paths data model (Stage 2), the compare-paths table, the chatbot (Stage 7), each agent (Stage 8). One spec per feature in `docs/specs/`, not one giant `spec.md`. Specs are also great input for AI: "build what this spec says." |
| `goal.md`, `PRD.md`, `TODO.md` | Common in other projects: the goal, product requirements, a task list. | ❌ | Same jobs as CLAUDE.md's "Project" section (goal), `docs/specs/` (requirements) and `docs/roadmap.md` (tasks). A second copy would drift. |
| `docs/project-files-guide.md` | This file. | ✅ | Look things up here. |
| `docs/architecture.md` | How the code fits together (moved out of CLAUDE.md to keep it short). | ✅ | Update when the structure changes. |
| `docs/claude-workflow-guide.md` | How to work with Claude Code: subagents, skills, hooks, MCP, `/goal`, best practices, example prompts. | ✅ | Read when unsure which Claude feature to use. |
| `LEARNING_LOG.md` | A diary of what was built and learned. | ❌ removed (decision 059) | The owner didn't read it. The key concept is in each task's report; the why is in `docs/decisions.md`. The old file is in git history. |
| `README.md` | The front page of the repo on GitHub: what the project is, how to run it, the live link. | ✅ | Update it when how to run the project changes, and at launch (add the live URL + screenshots). |
| `CHANGELOG.md` | A list of what changed in each release, written for users. | ❌ for now | Useful once the site is live and you ship updates people care about. |
| `CONTRIBUTING.md` | How other people can contribute (style rules, how to submit changes). | ❌ | Only if others start contributing. |
| `LICENSE` | Says what others may legally do with your code. Without one, nobody may reuse it. | ⏳ owner to decide | The repo is already public on GitHub. With no licence, the default is "all rights reserved": people can read it but not reuse it. Choose that on purpose, or an open licence (e.g. MIT for code, CC BY for text). Content and code can have different licences. |

## Code and configuration

| File | What it does | Status | When to use it |
|---|---|---|---|
| `requirements.txt` | The list of Python packages + exact versions. `pip install -r requirements.txt` rebuilds the environment anywhere. | ✅ | Update it whenever we install a package. |
| `pyproject.toml` | The modern, all-in-one Python project config (dependencies, tool settings for pytest, linters…). | ❌ for now | If we adopt tools like `uv` or `ruff`, or the config grows. `requirements.txt` is enough for now. |
| `.gitignore` | Files git should never track (`.venv/`, `.env`, caches). | ✅ | Add to it whenever a generated or secret file appears. |
| `.env` | Secrets (API keys) for your machine only. **Never committed, never shared.** Claude never reads it. | ⏳ Stage 7 | When we use a paid AI API. |
| `.env.example` | A copy of `.env` with the **names** of the settings but **no real values**, so others know what to set. | ⏳ Stage 7 | Created together with `.env`. Safe to commit. |
| `data/*.json` | Settings and facts (site name, paths, resources, the quote). | ✅ | Edit content here, never in templates. |
| `content/**/*.md` | Page text in Markdown, with a frontmatter header (`title`, `status`, `sources`, `last_checked`). | ✅ | Every guide page. |
| `tests/` | Automated tests (pytest). | ✅ | Every feature gets tests. CI runs them automatically. |
| `.github/workflows/*.yml` | GitHub Actions (CI): runs tests on every push. | ✅ (`tests.yml`) | Render deploys only after it passes. Add workflows for scheduled checks later (e.g. a weekly link checker). |
| `render.yaml` | Render's deployment config as a file ("infrastructure as code"). | ⏳ Step 7 (optional) | When the deploy settings should live in git instead of only in Render's dashboard. |
