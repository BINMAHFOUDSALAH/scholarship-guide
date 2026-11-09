// The explainer's choreography (marketing/README.md §9, decisions 089–092), in seconds, from the captured site data.
// Plain JavaScript with no imports, so the Remotion composition (the picture) and explainer.mjs (the music and its
// sounds) read the same times: every click, swipe and keystroke the music hears is the one the picture shows.
// Times are in beats of the music (100 BPM): B(scene, beats) from a scene's start, E(scene, beats) from its end.

// Two formats (decision 094). tall: the phone site in a phone, 9:16. wide: the desktop site in a browser window, 16:9,
// beside a column for the words. K: captured CSS px → screen px; SCREEN: the device's screen in the world; BAR: the
// status bar (phone) or the browser's tabs and toolbar above the page; VH: CSS px of the page that show.
export const GEOM = {
  tall: { id: "tall", W: 1080, H: 1920, K: 640 / 390, SCREEN: { x: 220, y: 580, w: 640, h: 1240 }, BAR: 52, ROW: 66, MENU_W: 430, MAX_ROWS: 8, radius: 76 },
  wide: { id: "wide", W: 1920, H: 1080, K: 0.8, SCREEN: { x: 96, y: 138, w: 1152, h: 804 }, BAR: 84, ROW: 44, MENU_W: 330, MAX_ROWS: 8, radius: 14 },
};
for (const g of Object.values(GEOM)) { g.PAGE = { x: g.SCREEN.x, y: g.SCREEN.y + g.BAR }; g.VH = Math.round((g.SCREEN.h - g.BAR) / g.K); }

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, p) => a + (b - a) * p;
export const ease = {
  lin: (p) => p,
  out: (p) => 1 - Math.pow(1 - p, 3),
  in: (p) => p * p * p,
  io: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
  expo: (p) => (p >= 1 ? 1 : 1 - Math.pow(2, -9 * p)) / (1 - Math.pow(2, -9)),
  back: (p) => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); },
};
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const win = (t, a, b, fi = 0.25, fo = 0.25) => Math.min(seg(t, a, a + fi), 1 - seg(t, b - fo, b));
// Keyframes: [[t, value, easing?], …]; values are numbers or arrays of numbers.
export function kf(t, frames) {
  if (t <= frames[0][0]) return frames[0][1];
  for (let i = 1; i < frames.length; i++) {
    const [t1, v1, e] = frames[i], [t0, v0] = frames[i - 1];
    if (t <= t1) {
      const p = ease[e || "io"](t1 === t0 ? 1 : (t - t0) / (t1 - t0));
      return Array.isArray(v0) ? v0.map((a, j) => lerp(a, v1[j], p)) : lerp(v0, v1, p);
    }
  }
  return frames[frames.length - 1][1];
}
export const onWorld = (G, r, scroll, slide = 0) => ({ x: G.PAGE.x + slide + r.x * G.K, y: G.PAGE.y + (r.y - scroll) * G.K, w: r.w * G.K, h: r.h * G.K });
export const mid = (b) => [b.x + b.w / 2, b.y + b.h / 2];
export const union = (a, b) => { const x = Math.min(a.x, b.x), y = Math.min(a.y, b.y); return { x, y, w: Math.max(a.x + a.w, b.x + b.w) - x, h: Math.max(a.y + a.h, b.y + b.h) - y }; };
// Words of a line, each kept whole (a lime part inside a word, like «و*اختبارات*», stays on the same line as the rest);
// *stars* mark the lime parts. w is the word's plain text.
export function words(text) {
  const out = [];
  let lime = false;
  for (const tok of text.split(/(\s+)/)) {
    if (!tok) continue;
    if (!tok.trim()) { if (out.length) out[out.length - 1].space += tok; continue; }
    const segs = [];
    for (const part of tok.split(/(\*)/)) { if (part === "*") { lime = !lime; continue; } if (part) segs.push({ t: part, lime }); }
    if (segs.length) out.push({ segs, space: "", w: segs.map((x) => x.t).join("") });
  }
  return out;
}

// Where a menu sits on the screen (screen px), opened under its select (or above it if there's no room).
export function menuBox(G, d, spec) {
  const { K, ROW, MENU_W, MAX_ROWS, BAR, SCREEN } = G;
  const sh = d.screens[spec.shot], r = d.rects[spec.shot][spec.id];
  const sx = r.x * K, sy = BAR + (r.y - sh.hold) * K, sw = r.w * K, shh = r.h * K;
  const n = Math.min(MAX_ROWS, d.menus[spec.id].items.length), h = n * ROW + 20;
  const w = Math.max(MENU_W, sw);
  const right = sx + sw, left = clamp(right - w, 20, SCREEN.w - 20 - w);
  let top = sy + shh + (G.id === "wide" ? 4 : 10);
  if (top + h > SCREEN.h - 30) top = sy - 10 - h;
  const off = Math.max(0, d.menus[spec.id].pick - (n - 1));
  return { left, top, w, h, n, off, sel: { x: sx, y: sy, w: sw, h: shh } };
}
const menuRowWorld = (G, d, spec, i) => { const m = menuBox(G, d, spec); return [G.SCREEN.x + m.left + m.w / 2 + (G.id === "wide" ? 20 : 40), G.SCREEN.y + m.top + 10 + (i - m.off) * G.ROW + G.ROW / 2]; };

// The mess: generic things a student juggles (no real list, date or score in any of them), placed by their centre.
export const CHAOS = [
  { at: 0, x: 520, y: 760, r: -4, kind: "browser", tabs: ["شروط القبول", "قائمة الجامعات", "المواعيد"], url: "…/admissions/requirements", lines: 6 },
  { at: 0.5, x: 250, y: 1190, r: -9, kind: "pdf", name: "قائمة الجامعات.pdf", lines: 7 },
  { at: 1, x: 830, y: 1250, r: 7, kind: "sticky", text: "آخر موعد؟" },
  { at: 1.5, x: 560, y: 1530, r: 3, kind: "chat", text: "كم درجة آيلتس المطلوبة؟" },
  { at: 2, x: 840, y: 520, r: 8, kind: "cal" },
  { at: 2.75, x: 470, y: 400, r: -2, kind: "search", text: "شروط القبول في جامعة…" },
  { at: 3.5, x: 300, y: 1720, r: -5, kind: "pill", text: "23 تبويبًا مفتوحًا" },
  { at: 4, x: 240, y: 640, r: -10, kind: "sticky", pink: true, text: "IELTS أم TOEFL؟" },
  { at: 4.5, x: 800, y: 1600, r: 10, kind: "pdf", name: "دليل المسار.pdf", lines: 6 },
  { at: 5, x: 600, y: 1090, r: -6, kind: "xls", name: "جامعاتي.xlsx" },
  { at: 5.5, x: 620, y: 260, r: 3, kind: "note", title: "تذكير", text: "راجع المواعيد قبل فوات الأوان" },
  { at: 6, x: 420, y: 1360, r: 6, kind: "browser", w: 520, tabs: ["التخصصات", "IELTS"], url: "…/international/apply", lines: 4 },
];

export function buildTimeline(d) {
  const G = GEOM[d.fmt || "tall"];
  return { G, ...(G.id === "wide" ? buildWide(d, G) : buildTall(d, G)) };
}

function buildTall(d, G) {
  const { K, SCREEN, VH } = G;
  const onW = (r, sc0, sl) => onWorld(G, r, sc0, sl);
  const P = d.plan, BEAT = P.beat;
  const S = Object.fromEntries(P.scenes.map((s) => [s.id, s]));
  const B = (id, beats) => S[id].start + beats * BEAT;
  const E = (id, beats) => S[id].start + S[id].dur - beats * BEAT;
  const sh = d.screens, rc = d.rects;
  const sc = (name, y) => clamp(Math.round(y), 0, Math.max(0, sh[name].h - VH));
  const mine = rc.results.rows.find((r) => r.mine);
  const items = rc.home.items, last = items[items.length - 1].card;
  const s = {
    hNow: sc("home", rc.home.now.y - 70),
    hEnd: sc("home", last.y + last.h - VH + 60),
    rMap: sc("rw0", rc.rw.chart.y + rc.rw.chart.h / 2 - VH * 0.45),
    rTog: sh.f0.hold,
    f0: sh.f0.hold, f1: sh.f1.hold, f2: sh.f2.hold, f3: sh.f3.hold,
    f3b: sc("f3", (rc.f3.applied ? rc.f3.applied.y : rc.f3.country.y + 200) - 150),
    top: sc("results", rc.results.applied.y - 150),
    mine: sc("results", mine.row.y - 150),
    uDate: sc("uni", rc.uni.date.y - 300),
    uEng: sc("uni", rc.uni.english.y - 330),
    pMine: sc("plan", (rc.plan.status || rc.plan.mine).y - 260),
  };
  const PL = (b) => B("plan", b);

  // Screens: opacity, scroll (CSS px) and slide (screen px).
  const fl = B("filters", 0);
  const shots = {
    home: { o: [[0, 1], [B("map", 0) - 0.001, 1], [B("map", 0), 0]],
      s: [[B("home", 2.5), 0], [B("home", 4.5), s.hNow, "expo"], [B("home", 7.1), s.hNow], [B("home", 9.4), s.hEnd, "io"]] },
    rw0: { o: [[B("map", 0) - 0.001, 0], [B("map", 0), 1], [B("map", 3.25), 1], [B("map", 3.4), 0], [B("map", 6.2), 0], [B("map", 6.35), 1], [fl + 1.05 * BEAT, 1], [fl + 1.2 * BEAT, 0]],
      s: [[B("map", 0), s.rMap], [B("map", 6.6), s.rMap], [B("map", 7.9), s.rTog, "io"]] },
    rw1: { o: [[B("map", 3.25), 0], [B("map", 3.4), 1], [B("map", 6.2), 1], [B("map", 6.35), 0]], s: [[0, s.rMap]] },
    f0: { o: [[fl + 1.05 * BEAT, 0], [fl + 1.2 * BEAT, 1], [B("filters", 4.45), 1], [B("filters", 4.6), 0]], s: [[0, s.f0]] },
    f1: { o: [[B("filters", 4.45), 0], [B("filters", 4.6), 1], [B("filters", 7.05), 1], [B("filters", 7.2), 0]], s: [[0, s.f1]] },
    f2: { o: [[B("filters", 7.05), 0], [B("filters", 7.2), 1], [B("filters", 9.85), 1], [B("filters", 10), 0]], s: [[0, s.f2]] },
    f3: { o: [[B("filters", 9.85), 0], [B("filters", 10), 1], [B("filters", 13.6), 1], [B("filters", 14.4), 0]], s: [[B("filters", 10.8), s.f3], [B("filters", 12.2), s.f3b]] },
    results: {
      o: [[B("filters", 13.6), 0], [B("filters", 14.4), 1], [B("results", 6.9), 1], [B("results", 7.8), 0]],
      s: [[B("results", 0.5), s.top], [B("results", 3.6), s.mine, "expo"]],
      x: [[B("results", 6.9), 0], [B("results", 7.7), 210, "out"]],
    },
    uni: { o: [[B("results", 6.9) - 0.001, 0], [B("results", 6.95), 1], [PL(2.87), 1], [PL(2.875), 0]],
      s: [[B("uni", 0.8), 0], [B("uni", 1.9), s.uDate, "io"], [B("uni", 5.4), s.uDate], [B("uni", 6.6), s.uEng, "io"], [PL(0.9), s.uEng], [PL(1.8), 0, "expo"]],
      x: [[B("results", 6.9), -640], [B("results", 7.7), 0, "out"]] },
    // «احفظ في خطتي» pressed: the same page saved, then a whip to «خطتي».
    uniS: { o: [[PL(2.87), 0], [PL(2.875), 1], [PL(4.85) - 0.001, 1], [PL(4.85), 0]], s: [[0, 0]] },
    // Until the light lands, the header still shows the count before the save (the unsaved page's top strip).
    uniH: { src: "uni", clip: rc.uni.planLink.y + rc.uni.planLink.h + 8, o: [[PL(2.87), 0], [PL(2.875), 1], [PL(3.75), 1], [PL(3.85), 0]], s: [[0, 0]] },
    plan: { o: [[PL(4.85) - 0.001, 0], [PL(4.85), 1], [B("waddah", 3), 1], [B("waddah", 3.1), 0]], s: [[PL(4.85), 0], [PL(6.8), 0], [PL(7.9), s.pMine, "io"]] },
  };

  // The menus: open on a click, the cursor goes down the list, the pick closes them.
  const menus = [
    { id: "track", shot: "f0", open: B("filters", 3.0), pick: B("filters", 4.4) },
    { id: "field", shot: "f1", open: B("filters", 5.6), pick: B("filters", 7.0) },
    { id: "country", shot: "f2", open: B("filters", 8.2), pick: B("filters", 9.8) },
  ];

  // Focus points (world px) for the camera and the cursor.
  const Wp = (r, sc0) => mid(onW(r, sc0));
  const status = items[0].status;
  const pStatus = Wp(status, s.hNow);
  const pCard = [mid(onW(items[0].card, s.hNow))[0], pStatus[1] + 40];
  const sR = onW(status, s.hNow), pPoint = [sR.x + sR.w + 34, sR.y + sR.h + 26];
  const chart = Wp(rc.rw.chart, s.rMap);
  const starP = Wp({ x: rc.rw.star.x, y: rc.rw.star.y, w: 0, h: 0 }, s.rMap);
  const starZone = mid(union(onW({ x: rc.rw.star.x - 20, y: rc.rw.star.y - 20, w: 40, h: 40 }, s.rMap), onW(rc.rw.readout, s.rMap)));
  const toggle = Wp(rc.f0.toggle, s.rTog);
  const sel = (name, id) => Wp(rc[name][id], sh[name].hold);
  const panel = mid(onW(union(union(rc.f0.track, rc.f0.field), rc.f0.country), s.f0));
  const head = Wp(union(mine.rank, mine.name), s.mine);
  const name = Wp(mine.name, s.mine);
  const date = Wp(rc.uni.date, s.uDate), eng = Wp(rc.uni.english, s.uEng), btn = Wp(rc.uni.button, s.uEng);
  const addr = { x: SCREEN.x + 130, y: SCREEN.y + 52 + 17, w: 380, h: 62 };
  const doneP = [SCREEN.x + 62, SCREEN.y + 52 + 50];
  const saveP = Wp(rc.uni.save, 0), linkP = Wp(rc.uni.planLink, 0);
  const lr = onW(rc.uni.planLink, 0), linkTip = [lr.x + lr.w * 0.72, lr.y + lr.h * 0.62];
  const saveZone = mid(union(onW(rc.uni.save, 0), onW(rc.uni.planLink, 0)));
  const hubP = rc.plan.hub ? [540, Math.min(onW(rc.plan.hub, 0).y + 260, 1500)] : [540, 1200];
  const statusP = Wp(rc.plan.status || rc.plan.mine, s.pMine);

  // Camera: [zoom, focus x, focus y, anchor x, anchor y, drop, tilt x, tilt y]. No hand-held drift: it stays still
  // unless it means to move (Shotcraft Q3).
  const cam = (z, f, cy = 1180) => [z, f[0], f[1], 540, cy, 0, 0, 0];
  const OFF = [1, 540, 1200, 540, 1220, 1500, 26, -16];
  const REST = [1, 540, 1200, 540, 1220, 0, 0, 0];
  const FALL = [0.9, 540, 1200, 540, 1220, 1900, 34, 10];
  // In the chat the phone sits right of centre, so وضّاح can stand beside it.
  const CHAT = [1.0, 540, 1290, 650, 1300, 0, 0, 0];
  const camFrames = [
    [0, OFF], [B("home", 0), OFF], [B("home", 2), REST, "out"],
    [B("home", 4.5), REST], [B("home", 5.3), cam(1.45, pCard, 1160)], [B("home", 6.8), cam(1.45, pCard, 1160)],
    [B("home", 7.6), [1.1, 540, 1210, 540, 1220, 0, 0, 0]], [B("map", 0.4), REST],
    [B("map", 0.9), REST], [B("map", 1.8), cam(1.42, chart, 1180)], [B("map", 2.9), cam(1.42, chart, 1180)],
    [B("map", 3.5), cam(1.55, starZone, 1180)], [B("map", 6.2), cam(1.55, starZone, 1180)], [B("map", 7.3), REST],
    [B("filters", 0.2), REST], [B("filters", 0.9), cam(1.2, toggle, 1150)], [B("filters", 1.6), cam(1.2, toggle, 1150)],
    [B("filters", 2.4), cam(1.32, panel, 1160)],
    // While a menu is open the camera frames it with its select, so its whole list shows.
    ...menus.flatMap((spec) => {
      const bx = menuBox(G, d, spec);
      const u = union({ x: SCREEN.x + bx.sel.x, y: SCREEN.y + bx.sel.y, w: bx.sel.w, h: bx.sel.h }, { x: SCREEN.x + bx.left, y: SCREEN.y + bx.top, w: bx.w, h: bx.h });
      const f = cam(Math.min(1.32, 1250 / u.h), mid(u), 1240);
      return [[spec.open - 0.05, null], [spec.open + 0.4, f], [spec.pick + 0.12, f]];
    }),
    [B("filters", 10.4), cam(1.32, panel, 1160)],
    [B("filters", 12.2), cam(1.16, [540, 1180], 1160)],
    [B("results", 0.6), cam(1.12, [540, 1210], 1200)],
    [B("results", 3.4), cam(1.12, [540, 1210], 1200)],
    [B("results", 4.4), cam(1.34, head, 1140)],
    [B("results", 6.6), cam(1.34, head, 1140)],
    [B("results", 7.8), cam(1.06, [540, 1215], 1210)],
    [B("uni", 1.6), cam(1.06, [540, 1215], 1210)],
    [B("uni", 2.6), cam(1.45, date, 1170)], [B("uni", 5.2), cam(1.45, date, 1170)],
    [B("uni", 6.0), cam(1.12, [540, 1215], 1200)],
    [B("uni", 7.2), cam(1.45, eng, 1170)], [B("uni", 11.6), cam(1.45, eng, 1170)],
    [B("official", 1.0), cam(1.25, btn, 1200)], [B("official", 2.0), cam(1.25, btn, 1200)],
    [B("official", 3.0), REST], [B("official", 4.2), REST], [B("official", 5.0), cam(1.55, mid(addr), 1100)],
    [PL(0), cam(1.55, mid(addr), 1100)], [PL(0.8), REST], [PL(1.8), REST], [PL(2.4), cam(1.25, saveZone, 1150)], [PL(4.45), cam(1.25, saveZone, 1150)],
    [PL(4.75), REST], [PL(5.7), REST], [PL(6.3), cam(1.2, hubP, 1180)], [PL(7.0), cam(1.2, hubP, 1180)], [PL(7.7), REST],
    [PL(8.4), cam(1.42, statusP, 1170)], [B("waddah", 0), cam(1.42, statusP, 1170)],
    [B("waddah", 1.9), FALL, "in"],
    [B("waddah", 9.2), [CHAT[0], CHAT[1], CHAT[2], CHAT[3], CHAT[4], 1500, 18, 0]],
    [B("waddah", 12), CHAT, "out"],
    [B("chat", 18.2), CHAT],
    [B("chat", 19.8), "A2"],
    [B("chat", 23.6), "A2"],
    [B("end", 1.4), [1.0, 540, 1290, 650, 1300, 1900, 30, 8], "in"],
  ];
  for (let i = 1; i < camFrames.length; i++) if (camFrames[i][1] === null) camFrames[i][1] = camFrames[i - 1][1]; // null = hold

  // A whip pan from the homepage to the الرواد page: the world flies off to one side and the new page comes in.
  const whip = [[B("home", 9.5), 0], [B("map", 0), -1300, "in"], [B("map", 0) + 0.0005, 1300], [B("map", 0.85), 0, "out"],
    [PL(4.5), 0], [PL(4.85), -1300, "in"], [PL(4.85) + 0.0005, 1300], [PL(5.6), 0, "out"]];
  const worldO = [[0, 1], [B("waddah", 0.8), 1], [B("waddah", 1.9), 0], [B("waddah", 9.2), 0], [B("waddah", 9.4), 1], [B("end", 0.4), 1], [B("end", 1.4), 0]];

  // The cursor: stops it travels between (world px), its clicks, its drags (a swipe that scrolls the page).
  const m = menus;
  const stops = [
    { t: B("home", 2.2), p: [650, 1560] },
    { t: B("home", 2.9), p: [650, 1060], travel: 0.45 },
    { t: B("home", 4.4), p: pPoint },
    { t: B("home", 6.9), p: [690, 1580] },
    { t: B("home", 7.5), p: [690, 1080], travel: 0.45 },
    { t: B("home", 9.3), p: [720, 1420] },
    { t: B("map", 1.2), p: [720, 1500] },
    { t: B("map", 3.2), p: [starP[0] + 6, starP[1] + 4] },
    { t: B("map", 6.2), p: [starP[0] + 6, starP[1] + 4] },
    { t: B("map", 6.5), p: [700, 1580] },
    { t: B("map", 7.0), p: [700, 1080], travel: 0.45 },
    { t: B("filters", 0.85), p: toggle },
    { t: m[0].open - 0.12, p: sel("f0", "track") },
    { t: m[0].pick - 0.15, p: menuRowWorld(G, d, m[0], d.menus.track.pick) },
    { t: m[1].open - 0.12, p: sel("f1", "field") },
    { t: m[1].pick - 0.15, p: menuRowWorld(G, d, m[1], d.menus.field.pick) },
    { t: m[2].open - 0.12, p: sel("f2", "country") },
    { t: m[2].pick - 0.15, p: menuRowWorld(G, d, m[2], d.menus.country.pick) },
    { t: B("filters", 12.0), p: [700, 1420] },
    { t: B("results", 0.25), p: [700, 1620] },
    { t: B("results", 0.85), p: [700, 1060], travel: 0.5 },
    { t: B("results", 2.6), p: [760, 1500] },
    { t: B("results", 6.4), p: name },
    { t: B("uni", 1.2), p: [720, 1500] },
    { t: B("uni", 2.4), p: [date[0] - 150, date[1] + 70] },
    { t: B("uni", 6.9), p: [eng[0] - 160, eng[1] + 80] },
    { t: B("official", 1.3), p: btn },
    { t: PL(0.1), p: doneP },
    { t: PL(2.75), p: saveP },
    { t: PL(4.3), p: linkTip },
  ];
  const clicks = [B("filters", 1.0), m[0].open - 0.05, m[0].pick - 0.05, m[1].open - 0.05, m[1].pick - 0.05, m[2].open - 0.05, m[2].pick - 0.05, B("results", 6.6), B("official", 1.5),
    PL(0.15), PL(2.85), PL(4.4)];
  const drags = [[B("home", 2.25), B("home", 2.95)], [B("home", 6.95), B("home", 7.55)], [B("map", 6.55), B("map", 7.05)], [B("results", 0.3), B("results", 0.9)]];
  const cursorOn = [[B("home", 2.0), B("official", 2.3)], [PL(-0.4), PL(4.75)]];

  // Highlights: a forest line with a lime halo, the rest of the screen dimmed a little.
  const rings = [
    { shot: "home", r: status, a: B("home", 4.7), b: B("home", 6.9) },
    { shot: "rw1", r: rc.rw.readout, a: B("map", 3.5), b: B("map", 6.2) },
    { shot: "results", r: union(mine.rank, mine.name), a: B("results", 4.0), b: B("results", 6.7) },
    { shot: "uni", r: rc.uni.date, a: B("uni", 2.2), b: B("uni", 5.3) },
    { shot: "uni", r: rc.uni.english, a: B("uni", 6.8), b: B("uni", 11.7) },
    { world: addr, a: B("official", 4.4), b: E("official", 0.15) },
    { shot: "plan", r: rc.plan.status || rc.plan.mine, a: PL(8.4), b: B("waddah", 0.6) },
  ];
  // The light travels from «احفظ» to «خطتي» in the header (design.md: a saved item's light flies to «خطتي»).
  const light = { a: PL(2.95), b: PL(3.75), from: saveP, to: linkP };
  // The الرواد stars light up one by one (right to left, as the page reads), then the one pointed at.
  const stars = rc.rw.stars.map((st) => st).sort((a, b) => b.x - a.x)
    .map((st, k) => ({ p: [st.x, st.y], at: B("map", 0.5) + k * 0.05, hover: st.rank === rc.rw.star.rank }));

  // The in-app browser: up from the bottom, the page loads, the address stays.
  const sheetY = [[B("official", 2.0), 1300], [B("official", 2.7), 0, "out"], [PL(0.25), 0], [PL(0.95), 1300, "in"]];
  const sheetOn = [B("official", 2.0), PL(1.0)];
  const prog = [[B("official", 2.6), 0], [B("official", 3.3), 0.62, "out"], [B("official", 3.95), 1, "in"]];
  const pageIn = B("official", 3.95);

  // The chat, in beats from its scene's start.
  const ch = (b) => B("chat", b);
  const chat = {
    on: B("waddah", 9), greet: ch(0.3), type1: [ch(2.0), ch(4.3)], q1: ch(4.6), dots1: [ch(4.9), ch(6.5)], a1: ch(6.5), chip1: ch(9.4),
    type2: [ch(10.8), ch(12.8)], q2: ch(13.1), dots2: [ch(13.4), ch(14.8)], a2: ch(14.8), chip2: ch(16.8),
  };

  // وضّاح, the host: [x, y (centre), height] on the frame, and his pose, scene by scene.
  const CORNER = [150, 1790, 290], PERCH = [165, 1185, 300];
  const mascot = [
    [0, [540, 2400, 500]], [B("brand", 0.2), [540, 2400, 500]], [B("brand", 1.2), [540, 1500, 500], "out"],
    [B("home", 0.2), [540, 1500, 500]], [B("home", 1.6), CORNER, "io"],
    [PL(9.0), CORNER], [B("waddah", 0.8), [150, 2350, 290], "in"],
    [B("waddah", 1.0), [540, 2400, 520]], [B("waddah", 3.4), [540, 1170, 520], "out"],
    [B("waddah", 8.2), [540, 1170, 520]], [B("waddah", 10.4), PERCH, "io"],
    [B("end", 0.8), PERCH], [B("end", 2.4), [540, 1700, 420], "out"],
  ];
  const pose = [
    [0, "wave"], [B("home", 1.0), "present"], [B("map", 0.6), "point"], [B("filters", 0.5), "present"],
    [B("results", 3.6), "point"], [B("uni", 0.6), "clipboard"], [B("official", 1.0), "point"],
    [PL(0.6), "present"], [PL(2.6), "point"], [PL(5.3), "cheer"], [PL(7.9), "clipboard"],
    [B("waddah", 1.0), "present"], [B("waddah", 4.0), "cheer"], [B("waddah", 9.6), "present"],
    [chat.dots1[0], "laptop"], [chat.a1, "read"], [ch(10.4), "present"], [chat.dots2[0], "laptop"], [chat.a2, "point"],
    [B("end", 1.0), "wave"],
  ];
  const mascotOn = [B("brand", 0.2), P.total];
  // His little hops when he changes pose (a squash and a spring), and the light that bursts from him at the drop.
  const hops = pose.slice(1).map(([t]) => t);
  const dropT = B("waddah", 4);

  // Sounds, for the music script.
  const ev = [];
  CHAOS.forEach((it, i) => ev.push({ t: S.chaos.start + it.at * BEAT, type: "paper", v: i }));
  S.chaos.lines.forEach((l) => ev.push({ t: S.chaos.start + l.at, type: "word" }));
  ev.push({ t: B("chaos", 7.05), type: "whoosh" });
  ev.push({ t: B("brand", 0.3), type: "pop" });
  ev.push({ t: B("home", 0.15), type: "whoosh" }, { t: B("home", 2.5), type: "swipe" }, { t: B("home", 7.1), type: "swipe" });
  ev.push({ t: B("map", 0), type: "whip" });
  stars.forEach((st, k) => { if (k % 3 === 0) ev.push({ t: st.at, type: "twinkle", v: k / 3 }); });
  ev.push({ t: B("map", 6.7), type: "swipe" });
  clicks.forEach((t) => ev.push({ t, type: "click" }));
  m.forEach((x) => ev.push({ t: x.open, type: "open" }));
  ev.push({ t: B("filters", 1.1), type: "open" });
  ev.push({ t: B("results", 0.5), type: "swipe" }, { t: B("results", 6.95), type: "swipe" }, { t: B("uni", 0.8), type: "swipe" }, { t: B("uni", 5.4), type: "swipe" });
  ev.push({ t: B("official", 2.0), type: "swipe" }, { t: pageIn, type: "load" });
  ev.push({ t: PL(0.3), type: "swipe" }, { t: PL(0.95), type: "swipe" }, { t: PL(2.87), type: "save" }, { t: light.a, type: "light" }, { t: PL(4.85), type: "whip" }, { t: PL(6.85), type: "swipe" });
  ev.push({ t: B("waddah", 0.2), type: "whoosh" }, { t: dropT, type: "shimmer" }, { t: B("waddah", 9.4), type: "whoosh" });
  const typing = (text, [a, b]) => { const q = [...text]; q.forEach((c, i) => { if (c.trim()) ev.push({ t: lerp(a, b, i / q.length), type: "type" }); }); };
  ev.push({ t: chat.greet, type: "recv" });
  typing(d.chat.q1, chat.type1); ev.push({ t: chat.q1, type: "send" }, { t: chat.a1, type: "recv" });
  typing(d.chat.q2, chat.type2); ev.push({ t: chat.q2, type: "send" }, { t: chat.a2, type: "recv" });
  ev.push({ t: B("end", 0.3), type: "pop" });

  return {
    S, B, E, BEAT, total: P.total, s, shots, menus, cam: camFrames, whip, worldO, stops, clicks, drags, cursorOn, rings, stars,
    sheetY, sheetOn, prog, pageIn, addr, chat, CHAT, mascot, pose, mascotOn, hops, dropT, light, events: ev.sort((a, b) => a.t - b.t),
    chatBox: { x: SCREEN.x, y: SCREEN.y + 52, w: 640, h: 1188, head: 114, avail: 1500, cx: 540, ax: 620, ay: 960, zmax: 1.3 },
  };
}

// The wide film (decision 094): the desktop site in a browser window on the left, the words in a column on the right
// (where an Arabic reader starts), وضّاح under them. The same scenes and beats as the tall film, told the desktop way:
// the wheel scrolls (no swipes), a click opens the official page in a new tab, and وضّاح's chat is a card of its own
// (it has no page until it launches, decision 084).
function buildWide(d, G) {
  const { K, SCREEN, VH } = G;
  const onW = (r, sc0, sl) => onWorld(G, r, sc0, sl);
  const P = d.plan, BEAT = P.beat;
  const S = Object.fromEntries(P.scenes.map((s) => [s.id, s]));
  const B = (id, beats) => S[id].start + beats * BEAT;
  const E = (id, beats) => S[id].start + S[id].dur - beats * BEAT;
  const PL = (b) => B("plan", b);
  const sh = d.screens, rc = d.rects;
  const sc = (name, y) => clamp(Math.round(y), 0, Math.max(0, sh[name].h - VH));
  const mine = rc.results.rows.find((r) => r.mine);
  const items = rc.home.items, last = items[items.length - 1].card;
  const s = {
    hNow: sc("home", rc.home.now.y - 70),
    hEnd: sc("home", last.y + last.h - VH + 60),
    rMap: 0,
    f0: sh.f0.hold, f1: sh.f1.hold, f2: sh.f2.hold, f3: sh.f3.hold,
    f3b: sc("f3", (rc.f3.applied ? rc.f3.applied.y : rc.f3.country.y + 200) - 120),
    top: sc("results", rc.results.applied.y - 120),
    mine: sc("results", mine.row.y - 260),
    uDate: sc("uni", rc.uni.date.y - 220),
    uEng: sc("uni", rc.uni.english.y - 260),
    pMine: sc("plan", (rc.plan.status || rc.plan.mine).y - 200),
  };

  const fl = B("filters", 0);
  const shots = {
    home: { o: [[0, 1], [B("map", 0) - 0.001, 1], [B("map", 0), 0]],
      s: [[B("home", 2.5), 0], [B("home", 4.5), s.hNow, "expo"], [B("home", 7.1), s.hNow], [B("home", 9.4), s.hEnd, "io"]] },
    rw0: { o: [[B("map", 0) - 0.001, 0], [B("map", 0), 1], [B("map", 3.25), 1], [B("map", 3.4), 0], [B("map", 6.2), 0], [B("map", 6.35), 1], [fl + 1.05 * BEAT, 1], [fl + 1.2 * BEAT, 0]],
      s: [[B("map", 0), 0], [B("map", 6.6), 0], [B("map", 7.9), s.f0, "io"]] },
    rw1: { o: [[B("map", 3.25), 0], [B("map", 3.4), 1], [B("map", 6.2), 1], [B("map", 6.35), 0]], s: [[0, 0]] },
    f0: { o: [[fl + 1.05 * BEAT, 0], [fl + 1.2 * BEAT, 1], [B("filters", 4.45), 1], [B("filters", 4.6), 0]], s: [[0, s.f0]] },
    f1: { o: [[B("filters", 4.45), 0], [B("filters", 4.6), 1], [B("filters", 7.05), 1], [B("filters", 7.2), 0]], s: [[0, s.f1]] },
    f2: { o: [[B("filters", 7.05), 0], [B("filters", 7.2), 1], [B("filters", 9.85), 1], [B("filters", 10), 0]], s: [[0, s.f2]] },
    f3: { o: [[B("filters", 9.85), 0], [B("filters", 10), 1], [B("filters", 13.6), 1], [B("filters", 14.4), 0]], s: [[B("filters", 10.8), s.f3], [B("filters", 12.2), s.f3b]] },
    results: { o: [[B("filters", 13.6), 0], [B("filters", 14.4), 1], [B("results", 6.9), 1], [B("results", 7.05), 0]],
      s: [[B("results", 0.5), s.top], [B("results", 3.6), s.mine, "expo"]] },
    uni: { o: [[B("results", 6.9), 0], [B("results", 7.05), 1], [PL(2.87), 1], [PL(2.875), 0]],
      s: [[B("uni", 0.8), 0], [B("uni", 1.9), s.uDate, "io"], [B("uni", 5.4), s.uDate], [B("uni", 6.6), s.uEng, "io"], [PL(0.9), s.uEng], [PL(1.8), 0, "expo"]] },
    uniS: { o: [[PL(2.87), 0], [PL(2.875), 1], [PL(4.6), 1], [PL(4.75), 0]], s: [[0, 0]] },
    // Until the light lands, the header still shows the count before the save (the unsaved page's top strip).
    uniH: { src: "uni", clip: rc.uni.planLink.y + rc.uni.planLink.h + 8, o: [[PL(2.87), 0], [PL(2.875), 1], [PL(3.75), 1], [PL(3.85), 0]], s: [[0, 0]] },
    plan: { o: [[PL(4.6), 0], [PL(4.75), 1], [B("waddah", 3), 1], [B("waddah", 3.1), 0]], s: [[PL(4.75), 0], [PL(6.8), 0], [PL(7.9), s.pMine, "io"]] },
  };
  // What the address bar reads, shot by shot (the official page has its own tab).
  const q = `?track=${d.filters.track}&field=${d.filters.field}&country=${d.filters.country}`;
  const urls = [[0, "wadihguide.com"], [B("map", 0), "wadihguide.com/universities?track=arruaad"], [B("filters", 4.5), `wadihguide.com/universities?track=${d.filters.track}`],
    [B("filters", 7.1), `wadihguide.com/universities?track=${d.filters.track}&field=${d.filters.field}`], [B("filters", 9.9), `wadihguide.com/universities${q}`],
    [B("results", 6.95), `wadihguide.com/universities/${d.filters.university}`], [PL(4.65), "wadihguide.com/my-plan"]];

  const menus = [
    { id: "track", shot: "f0", open: B("filters", 3.0), pick: B("filters", 4.4) },
    { id: "field", shot: "f1", open: B("filters", 5.6), pick: B("filters", 7.0) },
    { id: "country", shot: "f2", open: B("filters", 8.2), pick: B("filters", 9.8) },
  ];

  const Wp = (r, sc0) => mid(onW(r, sc0));
  const status = items[0].status;
  const pStatus = Wp(status, s.hNow);
  const cardR = onW(items[0].card, s.hNow), stR = onW(status, s.hNow);
  // The program card from its status to its name (its right, where an Arabic line starts).
  const zHome = Math.min(1.55, 1100 / (cardR.x + cardR.w - stR.x)), fHome = [(stR.x + cardR.x + cardR.w) / 2, stR.y + stR.h / 2];
  const chart = Wp(rc.rw.chart, 0);
  const starP = Wp({ x: rc.rw.star.x, y: rc.rw.star.y, w: 0, h: 0 }, 0);
  const starZone = mid(union(onW({ x: rc.rw.star.x - 30, y: rc.rw.star.y - 30, w: 60, h: 60 }, 0), onW(rc.rw.readout, 0)));
  const sel = (name, id) => Wp(rc[name][id], sh[name].hold);
  const panelR = onW(union(union(rc.f0.track, rc.f0.field), rc.f0.country), s.f0);
  const panel = mid(panelR);
  const head = Wp(union(mine.rank, mine.name), s.mine);
  const name = Wp(mine.name, s.mine);
  const date = Wp(rc.uni.date, s.uDate), eng = Wp(rc.uni.english, s.uEng), btn = Wp(rc.uni.button, s.uEng);
  // The browser: tabs (38 px) from the right, as on an Arabic desktop, then the toolbar (46 px) with the address.
  const addr = { x: SCREEN.x + 190, y: SCREEN.y + 38 + 6, w: SCREEN.w - 380, h: 34 };
  const tab2 = { x: SCREEN.x + SCREEN.w - 14 - 2 * 250 - 6, y: SCREEN.y + 5, w: 250, h: 33 };
  const closeP = [tab2.x + 20, tab2.y + 17];
  const saveP = Wp(rc.uni.save, 0), linkP = Wp(rc.uni.planLink, 0);
  const lr = onW(rc.uni.planLink, 0), linkTip = [lr.x + lr.w * 0.72, lr.y + lr.h * 0.62];
  const saveZone = mid(union(onW(rc.uni.save, 0), onW(rc.uni.planLink, 0)));
  const hubR = rc.plan.hub ? onW(rc.plan.hub, 0) : null;
  const hubP = hubR ? [hubR.x + hubR.w / 2, Math.min(hubR.y + hubR.h / 2, SCREEN.y + SCREEN.h - 200)] : [672, 560];
  const statusP = Wp(rc.plan.status || rc.plan.mine, s.pMine);

  // Camera: [zoom, focus x, focus y, anchor x, anchor y, drop, tilt x, tilt y]. In the wide film the browser window
  // never moves while you read: until وضّاح's night, zoom and focus act on the page inside the window (the window only
  // drops in and falls away), so nothing slides under the column of words. At rest the page is read at 1.25×, which
  // shows the site's whole content column larger. No hand-held drift (Shotcraft Q3).
  const CX = G.PAGE.x + SCREEN.w / 2, CY = G.PAGE.y + (SCREEN.h - G.BAR) / 2;
  const fit = (r, zmax) => Math.min(zmax, 1100 / Math.max(1, r.w), 690 / Math.max(1, r.h));
  const cam = (z, f) => [z, f[0], f[1], CX, CY, 0, 0, 0];
  const REST = [1.25, CX, CY, CX, CY, 0, 0, 0];
  const OFF = [1.25, CX, CY, CX, CY, 1250, 22, -10];
  const FALL = [1.25, CX, CY, CX, CY, 1100, 26, 8];
  const CARD = { x: 236, y: 70, w: 872, h: 880 };
  const CHAT = [1, CX, CY, CX, CY, 0, 0, 0];
  const camFrames = [
    [0, OFF], [B("home", 0), OFF], [B("home", 2), REST, "out"],
    [B("home", 4.6), REST], [B("home", 5.4), cam(zHome, fHome)], [B("home", 6.9), cam(zHome, fHome)],
    [B("home", 7.7), REST], [B("map", 0.4), REST],
    [B("map", 0.9), REST], [B("map", 1.8), cam(1.5, chart)], [B("map", 2.9), cam(1.5, chart)],
    [B("map", 3.5), cam(1.95, starZone)], [B("map", 6.2), cam(1.95, starZone)], [B("map", 7.3), REST],
    [B("filters", 0.4), REST], [B("filters", 1.4), cam(fit(panelR, 1.45), panel)], [B("filters", 2.4), cam(fit(panelR, 1.45), panel)],
    ...menus.flatMap((spec) => {
      const bx = menuBox(G, d, spec);
      const u = union({ x: SCREEN.x + bx.sel.x, y: SCREEN.y + bx.sel.y, w: bx.sel.w, h: bx.sel.h }, { x: SCREEN.x + bx.left, y: SCREEN.y + bx.top, w: bx.w, h: bx.h });
      const f = cam(Math.min(1.8, 660 / u.h, 1060 / u.w), mid(u));
      return [[spec.open - 0.05, null], [spec.open + 0.4, f], [spec.pick + 0.12, f]];
    }),
    [B("filters", 10.4), cam(fit(panelR, 1.45), panel)],
    [B("filters", 12.2), REST],
    [B("results", 0.6), REST], [B("results", 3.4), REST],
    [B("results", 4.4), cam(1.75, head)], [B("results", 6.6), cam(1.75, head)], [B("results", 7.6), REST],
    [B("uni", 1.6), REST],
    [B("uni", 2.6), cam(fit(onW(rc.uni.date, s.uDate), 1.6), date)], [B("uni", 5.2), cam(fit(onW(rc.uni.date, s.uDate), 1.6), date)],
    [B("uni", 6.0), REST],
    [B("uni", 7.2), cam(fit(onW(rc.uni.english, s.uEng), 1.6), eng)], [B("uni", 11.6), cam(fit(onW(rc.uni.english, s.uEng), 1.6), eng)],
    [B("official", 1.0), cam(1.45, btn)], [B("official", 2.0), cam(1.45, btn)],
    [B("official", 3.0), REST], [PL(0.8), REST], [PL(1.8), REST], [PL(2.4), cam(1.4, saveZone)], [PL(4.45), cam(1.4, saveZone)],
    [PL(4.75), REST], [PL(5.7), REST], [PL(6.3), cam(hubR ? fit(hubR, 1.3) : 1.2, hubP)], [PL(7.0), cam(hubR ? fit(hubR, 1.3) : 1.2, hubP)], [PL(7.7), REST],
    [PL(8.4), cam(1.6, statusP)], [B("waddah", 0), cam(1.6, statusP)],
    [B("waddah", 1.9), FALL, "in"],
    [B("waddah", 9.2), [1, CX, CY, CX, CY, 900, 16, 0]],
    [B("waddah", 12), CHAT, "out"],
    [B("chat", 18.2), CHAT],
    [B("chat", 19.8), "A2"],
    [B("chat", 23.6), "A2"],
    [B("end", 1.4), [1, CX, CY, CX, CY, 1100, 22, 6], "in"],
  ];
  for (let i = 1; i < camFrames.length; i++) if (camFrames[i][1] === null) camFrames[i][1] = camFrames[i - 1][1];

  // A page load on a desktop is a quick cross-fade (the address changes); no whip pans in the wide film.
  const whip = [[0, 0]];
  const worldO = [[0, 1], [B("waddah", 0.8), 1], [B("waddah", 1.9), 0], [B("waddah", 9.2), 0], [B("waddah", 9.4), 1], [B("end", 0.4), 1], [B("end", 1.4), 0]];

  const m = menus;
  const rest = [CX + 120, CY + 150];
  const stops = [
    { t: B("home", 2.2), p: rest },
    { t: B("home", 4.4), p: [pStatus[0] + 260, pStatus[1] + 60] },
    { t: B("home", 7.0), p: rest },
    { t: B("map", 1.2), p: [chart[0] + 260, chart[1] + 120] },
    { t: B("map", 3.2), p: [starP[0] + 3, starP[1] + 2] },
    { t: B("map", 6.2), p: [starP[0] + 3, starP[1] + 2] },
    { t: B("map", 6.7), p: rest },
    { t: m[0].open - 0.12, p: sel("f0", "track") },
    { t: m[0].pick - 0.15, p: menuRowWorld(G, d, m[0], d.menus.track.pick) },
    { t: m[1].open - 0.12, p: sel("f1", "field") },
    { t: m[1].pick - 0.15, p: menuRowWorld(G, d, m[1], d.menus.field.pick) },
    { t: m[2].open - 0.12, p: sel("f2", "country") },
    { t: m[2].pick - 0.15, p: menuRowWorld(G, d, m[2], d.menus.country.pick) },
    { t: B("filters", 12.0), p: rest },
    { t: B("results", 2.6), p: [CX + 200, CY + 120] },
    { t: B("results", 6.4), p: name },
    { t: B("uni", 1.2), p: rest },
    { t: B("uni", 2.4), p: [date[0] + 300, date[1] + 50] },
    { t: B("uni", 6.9), p: [eng[0] + 300, eng[1] + 60] },
    { t: B("official", 1.3), p: btn },
    { t: PL(0.1), p: closeP },
    { t: PL(2.75), p: saveP },
    { t: PL(4.3), p: linkTip },
  ];
  const clicks = [m[0].open - 0.05, m[0].pick - 0.05, m[1].open - 0.05, m[1].pick - 0.05, m[2].open - 0.05, m[2].pick - 0.05, B("results", 6.6), B("official", 1.5),
    PL(0.15), PL(2.85), PL(4.4)];
  const drags = [];
  const cursorOn = [[B("home", 2.0), B("official", 2.3)], [PL(-0.4), PL(4.75)]];
  // The wheel turns: the page scrolls under a still cursor.
  const wheels = [B("home", 2.5), B("home", 7.1), B("map", 6.6), B("results", 0.5), B("results", 3.6), B("uni", 0.8), B("uni", 5.4), PL(0.9), PL(6.8)];

  const rings = [
    { shot: "home", r: status, a: B("home", 4.7), b: B("home", 6.9) },
    { shot: "rw1", r: rc.rw.readout, a: B("map", 3.5), b: B("map", 6.2) },
    { shot: "results", r: union(mine.rank, mine.name), a: B("results", 4.0), b: B("results", 6.7) },
    { shot: "uni", r: rc.uni.date, a: B("uni", 2.2), b: B("uni", 5.3) },
    { shot: "uni", r: rc.uni.english, a: B("uni", 6.8), b: B("uni", 11.7) },
    { world: addr, a: B("official", 4.4), b: E("official", 0.15) },
    { shot: "plan", r: rc.plan.status || rc.plan.mine, a: PL(8.4), b: B("waddah", 0.6) },
  ];
  const light = { a: PL(2.95), b: PL(3.75), from: saveP, to: linkP };
  const stars = rc.rw.stars.map((st) => st).sort((a, b) => b.x - a.x)
    .map((st, k) => ({ p: [st.x, st.y], at: B("map", 0.5) + k * 0.05, hover: st.rank === rc.rw.star.rank }));

  // The official page: a new tab opens beside واضح's, loads, and stays; «خطتي» starts by closing it.
  const tab = { open: B("official", 1.8), close: PL(0.2) };
  const prog = [[B("official", 2.4), 0], [B("official", 3.2), 0.62, "out"], [B("official", 3.95), 1, "in"]];
  const pageIn = B("official", 3.95);

  const ch = (b) => B("chat", b);
  const chat = {
    on: B("waddah", 9), greet: ch(0.3), type1: [ch(2.0), ch(4.3)], q1: ch(4.6), dots1: [ch(4.9), ch(6.5)], a1: ch(6.5), chip1: ch(9.4),
    type2: [ch(10.8), ch(12.8)], q2: ch(13.1), dots2: [ch(13.4), ch(14.8)], a2: ch(14.8), chip2: ch(16.8),
  };

  // وضّاح stands under the words, in the right-hand column; centre stage for the logo and his own reveal.
  const COL = [1590, 868, 330], PERCH = [1590, 860, 350];
  const mascot = [
    [0, [1500, 1500, 460]], [B("brand", 0.2), [1500, 1500, 460]], [B("brand", 1.2), [1470, 690, 430], "out"],
    [B("home", 0.2), [1470, 690, 430]], [B("home", 1.6), COL, "io"],
    [PL(9.0), COL], [B("waddah", 0.8), [1590, 1450, 330], "in"],
    [B("waddah", 1.0), [660, 1500, 470]], [B("waddah", 3.4), [660, 600, 470], "out"],
    [B("waddah", 8.2), [660, 600, 470]], [B("waddah", 10.4), PERCH, "io"],
    [B("end", 0.8), PERCH], [B("end", 2.4), [1480, 690, 420], "out"],
  ];
  const pose = [
    [0, "wave"], [B("home", 1.0), "present"], [B("map", 0.6), "point"], [B("filters", 0.5), "present"],
    [B("results", 3.6), "point"], [B("uni", 0.6), "clipboard"], [B("official", 1.0), "point"],
    [PL(0.6), "present"], [PL(2.6), "point"], [PL(5.3), "cheer"], [PL(7.9), "clipboard"],
    [B("waddah", 1.0), "present"], [B("waddah", 4.0), "cheer"], [B("waddah", 9.6), "present"],
    [chat.dots1[0], "laptop"], [chat.a1, "read"], [ch(10.4), "present"], [chat.dots2[0], "laptop"], [chat.a2, "point"],
    [B("end", 1.0), "wave"],
  ];
  const mascotOn = [B("brand", 0.2), P.total];
  const hops = pose.slice(1).map(([t]) => t);
  const dropT = B("waddah", 4);

  const ev = [];
  CHAOS.forEach((it, i) => ev.push({ t: S.chaos.start + it.at * BEAT, type: "paper", v: i }));
  S.chaos.lines.forEach((l) => ev.push({ t: S.chaos.start + l.at, type: "word" }));
  ev.push({ t: B("chaos", 7.05), type: "whoosh" });
  ev.push({ t: B("brand", 0.3), type: "pop" });
  ev.push({ t: B("home", 0.15), type: "whoosh" });
  wheels.forEach((t) => ev.push({ t, type: "wheel" }));
  ev.push({ t: B("map", 0), type: "load" });
  stars.forEach((st, k) => { if (k % 3 === 0) ev.push({ t: st.at, type: "twinkle", v: k / 3 }); });
  clicks.forEach((t) => ev.push({ t, type: "click" }));
  m.forEach((x) => ev.push({ t: x.open, type: "open" }));
  ev.push({ t: B("results", 7.0), type: "load" }, { t: tab.open, type: "swipe" }, { t: pageIn, type: "load" });
  ev.push({ t: tab.close, type: "swipe" }, { t: PL(2.87), type: "save" }, { t: light.a, type: "light" }, { t: PL(4.7), type: "load" });
  ev.push({ t: B("waddah", 0.2), type: "whoosh" }, { t: dropT, type: "shimmer" }, { t: B("waddah", 9.4), type: "whoosh" });
  const typing = (text, [a, b]) => { const qq = [...text]; qq.forEach((c, i) => { if (c.trim()) ev.push({ t: lerp(a, b, i / qq.length), type: "type" }); }); };
  ev.push({ t: chat.greet, type: "recv" });
  typing(d.chat.q1, chat.type1); ev.push({ t: chat.q1, type: "send" }, { t: chat.a1, type: "recv" });
  typing(d.chat.q2, chat.type2); ev.push({ t: chat.q2, type: "send" }, { t: chat.a2, type: "recv" });
  ev.push({ t: B("end", 0.3), type: "pop" });

  return {
    S, B, E, BEAT, total: P.total, s, shots, urls, menus, cam: camFrames, whip, worldO, stops, clicks, drags, cursorOn, rings, stars,
    tab, tab2, prog, pageIn, addr, chat, CHAT, CARD, mascot, pose, mascotOn, hops, dropT, light, events: ev.sort((a, b) => a.t - b.t),
    chatBox: { x: CARD.x, y: CARD.y, w: CARD.w, h: CARD.h, head: 114, avail: 840, cx: CARD.x + CARD.w / 2, ax: CX, ay: 530, zmax: 1.22 },
    PAGE_ERA: B("waddah", 3),
  };
}

// The chat list's lift (each new message pushes the others up when needed) and the camera's push onto the second
// answer, once the messages are laid out (m: each message's top and height in the list; listH: the list's height).
export function chatTracks(tl, m, listH) {
  const lift = (k) => Math.max(0, m[k].top + m[k].h + 24 - listH);
  const c = tl.chat;
  const listY = [[0, 0], [c.q1, 0], [c.q1 + 0.3, lift("q1"), "out"], [c.dots1[0], lift("q1")], [c.dots1[0] + 0.3, lift("dots1"), "out"],
    [c.a1, lift("dots1")], [c.a1 + 0.4, lift("a1"), "out"], [c.q2, lift("a1")], [c.q2 + 0.3, lift("q2"), "out"],
    [c.dots2[0], lift("q2")], [c.dots2[0] + 0.3, lift("dots2"), "out"], [c.a2, lift("dots2")], [c.a2 + 0.4, lift("a2"), "out"]];
  // The push frames everything from the chat's header (with «قادم في ديسمبر») down to the answer, so the header is
  // never cut off: وضّاح isn't live, and the frame must keep saying so.
  const cb = tl.chatBox;
  const top = cb.y - 20, bottom = cb.y + cb.head + m.a2.top + m.a2.h - lift("a2") + 40;
  const z = Math.min(cb.zmax, cb.avail / (bottom - top));
  const A2 = [z, cb.cx, (top + bottom) / 2, cb.ax, cb.ay, 0, 0, 0];
  const cam = tl.cam.map(([t, v, e]) => [t, v === "A2" ? A2 : v, e]);
  return { listY, cam };
}

// The cursor's path between its stops: eased, on a slight arc; it leaves only after its click.
export function cursorAt(stops, t) {
  if (t <= stops[0].t) return stops[0].p;
  for (let i = 0; i < stops.length - 1; i++) {
    const a = stops[i], b = stops[i + 1];
    if (t > b.t) continue;
    const travel = Math.max(0.2, Math.min(b.travel || 0.62, b.t - a.t - 0.16));
    const dep = b.t - travel;
    if (t <= dep) return a.p;
    const p = ease.io(seg(t, dep, b.t));
    const dx = b.p[0] - a.p[0], dy = b.p[1] - a.p[1], dd = Math.hypot(dx, dy) || 1;
    const bow = Math.sin(Math.PI * p) * Math.min(60, dd * 0.12);
    return [a.p[0] + dx * p + (-dy / dd) * bow, a.p[1] + dy * p + (dx / dd) * bow];
  }
  return stops[stops.length - 1].p;
}
