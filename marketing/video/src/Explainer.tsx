// The explainer video (marketing/README.md §9, decisions 089–092), as a Remotion composition. Every frame is a pure
// function of its time t: the camera follows a cursor through the real site (screens captured from it, menus drawn
// from each select's real options), and وضّاح, the mascot, hosts it. The times all come from timeline.mjs, which the
// music reads too. Colours: the site's tokens.
import React, { useLayoutEffect, useRef, useState } from "react";
import { AbsoluteFill, Img, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import data from "../public/data.json";
import { fontsReady } from "./fonts";
import {
  CHAOS, K, ROW, SCREEN, buildTimeline, chatTracks, clamp, cursorAt, ease, kf, lerp, menuBox, mid, onWorld, seg, win, words,
} from "./timeline.mjs";
import { CSS } from "./styles";

/* eslint-disable @typescript-eslint/no-explicit-any */
const D: any = data;
const tl: any = buildTimeline(D);
const { S, B, E, BEAT } = tl;
const POSES = ["wave", "present", "point", "clipboard", "cheer", "laptop", "read"];
const MASCOT_RATIO = 1295 / 1215;

// Words of a line as spans; *stars* become lime.
const Words: React.FC<{ text: string; style: (i: number) => React.CSSProperties }> = ({ text, style }) => (
  <>{words(text).map(({ segs, space }: any, i: number) => (
    <span key={i} className="w" style={style(i)}>{segs.map((x: any, j: number) => <span key={j} style={{ color: x.lime ? "var(--lime)" : undefined }}>{x.t}</span>)}{space}</span>
  ))}</>
);
const rise = (t: number, a: number, i: number, step = 0.055, dur = 0.42, dist = 34) => {
  const p = ease.out(seg(t, a + i * step, a + i * step + dur));
  return { opacity: p, transform: `translateY(${(1 - p) * dist}px)`, filter: p < 1 ? `blur(${(1 - p) * 10}px)` : "none" } as React.CSSProperties;
};
const star = (x: number, y: number, s: number) => {
  const k = +(s * 0.16).toFixed(2);
  return `M${x} ${y - s}Q${x + k} ${y - k} ${x + s} ${y}Q${x + k} ${y + k} ${x} ${y + s}Q${x - k} ${y + k} ${x - s} ${y}Q${x - k} ${y - k} ${x} ${y - s}Z`;
};
const mix = (a: string, b: string, p: number) => {
  const h = (s: string) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16));
  const [x, y] = [h(a), h(b)];
  return "#" + x.map((v, i) => Math.round(lerp(v, y[i], p)).toString(16).padStart(2, "0")).join("");
};
const rng = (seed: number) => () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

export const Explainer: React.FC<{ audio: string | null }> = ({ audio }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // The chat is laid out once (after the fonts), so the list knows how far to lift and the camera where to push.
  const msgs = useRef<HTMLDivElement>(null);
  const [chatT, setChatT] = useState<any>(null);
  const [handle] = useState(() => delayRender("laying out the chat"));
  useLayoutEffect(() => {
    let done = false;
    fontsReady.then(() => document.fonts.ready).then(() => {
      if (done || !msgs.current) return;
      const m: any = {};
      for (const n of Array.from(msgs.current.querySelectorAll<HTMLElement>("[data-m]"))) m[n.dataset.m!] = { top: n.offsetTop, h: n.offsetHeight };
      m.dots1 = { top: m.a1.top, h: m.d1.h };
      m.dots2 = { top: m.a2.top, h: m.d2.h };
      setChatT({ ...chatTracks(tl, m, msgs.current.parentElement!.clientHeight), m });
      continueRender(handle);
    });
    return () => { done = true; };
  }, [handle]);
  const camFrames = chatT ? chatT.cam : tl.cam.map(([tt, v, e]: any) => [tt, v === "A2" ? tl.CHAT : v, e]);

  // Camera, with the whip pan's sideways flight and its blur.
  const [z, fx, fy, cx, cy, drop, rx, ry] = kf(t, camFrames);
  const wx = kf(t, tl.whip), wv = Math.abs(kf(t + 1 / 60, tl.whip) - wx);
  const hb = clamp(wv * 0.9, 0, 60);
  const nightO = Math.min(seg(t, B("waddah", 0.4), B("waddah", 3.2)), 1 - seg(t, B("end", 0.2), B("end", 1.6)));

  // Screens: where each captured page is, and how fast the visible one scrolls (fast scrolls blur along their way).
  const st: any = {};
  let vel = 0;
  for (const [name, track] of Object.entries<any>(tl.shots)) {
    const o = kf(t, track.o), s = kf(t, track.s), x = track.x ? kf(t, track.x) : 0;
    st[name] = { o, s, x };
    if (o > 0.5) vel = Math.max(vel, Math.abs(kf(t + 1 / 60, track.s) - s) * K);
  }
  const vb = clamp((vel - 6) * 0.45, 0, 16);

  return (
    <AbsoluteFill style={{ background: "#123d2f", direction: "rtl" }}>
      <style>{CSS}</style>
      <svg width="0" height="0" style={{ position: "absolute" }}>
        <filter id="vblur" x="0" y="-5%" width="100%" height="110%"><feGaussianBlur stdDeviation={`0 ${vb.toFixed(2)}`} /></filter>
        <filter id="hblur" x="-10%" y="0" width="120%" height="100%"><feGaussianBlur stdDeviation={`${hb.toFixed(2)} 0`} /></filter>
        <filter id="cblur" x="-10%" y="0" width="120%" height="100%"><feGaussianBlur stdDeviation={`${chaosBlur(t).toFixed(1)} 0`} /></filter>
        <filter id="grainf"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={5} /><feColorMatrix type="saturate" values="0" /></filter>
      </svg>
      <Background t={t} />
      <Night t={t} o={nightO} />
      <Intro t={t} />
      <Chaos t={t} />
      <div id="persp" style={{ filter: hb > 0.3 ? "url(#hblur)" : "none" }}>
        <div id="world" style={{ opacity: kf(t, tl.worldO), transform: `translate(${cx + wx}px, ${cy + drop}px) scale(${z}) rotateX(${rx}deg) rotateY(${ry}deg) translate(${-fx}px, ${-fy}px)` }}>
          <Phone t={t} st={st} vb={vb} msgs={msgs} chatT={chatT} />
          <Fx t={t} st={st} />
          <Cursor t={t} z={z} />
        </div>
      </div>
      <div id="scrim" style={{ opacity: win(t, B("home", 1.0), B("waddah", 1.0), 0.6, 0.5) }} />
      <div id="brandbar" style={{ opacity: win(t, B("home", 0.6), B("waddah", 1.0), 0.5, 0.5) }}>
        <Img src={staticFile("logo.svg")} /><span className="title">{D.text.name}</span>
      </div>
      <Brand t={t} />
      {nightO > 0 && <WaddahTitle t={t} />}
      <EndCard t={t} />
      <Captions t={t} />
      <Mascot t={t} z={z} />
      <div id="grain"><svg width="1080" height="1920"><rect width="1080" height="1920" filter="url(#grainf)" /></svg></div>
      {audio && <Audio src={staticFile(audio)} />}
    </AbsoluteFill>
  );
};

// ---------- the background: the forest, with two soft lights drifting across it ----------
const Background: React.FC<{ t: number }> = ({ t }) => (
  <div id="bg" className="layer">
    <div className="glow glow--leaf" style={{ transform: `translate(${-300 + Math.sin(t * 0.21) * 220}px, ${-200 + Math.cos(t * 0.17) * 260}px)` }} />
    <div className="glow glow--lime" style={{ transform: `translate(${200 + Math.cos(t * 0.15) * 260}px, ${700 + Math.sin(t * 0.19) * 300}px)` }} />
  </div>
);

// ---------- the opening question: a scholarship site, said in the first second ----------
const Intro: React.FC<{ t: number }> = ({ t }) => {
  const line = S.intro.lines[0];
  const a = S.intro.start + line.at;
  const out = seg(t, B("chaos", -0.2), B("chaos", 0.9));
  if (out >= 1) return null;
  const [l1, l2] = splitQuestion(line.text);
  // A route drawn from home (the lime star, right) to a pin far away (left): studying abroad, in one line. A paper
  // plane flies at its head, so the way it goes is plain.
  const draw = ease.io(seg(t, a + 0.3, B("chaos", 0)));
  const path = "M900 1470 C 760 1240, 380 1220, 190 1400";
  const bz = (u: number) => { const v = 1 - u; return [v * v * v * 900 + 3 * v * v * u * 760 + 3 * v * u * u * 380 + u * u * u * 190, v * v * v * 1470 + 3 * v * v * u * 1240 + 3 * v * u * u * 1220 + u * u * u * 1400]; };
  const n = Math.max(1, Math.round(draw * 80));
  const pts = Array.from({ length: n + 1 }, (_, i) => bz((i / n) * draw));
  const head = bz(draw), back = bz(Math.max(0, draw - 0.01));
  const ang = (Math.atan2(head[1] - back[1], head[0] - back[0]) * 180) / Math.PI;
  const planeO = draw > 0.02 ? 1 - seg(t, B("intro", 4.4), B("intro", 4.8)) : 0;
  return (
    <div className="layer" style={{ opacity: 1 - out, filter: out > 0 ? `blur(${out * 14}px)` : "none", transform: `scale(${1 - out * 0.06})` }}>
      <div className="question title">
        <div><Words text={l1} style={(i) => rise(t, a, i, 0.16, 0.6, 40)} /></div>
        <div style={{ color: "var(--lime)" }}><Words text={l2} style={(i) => rise(t, a + 0.5, i, 0.16, 0.6, 40)} /></div>
      </div>
      <svg className="layer" viewBox="0 0 1080 1920">
        <path d={path} fill="none" stroke="rgba(246,244,238,0.18)" strokeWidth="4" strokeDasharray="4 16" strokeLinecap="round" />
        {draw > 0 && <polyline points={pts.map((q) => q.join(",")).join(" ")} fill="none" stroke="#d8ed9b" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />}
        <g opacity={planeO} transform={`translate(${head[0]} ${head[1]}) rotate(${ang})`}>
          <path d="M26 0 L-18 -16 L-9 0 L-18 16 Z" fill="#f6f4ee" /><path d="M26 0 L-9 0 L-18 16 Z" fill="#c9d3cd" />
        </g>
        <circle cx="900" cy="1470" r="34" fill="#d8ed9b" opacity="0.18" /><path d={star(900, 1470, 20)} fill="#d8ed9b" />
        <g opacity={seg(t, B("intro", 4.6), B("intro", 5.2))} transform={`translate(190 1400) scale(${0.6 + 0.4 * ease.back(seg(t, B("intro", 4.6), B("intro", 5.3)))})`}>
          <path d="M0 -58C-22 -58 -38 -42 -38 -21C-38 6 0 34 0 34C0 34 38 6 38 -21C38 -42 22 -58 0 -58Z" fill="#f6f4ee" />
          <circle cx="0" cy="-22" r="13" fill="#184b3a" />
        </g>
      </svg>
    </div>
  );
};
const splitQuestion = (text: string) => {
  const w = text.split(" ");
  const i = Math.max(1, w.findIndex((x) => x.startsWith("و")));
  return [w.slice(0, i).join(" "), w.slice(i).join(" ")];
};

// ---------- the mess: the pile grows, the words take over, one swipe clears it ----------
function chaosBlur(t: number) {
  const sw = seg(t, B("chaos", 7.0), B("chaos", 7.6));
  const sv = sw > 0 && sw < 1 ? (1600 * 3 * Math.pow(sw, 2)) / (0.6 * BEAT * 60) : 0;
  return clamp(sv * 1.2, 0, 70);
}
const Chaos: React.FC<{ t: number }> = ({ t }) => {
  if (t < S.chaos.start - 0.1 || t > B("brand", 0.2)) return <Sweep t={t} />;
  const its = CHAOS.map((c: any) => ({ ...c, at: S.chaos.start + c.at * BEAT }));
  const n = its.filter((it: any) => t >= it.at).length;
  const creep = 1 + 0.07 * seg(t, S.chaos.start, B("chaos", 7));
  const lines = S.chaos.lines;
  const back = 0.6 * ease.io(seg(t, S.chaos.start + lines[0].at - 0.15, S.chaos.start + lines[0].at + 0.5));
  const sw = seg(t, B("chaos", 7.0), B("chaos", 7.6));
  return (
    <>
      <div id="chaos" style={{ transform: `translateX(${-1600 * ease.in(sw)}px) scale(${creep})`, filter: chaosBlur(t) > 0.5 ? "url(#cblur)" : "none" }}>
        {its.map((it: any, i: number) => {
          const p = seg(t, it.at, it.at + 0.32), q = ease.back(p);
          const shake = n * 0.6 * 0.35;
          const jx = Math.sin(t * 23 + i * 1.7) * shake, jy = Math.cos(t * 19 + i * 2.3) * shake;
          return (
            <div key={i} className="it-wrap" style={{ left: it.x, top: it.y, opacity: p > 0 ? Math.min(1, p * 3) : 0,
              transform: `translate(-50%, -50%) translate(${jx}px, ${jy}px) rotate(${it.r + (1 - p) * 9}deg) scale(${lerp(1.35, 1, q) * (1 - 0.06 * back)})`,
              filter: back > 0.01 ? `blur(${(back * 5.5).toFixed(2)}px) brightness(${(1 - 0.35 * back).toFixed(3)})` : "none" }}>
              <ChaosItem it={it} />
            </div>
          );
        })}
        <div id="chaosShade" style={{ opacity: back * 0.85 }} />
        {lines.map((l: any, i: number) => {
          const p = ease.out(seg(t, S.chaos.start + l.at, S.chaos.start + l.at + 0.45));
          return <div key={i} className="cw title" style={{ top: 640 + i * 200 + (i === 3 ? 50 : 0), color: i === 3 ? "var(--lime)" : undefined, opacity: p,
            transform: `scale(${lerp(1.35, 1, p)})`, filter: p < 1 ? `blur(${(1 - p) * 16}px)` : "none" }}>{l.text.replace(/\*/g, "")}</div>;
        })}
      </div>
      <Sweep t={t} />
    </>
  );
};
// A light sweeps the empty frame just before the logo lands (the film's one sweep, Shotcraft Q4).
const Sweep: React.FC<{ t: number }> = ({ t }) => {
  const lw = seg(t, B("chaos", 7.2), B("brand", 0.6));
  if (lw <= 0 || lw >= 1) return null;
  return <div id="sweep" style={{ opacity: Math.sin(Math.PI * lw) * 0.9, transform: `translateX(${lerp(1400, -700, ease.io(lw))}px) rotate(14deg)` }} />;
};
const Lines: React.FC<{ n: number }> = ({ n }) => <>{Array.from({ length: n }, (_, i) => <div key={i} className="ln" style={{ width: `${[100, 92, 78, 96, 60][i % 5]}%` }} />)}</>;
const ChaosItem: React.FC<{ it: any }> = ({ it }) => {
  switch (it.kind) {
    case "browser": return <div className="it it-browser" style={{ width: it.w || 600 }}><div className="tabs">{it.tabs.map((x: string, i: number) => <span key={i} className={`tab${i ? "" : " on"}`}>{x}</span>)}</div><div className="url">{it.url}</div><div className="body"><Lines n={it.lines} /></div></div>;
    case "pdf": return <div className="it it-pdf"><span className="badge">PDF</span><div className="name">{it.name}</div><Lines n={it.lines} /></div>;
    case "sticky": return <div className={`it it-sticky${it.pink ? " pink" : ""}`}>{it.text}</div>;
    case "chat": return <div className="it it-chat">{it.text}<small>11:58 PM</small></div>;
    case "cal": return <div className="it it-cal"><div className="top">التقويم</div><div className="grid">{Array.from({ length: 28 }, (_, i) => <i key={i} className={`${[5, 12, 19, 23].includes(i) ? "mark" : ""}${[12, 23].includes(i) ? " q" : ""}`} />)}</div></div>;
    case "search": return <div className="it it-search"><svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="7" fill="none" stroke="#57635d" strokeWidth="2.6" /><path d="M15.5 15.5L21 21" stroke="#57635d" strokeWidth="2.6" strokeLinecap="round" /></svg>{it.text}</div>;
    case "pill": return <div className="it it-pill">{it.text}</div>;
    case "xls": return <div className="it it-xls"><div className="top">{it.name}</div><table><tbody>{Array.from({ length: 5 }, (_, r) => <tr key={r}>{Array.from({ length: 4 }, (_, c) => <td key={c}>{(r + c) % 3 === 0 ? "؟" : ""}</td>)}</tr>)}</tbody></table></div>;
    case "note": return <div className="it it-note"><span className="ic">!</span><div><b>{it.title}</b><span>{it.text}</span></div></div>;
    default: return null;
  }
};

// ---------- the logo: «كل هذا، في مكان واحد.», held more than a second ----------
const Brand: React.FC<{ t: number }> = ({ t }) => {
  const a = B("brand", 0), p = ease.back(seg(t, a, a + 0.55));
  const o = win(t, a, B("home", 0.9), 0.15, 0.5);
  if (o <= 0) return null;
  const up = ease.io(seg(t, E("brand", 0.8), B("home", 0.9)));
  const la = S.brand.start + S.brand.lines[0].at;
  return (
    <div id="brand" style={{ opacity: o, transform: `translateY(${-up * 520}px) scale(${lerp(0.8, 1, p) * (1 - up * 0.6)})` }}>
      <div className="halo" style={{ opacity: 0.6 + 0.4 * Math.pow(Math.max(0, Math.cos(((t - a) / BEAT) * Math.PI)), 8) }} />
      <Img src={staticFile("logo.svg")} />
      <p className="name title">{D.text.name}</p>
      <p className="line"><Words text={S.brand.lines[0].text} style={(i) => rise(t, la, i, 0.08, 0.45, 26)} /></p>
    </div>
  );
};

// ---------- the phone: the captured pages, the menus, the in-app browser, وضّاح's chat ----------
const Phone: React.FC<{ t: number; st: any; vb: number; msgs: React.RefObject<HTMLDivElement | null>; chatT: any }> = ({ t, st, vb, msgs, chatT }) => (
  <div id="phone">
    <div className="side" style={{ left: -5, top: 250, height: 70 }} /><div className="side" style={{ left: -5, top: 350, height: 120 }} />
    <div className="side" style={{ left: -5, top: 490, height: 120 }} /><div className="side" style={{ right: -5, top: 380, height: 180 }} />
    <div id="screen">
      <div id="page" style={{ filter: vb > 0.2 ? "url(#vblur)" : "none" }}>
        {Object.entries<any>(tl.shots).map(([name]) => {
          const s = st[name];
          return <Img key={name} src={staticFile(`shots/${D.screens[name].file}`)} style={{ opacity: s.o, display: s.o > 0 ? "block" : "none", zIndex: name === "uni" ? 2 : 1, transform: `translate(${s.x}px, ${-s.s * K}px)` }} />;
        })}
      </div>
      <Sheet t={t} />
      <ChatUI t={t} msgs={msgs} chatT={chatT} />
      <Menus t={t} />
      <div id="status"><span className="time">9:41</span><StatusIcons /></div>
      <div id="island" />
    </div>
  </div>
);
const StatusIcons = () => (
  <svg width="110" height="26" viewBox="0 0 110 26"><g fill="#101713"><rect x="0" y="16" width="6" height="8" rx="1.5" /><rect x="9" y="11" width="6" height="13" rx="1.5" /><rect x="18" y="6" width="6" height="18" rx="1.5" /><rect x="27" y="1" width="6" height="23" rx="1.5" /><path d="M46 9a17 17 0 0 1 22 0l-2.5 2.8a13 13 0 0 0-17 0Z M50 14a11 11 0 0 1 14 0l-2.6 2.8a7 7 0 0 0-8.8 0Z M54 19a5 5 0 0 1 6 0l-3 3.3Z" /><rect x="74" y="3" width="32" height="18" rx="5" fill="none" stroke="#101713" strokeWidth="2" opacity="0.5" /><rect x="77" y="6" width="22" height="12" rx="2.5" /><rect x="107" y="9" width="2.5" height="6" rx="1" /></g></svg>
);

const Menus: React.FC<{ t: number }> = ({ t }) => (
  <>{tl.menus.map((spec: any) => {
    const m = D.menus[spec.id];
    const o = Math.min(seg(t, spec.open, spec.open + 0.16), 1 - seg(t, spec.pick + 0.08, spec.pick + 0.24));
    if (o <= 0) return null;
    const box = menuBox(D, spec);
    const p = ease.out(seg(t, spec.open, spec.open + 0.22));
    const arrive = spec.pick - 0.28; // the cursor reaches the row just before this
    return (
      <div key={spec.id} className="menu" style={{ left: box.left, top: box.top, width: box.w, height: box.h, opacity: o, transform: `translateY(${(1 - p) * -10}px) scaleY(${lerp(0.94, 1, p)})` }}>
        <div className="rows" style={{ transform: `translateY(${-box.off * ROW}px)` }}>
          {m.items.map((txt: string, i: number) => (
            <div key={i} className={`row${i === m.pick && t >= arrive && t < spec.pick - 0.05 ? " hover" : ""}${i === m.pick && t >= spec.pick - 0.05 ? " press" : ""}`}
              style={{ opacity: seg(t, spec.open + 0.02 * i, spec.open + 0.02 * i + 0.18) }}>
              <svg className="tick" viewBox="0 0 24 24">{i === m.current && <path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#184b3a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />}</svg><span>{txt}</span>
            </div>
          ))}
        </div>
      </div>
    );
  })}</>
);

const Sheet: React.FC<{ t: number }> = ({ t }) => {
  const on = t >= tl.sheetY[0][0] && t < B("waddah", 3.2);
  if (!on) return null;
  return (
    <div id="sheet" style={{ transform: `translateY(${kf(t, tl.sheetY)}px)` }}>
      <div className="bar"><span className="done">Done</span><div className="url"><svg viewBox="0 0 20 24"><rect x="2" y="10" width="16" height="13" rx="3" fill="#101713" /><path d="M6 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="#101713" strokeWidth="2.4" /></svg><span>{D.rects.official.host}</span></div><span style={{ width: 52 }} /></div>
      <div className="prog" style={{ width: kf(t, tl.prog) * 640, opacity: 1 - seg(t, tl.pageIn + 0.05, tl.pageIn + 0.35) }} />
      <div className="pg"><Img src={staticFile(`shots/${D.screens.official.file}`)} style={{ opacity: seg(t, tl.pageIn, tl.pageIn + 0.2) }} /></div>
    </div>
  );
};

const ChatUI: React.FC<{ t: number; msgs: React.RefObject<HTMLDivElement | null>; chatT: any }> = ({ t, msgs, chatT }) => {
  const c = tl.chat, C = D.chat;
  const on = t >= c.on && t < B("end", 1.6);
  const pop = (at: number): React.CSSProperties => {
    const p = ease.back(seg(t, at, at + 0.35));
    return { opacity: seg(t, at, at + 0.15), transform: `translateY(${(1 - p) * 24}px) scale(${lerp(0.92, 1, p)})` };
  };
  const chip = (src: string, at: number) => {
    const p = ease.back(seg(t, at, at + 0.4));
    return <span className="chip" style={{ opacity: seg(t, at, at + 0.15), transform: `scale(${lerp(0.6, 1, p)})` }}><b>1</b><bdi dir="ltr">{src}</bdi></span>;
  };
  const dots = (k: number, [a, b]: number[]) => {
    const o = Math.min(seg(t, a, a + 0.15), 1 - seg(t, b - 0.05, b));
    return (
      <div data-m={`d${k}`} className="cb cb--a cb--dots" style={{ top: chatT ? chatT.m[k === 1 ? "a1" : "a2"].top : 0, opacity: o, transform: `scale(${lerp(0.85, 1, ease.back(seg(t, a, a + 0.3)))})` }}>
        <div className="dots">{[0, 1, 2].map((i) => { const v = Math.max(0, Math.sin(t * 8 - i * 0.9)); return <i key={i} style={{ transform: `translateY(${-6 * v}px)`, opacity: 0.4 + 0.6 * v }} />; })}</div>
      </div>
    );
  };
  // The question being typed in the box; sent, the box empties.
  const typed = (text: string, [a, b]: number[], sent: number) => { if (t < a || t >= sent) return null; const q = [...text]; return q.slice(0, Math.round(q.length * seg(t, a, b))).join(""); };
  const cur = typed(C.q1, c.type1, c.q1) ?? typed(C.q2, c.type2, c.q2);
  return (
    // Always laid out (for the measure), shown only in its scenes.
    <div id="chatui" style={{ opacity: on ? 1 : 0, visibility: on ? "visible" : "hidden" }}>
      <div className="head"><svg viewBox="-16 -16 32 32"><circle r="15" fill="#d8ed9b" opacity="0.55" /><path d="M0 -13 Q2.1 -2.1 13 0 Q2.1 2.1 0 13 Q-2.1 2.1 -13 0 Q-2.1 -2.1 0 -13Z" fill="#184b3a" /></svg><span className="title">{D.text.waddah}</span><span className="soon">{D.text.when}</span></div>
      <div className="list">
        <div className="msgs" ref={msgs} style={{ transform: `translateY(${-(chatT ? kf(t, chatT.listY) : 0)}px)` }}>
          <div data-m="greet" className="cb cb--a" style={pop(c.greet)}>{C.greeting}</div>
          <div data-m="q1" className="cb cb--q" style={pop(c.q1)}>{C.q1}</div>
          <div data-m="a1" className="cb cb--a" style={pop(c.a1)}>
            <ol>{C.a1.map((l: string, i: number) => { const a = c.a1 + 0.1 + i * 0.9 * BEAT, p = ease.out(seg(t, a, a + 0.45)); return <li key={i} style={{ opacity: p, transform: `translateY(${(1 - p) * 14}px)` }}>{l}</li>; })}</ol>
            {chip(C.src1, c.chip1)}
          </div>
          <div data-m="q2" className="cb cb--q" style={pop(c.q2)}>{C.q2}</div>
          <div data-m="a2" className="cb cb--a" style={pop(c.a2)}>
            <span>{words(C.a2).map(({ w, space }: any, i: number) => { const a = c.a2 + 0.1 + i * 0.16, p = ease.out(seg(t, a, a + 0.4)); return <span key={i} className="w" style={{ opacity: p, transform: `translateY(${(1 - p) * 12}px)` }}>{w.split(/(\d+)/).map((x: string, j: number) => (/^\d+$/.test(x) ? <span key={j} className="num">{x}</span> : x))}{space}</span>; })}</span><br />
            {chip(C.src2, c.chip2)}
          </div>
          {dots(1, c.dots1)}
          {dots(2, c.dots2)}
        </div>
      </div>
      <div className="input"><span className="txt">{cur == null ? <span className="ph">{C.placeholder}</span> : <>{cur}<span className="caret" style={{ opacity: Math.floor(t * 2.5) % 2 === 0 || cur.length < 40 ? 1 : 0 }} /></>}</span>
        <span className="send"><svg viewBox="0 0 24 24"><path d="M12 19V5M5.5 11.5L12 5l6.5 6.5" fill="none" stroke="#f6f4ee" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" /></svg></span></div>
    </div>
  );
};

// ---------- highlights: rings (the rest dimmed a little), the الرواد stars lighting up, click ripples ----------
const Fx: React.FC<{ t: number; st: any }> = ({ t, st }) => {
  const out: React.ReactNode[] = [];
  tl.rings.forEach((r: any, ri: number) => {
    if (t < r.a || t > r.b) return;
    const b = r.world || onWorld(r.r, st[r.shot].s, st[r.shot].x);
    const pad = 12, draw = ease.out(seg(t, r.a, r.a + 0.5)), o = 1 - seg(t, r.b - 0.2, r.b);
    const box = { x: b.x - pad, y: b.y - pad, width: b.w + 2 * pad, height: b.h + 2 * pad, rx: 16 };
    out.push(
      <g key={`r${ri}`}>
        <defs><mask id={`m${ri}`}><rect x={SCREEN.x} y={SCREEN.y} width="640" height="1240" fill="#fff" /><rect {...box} fill="#000" /></mask></defs>
        <rect x={SCREEN.x} y={SCREEN.y} width="640" height="1240" rx="76" fill="#0a2018" opacity={0.22 * draw * o} mask={`url(#m${ri})`} />
        <g opacity={o}><rect className="ring-halo" {...box} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw} opacity="0.85" /><rect className="ring-line" {...box} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw} /></g>
      </g>,
    );
  });
  const mapOn = Math.min(seg(t, B("map", 0.3), B("map", 0.6)), 1 - seg(t, B("map", 6.4), B("map", 6.9)));
  if (mapOn > 0) {
    const scroll = kf(t, tl.shots.rw0.s);
    tl.stars.forEach((sp: any, k: number) => {
      const [x, y] = mid(onWorld({ x: sp.p[0], y: sp.p[1], w: 0, h: 0 }, scroll));
      const p = seg(t, sp.at, sp.at + 0.7);
      if (p > 0 && p < 1) out.push(<circle key={`sr${k}`} cx={x} cy={y} r={6 + ease.out(p) * 34} fill="none" stroke="#d8ed9b" strokeWidth={4 * (1 - p) + 0.5} opacity={(1 - p) * 0.9 * mapOn} />);
      const lit = seg(t, sp.at, sp.at + 0.25) * mapOn;
      if (lit > 0) out.push(<circle key={`sg${k}`} cx={x} cy={y} r="13" fill="#d8ed9b" opacity={0.28 * lit * (0.55 + 0.45 * Math.sin(t * 3.1 + sp.p[0] * 0.07))} />);
      if (sp.hover) {
        const h = Math.min(seg(t, B("map", 3.2), B("map", 3.6)), 1 - seg(t, B("map", 6.0), B("map", 6.3)));
        if (h > 0) out.push(<g key="hov"><circle cx={x} cy={y} r={22 + 3 * Math.sin(t * 6)} fill="#d8ed9b" opacity={0.4 * h} /><circle cx={x} cy={y} r="30" fill="none" stroke="#d8ed9b" strokeWidth="3" opacity={0.9 * h} /></g>);
      }
    });
  }
  tl.clicks.forEach((c: number, i: number) => {
    const p = seg(t, c, c + 0.5);
    if (p <= 0 || p >= 1) return;
    const at = cursorAt(tl.stops, c);
    out.push(<g key={`c${i}`}><circle cx={at[0]} cy={at[1]} r={14 + ease.out(p) * 46} fill="none" stroke="#d8ed9b" strokeWidth={6 * (1 - p) + 1} opacity={(1 - p) * 0.9} /><circle cx={at[0]} cy={at[1]} r={10 + ease.out(p) * 26} fill="rgba(24,75,58,0.25)" opacity={1 - p} /></g>);
  });
  return <svg id="fx" viewBox="0 0 1080 1920">{out}</svg>;
};

const Cursor: React.FC<{ t: number; z: number }> = ({ t, z }) => {
  const cp = cursorAt(tl.stops, t);
  const press = Math.max(0, ...tl.clicks.map((c: number) => 1 - Math.abs(t - c) / 0.09));
  const drag = tl.drags.some(([a, b]: number[]) => t >= a && t <= b) ? 1 : 0;
  const cs = (1 - 0.16 * Math.max(press, drag)) / Math.pow(z, 0.55);
  return (
    <div id="cursor" style={{ opacity: win(t, tl.cursorOn[0], tl.cursorOn[1], 0.3, 0.3), transform: `translate(${cp[0]}px, ${cp[1]}px) scale(${cs})` }}>
      <svg viewBox="0 0 32 38"><path d="M2 2 L2 31 L9.5 24 L14.5 35.5 L19.5 33.3 L14.6 22 L25 22 Z" fill="#f6f4ee" stroke="#101713" strokeWidth="2.2" strokeLinejoin="round" /></svg>
    </div>
  );
};

// ---------- captions, word by word ----------
const Captions: React.FC<{ t: number }> = ({ t }) => (
  <>{D.plan.scenes.flatMap((s: any) => (["intro", "chaos", "brand", "waddah"].includes(s.id) ? [] : s.lines.map((l: any, i: number) => {
    const next = s.lines[i + 1];
    const a = s.start + l.at, b = l.until != null ? s.start + l.until : next ? s.start + next.at : s.start + s.dur;
    if (t < a - 0.05 || t > b + 0.05) return null;
    const out = seg(t, b - 0.3, b);
    return (
      <div key={`${s.id}${i}`} className="cap"><p dir="rtl"><Words text={l.text} style={(j) => {
        const p = ease.out(seg(t, a + j * 0.055, a + j * 0.055 + 0.42));
        return { opacity: p * (1 - out), transform: `translateY(${(1 - p) * 34 - out * 26}px)`, filter: p < 1 ? `blur(${(1 - p) * 10}px)` : "none" };
      }} /></p></div>
    );
  })))}</>
);

// ---------- وضّاح, the host: poses, little hops between them, a soft shadow under him ----------
const Mascot: React.FC<{ t: number; z: number }> = ({ t, z }) => {
  if (t < tl.mascotOn[0]) return null;
  const [x0, y0, h0] = kf(t, tl.mascot);
  // In the corner he ducks down while the camera moves in close, so he never hides what it's showing.
  const tuck = t > B("home", 1.6) && t < B("waddah", 0.6) ? ease.io(clamp((z - 1.08) / 0.3)) : 0;
  const x = x0 - 50 * tuck, y = y0 + 125 * tuck, h = h0 * (1 - 0.15 * tuck);
  const w = h * MASCOT_RATIO;
  let cur = tl.pose[0][1], since = 0, prev = cur;
  for (const [pt, p] of tl.pose) if (t >= pt) { prev = cur; cur = p; since = pt; }
  const sw = seg(t, since, since + 0.12);
  const hop = Math.sin(Math.PI * seg(t, since, since + 0.3)) * (since > 0 ? 1 : 0);
  const bob = Math.sin(t * 2.4) * 6;
  // The burst of light at the drop, from him.
  const fl = seg(t, tl.dropT, tl.dropT + 1.2);
  return (
    <>
      {fl > 0 && fl < 1 && <div id="flash" style={{ opacity: Math.pow(1 - fl, 2) * 0.9, transform: `translate(${x}px, ${y}px) scale(${0.2 + ease.out(fl) * 1.1})` }} />}
      <div className="m-shadow" style={{ left: x - w * 0.32, top: y + h * 0.43, width: w * 0.64, height: h * 0.1, opacity: 0.5 - 0.15 * (bob / 6) }} />
      <div className="mascot" style={{ left: x - w / 2, top: y - h / 2 + bob, width: w, height: h, transform: `scale(${1 + 0.05 * hop}, ${1 - 0.07 * hop}) translateY(${-hop * 14}px)` }}>
        {POSES.map((p) => (
          <Img key={p} src={staticFile(`waddah/${p}.webp`)} style={{ opacity: p === cur ? sw : p === prev && sw < 1 ? 1 - sw : 0 }} />
        ))}
      </div>
    </>
  );
};

// ---------- the night: the teaser's cut-paper scene, with its depth, its stars and its dawn ----------
const STARS = (() => { const r = rng(7); return Array.from({ length: 90 }, () => ({ x: r() * 1080, y: 40 + r() * 1200, rad: 1.1 + r() * 2.6, ph: r() * 6.28, o: 0.25 + r() * 0.5 })); })();
const ART = { x: 0, y: 1200, s: 2.4 };
const Night: React.FC<{ t: number; o: number }> = ({ t, o }) => {
  if (o <= 0) return null;
  const lt = (t - S.waddah.start) / BEAT;
  const r = 1 - ease.out(seg(lt, 0.5, 5));
  const push = 1 + 0.05 * seg(lt, 2, 40);
  const dawn = ease.io(seg(lt, 12, 12 + 26));
  return (
    <div id="night" className="layer" style={{ opacity: o }}>
      <svg viewBox="0 0 1080 1920">
        <defs><radialGradient id="dawn" cx="0.74" cy="0.86" r="0.75"><stop offset="0" stopColor={mix("#10372a", "#d8ed9b", 0.1 + dawn * 0.42)} /><stop offset="1" stopColor="#10372a" stopOpacity="0" /></radialGradient></defs>
        <rect width="1080" height="1920" fill="#10372a" />
        <rect width="1080" height="1920" fill="url(#dawn)" opacity={0.35 + dawn * 0.65} />
        <g transform={`translate(${t * -4} 0)`}>{STARS.map((s, i) => <circle key={i} cx={s.x} cy={s.y} r={s.rad} fill="#f6f4ee" opacity={s.o * (0.6 + 0.4 * Math.sin(t * 1.7 + s.ph))} />)}</g>
        <g transform={`translate(0 ${(1 - dawn) * 200})`}><circle cx="860" cy="1640" r="190" fill="#d8ed9b" opacity="0.12" /><circle cx="860" cy="1640" r="90" fill="#d8ed9b" opacity="0.14" /></g>
        <g transform={`translate(540 1560) scale(${push}) translate(-540 -1560)`}><g transform={`translate(${ART.x} ${ART.y}) scale(${ART.s})`}>
          <g transform={`translate(0 ${r * 30})`}>
            <path className="art-moon" d="M66 28A17 17 0 1 0 66 62A19 19 0 0 1 66 28Z" style={{ opacity: 0.92 * (1 - seg(lt, 8, 10)) }} />
            <path className="art-city" d="M62 300V196c0-14 9-24 20-26c11 2 20 12 20 26v18h14v-34l9-14l9 14v34h12v-12l26-16l26 16v12h18v-18l7-24l7 24v18h12V300Z" />
            <g className="art-city-cols"><path d="M156 214v-10M164 214v-10M172 214v-10M180 214v-10M188 214v-10M196 214v-10" /></g>
            <circle className="art-city-clock" cx="125" cy="190" r="3.6" />
          </g>
          <g transform={`translate(0 ${r * 45})`}>
            <path className="art-dune--mid" d="M-30 300C40 262 130 244 250 242C350 240 430 254 520 300Z" />
            <path className="art-dune-edge" d="M-30 300C40 262 130 244 250 242C350 240 430 254 520 300" />
            <g transform="translate(418 266) scale(0.78)">
              <path className="art-palm-trunk" d="M-4 4C-2 -22 -4 -44 2 -64h6C4 -44 6 -22 6 4Z" />
              <path className="art-palm-frond" d="M5 -64C-12 -80 -36 -80 -54 -64C-34 -70 -16 -68 5 -64Z" />
              <path className="art-palm-frond" d="M5 -64C10 -84 30 -94 54 -88C34 -84 18 -76 5 -64Z" />
              <path className="art-palm-frond art-palm-frond--back" d="M5 -64C22 -70 44 -64 58 -44C42 -56 24 -62 5 -64Z" />
              <path className="art-palm-frond art-palm-frond--back" d="M5 -64C-10 -60 -28 -46 -34 -28C-22 -44 -10 -56 5 -64Z" />
              <path className="art-palm-frond" d="M5 -64C-4 -82 -20 -92 -40 -94C-22 -86 -8 -76 5 -64Z" />
            </g>
          </g>
          <g transform={`translate(0 ${r * 70})`}>
            <path className="art-dune--near" d="M150 300C180 270 240 256 300 255C364 254 420 270 470 300Z" />
            <ellipse className="help-glow" cx="240" cy="216" rx="40" ry="28" opacity={0.22 + 0.12 * Math.sin(t * 2)} />
            <path className="help-leg" d="M300 254L262 240L254 258" />
            <path className="help-shoe" d="M260 256h-22a5 5 0 0 0 0 10h22z" />
            <path className="help-laptop" d="M232 238L276 238" />
            <path className="help-screen" d="M234 236L226 204" />
            <path className="help-body" d="M290 258C284 228 288 204 300 194C308 188 322 188 330 194C342 204 346 228 340 258Z" />
            <path className="help-arm" d="M298 210C288 222 276 230 262 234" />
            <circle className="help-head" cx="315" cy="174" r="15" />
            <path className="help-hair" d="M300.5 178C298 166 304 159 315 159C326 159 331.5 166 329.5 178C328 184 324 187 320 188C316 184 309 183 304 185C302 183 301 181 300.5 178Z" />
            <ellipse className="help-ear" cx="301" cy="176" rx="2.6" ry="4" />
            <path className="help-rim" d="M291 250C286 226 290 206 300 196M315 159A15 15 0 0 0 300 178" />
          </g>
        </g></g>
      </svg>
    </div>
  );
};

// «وشيءٌ أخير…», then the name on the drop, «قادم في ديسمبر», the line; then up and away for the chat.
const WaddahTitle: React.FC<{ t: number }> = ({ t }) => {
  const lt = (t - S.waddah.start) / BEAT;
  const ia = S.waddah.start + S.waddah.lines[0].at;
  const iOut = seg(lt, 3.4, 3.95);
  const lift = ease.io(seg(lt, 5.8, 7.2));
  const mp = ease.back(seg(lt, 4.0, 4.7));
  const titleOut = seg(t, B("chat", 0), B("chat", 0.7));
  return (
    <>
      <div id="wintro" className="title" style={{ opacity: 1 - iOut, transform: `scale(${1 + 0.03 * seg(lt, 0.6, 4) + iOut * 0.08})`, filter: iOut > 0 ? `blur(${iOut * 14}px)` : "none" }}>
        <Words text={S.waddah.lines[0].text} style={(i) => rise(t, ia, i, 0.3, 0.7, 30)} />
      </div>
      <div id="wtitle" style={{ opacity: 1 - titleOut }}>
        <div className="mark" style={{ opacity: seg(lt, 4.0, 4.3), transform: `translateY(${lerp(420, 0, lift)}px) scale(${lerp(0.7, 1, mp) * lerp(1.25, 1, lift)})` }}>
          <svg width="150" height="150" viewBox="-16 -16 32 32"><circle r="15" fill="#d8ed9b" opacity={0.18 + 0.14 * Math.pow(Math.max(0, Math.cos(lt * Math.PI)), 8)} /><path d="M0 -13 Q2.1 -2.1 13 0 Q2.1 2.1 0 13 Q-2.1 2.1 -13 0 Q-2.1 -2.1 0 -13Z" fill="#d8ed9b" /></svg>
          <span className="title">{D.text.waddah}</span>
        </div>
        <p className="when" style={{ opacity: seg(lt, 4.6, 5.1), transform: `translateY(${lerp(420, 0, lift) + (1 - ease.out(seg(lt, 4.6, 5.2))) * 20}px)` }}>{D.text.when}</p>
        <p className="sub" style={{ transform: `translateY(${lerp(420, 0, lift)}px)` }}>
          <Words text={D.text.line} style={(i) => { const q = ease.out(seg(lt, 7.2 + i * 0.12, 7.2 + i * 0.12 + 0.7)); return { opacity: q, transform: `translateY(${(1 - q) * 20}px)` }; }} />
        </p>
      </div>
    </>
  );
};

const EndCard: React.FC<{ t: number }> = ({ t }) => {
  if (t < B("end", 0)) return null;
  const pop = (at: number): React.CSSProperties => {
    const p = ease.back(seg(t, B("end", at), B("end", at) + 0.55));
    return { opacity: seg(t, B("end", at), B("end", at) + 0.3), transform: `translateY(${(1 - p) * 40}px) scale(${lerp(0.85, 1, p)})` };
  };
  return (
    <div id="end">
      <Img src={staticFile("logo.svg")} style={pop(0.3)} />
      <p className="name title" style={pop(0.7)}>{D.text.name}</p>
      <p className="url" style={pop(1.5)}>wadihguide.com</p>
      <p className="note" style={pop(2.2)}>{D.text.independent}</p>
    </div>
  );
};
