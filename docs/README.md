# Documentation

A map of the project's documents. To run the code, start with the main [README](../README.md).

## The essentials

| Document | Read it for |
|---|---|
| [architecture.md](architecture.md) | How the code fits together |
| [decisions.md](decisions.md) | Every design choice, with the alternatives and why |
| [roadmap.md](roadmap.md) | Where the project is, what's next, and the owner's to-dos |
| [log.md](log.md) | What each working session did, newest first |

## Feature specs

Written before building a feature.

- [universities-explorer.md](specs/universities-explorer.md): the universities explorer and the requirements schema
- [search.md](specs/search.md): site search, the first step towards a chatbot that answers only from verified content
- [english-site.md](specs/english-site.md): the English version of the site

## Research notes

The evidence behind the site: what was read on official pages, when, and what couldn't be confirmed. Notes are kept as written, so a note can be older than the site. The site's current facts are in `data/` and `content/`.

**Programs and facts**

- [custodian-scholarship-2026-27.md](research/custodian-scholarship-2026-27.md): the government scholarship, fact by fact
- [custodian-faq-2026-10.md](research/custodian-faq-2026-10.md): extra student questions on the government scholarship
- [aramco-cdpne-2026-27.md](research/aramco-cdpne-2026-27.md): Aramco's programs for high school graduates
- [kgsp-2026-27.md](research/kgsp-2026-27.md): the KAUST Gifted Student Program
- [paths-research.md](research/paths-research.md): the first draft of the programs, now partly replaced by the notes above
- [grade-pages-2026-10.md](research/grade-pages-2026-10.md): the grade pages and which tests each destination asks for
- [tests-resources-2026-10.md](research/tests-resources-2026-10.md): SAT, TOEFL and القدرات/التحصيلي
- [timeline-2026-10.md](research/timeline-2026-10.md): US applications against the scholarship's timing
- [us-applications-2026-10.md](research/us-applications-2026-10.md): Common App, UC, fees and waivers
- [field-majors-classification-2026-11.md](research/field-majors-classification-2026-11.md): example majors where the Ministry's guide has too little
- [arabic-names-to-check.md](research/arabic-names-to-check.md): university names in Arabic, for the owner to check

**Audits and evaluations**

- [product-audit-2026-10-13.md](research/product-audit-2026-10-13.md): the product direction (decision 057)
- [product-audit-2026-10.md](research/product-audit-2026-10.md): the earlier product audit
- [requirements-audit-2026-10-13.md](research/requirements-audit-2026-10-13.md): every university requirement checked against its source
- [career-exploration-evaluation-2026-11.md](research/career-exploration-evaluation-2026-11.md): should the site build an interests assessment?

**Design and UX**

- [design-direction-2026-11-07.md](research/design-direction-2026-11-07.md): the current plan: the «الطريق والنجوم» redesign, the AI guide وضّاح and its teaser (decisions 081–082)
- [design-direction-2026-10-17.md](research/design-direction-2026-10-17.md): the previous design direction (decision 062), whose palette, type and rules stay
- [ux-audit-2026-10-16.md](research/ux-audit-2026-10-16.md): UX audit and targeted redesign
- [design-audit-2026-10.md](research/design-audit-2026-10.md): design audit and improvement pass
- [ux-redesign-2026-10.md](research/ux-redesign-2026-10.md): audit, research and direction for the first redesign

**Briefs for research agents**

The instructions given to research subagents, with what each batch saved and what it couldn't read.

- University requirements: [UK](research/emdad-wave-2-uk-brief.md), [Australia, Canada, Singapore](research/emdad-wave-3-brief.md), [other US + India](research/emdad-wave-4-brief.md), [Europe](research/emdad-wave-5-eu-brief.md)
- Re-checks: [English tests + US essays](research/english-essays-recheck-brief.md), [الرواد + US tests](research/rowwad-us-tests-recheck-brief.md)

## Working with Claude Code

- [claude-workflow-guide.md](claude-workflow-guide.md): which Claude Code feature to use when
- [project-files-guide.md](project-files-guide.md): what each special project file does, and when to add one

## Elsewhere in the repository

- [`marketing/`](../marketing/README.md): the launch ad's guide and build scripts (paused)
