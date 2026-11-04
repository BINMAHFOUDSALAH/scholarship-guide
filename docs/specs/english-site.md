# The English version of واضح (decision 066)

Owner's request (2026-11-03): an English toggle, because many users are Saudi students who don't read Arabic. The whole site at once; the toggle goes live only when everything is translated. The owner does not read the English: the meaning check below is our job. Reverses decision 004 (its reason, stale translations, is handled by design).

Branch: `feature/english-site` (groundwork), finished on `feature/english-site-tisyc3` (2026-11-04). **Status: all steps below done**; what stays true for maintenance is in decision 066, `docs/architecture.md` and CLAUDE.md. The owner approved commits and pushes on this branch. Never merge to `main` without asking.

## How it works (built)
- **Addresses:** Arabic stays where it is; `/en/...` is the same page in English. `i18n.LanguageMiddleware` strips `/en` and sets the language in a contextvar, so routes exist once. `url_for` (`url_for_language`) and `render()` + `localize_links()` in `main.py` keep links in English. Static files have one address. No automatic redirect.
- **Toggle and Google tags:** `base.html` (`.lang-toggle`, `hreflang`, canonical). `.lang-toggle` has **no CSS yet**.
- **Translations:** `data/i18n/*.en.json`, `{"exact Arabic": "English"}`, loaded by `i18n.load()`. The folder doesn't exist yet. If the Arabic changes, the old English stops matching, so a test can fail on it: a stale translation can't be shown.
- **Data stays Arabic; translation happens when shown.** `env.finalize` translates every `{{ value }}`, so logic like `x.event_ar == "آخر موعد للتقديم"` keeps working. `_("نص")` = text written in a template; `_f("نص {x}", x=v)` = a sentence with values; `tr` / `tf` = the same in Python; `ar(x)` keeps Arabic on English pages (only inside `lang="ar"`); `is_en()` for the few layout differences.
- **Names from the data:** universities, fields and majors use the guide's official `name_en` (`i18n.add_from_data`). Written translations win.
- **Pages:** `content/en/<section>/<slug>.md`. Frontmatter holds only translated keys (title, description, stage_ar, activity, resources, next_step…); sources, status and dates come from the Arabic file (`load_page` merges them). Add `translated_from: <content.source_hash(section, slug)>`. Keep every `{#id}` from the Arabic: other pages link to those anchors. **Page titles must also reach the translation lookup** (program_links and guide_groups in main.py are computed once at startup from Arabic titles): add Arabic title → English title automatically at startup, or put them in the JSON.
- **JavaScript:** `t()` reads `window.WADIH_I18N`, written into English pages from `data/i18n/js.en.json`. `BASE` = `/en` on English pages. Keys with values use `{name}` / `{n}`. Also needed: `فاتح`, `داكن`, `التبديل إلى الوضع الفاتح`, `التبديل إلى الوضع الداكن`, `المقطع الأصلي`.
- **Search:** `site_search_en` is a second index built at startup under `use_lang("en")`.

## Still to do, in order
1. **Interface text:** run `python scripts/i18n_worklist.py <folder>` for the lists. Write `data/i18n/ui.en.json` (`tpl.json` + `py.json`) and `js.en.json`. Include «→» → «←» and «» as “ ” (keys such as `«`, `»`, `».`, `»؟`), and «، » as `, `. Fragment keys are shown in sentence order, so translate each with its context in the template, and add spaces where a key ends joined to a value (for example `، ل` → `, for `).
2. **Guides, grades, programs:** `content/en/` (14 files, about 4,200 words).
3. **Data:** `data/i18n/data.en.json` (`top.json`; includes `paths.json`, واعد, `apply_year`, `home`, `test_needs`, `site.json`, countries). Skip what's never shown (`aliases`, research notes, quotes).
4. **University files:** `data/i18n/universities.en.json` (`uni.json`: 1,419 unique strings, about 15,800 words). Parallel Haiku subagents, about 80 strings per batch, each with this file's glossary and strict JSON output. Tell the owner why subagents are used (CLAUDE.md, decision 037). If a subagent fails or reports another model, stop and say so.
5. **Meaning check of everything:** a separate pass compares every Arabic/English pair and reports only differences of meaning (minimum vs recommended, required vs optional, "not accepted" vs "not listed", who is eligible, negatives, conditions). The main session decides every finding. Then read a sample itself.
6. **Tests** (`tests/test_english.py`):
   - every Arabic text has English (templates, Python, data, files), with no unused keys;
   - every number, date, URL and Latin name in the Arabic is in the English, and the English adds none;
   - each `content/en` file matches its `translated_from`, and all 14 exist;
   - every English page (all sitemap pages plus filter/search variants, 404, partials) has no Arabic outside `lang="ar"`, no «», and `lang="en" dir="ltr"`;
   - all internal links stay in `/en`, every anchor exists, status 200;
   - `/en/universities`, `/en/search`, `/en/api/suggestions` and redirects work; drafts stay hidden in English too; no third-party requests;
   - English formal-tone/glossary spot checks; `tests/test_stale_facts.py` and the dialect test still pass.
7. **Design:** `.lang-toggle` CSS (a clear control in the header, phone included). Check LTR at 390 and 1280 px, both themes: header, route, tables, star chart, `text-align: end` (style.css ~2948, ~3443, comments assume RTL), `▸` markers, Naskh titles in Latin (does `--font-title` suit English? `.claude/rules/design.md` governs). The logo never changes. Add `text_pairs` to `test_design.py` if colours are added.
8. **Arabic unchanged:** `python scripts/compare_arabic_pages.py save <folder>` on a clean checkout of `main` (`git worktree`), then `compare` on this branch: must report 0 differ (the toggle and hreflang tags are ignored). Run `pytest`, and `scripts/check_explorer.mjs` plus an English run of the same flows in a browser.
9. **Docs:** decision 066 in `docs/decisions.md` (supersedes 004; alternatives: `.po` gettext, duplicate templates, translated fields beside `_ar`, machine translation in the browser), `docs/architecture.md`, `CLAUDE.md` (project line "One Arabic site…", commands), `docs/roadmap.md`, and the `/update-site` skill + `.claude/rules`: **every Arabic change now needs its English in the same commit.** Also `scripts/stale_facts.py` if it should ignore `content/en`.
10. Open a pull request. Do not merge. Report to the owner: what was checked, what wasn't (real phones), and a short list of strings for a person to read if they want.

## Glossary (use these everywhere)
| Arabic | English |
|---|---|
| واضح | Wadih |
| برنامج خادم الحرمين الشريفين للابتعاث | Custodian of the Two Holy Mosques Scholarship Program (use `paths.json` `name_en` if it differs) |
| مسار الرواد / إمداد / واعد / البحث والتطوير | Check `name_en` in `paths.json` first, and the Ministry's own English if published; never invent an official name. Short forms stay transliterated the same way everywhere. Show the Arabic name beside it on the program pages (done in templates). |
| الدليل الاسترشادي | the official guide (the Ministry's universities guide) |
| قوائم الابتعاث | the scholarship lists |
| الحد الأدنى / الموصى به | minimum / recommended (never a bare number) |
| مهارات الاختبار: الاستماع، القراءة، الكتابة، التحدث | test skills: listening, reading, writing, speaking |
| لا يُقبل لإثبات اللغة | not accepted as proof of English |
| ليس ضمن الاختبارات التي تذكرها الجامعة | not among the tests the university lists (≠ not accepted) |
| لم نتحقق منه | not verified by us |
| لا يوجد حد أدنى منشور | no published minimum |
| أول / ثاني / ثالث ثانوي | Grade 10 / 11 / 12 |
| القدرات، التحصيلي | Qudurat (General Aptitude Test), Tahsili (Achievement Test) |
| القبول المشروط / غير المشروط | conditional / unconditional admission |
| السنة التحضيرية | foundation year (preparatory year) |
| الشهادة الثانوية السعودية | the Saudi secondary certificate |
| مفتوح الآن / مغلق / لم يفتح بعد | open now / closed / not open yet |
| قائمتي | My list |
| الأدلة | Guides |
| المصدر | Source |

Rules: plain, respectful English for a Saudi high school student. Add nothing that isn't in the Arabic: no extra advice or softening, and keep hedges and conditions exactly. Keep numbers, dates and Latin names exactly. Our Arabic summary of an official text is translated as our summary, never presented as an official quote. English pages say once, near the sources (About page + footer line), that the English is our translation and the official source decides. Official sources may be in Arabic only; that's fine, a small "(in Arabic)" where it helps.

## Things to watch
- `scripts/i18n_worklist.py` finds literals automatically; the tests are the real check. Python-built strings use `tf`, and keys hold `{name}` placeholders, which the fact-matching test must ignore.
- A few Arabic keys are one word that could need two English words by context; split the key if so (for example `في`, `من`).
- `نتائج` search in Arabic on English pages returns nothing: fine, the hint says to use English.
