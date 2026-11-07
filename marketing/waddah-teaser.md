# وضّاح's teaser: the X post and the kit (decisions 082, 083)

Drafts for the owner to review and post. Every line comes from `data/waddah.json` or the plan (§6); nothing here promises
more than `/waddah` says. Guardrails: say it's AI, no accuracy figures, no privacy promise beyond "we never ask for your
name, grades or ID".

## The kit ($0, made on your laptop)

Run the site, then `node marketing/src/waddah_cards.mjs`. It writes:

- `app/static/img/waddah-og.png`: the preview WhatsApp and X show for `/waddah` (committed);
- `marketing/out/waddah-story.png`: a 9:16 still for Snapchat, X or a WhatsApp status;
- `marketing/out/waddah-dawn.mp4`: a 6-second 9:16 clip, the night lightening until the light rises (needs ffmpeg).

`marketing/out/` is git-ignored: the files stay on your machine.

## The post (Arabic, X)

> وضّاح قادم في ديسمبر.
>
> دليلك الذكي في واضح: اسأله عن الابتعاث والجامعات والاختبارات، فيجيبك من المصادر الرسمية ويريك من أين عرف.
>
> ماذا ستسأله أول مرة؟ اكتب سؤالك في الردود.
>
> wadihguide.com/waddah

Attach the clip (`waddah-dawn.mp4`) or the still. The replies become the eval seed's student questions
(`docs/specs/eval-seed.json`, "from X replies"): copy the questions only, never names or handles.

## Three follow-up posts, one promise each

1. «من المصدر: مع كل جواب رابط مصدره الرسمي، ولا يعرض جملة لا يجد مصدرها.»
2. «بلا تخمين: إن لم يجد الجواب قال "لا أعرف"، ودلّك على الجهة المختصة.»
3. «بلا بياناتك: لا يسألك عن اسمك أو درجاتك أو رقم هويتك.»

## Before posting (owner)

- The name check: SAIP (the Saudi trademark register), the app stores, an X handle.
- Read `/waddah` on your phone in both languages.
