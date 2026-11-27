# Wadih roadmap

Wadih helps Saudi high school students find opportunities, understand which requirements apply to them, and take the next step. Support both paths: applying to a university before pursuing a scholarship, and applying directly to a program such as Aramco or KAUST.

Use the current request to guide the work. When I ask for the next step, pick the first open item that fits the current direction. Work across related pages when that helps complete the task, and mark an item done after verification.

## Current milestone — finish the redesign

- [x] Earlier passes established the site foundation and homepage, replaced the four-point sparkle, and added the sourced وضّاح preview. See [log.md](log.md) and Git history for details.
- [ ] Choose and implement a distinctive Arabic-first design across the site. Use the [design guidance](../.claude/rules/design.md) and the current redesign brief. Choose the order of work based on how students use the site.
- [ ] Make university discovery work for students who know a subject or a country but are unfamiliar with scholarship tracks. Make results easy to scan and compare. Test an Arabic search such as «علوم الحاسب».
- [ ] Lead university and program pages with the answers students need. Show scholarship list status, admission requirements, deadlines, and official sources. Explain when to apply and make differences between tracks such as الرواد and إمداد clear.
- [ ] Make «خطتي» lead with saved choices and the student’s next useful action. Show relevant dates in order and give maps or progress illustrations space when they help.
- [ ] Review the experience across grade pages, guides, search, «جرّب قبل أن تقرر», and empty and error states. Test realistic student tasks on mobile and desktop, including Arabic and English and both themes where supported.
- [ ] Verify requirements and deadlines touched by the redesign. Recheck the official wording before publishing claims about eligible degrees, majors, list sizes, or admission rules. Share the PR and preview or local test steps. I review, test, and merge it.

## Next milestone — launch وضّاح

Keep Wadih and its public tools free to browse. Use Google sign-in for students who choose to use وضّاح. Start with first-time visitors.

- [ ] Update [agent.md](specs/agent.md) and [accounts.md](specs/accounts.md) to reflect the current product direction. Define what profile details the agent needs, what students can edit or delete, and which actions they can take through وضّاح.
- [ ] Build one complete journey. A student signs in, asks an Arabic scholarship question, gets a source-backed shortlist and a practical next step, and can add that step to «خطتي». Include undo for reversible actions.
- [ ] Use the same verified records the website uses for scores, deadlines, and scholarship list membership. Retrieve relevant guides for explanations. Cite official sources and identify what still needs checking. Keep meeting a published requirement distinct from being accepted.
- [ ] Verify the records used by the pilot. Start with [eval-seed.json](specs/eval-seed.json) and add cases that cover ambiguous names, missing requirements, outdated deadlines, and whether an action saved the right thing to the right account.
- [ ] Run a small pilot. Compare the agent with using the Finder and «خطتي» directly. Record data gaps and agent failures, fix them at their source, and rerun the same cases.
- [ ] Add opt-in email reminders for verified deadlines. Test changed dates, unsubscribe, and duplicate delivery before enabling them for students.

## Ongoing work

- Expand verified university coverage based on student questions and gaps found in testing.
- Review the «Site check» findings and keep official sources, verification dates, and application cycles current.