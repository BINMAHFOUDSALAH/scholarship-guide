# وضّاح's teaser: the X post and the kit (decisions 082–084)

Drafts for the owner to review and post. Every line comes from `data/waddah.json` or the plan (§6); nothing here promises
more than the homepage's teaser says (only a teaser until launch: no page, no details, decision 084). Guardrails: say it's AI, no accuracy figures, no privacy promise beyond "we never ask for your
name, grades or ID".

## The kit ($0, made on your laptop)

Run the site, then `node marketing/src/waddah_cards.mjs`. It writes:

- `marketing/out/waddah-og.png`: a 1200×630 share image;
- `marketing/out/waddah-story.png`: a 9:16 still for Snapchat, X or a WhatsApp status;
- `marketing/out/waddah-dawn.mp4`: a 6-second 9:16 clip, the night lightening until the light rises (needs ffmpeg).

`marketing/out/` is git-ignored: the files stay on your machine.

## The post (Arabic, X)

> وضّاح قادم في ديسمبر.
>
> دليلك الذكي في واضح: اسأله عن الابتعاث والجامعات والاختبارات.
>
> ماذا ستسأله أول مرة؟ اكتب سؤالك في الردود.
>
> wadihguide.com

Attach the clip (`waddah-dawn.mp4`) or the still. The replies become the eval seed's student questions
(`docs/specs/eval-seed.json`, "from X replies"): copy the questions only, never names or handles.

## Follow-up posts

Not yet (decision 084): until launch, only the teaser. What وضّاح promises and how it answers are posted when it launches.

## Before posting (owner)

- The name check: SAIP (the Saudi trademark register), the app stores, an X handle.
- Read the teaser on the homepage on your phone in both languages.
