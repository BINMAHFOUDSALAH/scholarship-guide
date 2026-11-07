# Accounts: sign-in for students who choose وضّاح (Phase 2 spec)

**Status:** written in Phase 1 Part C (C6, 2026-11-07), built in Phase 2 (from 2026-11-25). Decisions 014–016, 078, 082, 083.
The answer engine: [agent.md](agent.md).

## 1. The rule

**The site stays fully usable without an account.** Every page, the explorer, «جرّب قبل أن تقرر», «السنة في سطر» and
«خطتي» on the device work as they do today. An account exists for one reason now: to use وضّاح. A second benefit comes
with it: the plan on every device.

## 2. The moment of sign-in

- Shown only when a student asks وضّاح something, or taps «دخول» (the header slot behind `accounts_open` in
  `data/waddah.json`, already in `base.html`).
- The sheet says why, as a benefit, in one line: «احفظ خطتك على كل أجهزتك، واسأل وضّاح.», then what we keep (§4) and
  what we never ask for. Then email + password. No social sign-in in v1 (decision 078).
- Never a wall in front of content; never a pop-up on arrival.

## 3. Sign-in

- **Email + password.** Passwords hashed with a slow, salted algorithm (Argon2id, or bcrypt if the host can't run it);
  at least 10 characters; checked against a short list of common passwords. No password rules beyond that.
- **Email verification** before وضّاح answers (one link, valid 24 hours).
- **Password reset** by email (one link, valid 1 hour, single use).
- **Sessions:** a server-side session id in a `Secure; HttpOnly; SameSite=Lax` cookie, 30 days, rotated at sign-in;
  sign out everywhere from the account page.
- **CSRF:** a token on every POST form; `SameSite=Lax` as a second layer.
- **Rate limits:** sign-in and reset by email and by IP (e.g. 5 tries in 15 minutes), with a neutral message that never
  says whether an email has an account.

## 4. What we keep (and nothing else)

| Kept | Why |
|---|---|
| Email address | sign-in, verification, reset |
| Password hash | sign-in |
| Created / last sign-in dates | security, deleting stale accounts |
| The plan: `{"v": 1, "items": [{type, id, status, updated}]}` | the same JSON as `localStorage["wadih:plan"]` (`app/plan.py`) |
| The grade slug (optional) | «صفّك» on every device, like `wadih:grade` today |
| Counts of questions asked (per day) | the rate limit and the daily cap |

**Never:** name, national ID, phone, grades, scores, passport, school, the questions or the answers. The plan holds no
grades or IDs by design, so plan-aware answers can't leak them.

## 5. The plan moves in

- At first sign-in, if this browser holds a plan, offer once: «انقل خطتك من هذا الجهاز إلى حسابك» (merge, newest status
  wins per item, `plan.clean()` on the server, ≤ 100 items).
- Signed in, the page reads and writes the account's plan (the same POST rows, `.ics` and hub); the device copy stays
  as a cache.
- Signed out, nothing changes from today.

## 6. Deletion and export

- «احذف حسابي» on the account page: deletes the account, its plan and its sessions at once (no 30-day limbo); the
  confirmation email is the last message we send.
- «نزّل بياناتي»: the email, dates and plan as JSON.
- Accounts with no sign-in for 24 months are deleted after one email warning.

## 7. Minors and the PDPL (owner's review, before any data is collected)

- Most users are under 18. Before launch, the owner reviews the Personal Data Protection Law and its regulations for:
  consent for minors (whether a guardian's consent is needed and how it's recorded); transfer outside the Kingdom
  (the host in Frankfurt, Anthropic's processing); a privacy notice in Arabic and English; the breach notice duty.
- Until that review is done and written into `docs/decisions.md`, accounts stay off (`accounts_open: false`).

## 8. Infrastructure (ask before spending, CLAUDE.md)

- **Database:** Postgres (the host's managed instance, or SQLite on a persistent disk for the first weeks if the owner
  prefers $0); migrations with Alembic. Three tables: `users`, `plans` (user id → plan JSON, updated), `sessions`.
- **Email:** a transactional service with a free tier, sending only verification, reset and the deletion receipt; an
  SPF/DKIM-signed sender on wadihguide.com. No marketing email.
- **Secrets:** the host's environment variables; never in the repo; `.env` stays unread (CLAUDE.md).

## 9. Tests (Phase 2)

Sign-up, verify, sign-in, sign-out-everywhere, reset, rate limits, CSRF rejection, the plan merge (newest wins, junk
dropped), deletion removes every row, export matches what's stored, and the whole site still passes its tests with
accounts off.
