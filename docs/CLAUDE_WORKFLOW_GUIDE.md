# Claude Code Workflow Guide (for Wadih)

A short, practical guide to working with Claude Code on this project. Sources are linked at the bottom.

## Key terms (plain words)

| Term | What it means |
|---|---|
| **Context window** | Claude's working memory for one conversation: every message, file read, and command output. It fills up, and quality drops when it's full. **This is the main thing to manage.** |
| **CLAUDE.md** | A file Claude reads at the start of **every** session: the project's rules and commands. Keep it short; long files get ignored. |
| **Plan mode** | Claude reads and plans but changes nothing until you approve. |
| **Subagent** | A helper Claude starts with its **own fresh memory**. It does a job (e.g. reads 40 files) and returns only a summary, so your main conversation stays clean. |
| **Skill** | A saved recipe (`.claude/skills/<name>/SKILL.md`) for a repeated task. Claude loads it only when relevant, or you run it with `/name`. |
| **Hook** | A script that runs **automatically** at a fixed moment (e.g. after every edit). Guaranteed, unlike instructions, which are advice. |
| **Permission rule** | Allows or blocks specific actions for Claude (in `.claude/settings.json`). Wadih blocks reading `.env`. |
| **MCP** | Model Context Protocol: a standard way to plug external tools and data (databases, Notion, Figma…) into Claude. |
| **Slash command** | A shortcut you type, like `/clear` or `/code-review`. |
| **Checkpoint / rewind** | Claude saves your files before each change; you can roll back. Not a replacement for git. |
| **CI (GitHub Actions)** | A robot on GitHub that runs the tests on every push. Wadih only goes live when it passes. |

## What to use when

| Situation | Use | Not |
|---|---|---|
| Rules that are always true (style, "never invent facts") | **CLAUDE.md** | Long tutorials or file-by-file descriptions (→ `docs/architecture.md`) |
| Change touches several files, or you're unsure how | **Plan mode** first | Plan mode for tiny fixes: if the change fits in one sentence, just ask |
| Wide research ("how does X work across the code?"), or an independent check of a big change | **Subagent** | Small, focused tasks: the main conversation is faster |
| A multi-step task you've already done 2–3 times the same way (e.g. "add a verified news item") | **Skill** | Writing a recipe for something you haven't done yet |
| Something that must happen **every** time, with no exceptions | **Hook** or **permission rule** | Asking Claude to "remember" |
| Talking to GitHub, Render, etc. | Command-line tools (`gh`) | MCP when a CLI already works |
| Connecting a database or other system to Claude, or giving Wadih's AI its data later | **MCP** | Adding servers "just in case" |
| Switching to an unrelated task | **`/clear`** (fresh context) | One endless session mixing everything |
| An attempt went wrong | **Rewind** (Esc Esc or `/rewind`), or "undo that" | Correcting the same mistake 3+ times; instead, `/clear` and write a better prompt |

## Best practices (Anthropic + experienced developers)

1. **Give Claude a way to check its work.** Tests, a screenshot, a command that passes or fails. Wadih has 51 tests, and every task ends with `pytest`.
2. **Explore → Plan → Code → Commit.** Skip planning only for tiny, clear changes.
3. **Be specific.** Name the file, the situation, and what "done" looks like.
4. **Ask for evidence, not "it works."** Test output, a screenshot, the command and its result.
5. **Keep CLAUDE.md short.** For each line, ask: "Would removing this cause mistakes?" If not, cut it.
6. **Manage context.** `/clear` between unrelated tasks. Long, messy sessions make Claude worse.
7. **Use a second opinion for big changes.** A fresh reviewer (`/code-review`, or "use a subagent to review this diff against the plan") catches what the author misses. Only act on findings about correctness or the requirements, not every nitpick.
8. **Enforce, don't hope.** If a rule really matters, make it a test, a hook, or a permission rule.
9. **Commit often** with clear messages; git is your real safety net.

## How to ask Claude (examples for Wadih)

- **Plan first:** "Plan how to add a page for the Aramco path. Don't change anything yet."
- **Verify:** "Add the news item, run pytest, and show me the output."
- **Use a subagent:** "Use a subagent to check every source link in `data/` and report broken ones."
- **Review:** "Run /code-review on my changes before I commit."
- **Learn:** "Explain how `load_page()` keeps URLs from reaching other files, then give me one short question."
- **Enforce a rule:** "Write a hook that runs pytest after every edit to `app/`."
- **Interview me for a big feature:** "I want to build email alerts. Interview me with questions, then write a spec to `docs/specs/email-alerts.md`."
- **Fresh start:** `/clear`, then "Read CLAUDE.md and the roadmap, then continue from the next step."

## What Wadih uses today vs later

- **Today:** CLAUDE.md, plan mode, tests, CI (GitHub Actions + Render deploy-after-checks), the `.env` permission rule, checkpoints, and subagents only when worth it.
- **Later:** skills for repeated content tasks (news, paths), maybe a Stop hook that runs tests, a weekly link-check workflow, and building an **MCP server** for Wadih's verified data during the AI stages (a strong FDE portfolio piece).
- Which project files exist and when to add them: [project-files-guide.md](project-files-guide.md).

## Sources
- Anthropic, *Best practices for Claude Code*: https://code.claude.com/docs/en/best-practices
- Anthropic, *Extend Claude Code (features overview)*: https://code.claude.com/docs/en/features-overview
- CLAUDE.md files: https://code.claude.com/docs/en/memory
- Skills: https://code.claude.com/docs/en/skills
- Hooks: https://code.claude.com/docs/en/hooks-guide
- Subagents: https://code.claude.com/docs/en/sub-agents
- Permissions: https://code.claude.com/docs/en/permissions
- Plan mode and permission modes: https://code.claude.com/docs/en/permission-modes
- MCP: https://code.claude.com/docs/en/mcp
- Checkpointing: https://code.claude.com/docs/en/checkpointing
- Render, *Deploys* (Auto-Deploy "After CI Checks Pass"): https://render.com/docs/deploys and https://render.com/changelog/skip-auto-deploying-if-ci-checks-fail
- GitHub Actions documentation: https://docs.github.com/en/actions
