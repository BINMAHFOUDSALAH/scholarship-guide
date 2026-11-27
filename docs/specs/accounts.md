# Wadih accounts

Accounts give students access to وضّاح, an editable profile, and a place to save the next steps they choose. Build this after the redesign, alongside the [agent](agent.md). See the [roadmap](../plan.md) for rollout.

## Sign-in experience

- Keep Wadih’s public guides, University Finder, and exploration tools free to browse.
- Offer Google sign-in when a student chooses to use وضّاح. Explain the benefit in clear Arabic: «سجّل الدخول لاستخدام وضّاح وحفظ خطواتك في خطتي.»
- After sign-in, return students to the page or agent task they started. Each new account starts with a fresh «خطتي».

## Authentication and access

- Verify Google sign-in on the server. Link the Wadih account to Google’s stable `sub` identifier. Request only the sign-in information Wadih needs.
- Use an expiring, revocable server-side session with a secure, HTTP-only cookie. Apply CSRF protection to requests that change account data.
- Identify the student from the verified session. Check ownership on every profile and plan operation, including actions requested by وضّاح.

## What students can save and control

- Let students add or edit their school year, interests, intended destinations, and optional test scores. Ask for those details when they help answer a question. Make it clear when a detail will be saved to the profile.
- Store saved universities, tasks, and application progress under the student’s account. Use the same server operations for website buttons and وضّاح.
- Add email reminders after the core pilot. Let students opt in, choose which saved universities to follow, and turn reminders off.
- Let students download or delete their account data. On deletion, revoke active sessions and cancel pending reminders.
- Before public rollout, document what Wadih stores, what its providers process, and how consent applies for the students it serves. Test with synthetic accounts in staging.

## Verification

Test guest access, Google sign-in and cancellation, sign-out, session expiry, profile edits, and account deletion. Use two test accounts to verify that each can access and change only its own records. Complete one Arabic browser journey from sign-in through an action in «خطتي». When reminders are enabled, verify that turning them off prevents future sends.