// The explainer's styles: the site's tokens (forest, paper, ink, lime), its fonts, and the phone, menus, chat and
// mascot. Text meant to be read is sized for a phone held upright (Remotion's layout rules: headlines ≥ 84 px on a
// 1080 px frame, supporting text ≥ 44 px; Shotcraft Q11).
export const CSS = `
:root { --forest: #184b3a; --night: #10372a; --paper: #f6f4ee; --ink: #101713; --lime: #d8ed9b; --mist: #c3cdc6; }
* { box-sizing: border-box; }
body { margin: 0; }
.layer { position: absolute; inset: 0; }
.layer > svg, svg.layer { position: absolute; inset: 0; width: 1080px; height: 1920px; }
#root, .title { font-family: "Noto Naskh Arabic", serif; font-weight: 700; }
div, p, span { font-family: "IBM Plex Sans Arabic", sans-serif; }
.title, .title span { font-family: "Noto Naskh Arabic", serif; font-weight: 700; }
.w { display: inline-block; white-space: pre; }
p { margin: 0; }

#bg { background: radial-gradient(130% 80% at 50% 10%, #215c47 0%, #184b3a 45%, #0f3528 100%); overflow: hidden; }
.glow { position: absolute; width: 1300px; height: 1300px; border-radius: 50%; left: 0; top: 0; }
.glow--lime { background: radial-gradient(closest-side, rgba(216, 237, 155, 0.13), rgba(216, 237, 155, 0)); }
.glow--leaf { background: radial-gradient(closest-side, rgba(70, 140, 108, 0.32), rgba(70, 140, 108, 0)); }
#night svg { display: block; width: 1080px; height: 1920px; }

/* The opening question. */
.question { position: absolute; left: 60px; right: 60px; top: 560px; text-align: center; color: var(--paper); font-size: 128px; line-height: 1.32; direction: rtl; text-shadow: 0 10px 40px rgba(0, 0, 0, 0.35); }

/* The mess. */
#chaos { position: absolute; inset: 0; transform-origin: 540px 960px; }
.it-wrap { position: absolute; }
.it { direction: rtl; color: var(--ink); box-shadow: 0 34px 70px rgba(2, 14, 9, 0.5), 0 8px 18px rgba(2, 14, 9, 0.3); }
.ln { height: 14px; border-radius: 7px; background: #dfe4e1; margin: 0 0 16px; }
.it-browser { background: #fff; border-radius: 22px; overflow: hidden; }
.it-browser .tabs { display: flex; gap: 6px; background: #dfe3e0; padding: 14px 14px 0; }
.it-browser .tab { background: #c9d0cb; color: #44514b; font-size: 22px; padding: 10px 18px 12px; border-radius: 12px 12px 0 0; white-space: nowrap; }
.it-browser .tab.on { background: #fff; color: var(--ink); font-weight: 600; }
.it-browser .url { margin: 16px 22px 0; height: 44px; border-radius: 12px; background: #eef1ef; color: #57635d; font-size: 20px; display: flex; align-items: center; padding: 0 18px; direction: ltr; }
.it-browser .body { padding: 22px 26px 12px; }
.it-pdf { width: 300px; background: #fff; border-radius: 14px; padding: 26px 26px 14px; }
.it-pdf .badge { display: inline-block; background: #c8463c; color: #fff; font-weight: 700; font-size: 24px; line-height: 1; padding: 8px 14px 10px; border-radius: 8px; direction: ltr; }
.it-pdf .name { font-size: 25px; font-weight: 600; margin: 16px 0 20px; }
.it-sticky { width: 310px; min-height: 260px; padding: 36px 32px; font-family: "Noto Naskh Arabic", serif; font-weight: 700; font-size: 46px; line-height: 1.35; color: #3d3410; background: #f4e27a; border-radius: 4px; }
.it-sticky.pink { background: #f3b7c2; color: #4a1f28; }
.it-chat { background: #dff4cf; color: #16261b; font-size: 36px; padding: 22px 32px 26px; border-radius: 34px 34px 8px 34px; white-space: nowrap; }
.it-chat small { display: block; font-size: 20px; color: #5d7064; margin-top: 4px; direction: ltr; text-align: left; }
.it-cal { width: 340px; background: #fff; border-radius: 18px; overflow: hidden; }
.it-cal .top { background: #c8463c; color: #fff; font-weight: 700; font-size: 30px; padding: 12px 22px 16px; }
.it-cal .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; padding: 18px; }
.it-cal .grid i { display: block; height: 30px; border-radius: 50%; background: #eef1ef; position: relative; }
.it-cal .grid i.mark { background: none; box-shadow: inset 0 0 0 4px #c8463c; }
.it-cal .grid i.q::after { content: "؟"; position: absolute; inset: 0; display: grid; place-items: center; color: #c8463c; font-weight: 700; font-size: 24px; }
.it-search { width: 660px; background: #fff; border-radius: 999px; padding: 24px 34px 28px; font-size: 32px; display: flex; gap: 18px; align-items: center; white-space: nowrap; }
.it-search svg { width: 34px; height: 34px; flex: none; }
.it-pill { background: #0b1712; color: var(--paper); font-size: 30px; font-weight: 600; padding: 16px 30px 20px; border-radius: 999px; white-space: nowrap; }
.it-xls { width: 420px; background: #fff; border-radius: 16px; overflow: hidden; }
.it-xls .top { background: #1f7a4a; color: #fff; font-size: 24px; font-weight: 600; padding: 12px 20px 14px; direction: ltr; text-align: right; }
.it-xls table { border-collapse: collapse; width: 100%; font-size: 22px; color: #5b6761; }
.it-xls td { border: 1px solid #e1e5e2; height: 40px; text-align: center; }
.it-note { width: 520px; background: rgba(246, 244, 238, 0.97); border-radius: 30px; padding: 22px 26px 24px; display: flex; gap: 18px; align-items: center; }
.it-note .ic { width: 64px; height: 64px; border-radius: 16px; background: #c8463c; flex: none; display: grid; place-items: center; color: #fff; font-weight: 700; font-size: 34px; }
.it-note b { display: block; font-size: 24px; color: #57635d; font-weight: 600; }
.it-note span { font-size: 30px; font-weight: 600; }
#chaosShade { position: absolute; inset: 0; background: radial-gradient(70% 45% at 50% 52%, rgba(9, 30, 22, 0.92), rgba(9, 30, 22, 0.55)); }
.cw { position: absolute; left: 0; right: 0; text-align: center; font-size: 150px; line-height: 1.25; color: var(--paper); text-shadow: 0 4px 18px rgba(0, 0, 0, 0.6), 0 10px 40px rgba(0, 0, 0, 0.5); }
#sweep { position: absolute; top: -200px; width: 520px; height: 2400px; left: 0;
  background: linear-gradient(90deg, rgba(216, 237, 155, 0) 0%, rgba(216, 237, 155, 0.5) 50%, rgba(216, 237, 155, 0) 100%); filter: blur(30px); }

/* The world the camera moves through. */
#persp { position: absolute; inset: 0; perspective: 2600px; perspective-origin: 540px 1100px; }
#world { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; }
#phone { position: absolute; left: 200px; top: 560px; width: 680px; height: 1280px; border-radius: 96px;
  background: linear-gradient(145deg, #3b4f47 0%, #13201b 30%, #0a1410 70%, #2a3a33 100%);
  box-shadow: 0 60px 120px rgba(2, 14, 9, 0.55), 0 18px 40px rgba(2, 14, 9, 0.35), inset 0 0 0 2px rgba(255, 255, 255, 0.08); }
#phone::before { content: ""; position: absolute; inset: 8px; border-radius: 88px; background: #050b08; }
.side { position: absolute; width: 7px; border-radius: 4px; background: #24332d; }
#screen { position: absolute; left: 20px; top: 20px; width: 640px; height: 1240px; border-radius: 76px; overflow: hidden; background: var(--paper); isolation: isolate; }
#page { position: absolute; left: 0; top: 52px; width: 640px; height: 1188px; overflow: hidden; z-index: 1; }
#page img { position: absolute; left: 0; top: 0; width: 640px; }
#status { position: absolute; left: 0; top: 0; width: 640px; height: 52px; background: var(--paper); display: flex; align-items: center;
  justify-content: space-between; padding: 6px 58px 0; direction: rtl; color: var(--ink); font-weight: 600; font-size: 24px; z-index: 6; }
#status .time { direction: ltr; }
#island { position: absolute; left: 248px; top: 14px; width: 144px; height: 40px; border-radius: 20px; background: #050b08; z-index: 7; }
.menu { position: absolute; background: #ffffff; border-radius: 22px; box-shadow: 0 24px 60px rgba(8, 22, 16, 0.28), 0 0 0 1px rgba(16, 23, 19, 0.08);
  overflow: hidden; transform-origin: 50% 0; z-index: 5; padding: 10px 0; direction: rtl; }
.menu .rows { position: relative; }
.menu .row { height: 66px; display: flex; align-items: center; gap: 16px; padding: 0 26px; font-size: 26px; color: var(--ink); white-space: nowrap; }
.menu .row.hover { background: rgba(24, 75, 58, 0.10); }
.menu .row.press { background: var(--forest); color: var(--paper); }
.menu .tick { width: 24px; height: 24px; flex: none; }
.menu .row span { min-width: 0; overflow: hidden; text-overflow: ellipsis; }

#sheet { position: absolute; left: 0; top: 0; width: 640px; height: 1240px; background: #f1f2f1; z-index: 2; box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.25); }
#sheet .bar { position: absolute; left: 0; right: 0; top: 52px; height: 96px; display: flex; align-items: center; gap: 16px; padding: 0 24px; direction: ltr; border-bottom: 1px solid #d6dad7; }
#sheet .done { font-size: 26px; font-weight: 600; color: #1a6dde; }
#sheet .url { flex: 1; height: 62px; border-radius: 18px; background: #e2e5e3; display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 26px; color: var(--ink); }
#sheet .url svg { width: 20px; height: 24px; }
#sheet .prog { position: absolute; left: 0; top: 146px; height: 5px; background: #1a6dde; border-radius: 0 3px 3px 0; }
#sheet .pg { position: absolute; left: 0; top: 149px; width: 640px; height: 1091px; overflow: hidden; background: #fff; }
#sheet .pg img { width: 640px; display: block; }

/* وضّاح's chat, as it will look (not live yet: «قادم في ديسمبر» in its header). */
#chatui { position: absolute; left: 0; top: 52px; width: 640px; height: 1188px; background: var(--paper); z-index: 3; direction: rtl; color: var(--ink); }
#chatui .head { height: 112px; display: flex; align-items: center; gap: 16px; padding: 0 34px; border-bottom: 2px solid #e1e5e0; background: #fbfaf6; }
#chatui .head svg { width: 54px; height: 54px; }
#chatui .head .title { font-size: 46px; color: var(--forest); line-height: 1; padding-bottom: 8px; }
#chatui .head .soon { margin-inline-start: auto; font-size: 23px; font-weight: 700; color: var(--ink); background: var(--lime); padding: 4px 16px 8px; border-radius: 8px; }
#chatui .list { position: absolute; left: 0; right: 0; top: 114px; bottom: 128px; overflow: hidden; }
#chatui .msgs { position: absolute; left: 0; right: 0; top: 0; padding: 30px 26px 0; }
.cb { position: relative; max-width: 88%; width: fit-content; font-size: 34px; line-height: 1.55; padding: 18px 26px 22px; border-radius: 30px; margin: 0 0 24px; transform-origin: 100% 0; }
.cb--a { background: #fff; color: var(--ink); box-shadow: inset 0 0 0 2px #e2e7e1, 0 6px 18px rgba(16, 23, 19, 0.05); border-start-start-radius: 8px; }
.cb--q { background: var(--forest); color: var(--paper); margin-inline-start: auto; border-start-end-radius: 8px; transform-origin: 0 0; }
.cb ol { margin: 4px 0 0; padding-inline-start: 38px; }
.cb li { margin: 0 0 6px; }
.cb li::marker { color: var(--forest); font-weight: 700; }
.cb .num { background: var(--lime); border-radius: 8px; padding: 0 8px; font-weight: 700; }
.cb .chip { display: inline-flex; align-items: center; gap: 10px; margin-top: 12px; font-size: 22px; color: #2f3d36; background: #eef2eb; padding: 4px 16px 6px 6px; border-radius: 999px; }
.cb .chip b { display: inline-grid; place-items: center; width: 32px; height: 32px; border-radius: 50%; background: var(--forest); color: var(--paper); font-size: 19px; }
.cb--dots { position: absolute; right: 26px; padding: 22px 26px; }
.cb--dots .dots { display: flex; gap: 12px; }
.cb--dots i { width: 14px; height: 14px; border-radius: 50%; background: var(--forest); display: block; }
#chatui .input { position: absolute; left: 24px; right: 24px; bottom: 30px; height: 84px; border-radius: 42px; background: #fff; box-shadow: inset 0 0 0 2px #dbe1dc; display: flex; align-items: center; padding: 0 30px 0 11px; gap: 12px; }
#chatui .input .txt { flex: 1; font-size: 32px; white-space: nowrap; overflow: hidden; }
#chatui .input .ph { color: #8a968f; }
#chatui .input .caret { display: inline-block; width: 3px; height: 38px; background: var(--forest); vertical-align: middle; margin-inline-start: 2px; }
#chatui .input .send { width: 62px; height: 62px; border-radius: 50%; background: var(--forest); display: grid; place-items: center; flex: none; }
#chatui .input .send svg { width: 30px; height: 30px; }

#fx { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; pointer-events: none; }
.ring-halo { fill: none; stroke: var(--lime); stroke-width: 16; stroke-linejoin: round; }
.ring-line { fill: none; stroke: var(--forest); stroke-width: 5; stroke-linejoin: round; }
#cursor { position: absolute; left: 0; top: 0; width: 0; height: 0; z-index: 5; }
#cursor svg { position: absolute; left: -8px; top: -4px; width: 64px; height: 76px; overflow: visible; filter: drop-shadow(0 8px 10px rgba(5, 20, 14, 0.35)); }

/* Words over the phone: a scrim keeps them legible. */
#scrim { position: absolute; left: 0; right: 0; top: 0; height: 760px;
  background: linear-gradient(180deg, #0f3528 0%, #0f3528 76%, rgba(15, 53, 40, 0) 100%); }
#brandbar { position: absolute; top: 56px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 20px; color: var(--paper); }
#brandbar img { width: 70px; height: 70px; border-radius: 22%; box-shadow: 0 0 0 3px rgba(246, 244, 238, 0.18); }
#brandbar span { font-size: 56px; line-height: 1; }
.cap { position: absolute; left: 70px; right: 70px; top: 150px; height: 400px; display: flex; align-items: center; justify-content: center; text-align: center; color: var(--paper); }
.cap p { margin: 0; font-weight: 700; font-size: 80px; line-height: 1.42; text-wrap: balance; }

#brand { position: absolute; left: 0; right: 0; top: 500px; text-align: center; transform-origin: 540px 200px; color: var(--paper); }
#brand .halo { position: absolute; left: calc(50% - 200px); top: -110px; width: 400px; height: 400px; border-radius: 50%; background: radial-gradient(closest-side, rgba(216, 237, 155, 0.35), rgba(216, 237, 155, 0)); }
#brand img { position: relative; width: 220px; height: 220px; display: block; margin: 0 auto 8px; border-radius: 22%; box-shadow: 0 0 0 5px rgba(246, 244, 238, 0.18), 0 30px 70px rgba(0, 0, 0, 0.35); }
#brand .name { position: relative; font-size: 180px; line-height: 1.3; }
#brand .line { position: relative; font-size: 76px; font-weight: 700; color: #eef2ef; margin-top: 6px; text-wrap: balance; }

#wintro { position: absolute; left: 0; right: 0; top: 540px; text-align: center; font-size: 140px; line-height: 1.3; color: var(--paper); }
#wtitle { position: absolute; left: 60px; right: 60px; top: 150px; text-align: center; color: var(--paper); }
#wtitle .mark { display: flex; align-items: center; justify-content: center; gap: 30px; }
#wtitle .mark .title { font-size: 190px; line-height: 1.25; }
#wtitle .when { font-size: 70px; font-weight: 700; color: var(--lime); }
#wtitle .sub { font-size: 52px; line-height: 1.5; color: #dfe5e1; margin: 10px auto 0; }

#end { position: absolute; left: 60px; right: 60px; top: 560px; text-align: center; color: var(--paper); }
#end img { width: 210px; height: 210px; display: block; margin: 0 auto 6px; border-radius: 22%; box-shadow: 0 0 0 5px rgba(246, 244, 238, 0.18), 0 30px 70px rgba(0, 0, 0, 0.35); }
#end .name { font-size: 160px; line-height: 1.3; margin: 0 0 40px; }
#end .url { display: inline-block; direction: ltr; background: var(--lime); color: var(--ink); font-weight: 700; font-size: 76px; padding: 16px 60px 24px; border-radius: 999px; margin: 0 0 44px; box-shadow: 0 20px 60px rgba(216, 237, 155, 0.25); }
#end .note { font-size: 44px; font-weight: 600; color: #e3e9e5; }

/* وضّاح, the mascot. */
.mascot { position: absolute; transform-origin: 50% 100%; }
.mascot img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; filter: drop-shadow(0 26px 30px rgba(2, 14, 9, 0.35)); }
.m-shadow { position: absolute; border-radius: 50%; background: radial-gradient(closest-side, rgba(2, 14, 9, 0.55), rgba(2, 14, 9, 0)); }
#flash { position: absolute; left: 0; top: 0; width: 2400px; height: 2400px; margin: -1200px 0 0 -1200px; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(236, 248, 200, 0.95), rgba(216, 237, 155, 0.5) 30%, rgba(216, 237, 155, 0) 70%); }
#grain { position: absolute; inset: 0; opacity: 0.05; mix-blend-mode: overlay; pointer-events: none; }

/* The teaser's own art (style.css, decision 087). */
.art-moon { fill: #f6f4ee; opacity: 0.92; } .art-city { fill: #1d5040; } .art-city-cols path { fill: none; stroke: #10372a; stroke-width: 3; } .art-city-clock { fill: #10372a; }
.art-dune--mid { fill: #154434; } .art-dune-edge { fill: none; stroke: #f6f4ee; stroke-opacity: 0.14; stroke-width: 1.5; }
.art-dune--near { fill: #0e3125; } .art-palm-trunk { fill: #7f998d; } .art-palm-frond { fill: #9fb3aa; } .art-palm-frond--back { fill: #6f8a7e; }
.help-leg, .help-arm, .help-laptop, .help-screen, .help-rim { fill: none; stroke-linecap: round; stroke-linejoin: round; }
.help-leg { stroke: #c9d3cd; stroke-width: 15; } .help-arm { stroke: #dfe5e1; stroke-width: 9; } .help-shoe { fill: #f6f4ee; }
.help-body { fill: #dfe5e1; } .help-head { fill: #f6f4ee; } .help-hair { fill: #081d16; } .help-ear { fill: #f6f4ee; }
.help-rim { stroke: var(--lime); stroke-width: 2.2; stroke-opacity: 0.85; } .help-glow { fill: var(--lime); }
.help-laptop { stroke: #9fb3aa; stroke-width: 5; } .help-screen { stroke: var(--lime); stroke-width: 4.5; }
/* ---------- The wide film (decision 094): the desktop site in a browser window, the words in a column on the right. ---------- */
.wide .layer > svg, .wide svg.layer, .wide #night svg, .wide #fx { width: 1920px; height: 1080px; }
.wide #persp { perspective: 3000px; perspective-origin: 672px 540px; }
.wide #world { width: 1920px; height: 1080px; }
.wide #chaos { transform-origin: 960px 540px; }
.wide .question { top: 240px; left: 120px; right: 120px; font-size: 116px; }
.wide .cw { font-size: 124px; }
.wide #chaosShade { background: radial-gradient(60% 70% at 50% 50%, rgba(9, 30, 22, 0.92), rgba(9, 30, 22, 0.55)); }
.wide #sweep { height: 1500px; top: -200px; }
#browser { position: absolute; border-radius: 14px; overflow: hidden; background: #e7eae8; isolation: isolate;
  box-shadow: 0 50px 110px rgba(2, 14, 9, 0.55), 0 14px 34px rgba(2, 14, 9, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.08); }
#browser .tabs { position: absolute; left: 0; right: 0; top: 0; height: 38px; display: flex; gap: 6px; padding: 5px 14px 0; direction: rtl; background: #dde1de; }
#browser .tab { position: relative; width: 250px; height: 33px; border-radius: 10px 10px 0 0; display: flex; align-items: center; gap: 9px; padding: 0 12px; color: #4a5650; font-size: 15px; font-weight: 600; overflow: hidden; white-space: nowrap; flex: none; }
#browser .tab.on { background: #f7f8f7; color: var(--ink); }
#browser .tab img { width: 18px; height: 18px; border-radius: 22%; flex: none; }
#browser .tab .tt { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
#browser .tab .globe { width: 16px; height: 16px; border-radius: 50%; border: 2px solid #6b7771; flex: none; }
#browser .tab .x { width: 10px; height: 10px; flex: none; background: linear-gradient(45deg, transparent 44%, #6b7771 44%, #6b7771 56%, transparent 56%), linear-gradient(-45deg, transparent 44%, #6b7771 44%, #6b7771 56%, transparent 56%); }
#browser .plus { width: 26px; height: 26px; margin-top: 3px; flex: none; background: linear-gradient(#6b7771, #6b7771) center / 12px 2px no-repeat, linear-gradient(#6b7771, #6b7771) center / 2px 12px no-repeat; }
#browser .toolbar { position: absolute; left: 0; right: 0; top: 38px; height: 46px; background: #f7f8f7; border-bottom: 1px solid #d9ddda; }
#browser .navs { position: absolute; right: 18px; top: 11px; }
#browser .addr { position: absolute; left: 190px; right: 190px; top: 6px; height: 34px; border-radius: 17px; background: #e9ece9; display: flex; align-items: center; justify-content: center; gap: 9px; font-size: 16px; color: #2c3631; font-weight: 500; }
#wpage { position: absolute; left: 0; top: 84px; width: 1152px; height: 720px; overflow: hidden; background: var(--paper); z-index: 1; }
#zw { position: absolute; left: 0; top: 0; width: 1152px; height: 720px; transform-origin: 0 0; }
#wpage img { position: absolute; left: 0; top: 0; width: 1152px; }
#browser .official { position: absolute; left: 0; top: 0; width: 1152px; height: 720px; overflow: hidden; background: #fff; z-index: 4; }
#browser .official img { width: 1152px; display: block; }
#browser > .prog { position: absolute; left: 0; top: 84px; height: 3px; background: #1a6dde; z-index: 6; }
.fxp { position: absolute; overflow: visible; pointer-events: none; z-index: 6; }
#zw .menu { z-index: 5; }
.wide .menu { border-radius: 10px; padding: 10px 0; box-shadow: 0 16px 40px rgba(8, 22, 16, 0.25), 0 0 0 1px rgba(16, 23, 19, 0.1); }
.wide .menu .row { height: 44px; font-size: 19px; gap: 10px; padding: 0 16px; }
.wide .menu .tick { width: 16px; height: 16px; }
#chatcard { position: absolute; border-radius: 26px; overflow: hidden; background: var(--paper); box-shadow: 0 50px 110px rgba(2, 14, 9, 0.55), 0 14px 34px rgba(2, 14, 9, 0.35); }
.wide #chatui { top: 0; width: 100%; height: 100%; }
.wide #fx .ring-halo { stroke-width: 10; }
.wide #fx .ring-line { stroke-width: 3.5; }
.wide #cursor svg { left: -4px; top: -2px; width: 30px; height: 36px; filter: drop-shadow(0 4px 5px rgba(5, 20, 14, 0.35)); }
.wide #scrim { left: auto; right: 0; top: 0; bottom: 0; width: 680px; height: auto;
  background: linear-gradient(270deg, #0f3528 0%, #0f3528 74%, rgba(15, 53, 40, 0) 100%); }
.wide #brandbar { left: 1290px; right: 50px; top: 74px; gap: 16px; }
.wide #brandbar img { width: 58px; height: 58px; }
.wide #brandbar span { font-size: 46px; }
.wide .cap { left: 1296px; right: 52px; top: 160px; height: 480px; }
.wide .cap p { font-size: 64px; line-height: 1.45; }
.wide #brand { left: 160px; right: 760px; top: 250px; transform-origin: 500px 200px; }
.wide #brand .halo { left: calc(50% - 200px); }
.wide #brand img { width: 190px; height: 190px; }
.wide #brand .name { font-size: 150px; }
.wide #brand .line { font-size: 62px; }
.wide #wintro { left: 1296px; right: 52px; top: 360px; font-size: 110px; }
.wide #wtitle { left: 1296px; right: 52px; top: 250px; }
.wide #wtitle .mark { gap: 20px; }
.wide #wtitle .mark .title { font-size: 124px; }
.wide #wtitle .mark svg { width: 92px; height: 92px; }
.wide #wtitle .when { font-size: 52px; }
.wide #wtitle .sub { font-size: 40px; }
.wide #end { left: 160px; right: 760px; top: 230px; }
.wide #end img { width: 170px; height: 170px; }
.wide #end .name { font-size: 132px; margin: 0 0 30px; }
.wide #end .url { font-size: 60px; padding: 12px 50px 20px; margin: 0 0 34px; }
.wide #end .note { font-size: 36px; }
`;
