# Launch ad «الشلة»: production guide

The first ad for واضح: a 30-second vertical video (plus 15s and 6s cutdowns) that makes a grade 12 student feel understood and gives one clear reason to open wadihguide.com. Why it's built this way: decision 044.

**Status (2026-10-12):**
- Built and verified: the real site footage, captions, end card, and the build pipeline.
- Still placeholders: the 4 AI shots (Higgsfield) and the 9 voice lines (ElevenLabs).
- The current rough cut is `marketing/out/wadih-ad-30s-9x16.mp4`.

---

## 1. The idea

A school break. His friends already know their plans («أرامكو»، «الرواد»), and one of them turns to him: «وأنت؟ وش ناوي؟». He doesn't know. He opens واضح on his phone, and we see **the real site**: his grade, a search for the major he likes, a university with its official source, saved to «قائمتي». Back with his friends, the honest ending: «لسّه أقرّر… بس عرفت خطوتي الجاية».

**Why this version:**
- **Relatable:** every student has been asked «وش ناوي؟» while friends seemed sure.
- **Honest:** the ad doesn't promise an answer, only a next step. That is exactly what the site does.
- **The product is the hero:** 14 of the 30 seconds are real screen footage of features that exist today.
- **AI only where it's safe and useful:** 4 short scene-setting shots, framed so no AI teenager's face is identifiable (backs, shoulders, hands, soft focus). Reasons:
  - Snapchat stopped recommending *wholly* AI-generated videos in Spotlight (31 Jul 2026).
  - TikTok asks for AI labels and may restrict AI likenesses of minors (unconfirmed, see §8).
  - A brand built on "real, sourced" shouldn't open with a fake face.
- The first AI shot carries «مشهد تمثيلي مولَّد بالذكاء الاصطناعي».

## 2. Script and timing (30s master, 1080×1920)

The captions are exactly what the voice says. Both come from `LINES` in `marketing/src/build_ad.py`, the single source of truth.

| Time | Picture | Voice (file) | Who |
|---|---|---|---|
| 0.0–3.0 | AI shot 1: four boys in thobes on a bench at break, from behind | «أنا خلاص، بقدّم على أرامكو.» (`l01`) | friend 1 |
| 3.0–6.4 | AI shot 2: over a friend's shoulder; our student in soft focus | «وأنا الرواد… أبي أدرس برّا.» (`l02`) · «وأنت؟ وش ناوي؟» (`l03`) | friend 2, friend 3 |
| 6.4–9.6 | AI shot 3: his hands, the phone (screen not visible), a pause | «…ما أدري.» (`l04`) | hero |
| 9.6–23.6 | **Real site**: «ثالث ثانوي» → typing «الذكاء الاصطناعي» → suggestion → results → جامعة هارفارد → scroll to «المصدر: الدليل الاسترشادي، صفحة 5» (ringed) → «احفظ في قائمتي» → «قائمتي» | «لقيت «واضح».» (`l05`) · «اخترت صفّي، وبحثت عن التخصص اللي يعجبني…» (`l06`) · «وكل معلومة معها رابط مصدرها الرسمي.» (`l07`) | hero |
| 23.6–27.0 | AI shot 4: back with friends, from the side; he slips the phone into his pocket | «أنا؟ لسّه أقرّر…» (`l08`) · «بس عرفت خطوتي الجاية.» (`l09`) | hero |
| 27.0–30.0 | End card: logo, «واضح», «مستقبلك بعد الثانوية، بوضوح», **wadihguide.com** (lime chip), «مجاني · بدون تسجيل · دليل مستقل، غير تابع لأي جهة حكومية» | (none) | |

**Cutdowns (built automatically):**
- **15s:** the question, the site, the source, the ending, the end card.
- **6s:** «وأنت؟ وش ناوي؟», the source ring, the end card.

**Honesty rules for every version:**
- Only shipped features appear. No accounts, alerts or chatbot.
- No program logos, so nothing suggests official endorsement.
- No deadlines in captions or voice.
- Re-capture the site before re-posting after 1 Nov 2026: Harvard's "1 نوفمبر 2026" date is visible for about a second.

## 3. How the pieces connect

```
wadihguide.com ──capture_site.mjs (Edge, headless)──► marketing/assets/screen/
Higgsfield (you) ──download──► marketing/assets/clips/shot1–4.mp4
ElevenLabs ──make_voice.py (API)──► marketing/assets/voice/l01–l09.mp3
ElevenLabs Sound Effects (you) ──download──► marketing/assets/ambience.mp3 (optional)
                         └──────────── build_ad.py (ffmpeg + Edge for Arabic text) ──► marketing/out/*.mp4
```

Commands, from the repo root. Re-capture the live site first if it has changed:

```powershell
node marketing/src/capture_site.mjs
```

Make the voice lines (needs §5 done first):

```powershell
.venv\Scripts\python.exe marketing/src/make_voice.py
```

Build the 30s, 15s and 6s videos:

```powershell
.venv\Scripts\python.exe marketing/src/build_ad.py
```

- `marketing/assets/` and `marketing/out/` are git-ignored (big media files).
- CapCut is **optional**: open `wadih-ad-30s-9x16.mp4` there only if you want music or hand-tuned cuts.
- If you add music, use only tracks marked for commercial use. CapCut's library has its own licence terms.

## 4. Higgsfield: the 4 AI shots

**Which plan:** the free plan has **0 credits and no commercial use** (higgsfield.ai/pricing, read 2026-10-11), so it can't make this ad.
- **Starter** ($19/month, 270 credits, commercial use included) is enough: the job needs about 110 credits.
- **Cheaper alternative:** Google Veo 3.1 Lite through the Gemini API at $0.08/sec at 1080p. 4 shots × 5s × 3 takes ≈ **$5**, and Claude can run it from here once you enable billing and give a key the same safe way as ElevenLabs.

**Steps (Starter):**
1. Open https://higgsfield.ai → **Sign up** / **Login** (you do this).
2. **Pricing** → Starter → pay. Your call; check that the renewal is monthly, and cancel after the job if you don't need it.
3. **Image** → model **Nano Banana Pro**, aspect **9:16**. Generate a start frame per shot with *Look + Shot N image* below, 2 options each (≈16 credits). Pick frames where no face is clearly visible.
4. **Video** → model **Kling 3.0**, **1080p**, **5s**, **Image to video**: upload the chosen frame and paste *Shot N motion*. 2–3 takes per shot (≈8 credits each).
5. Download the best take of each → rename to `shot1.mp4` … `shot4.mp4` → put them in `marketing/assets/clips/`.
6. Tell Claude to rebuild. The script trims each clip to its slot (3.0 / 3.4 / 3.2 / 3.4 s).

**Look (paste before every image prompt):**
> Photorealistic documentary still, handheld 35mm look, soft late-morning sun. A public boys' high school courtyard in Riyadh, Saudi Arabia: beige plaster walls, shaded seating area, simple metal benches, a few palm trees. Saudi teenage boys aged 17–18 in clean white thobes, some bareheaded, some wearing a red-and-white shemagh. Natural muted colours. No visible faces: backs, shoulders, hands, or faces turned away and out of focus. No text, no signs, no letters, no logos, no flags. Vertical 9:16.

| Shot | Image prompt (after the Look) | Motion prompt (Kling 3.0, 5s) |
|---|---|---|
| 1 | Four boys sitting side by side on a shaded bench during break, seen from directly behind at shoulder height; one holds a small juice box; relaxed, chatting. | Slow handheld push-in from behind; the boys shift and gesture while talking; light breeze; no camera cuts. |
| 2 | Over-the-shoulder shot: a boy's white-thobe shoulder sharp in the left foreground; across from him a friend sits out of focus (shallow depth of field, face fully blurred); courtyard soft behind. | The blurred friend gestures as if asking a question; the foreground shoulder turns slightly; subtle handheld sway. |
| 3 | Close-up of a teenage boy's hands holding a smartphone on his lap, white thobe sleeves, the screen tilted away from camera (not visible), friends blurred in the background. | The thumb hovers, hesitates, then starts scrolling; background chatter feels distant; very slow push-in. |
| 4 | Three-quarter back view of the same boy among his friends (all faces turned away or out of focus), slipping his phone into his thobe's side pocket, shoulders relaxing. | He puts the phone in his pocket and gives a small nod toward a friend; warm light; gentle handheld drift. |

**Negative prompt / avoid** (where the tool has a field): text, letters, Arabic script, logos, flags, school badges, close-up faces, girls (a boys' school), extra fingers, warped phones.

**Check every take:** six-finger hands, melting thobes, readable fake text, or a face that looks clearly identifiable. Reject those.

## 5. ElevenLabs: the 9 voice lines

**Plan:** auditioning on the free plan is fine, but the free plan has **no commercial licence**. Final audio needs **Starter** ($6 the first month, commercial licence; elevenlabs.io/pricing, read 2026-10-11). This script is ~200 characters, so even 5 takes per line stay far below Starter's 30k credits.

**Steps:**
1. Open https://elevenlabs.io → **Log in** (you).
2. **Voices → Voice Library** → filter **Language: Arabic**, **Accent: Saudi**. Listen and pick **4 young-sounding male voices** that are clearly different from each other:
   - **hero:** calm, a bit unsure.
   - **friend1:** confident.
   - **friend2:** excited.
   - **friend3:** friendly.
   - **Add** each to *My Voices* and copy its **Voice ID**.
   - If none sounds 17–18: **Voice Design**, e.g. "A Saudi young man around 18, Najdi accent, warm, casual, quiet".
3. **Upgrade to Starter** when you're happy with the voices (your decision; Claude never pays).
4. **API key:** profile → **API Keys** → **Create**:
   - Name `wadih-ad`.
   - **Restrict** it to *Text to Speech* (+ *Models: read*).
   - Set a **credit limit** (e.g. 3,000).
   - Copy it once. **Don't paste it into the chat.**
5. Save the key on your laptop, **outside the repo**:
   - Open PowerShell → `notepad $HOME\.wadih\elevenlabs.key`.
   - Create the folder `.wadih` first if Notepad says it doesn't exist: `mkdir $HOME\.wadih`.
   - Paste the key, save.
6. Create `marketing/voices.json` (voice IDs are not secret):
   ```json
   {"hero": "VOICE_ID", "friend1": "VOICE_ID", "friend2": "VOICE_ID", "friend3": "VOICE_ID"}
   ```
7. Tell Claude. It runs `make_voice.py`, checks each line's length against its slot, adjusts timings if needed, and rebuilds. You listen and ask for retakes by line id (e.g. `make_voice.py l04 l09`).
8. **Optional ambience:** ElevenLabs **Sound Effects**:
   - Prompt: "Quiet school courtyard during break, distant teenage boys chatting, light breeze, no music, 10 seconds".
   - Download → `marketing/assets/ambience.mp3`. It plays softly under the first three shots only.

**Pronunciation check:** «برّا», «أقرّر», «الجاية», «واضح». If a voice reads one in formal Arabic, respell the word in `LINES` (keep the caption correct), or try another voice.

## 6. Versions per platform

All 9:16 at 1080×1920, H.264 + AAC, captions burned in (most people watch muted). Text sits between y≈250 and y≈1500, and is centred, to stay clear of the apps' buttons.

| Platform | File | Notes |
|---|---|---|
| Snapchat (Story + Spotlight) | 30s | Saudi Arabia's biggest youth platform. Not "wholly AI", so still eligible for Spotlight recommendations. |
| TikTok | 30s | Turn on **"AI-generated content"** when posting. |
| Instagram Reels / YouTube Shorts | 30s | Add the AI label where offered ("Made with AI" / "Altered or synthetic content"). |
| X | 30s | Pin it; the link goes in the post. |
| WhatsApp / Telegram (counsellors, groups) | 15s | Small file, quick to forward. |
| Later paid tests | 15s and 6s | Only after organic data and your approval. |

**Post text (Arabic, ready to paste; change only the `src`):**
> كل الشلة عارفين وش بيسوون بعد الثانوية… وأنت؟
> واضح: دليل مجاني لطالب الثانوية. برامج الابتعاث، وقوائم جامعاتها، وكل معلومة مع رابط مصدرها الرسمي. بدون تسجيل.
> wadihguide.com/?src=snap
> دليل مستقل، غير تابع لأي جهة حكومية.

`src` values: `snap`, `tiktok`, `ig`, `yt`, `x`, `tg`, `wa`.

## 7. Launch plan (soft launch, organic only)

**Week 1:**
- Post on X (your account) and Snapchat.
- Send the 15s to the Telegram group and 3–5 school counsellors or teachers with one line: «دليل مجاني ومستقل لطلاب الثانوية، ودي برأيكم».

**Week 2:**
- TikTok + Reels.
- Answer every comment and DM. Real questions feed the FAQ step on the roadmap.

**Day 14 review:** compare against the targets, change one thing (the hook line or the first shot), and re-post.

**Measuring without trackers:**
- Every link carries `?src=…`. Uvicorn's access log on Render prints each request with its query, so Render → Logs → search `src=snap` counts visits per platform.
- Copy the counts within a few days; logs aren't kept forever.

| Metric (first 14 days) | Target | Where to read it |
|---|---|---|
| 3-second view rate | ≥ 30% | Each app's analytics |
| Average watch time | ≥ 40% of length | Each app's analytics |
| Visits from `src=` links | ≥ 300 | Render logs |
| Feedback messages on X | ≥ 10 | X DMs / replies |
| Counsellor or teacher groups sharing it | ≥ 3 | Ask them |

**Paid boost:** only after day 14, with your approval and a fixed cap. Before paying, read each platform's current rules on ads that reach under-18s.

## 8. Sources (read 2026-10-11)

- Higgsfield plans, credits, and commercial use per plan: https://higgsfield.ai/pricing
- ElevenLabs plans (commercial licence from Starter): https://elevenlabs.io/pricing
- ElevenLabs API and models: https://elevenlabs.io/docs/api-reference/text-to-speech/convert, https://elevenlabs.io/docs/models
- Gemini API Veo 3.1 prices: https://ai.google.dev/gemini-api/docs/pricing
- Snapchat Spotlight and wholly AI-generated video (31 Jul 2026), news coverage: https://thenextweb.com/news/snapchat-spotlight-bans-ai-generated-videos-recommendations
- Snapchat in Saudi Arabia (25M+ monthly users, 90% aged 13–34), Gulf News: https://gulfnews.com/world/gulf/saudi/snapchat-dominates-among-saudi-youth-with-90-of-users-aged-13-34-1.500043687
- **Not verified:** TikTok's exact rule on AI likenesses of minors. Its guidelines page didn't render for Claude, and the claim comes from a third-party blog: https://www.cinerads.com/blog/tiktok-ai-content-policy. The ad avoids identifiable AI faces either way. Check TikTok's own guidelines before any paid TikTok ad.
