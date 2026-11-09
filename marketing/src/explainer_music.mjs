// The explainer's soundtrack (marketing/README.md §9, decisions 091–092), synthesised here: no samples, no library, no
// licence question. 100 BPM, in maqam Hijaz on D (D E♭ F♯ G A B♭ C, so the chords come from G minor), scored scene
// by scene the way a composer cuts to picture, with an Arabic voice over a modern beat:
//   intro     the question: warm B♭ major, the oud's first phrase, hopeful
//   chaos     the mess: a cluster on D and E♭, a heartbeat, a ticking clock, an anxious oud trill; a swipe, a breath of
//             silence, and…
//   brand     the hit: the oud states the motif, the Hijaz run D–E♭–F♯–G–A and back
//   home      a light verse (G minor, E♭, C minor): the darbuka's teks, a shaker, an oud answer
//   map       the stars: no kick, high bells in arpeggios over E♭ → D
//   filters   the groove: the darbuka plays maqsum, a half-time kick, a plucked ostinato
//   results   the build: C minor → D, four-on-the-floor, hats and arpeggio climbing, a roll into…
//   uni       the second verse, full, with an oud counter-line
//   official  E♭ → D, the Hijaz cadence, landing on the beat the official page appears; a breath
//   waddah    the breakdown: the oud's tremolo comes down the scale (A–G–F♯–E♭) under a riser, then the drop on «وضّاح»
//   chat      the chorus, warm and lifting: G minor opening onto B♭ and F major, eight bars of a new lead (no loop),
//             maqsum with ornaments, a riq (the Arabic tambourine), soft Gulf handclaps, an octave bass
//   end       a breath, then the final hit on D: the motif once more, slowly, down to D, ringing out.
// Every click, menu, swipe, keystroke, message and reveal gets its own sound (the stage's events()). Voice clips sit
// on top and the music steps back under them. A file in marketing/assets/explainer/music.* replaces the music.

import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";

const SR = 48000;
const TAU = Math.PI * 2;
const hz = (m) => 440 * Math.pow(2, (m - 69) / 12);
// "D5" → MIDI 74; "Bb2", "F#4" work too.
const nm = (s) => { const m = /^([A-G])(b|#)?(-?\d)$/.exec(s); return 12 * (+m[3] + 1) + { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 }[m[1]] + (m[2] === "b" ? -1 : m[2] === "#" ? 1 : 0); };
const notes = (str) => str.trim().split(/\s+/).map((x) => (x === "-" ? null : nm(x)));
const CHORD = Object.fromEntries(Object.entries({
  Dx: ["D2", "D3 Eb3 A3 D4 Eb4", "D4 Eb4 A4 D5"],     // the mess: D rubbing against its Hijaz neighbour E♭
  D:  ["D2", "D3 A3 D4 F#4 A4", "F#4 A4 D5 F#5"],
  Gm: ["G1", "G2 D3 Bb3 D4 G4", "G4 Bb4 D5 G5"],
  Eb: ["Eb2", "Eb3 G3 Bb3 D4 G4", "G4 Bb4 Eb5 G5"],
  Cm: ["C2", "C3 G3 C4 Eb4 G4", "G4 C5 Eb5 G5"],
  Bb: ["Bb1", "Bb2 F3 Bb3 D4 F4", "F4 Bb4 D5 F5"],
  F:  ["F2", "F3 C4 F4 A4 C5", "F4 A4 C5 F5"],
}).map(([k, [r, p, a]]) => [k, { root: nm(r), pad: notes(p), arp: notes(a) }]));

// The score: per part, its chords (one a bar) and how each instrument plays.
//   kick: "none" | "heart" | "one" | "half" (1 and 3) | "four";  hats: 0 none, 1 eighths, 2 sixteenths, "shaker"
//   clap: 0 none, 1 on 4, 2 on 2 and 4;  bass: null | "whole" | "quarter" | "eighth" | "octave"
//   arp: null | [step in beats, pattern of chord-tone indexes, level];  perc: the darbuka's pattern (PERC)
const SCORE = {
  intro:    { chords: ["Bb", "D"], pad: [700, 1400, 0.85], kick: "none", hats: 0, clap: 0, bass: "whole", arp: null, bells: "soft" },
  chaos:    { chords: ["Dx", "Dx"], pad: [260, 1200, 1.15], kick: "heart", hats: 0, clap: 0, bass: null, arp: null },
  brand:    { chords: ["D", "D"], pad: [1500, 2000, 0.9], kick: "one", hats: 0, clap: 0, bass: "whole", arp: null },
  home:     { chords: ["Gm", "Eb", "Cm"], pad: [1100, 1500, 0.6], kick: "half", hats: "shaker", clap: 1, bass: "maqsum", arp: [0.5, [0, 1, 2, 1], 0.05], perc: "maqsum" },
  map:      { chords: ["Eb", "D"], pad: [1700, 2400, 0.7], kick: "half", hats: "shaker", clap: 0, bass: "whole", arp: null, bells: true, perc: "light" },
  filters:  { chords: ["Gm", "Eb", "Cm", "D"], pad: [1300, 1600, 0.55], kick: "half", hats: 1, clap: 2, bass: "maqsum", arp: [0.5, [0, 1, 2, 3, 2, 1, 2, 1], 0.055], perc: "maqsum" },
  results:  { chords: ["Cm", "D"], pad: [1200, 2800, 0.6], kick: "four", hats: 2, clap: 2, bass: "eighth", arp: [0.25, [0, 1, 2, 3], 0.055], roll: true, perc: "maqsum" },
  uni:      { chords: ["Gm", "Eb", "D"], pad: [1800, 2000, 0.6], kick: "four", hats: 1, clap: 2, bass: "maqsum", arp: [0.25, [0, 2, 1, 3, 2, 1, 3, 2], 0.045], perc: "maqsum+" },
  official: { chords: ["Eb", "D"], pad: [1600, 2600, 0.65], kick: "half", hats: 1, clap: 0, bass: "whole", arp: null, perc: "light", stop: true },
  break:    { chords: ["Eb"], pad: [500, 3000, 0.95], kick: "none", hats: 0, clap: 0, bass: null, arp: null },
  drop:     { chords: ["Gm", "Eb", "Bb", "F", "Gm", "Eb", "Cm", "Eb"], pad: [2000, 2400, 0.75], kick: "four", hats: "riq", clap: 2, bass: "maqsum", arp: [0.5, [0, 2, 1, 3], 0.04], perc: "maqsum+", fills: [3, 7], stop: true, lift: 4, gulf: true },
  end:      { chords: ["D"], pad: [2000, 800, 1.0], kick: "none", hats: 0, clap: 0, bass: "whole", arp: null, once: 4 },
};
// The darbuka, in sixteenths: D doum (the low centre), T tek (the rim), k ka (a softer rim).
const PERC = {
  maqsum: "D-T---T-D---T---",
  "maqsum+": "D-Tk-kT-D-k-T-kk",
  light: "--k---T-----k-T-",
  teks: "------k-------T-",
  fill: "TkTkTkTkTkTkDDTk",
};
// The oud's lines, in steps from the start of their part (null = rest). The motif is the Hijaz run D–E♭–F♯–G–A.
const MELODY = {
  intro: { step: 0.5, vel: 0.2, notes: notes("- - D5 F5 G5 - F5 D5 C5 - A4 -") },
  brand: { step: 0.5, vel: 0.26, notes: notes("D5 Eb5 F#5 G5 A5 - G5 F#5 Eb5 - D5 -") },
  home: { step: 0.5, vel: 0.18, notes: notes("- - - - - - - - D5 - Eb5 F#5 G5 - F#5 Eb5 D5 - - -") },
  uni: { step: 1, vel: 0.15, notes: notes("G5 A5 Bb5 A5 G5 F#5 G5 - Eb5 F#5 Eb5 D5") },
  official: { step: 0.5, vel: 0.2, notes: notes("- - - - - - - - D5 - F#5 - A5 - D6 -") },
  drop: { step: 0.5, vel: 0.25, notes: notes(`
    G5 - A5 Bb5 A5 G5 F#5 G5   Bb5 - G5 - Eb5 F5 G5 -     F5 - Bb5 C6 D6 - C6 Bb5    C6 - A5 - F5 G5 A5 -
    D6 - Bb5 G5 A5 Bb5 C6 D6   Eb6 - D6 C6 Bb5 - G5 Bb5   C6 - Bb5 A5 G5 F#5 G5 A5   Bb5 A5 G5 F#5 Eb5 - F#5 -`) },
  end: { step: 1, vel: 0.26, notes: notes("A5 G5 F#5 Eb5 D5") },
};
// The breakdown: the oud's tremolo (rīsha) down the scale, [beat, note, beats].
const TREMOLO = [[0, "A4", 1.5], [1.5, "G4", 1], [2.5, "F#4", 0.75], [3.25, "Eb4", 0.75]];
// The string section (the sound of Arabic pop): legato lines, a note held until the next one ("-" holds). `double`
// plays an oud line an octave lower, in unison with it, the way a firqa's violins follow the soloist.
const STRINGS = {
  brand: { double: "brand", shift: -12, vel: 0.55 },
  home: { step: 1, vel: 0.32, notes: notes("D5 - C5 Bb4 Bb4 - A4 G4 G4 -") },
  map: { step: 1, vel: 0.3, notes: notes("G4 - - Bb4 A4 - - F#4") },
  filters: { step: 1, vel: 0.3, notes: notes("G4 A4 Bb4 - Bb4 C5 Bb4 G4 G4 Eb4 G4 C5 A4 - F#4 -") },
  results: { step: 0.5, vel: 0.36, notes: notes("C5 D5 Eb5 F5 G5 - Eb5 - F#5 G5 A5 Bb5 A5 - - -") },
  uni: { double: "uni", shift: -12, vel: 0.5 },
  official: { step: 1, vel: 0.34, notes: notes("G4 - Bb4 - A4 - F#4 -") },
  drop: { double: "drop", shift: -12, vel: 0.62 },
  end: { double: "end", shift: -12, vel: 0.55 },
};
// The qanun's runs: a quick sweep up the Hijaz scale into a new part, in 32nd notes ending on its downbeat.
const RUN = notes("D4 Eb4 F#4 G4 A4 Bb4 C5 D5 Eb5 F#5 G5 A5 Bb5 C6 D6");

// A sine table: fast enough to build a minute of additive synthesis in a few seconds.
const TS = 8192, SIN = new Float32Array(TS + 1);
for (let i = 0; i <= TS; i++) SIN[i] = Math.sin((i / TS) * TAU);
const fsin = (cycles) => { const x = (cycles - Math.floor(cycles)) * TS, i = x | 0; return SIN[i] + (SIN[i + 1] - SIN[i]) * (x - i); };
// A band-pass filter (RBJ's cookbook), as a function of the next sample.
function bp(f, q) {
  const w = TAU * f / SR, al = Math.sin(w) / (2 * q), a0 = 1 + al;
  const b0 = al / a0, b2 = -al / a0, a1 = -2 * Math.cos(w) / a0, a2 = (1 - al) / a0;
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  return (x) => { const y = b0 * x + b2 * x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = x; y2 = y1; y1 = y; return y; };
}

export function soundtrack(plan, events, file, { music = null, sfxOnly = null } = {}) {
  const n = Math.ceil((plan.total + 1.2) * SR);
  const mL = new Float32Array(n), mR = new Float32Array(n);   // music
  const sL = new Float32Array(n), sR = new Float32Array(n);   // sounds
  const verb = new Float32Array(n);                            // reverb send (mono)
  const S = Object.fromEntries(plan.scenes.map((s) => [s.id, s]));
  const beat = plan.beat, bar = plan.bar;
  const wT = S.waddah.start, dropT = wT + 4 * beat, endT = S.end.start;
  let seed = 11;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;
  const span = (t0, dur) => [Math.max(0, Math.floor(t0 * SR)), Math.min(n, Math.ceil((t0 + dur) * SR))];

  // The parts in time: each scene is one, except وضّاح's two: its breakdown, then the chorus through the chat.
  const parts = [];
  for (const s of plan.scenes) {
    if (s.id === "waddah") { parts.push({ id: "break", t0: wT, t1: dropT }); continue; }
    if (s.id === "chat") { parts.push({ id: "drop", t0: dropT, t1: s.start + s.dur }); continue; }
    parts.push({ id: s.id, t0: s.start, t1: s.id === "end" ? s.start + s.dur + 1 : s.start + s.dur });
  }
  // A part that ends with a breath stops its drums and bass half a beat early.
  const quiet = (p) => (SCORE[p.id].stop ? p.t1 - beat / 2 : p.t1);

  // Kicks first: the pad and the bass breathe with them (sidechain).
  const kicks = [];
  for (const p of parts) {
    const sc = SCORE[p.id];
    if (sc.kick === "one") kicks.push([p.t0, 0.5]);
    if (sc.kick === "heart") for (const [b, a] of [[0, 0.3], [0.4, 0.2], [3, 0.32], [3.4, 0.22], [5, 0.34], [5.4, 0.24], [6, 0.36], [6.3, 0.26], [6.6, 0.38], [6.9, 0.3]]) kicks.push([p.t0 + b * beat, a]);
    for (let t = p.t0, i = 0; t < quiet(p) - 1e-6; t += beat, i++) if (sc.kick === "four" || (sc.kick === "half" && i % 2 === 0)) kicks.push([t, 0.5]);
  }
  kicks.push([endT, 0.65]); // the final hit
  const duck = new Float32Array(n).fill(1);
  for (const [t0] of kicks) {
    const [a, b] = span(t0, 0.45);
    for (let k = a; k < b; k++) duck[k] = Math.min(duck[k], 1 - 0.5 * Math.exp(-(k / SR - t0) / 0.11));
  }

  if (music) {
    const raw = execFileSync("ffmpeg", ["-v", "error", "-i", music, "-f", "f32le", "-ac", "2", "-ar", String(SR), "-"], { maxBuffer: 1 << 30 });
    const pcm = new Float32Array(raw.buffer, raw.byteOffset, raw.byteLength / 4);
    for (let k = 0; k < n && 2 * k + 1 < pcm.length; k++) { mL[k] = pcm[2 * k]; mR[k] = pcm[2 * k + 1]; }
  } else {
    for (const p of parts) {
      const sc = SCORE[p.id];
      const len = p.t1 - p.t0, qEnd = quiet(p);
      // Chords, one a bar (a part that ends mid-bar ends on its last chord).
      // (The end holds one chord for `once` seconds, then lets it ring.)
      for (let k = 0; k * bar < len - 1e-6 && !(sc.once && k > 0); k++) {
        const c = CHORD[sc.chords[Math.min(k, sc.chords.length - 1)]];
        const t0 = p.t0 + k * bar, t1 = sc.once ? p.t0 + sc.once : Math.min(p.t0 + (k + 1) * bar, p.t1);
        // The mess's pad stops dead before the logo (the breath); the end's rings out.
        const rel = p.id === "end" ? 4.5 : p.id === "chaos" ? 0.04 : 0.45;
        pad(t0, p.id === "chaos" ? Math.min(t1, p.t1 - 0.12) : t1, c, sc.pad, rel, (t0 - p.t0) / len, (t1 - p.t0) / len, !["chaos", "break", "end"].includes(p.id));
        bass(t0, Math.min(t1, qEnd), c, sc.bass);
        if (sc.arp) {
          const [step, pat, vel] = sc.arp;
          for (let t = t0, i = 0; t < Math.min(t1, qEnd) - 1e-6; t += step * beat, i++) {
            const rising = sc.roll ? (t - p.t0) / len : 0;   // the build climbs an octave
            pluck(t, c.arp[pat[i % pat.length]] + (rising > 0.6 ? 12 : 0), vel * (i % 4 === 0 ? 1.25 : 1), ((i % 3) - 1) * 0.35);
          }
        }
        // The stars: bells in arpeggios, up then down, an octave above the chord.
        if (sc.bells) for (let i = 0; t0 + i * beat / (sc.bells === "soft" ? 2 : 4) < t1 - 1e-6; i++) {
          const up = [0, 1, 2, 3, 2, 3, 1, 2][i % 8], soft = sc.bells === "soft";
          bell(t0 + i * beat / (soft ? 2 : 4), hz(c.arp[up] + 12), (soft ? 0.01 : 0.016) * (1 + 0.4 * (i % 4 === 0)), ((i % 5) - 2) * 0.22, true);
        }
        // In the chorus's second half, a high line doubles each chord's root: the lift.
        if (sc.lift && k >= sc.lift) sine(t0, hz(c.root + 36), 0.02, 1.4);
      }
      // Drums.
      for (let t = p.t0, i = 0; t < qEnd - 1e-6; t += beat, i++) {
        if (sc.clap === 2 && i % 2 === 1) clap(t, 0.2);
        if (sc.clap === 1 && i % 4 === 3) clap(t, 0.17);
        if (sc.hats === 1 || sc.hats === 2) hat(t + beat / 2, false, 0.03);
        if (sc.hats === 2) { const g = p.id === "results" ? 0.01 + 0.024 * (t - p.t0) / len : 0.016; hat(t + beat / 4, false, g); hat(t + 3 * beat / 4, false, g); }
        if ((sc.hats === 1 || sc.hats === 2) && i % 4 === 3) hat(t + beat / 2, true, 0.02);
        if (sc.hats === "shaker") for (let j = 0; j < 4; j++) shaker(t + j * beat / 4, j % 2 ? 0.042 : 0.024);
        if (sc.hats === "riq") { riq(t, 0.05); riq(t + beat / 2, 0.075); if (i % 2) riq(t + 3 * beat / 4, 0.035); }
        // Gulf handclaps: two hands a little apart, on the off-beats of a khaleeji pattern, soft and wide.
        if (sc.gulf) for (const j of [2, 5, 7, 10, 14]) if (i % 4 === Math.floor(j / 4)) { const tt = t + (j % 4) * beat / 4; clap(tt, 0.06, -0.6); clap(tt + 0.012, 0.05, 0.6); }
      }
      // The darbuka: its pattern bar by bar; a fill on the bars named in `fills`.
      if (sc.perc) for (let k = 0; p.t0 + k * bar < qEnd - 1e-6; k++) {
        const fill = sc.fills && sc.fills.includes(k);
        const pat = PERC[sc.perc];
        for (let j = 0; j < 16; j++) {
          const t = p.t0 + k * bar + j * beat / 4;
          if (t >= qEnd - 1e-6) break;
          const ch = fill && j >= 8 ? PERC.fill[j] : pat[j];
          const hush = sc.perc === "light" || sc.perc === "teks" ? 0.6 : 1;
          if (ch === "D") doum(t, 0.3 * hush);
          else if (ch === "T") tek(t, 0.16 * hush, false);
          else if (ch === "k") tek(t, 0.09 * hush, true);
        }
      }
      // The last half bar of a build rolls into what comes next.
      if (sc.roll) for (let t = p.t1 - 2 * beat, i = 0; t < p.t1 - 1e-6; t += beat / 4, i++) clap(t, 0.05 + 0.012 * i);
      // The oud.
      const mel = MELODY[p.id];
      if (mel) mel.notes.forEach((m, i) => {
        if (m == null) return;
        const t = p.t0 + i * mel.step * beat;
        if (t >= p.t1 + (p.id === "end" ? 3 : 0)) return;
        const held = p.id === "end" && i === mel.notes.length - 1;
        const nextGap = mel.notes.slice(i + 1).findIndex((x) => x != null);
        const dur = held ? 3.2 : Math.min(1.2, (nextGap < 0 ? 2 : nextGap + 1) * mel.step * beat + 0.15);
        oud(t, m, mel.vel, 0.1, dur);
        if (held) tremolo(t + 0.9, m, mel.vel * 0.45, 0.1, 1.6);
      });
      // The strings.
      const st = STRINGS[p.id];
      if (st) {
        const src = st.double ? MELODY[st.double] : st, ns = src.notes, step = src.step * beat;
        const stop = p.id === "end" ? p.t1 + 2.5 : quiet(p);
        ns.forEach((m, i) => {
          if (m == null) return;
          const t = p.t0 + i * step;
          if (t >= stop - 1e-6) return;
          const next = ns.slice(i + 1).findIndex((x) => x != null);
          const dur = next < 0 ? stop - t : Math.min((next + 1) * step, stop - t);
          strings(t, m + (st.shift || 0), dur + 0.03, st.vel);
        });
      }
    }
    // The mess: an anxious trill on D and E♭ that grows, under a clock that speeds up.
    for (let t = S.chaos.start + 2 * beat, i = 0; t < S.chaos.start + 7 * beat; t += beat / 4, i++) {
      const p = (t - S.chaos.start) / (7 * beat);
      oud(t, nm(i % 2 ? "Eb4" : "D4"), 0.03 + 0.09 * p, -0.2, 0.2);
    }
    for (let t = S.chaos.start, i = 0; t < S.chaos.start + 7.5 * beat; i++) {
      tick(t, 0.05 + 0.05 * (t - S.chaos.start) / (7.5 * beat));
      t += t < S.chaos.start + 4 * beat ? beat / 2 : beat / 4;
    }
    // The qanun sweeps up into the parts that lift: home, the second verse, the chorus.
    for (const [t1, lo, vel] of [[S.home.start, 0, 0.1], [S.uni.start, 0, 0.12], [dropT, 7, 0.13]]) {
      const run = RUN.slice(lo, lo + 8);
      run.forEach((m, i) => qanun(t1 - (run.length - i) * beat / 8, m, vel * (0.6 + 0.4 * i / run.length), (i / run.length - 0.5) * 0.8));
    }
    // The breakdown's tremolo.
    for (const [b, m, d] of TREMOLO) tremolo(wT + b * beat, nm(m), 0.12, -0.1, d * beat);
    // Kicks, cymbals, risers, hits.
    for (const [t0, a] of kicks) kick(t0, a);
    for (const [t, a] of [[S.brand.start, 0.12], [S.home.start, 0.06], [S.uni.start, 0.1], [dropT, 0.16], [endT, 0.15]]) crash(t, a);
    swell(S.home.start - 2 * beat, 2 * beat, 0.04);
    swell(S.results.start - 2 * beat, 2 * beat, 0.05);
    swell(S.uni.start - 2 * beat, 2 * beat, 0.05);
    swell(endT - 2 * beat, 1.5 * beat, 0.05);
    riser(S.chaos.start + 3 * beat, 4 * beat, 0.08);
    riser(wT + 1 * beat, dropT - wT - 1 * beat, 0.14);
    impact(S.brand.start, 0.5);
    impact(dropT, 0.6);
    impact(endT, 0.45);
  }

  // ---- the sounds of the video's actions ----
  const SCALE = ["D6", "Eb6", "F#6", "G6", "A6", "Bb6", "C7", "D7", "Eb7", "F#7"];
  for (const e of events) {
    const t = e.t;
    if (e.type === "click") {
      tone(t, 0.03, (lt) => (fsin(2300 * lt) * 0.5 + fsin(3400 * lt) * 0.3) * Math.exp(-lt / 0.007) * 0.14 + fsin(180 * lt) * Math.exp(-lt / 0.02) * 0.1);
    } else if (e.type === "open") {
      tone(t, 0.12, (lt) => fsin((380 + 2400 * lt) * lt) * Math.exp(-lt / 0.05) * 0.07);
    } else if (e.type === "pop") {
      // A soft, low "thup", like something set down: no bloop (Shotcraft S1).
      tone(t, 0.12, (lt) => fsin((260 - 600 * lt) * lt) * Math.min(1, lt / 0.003) * Math.exp(-lt / 0.035) * 0.08);
    } else if (e.type === "tick") {
      tone(t, 0.03, (lt) => fsin(1800 * lt) * Math.exp(-lt / 0.008) * 0.05);
    } else if (e.type === "type") {
      const a = 0.025 + 0.02 * Math.abs(rnd());
      tone(t, 0.02, (lt) => (rnd() * 0.6 + fsin(3800 * lt) * 0.4) * Math.exp(-lt / 0.004) * a);
    } else if (e.type === "paper") {
      // Something lands on the pile: a soft slap of paper and a thump, each a little different.
      const f = 140 + 30 * ((e.v * 7) % 5), lp = bp(1800 + 300 * ((e.v * 3) % 4), 0.8);
      tone(t, 0.16, (lt) => lp(rnd()) * Math.exp(-lt / 0.03) * 0.22 + fsin(f * lt) * Math.exp(-lt / 0.05) * 0.12);
    } else if (e.type === "word") {
      // A word lands: a deep, short hit under it.
      let ph = 0;
      tone(t, 0.6, (lt) => { ph += (55 + 50 * Math.exp(-lt / 0.04)) / SR; return fsin(ph) * Math.exp(-lt / 0.22) * 0.14; });
    } else if (e.type === "send") {
      tone(t, 0.16, (lt) => fsin((420 + 3600 * lt) * lt) * Math.min(1, lt / 0.01) * Math.exp(-lt / 0.05) * 0.08);
    } else if (e.type === "recv") {
      // A message arrives: a muted tap and one quiet note of the chord.
      tone(t, 0.08, (lt) => fsin(420 * lt) * Math.min(1, lt / 0.002) * Math.exp(-lt / 0.02) * 0.06);
      bell(t + 0.02, hz(nm("D6")), 0.012, 0.1);
    } else if (e.type === "load") {
      // The official page arrives: a soft settle, felt more than heard.
      tone(t, 0.3, (lt) => fsin((180 - 160 * lt) * lt) * Math.min(1, lt / 0.01) * Math.exp(-lt / 0.09) * 0.07);
    } else if (e.type === "twinkle") {
      bell(t, hz(nm(SCALE[e.v % SCALE.length])), 0.013, ((e.v % 5) - 2) * 0.3);
    } else if (e.type === "whoosh" || e.type === "swipe" || e.type === "whip") {
      const dur = e.type === "whoosh" ? 0.8 : e.type === "whip" ? 0.45 : 0.4, amp = e.type === "swipe" ? 0.12 : 0.17;
      let lp = 0, lp2 = 0;
      const [a, b] = span(t - dur * 0.5, dur);
      for (let k = a; k < b; k++) {
        const p = (k - a) / (b - a), env = Math.pow(Math.sin(Math.PI * p), 2);
        const c = (e.type === "whip" ? 0.05 : 0.015) + 0.2 * env;
        lp += c * (rnd() - lp); lp2 += c * (lp - lp2);
        const v = lp2 * env * amp * 3, pan = (p - 0.5) * (e.type === "whip" ? -1.6 : 1.2);
        sL[k] += v * (1 - pan); sR[k] += v * (1 + pan);
      }
    } else if (e.type === "chime" || e.type === "shimmer") {
      // In the key: D major (Hijaz's home) for the logo, G minor for the drop.
      const seq = e.type === "chime" ? ["D5", "F#5", "A5", "D6"] : ["G5", "Bb5", "D6", "G6"];
      seq.forEach((m, i) => bell(t + i * 0.09, hz(nm(m)), e.type === "chime" ? 0.05 : 0.032, (i - 1.5) * 0.25));
    }
  }

  // ---- reverb (Freeverb's combs and all-passes) on the send ----
  const wet = freeverb(verb);
  for (let k = 0; k < n; k++) { mL[k] += wet[0][k] * 0.32; mR[k] += wet[1][k] * 0.32; }

  // ---- a master EQ on the music: a little less boom under 120 Hz, a little more air above 6 kHz (one-pole shelves) ----
  for (const ch of [mL, mR]) {
    const lo = Math.exp(-TAU * 120 / SR), hi = Math.exp(-TAU * 6000 / SR);
    let l1 = 0, h1 = 0;
    for (let k = 0; k < n; k++) {
      const x = ch[k];
      l1 = x + lo * (l1 - x); h1 = x + hi * (h1 - x);
      ch[k] = x - 0.22 * l1 + 0.45 * (x - h1);
    }
  }

  // ---- voice on top; the music steps back under it ----
  const vdk = new Float32Array(n).fill(1), voice = new Float32Array(n);
  for (const s of plan.scenes) for (const l of s.lines) {
    if (!l.voice) continue;
    const raw = execFileSync("ffmpeg", ["-v", "error", "-i", l.voice, "-af", "loudnorm=I=-16:TP=-1.5", "-f", "f32le", "-ac", "1", "-ar", String(SR), "-"], { maxBuffer: 1 << 28 });
    const v = new Float32Array(raw.buffer, raw.byteOffset, raw.byteLength / 4), i0 = Math.floor((s.start + l.at) * SR);
    for (let k = 0; k < v.length && i0 + k < n; k++) voice[i0 + k] += v[k];
    for (let k = Math.max(0, i0 - SR * 0.2); k < Math.min(n, i0 + v.length + SR * 0.3); k++) vdk[k] = 0.35;
  }
  // The action sounds sit under the music, not on top of it (subtle, as the owner asked).
  const SFX = 0.7;
  let gv = 1;
  const L = new Float32Array(n), R = new Float32Array(n);
  for (let k = 0; k < n; k++) {
    gv += (vdk[k] - gv) * 0.0005;
    L[k] = mL[k] * gv + sL[k] * SFX + voice[k];
    R[k] = mR[k] * gv + sR[k] * SFX + voice[k];
  }

  // ---- master: level to about -16 dB RMS, a soft clip for the peaks, a fade only at the very end ----
  let sq = 0;
  for (let k = 0; k < n; k++) sq += L[k] * L[k] + R[k] * R[k];
  const rms = Math.sqrt(sq / (2 * n)) || 1, pre = 0.16 / rms;
  let peak = 0;
  for (let k = 0; k < n; k++) {
    const t = k / SR, fade = Math.min(1, t / 0.05) * Math.min(1, Math.max(0, (plan.total + 1.1 - t) / 0.9));
    L[k] = Math.tanh(L[k] * pre * 1.15) * fade; R[k] = Math.tanh(R[k] * pre * 1.15) * fade;
    peak = Math.max(peak, Math.abs(L[k]), Math.abs(R[k]));
  }
  const post = peak > 0.89 ? 0.89 / peak : 1;
  const wav = (to, l, r) => {
    const buf = Buffer.alloc(44 + n * 4);
    buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write("WAVE", 8); buf.write("fmt ", 12);
    buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
    buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(n * 4, 40);
    for (let k = 0; k < n; k++) {
      buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, l[k] * post)) * 32767), 44 + k * 4);
      buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, r[k] * post)) * 32767), 46 + k * 4);
    }
    writeFileSync(to, buf);
  };
  wav(file, L, R);
  // The same sounds (and voice) without the music, at the same level, for a cut with your own licensed track.
  if (sfxOnly) {
    const l = new Float32Array(n), r = new Float32Array(n);
    for (let k = 0; k < n; k++) {
      const t = k / SR, fade = Math.min(1, t / 0.05) * Math.min(1, Math.max(0, (plan.total + 1.1 - t) / 0.9));
      l[k] = Math.tanh((sL[k] * SFX + voice[k]) * pre * 1.15) * fade; r[k] = Math.tanh((sR[k] * SFX + voice[k]) * pre * 1.15) * fade;
    }
    wav(sfxOnly, l, r);
  }

  // ---------- instruments ----------
  // Pad: detuned additive saws; the brightness opens across the part ([from, to] Hz), with an overall gain.
  function pad(t0, t1, c, [b0, b1, gain], rel, p0, p1, breathe) {
    const [a, b] = span(t0, t1 - t0 + rel);
    c.pad.forEach((m, j) => {
      const f = hz(m), pan = (j / (c.pad.length - 1) - 0.5) * 0.7;
      for (const det of [-0.0035, 0.0035]) {
        const fd = f * (1 + det);
        let w = [], blk = -1;
        for (let k = a; k < b; k++) {
          const t = k / SR, lt = t - t0;
          const env = Math.min(1, lt / 0.22) * (t > t1 ? Math.max(0, 1 - (t - t1) / rel) : 1);
          if (env <= 0) continue;
          if ((k >> 8) !== blk) {
            blk = k >> 8;
            const cut = b0 + (b1 - b0) * (p0 + (p1 - p0) * Math.min(1, lt / Math.max(0.01, t1 - t0)));
            w = [1, 2, 3, 4, 5, 6].map((h) => (1 / h) / Math.sqrt(1 + Math.pow((h * fd) / cut, 4)));
          }
          let v = 0;
          for (let h = 0; h < 6; h++) v += w[h] * fsin(fd * (h + 1) * t + j * 0.13 * (h + 1));
          v *= 0.016 * gain * env * (breathe ? duck[k] : 1);
          mL[k] += v * (1 - pan); mR[k] += v * (1 + pan);
          verb[k] += v * 0.35;
        }
      }
    });
  }
  function bass(t0, t1, c, style) {
    if (!style || t1 <= t0) return;
    const f0 = hz(c.root);
    // The maqsum bass: root, octave and fifth on the darbuka's syncopations, a little pushed ahead of the beat.
    if (style === "maqsum") {
      const pat = [[0, 0, 1], [3, 0, 0.7], [6, 12, 0.8], [8, 0, 1], [10, 7, 0.75], [14, 12, 0.7], [16]];
      for (let i = 0; i < pat.length - 1; i++) {
        const t = t0 + pat[i][0] * beat / 4;
        if (t >= t1 - 1e-6) break;
        const len = Math.min((pat[i + 1][0] - pat[i][0]) * beat / 4 * 0.82, t1 - t);
        const f = f0 * Math.pow(2, pat[i][1] / 12), [a, b] = span(t, len + 0.04);
        for (let k = a; k < b; k++) {
          const lt = k / SR - t;
          const env = Math.min(1, lt / 0.006) * (0.55 + 0.45 * Math.exp(-lt / 0.08)) * (lt > len ? Math.max(0, 1 - (lt - len) / 0.04) : 1);
          const ph = f * lt;
          const v = (Math.tanh(1.8 * (fsin(ph) + 0.4 * fsin(2 * ph) + 0.15 * fsin(3 * ph))) * 0.15 + fsin(ph) * 0.06) * env * pat[i][2] * duck[k];
          mL[k] += v; mR[k] += v;
        }
      }
      return;
    }
    const step = style === "whole" ? t1 - t0 : style === "quarter" ? beat : beat / 2;
    for (let t = t0, i = 0; t < t1 - 1e-6; t += step, i++) {
      const f = style === "octave" && i % 4 === 3 ? f0 * 2 : f0;
      const len = Math.min(step, t1 - t) * (style === "whole" ? 1 : 0.86);
      const [a, b] = span(t, len + 0.04);
      for (let k = a; k < b; k++) {
        const lt = k / SR - t;
        const env = Math.min(1, lt / 0.008) * (style === "whole" ? Math.exp(-lt / 2.5) : 0.6 + 0.4 * Math.exp(-lt / 0.09)) * (lt > len ? Math.max(0, 1 - (lt - len) / 0.04) : 1);
        const ph = f * lt;
        const v = Math.tanh(1.6 * (fsin(ph) + 0.35 * fsin(2 * ph) + 0.12 * fsin(3 * ph))) * 0.17 * env * duck[k];
        mL[k] += v; mR[k] += v;
      }
    }
  }
  function tone(t0, dur, fn) {
    const [a, b] = span(t0, dur);
    for (let k = a; k < b; k++) { const v = fn(k / SR - t0); sL[k] += v; sR[k] += v; }
  }
  function sine(t0, f, amp, dec) {
    const [a, b] = span(t0, dec * 4);
    for (let k = a; k < b; k++) { const lt = k / SR - t0; const v = fsin(f * lt) * amp * Math.min(1, lt / 0.01) * Math.exp(-lt / dec); mL[k] += v; mR[k] += v; verb[k] += v * 0.6; }
  }
  // Karplus–Strong: a burst of soft noise in a delay line that loses its highs each pass, like a plucked string.
  function pluck(t0, m, vel, pan, dur = 1.4) {
    const f = hz(m), len = Math.max(2, Math.round(SR / f - 0.5));
    const line = new Float32Array(len);
    let prev = 0;
    for (let i = 0; i < len; i++) { prev = prev * 0.5 + rnd() * 0.5; line[i] = prev; }
    const decay = 0.996 - Math.min(0.006, f / 200000);
    const [a, b] = span(t0, dur);
    for (let k = a, i = 0; k < b; k++, i++) {
      const j = i % len, nx = (j + 1) % len;
      const y = line[j];
      line[j] = decay * 0.5 * (y + line[nx]);
      const v = y * vel * Math.min(1, i / 40);
      mL[k] += v * (1 - pan); mR[k] += v * (1 + pan);
      verb[k] += v * 0.3;
    }
  }
  // Strings: three players a few cents apart (an ensemble), each a band-limited saw with a vibrato that comes in
  // after the note starts, a soft bow attack and a short release; spread across the stereo field.
  function strings(t0, m, dur, vel) {
    const f = hz(m), rel = 0.22, [a, b] = span(t0, dur + rel);
    const H = Math.max(1, Math.min(12, Math.floor(6000 / f)));
    const w = [];
    for (let h = 1; h <= H; h++) w.push((1 / h) / Math.sqrt(1 + Math.pow((h * f) / 2800, 4)));
    [[-0.005, -0.55], [0, 0], [0.0055, 0.55]].forEach(([det, pn], vi) => {
      const fd = f * (1 + det), vr = 5.1 + vi * 0.45;
      let ph = vi * 0.37;
      for (let k = a; k < b; k++) {
        const lt = k / SR - t0;
        const env = Math.min(1, lt / 0.07) * (lt > dur ? Math.max(0, 1 - (lt - dur) / rel) : 1);
        if (env <= 0) continue;
        ph += (fd * (1 + 0.005 * Math.min(1, Math.max(0, (lt - 0.15) / 0.3)) * fsin(vr * lt + vi))) / SR;
        let v = 0;
        for (let h = 0; h < H; h++) v += w[h] * fsin(ph * (h + 1));
        v *= vel * env * 0.032 * (0.7 + 0.3 * duck[k]);
        mL[k] += v * (1 - pn); mR[k] += v * (1 + pn);
        verb[k] += v * 0.5;
      }
    });
  }
  // The qanun: a bright plucked course of strings (the note and a faint octave), short and sparkling.
  function qanun(t0, m, vel, pan) {
    pluck(t0, m, vel, pan, 0.9);
    pluck(t0 + 0.004, m + 12, vel * 0.3, -pan, 0.5);
  }
  // The oud: a plucked string struck near the bridge (the excitation combed for its nasal bite), through a wooden
  // body (a resonance around 240 Hz) with a little brightness on top; short sustain, like gut on a fretless neck.
  function oud(t0, m, vel, pan, dur = 1.0) {
    const f = hz(m), len = Math.max(2, Math.round(SR / f - 0.5));
    const line = new Float32Array(len), raw = new Float32Array(len);
    let prev = 0;
    for (let i = 0; i < len; i++) { prev = prev * 0.3 + rnd() * 0.7; raw[i] = prev; }
    const d = Math.max(1, Math.round(len * 0.13));
    for (let i = 0; i < len; i++) line[i] = raw[i] - 0.75 * raw[(i - d + len) % len];
    const decay = 0.9955 - Math.min(0.004, f / 260000);
    const body = bp(240, 1.6), bite = bp(2400, 2.0);
    const [a, b] = span(t0, dur + 0.05);
    for (let k = a, i = 0; k < b; k++, i++) {
      const j = i % len, nx = (j + 1) % len;
      const y = line[j];
      line[j] = decay * 0.5 * (y + line[nx]);
      const lt = i / SR;
      const env = Math.min(1, i / 24) * (lt > dur ? Math.max(0, 1 - (lt - dur) / 0.05) : 1);
      const v = (y * 0.7 + body(y) * 0.9 + bite(y) * 0.25) * vel * env;
      mL[k] += v * (1 - pan); mR[k] += v * (1 + pan);
      verb[k] += v * 0.28;
    }
  }
  // Rīsha: the oud's fast tremolo on one note, the pick going down and up.
  function tremolo(t0, m, vel, pan, dur) {
    for (let t = t0, i = 0; t < t0 + dur - 0.02; t += 0.075, i++) oud(t, m, vel * (i % 2 ? 0.7 : 1) * (0.85 + 0.15 * Math.sin(i * 0.7)), pan, 0.2);
  }
  function kick(t0, amp) {
    const [a, b] = span(t0, 0.5);
    let ph = 0;
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0;
      ph += (44 + 110 * Math.exp(-lt / 0.035)) / SR;
      const v = (fsin(ph) * Math.exp(-lt / 0.26) + rnd() * 0.25 * Math.exp(-lt / 0.004)) * amp;
      mL[k] += v; mR[k] += v;
    }
  }
  // The darbuka: the doum is the skin's low centre (a falling pitch), the tek its rim (a bright, dry snap).
  function doum(t0, amp) {
    let ph = 0;
    const [a, b] = span(t0, 0.5);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0;
      ph += (88 + 60 * Math.exp(-lt / 0.018)) / SR;
      const v = (fsin(ph) * Math.exp(-lt / 0.2) + 0.35 * fsin(ph * 2.3) * Math.exp(-lt / 0.05) + rnd() * 0.25 * Math.exp(-lt / 0.003)) * amp;
      mL[k] += v * 0.9; mR[k] += v * 1.1; verb[k] += v * 0.15;
    }
  }
  function tek(t0, amp, soft) {
    const f1 = bp(soft ? 2600 : 3400, 1.4);
    const [a, b] = span(t0, 0.12);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0;
      const v = (f1(rnd()) * Math.exp(-lt / (soft ? 0.018 : 0.026)) * 2.2 + fsin((soft ? 700 : 880) * lt) * Math.exp(-lt / 0.015) * 0.5) * amp;
      mL[k] += v * 0.75; mR[k] += v * 1.25; verb[k] += v * 0.25;
    }
  }
  function shaker(t0, amp) {
    const f1 = bp(6500, 0.9);
    const [a, b] = span(t0, 0.08);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0;
      const v = f1(rnd()) * Math.min(1, lt / 0.006) * Math.exp(-lt / 0.02) * amp * 2;
      mL[k] += v * 1.25; mR[k] += v * 0.75;
    }
  }
  // The riq: a frame drum's jingles, a bright shimmer that rings a little.
  function riq(t0, amp) {
    const j1 = bp(7200, 3), j2 = bp(9800, 4), skin = bp(1100, 1.2);
    const [a, b] = span(t0, 0.22);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0, x = rnd();
      const v = ((j1(x) + j2(x) * 0.7) * Math.exp(-lt / 0.07) * (1 + 0.3 * Math.sin(lt * 260)) * 2.4 + skin(x) * Math.exp(-lt / 0.012) * 0.6) * amp;
      mL[k] += v * 0.7; mR[k] += v * 1.3; verb[k] += v * 0.15;
    }
  }
  function tick(t0, amp) {
    const [a, b] = span(t0, 0.03);
    for (let k = a; k < b; k++) { const lt = k / SR - t0; const v = (fsin(3100 * lt) * 0.6 + rnd() * 0.4) * Math.exp(-lt / 0.004) * amp; mL[k] += v * 0.7; mR[k] += v * 1.3; }
  }
  function clap(t0, amp, pan = 0) {
    let hp = 0, lp = 0, last = 0;
    const [a, b] = span(t0, 0.3);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0, x = rnd();
      hp = 0.85 * (hp + x - last); last = x; lp += 0.45 * (hp - lp);
      const burst = [0, 0.011, 0.022].reduce((s, o) => s + (lt >= o ? Math.exp(-(lt - o) / 0.006) : 0), 0);
      const v = lp * (burst * 0.6 + Math.exp(-lt / 0.11) * 0.5) * amp;
      mL[k] += v * (1 - pan); mR[k] += v * (1 + pan); verb[k] += v * 0.5;
    }
  }
  function hat(t0, open, amp) {
    let a1 = 0, a2 = 0;
    const d = open ? 0.12 : 0.028, [a, b] = span(t0, d * 5);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0, x = rnd();
      const h = x - a1; a1 = x; const h2 = h - a2; a2 = h;
      const v = h2 * Math.exp(-lt / d) * amp;
      mL[k] += v * 0.8; mR[k] += v * 1.2;
    }
  }
  // A cymbal: bright noise that rings and dies away, on the downbeats that start a new part.
  function crash(t0, amp) {
    let a1 = 0;
    const [a, b] = span(t0, 2.5);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0, x = rnd(), h = x - a1; a1 = x;
      const v = h * (Math.exp(-lt / 0.9) * 0.8 + Math.exp(-lt / 0.05) * 0.4) * amp;
      mL[k] += v * 0.9; mR[k] += v * 1.1; verb[k] += v * 0.3;
    }
  }
  // A reversed cymbal: swells up into a downbeat.
  function swell(t0, dur, amp) {
    let a1 = 0;
    const [a, b] = span(t0, dur);
    for (let k = a; k < b; k++) {
      const p = (k - a) / (b - a), x = rnd(), h = x - a1; a1 = x;
      const v = h * Math.pow(p, 3) * amp;
      mL[k] += v; mR[k] += v;
    }
  }
  function riser(t0, dur, amp) {
    let lp = 0;
    const [a, b] = span(t0, dur);
    for (let k = a; k < b; k++) {
      const p = (k - a) / (b - a), lt = k / SR - t0;
      const c = 0.01 + 0.5 * p * p;
      lp += c * (rnd() - lp);
      const sweep = fsin((180 * lt) + (900 * lt * lt) / (2 * dur));
      const v = (lp * 0.8 + sweep * 0.15) * p * p * amp;
      mL[k] += v; mR[k] += v; verb[k] += v * 0.4;
    }
  }
  function impact(t0, amp) {
    let ph = 0, lp = 0;
    const [a, b] = span(t0, 1.8);
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0;
      ph += (38 + 40 * Math.exp(-lt / 0.08)) / SR;
      lp += 0.05 * (rnd() - lp);
      const v = (fsin(ph) * Math.exp(-lt / 0.55) + lp * 2 * Math.exp(-lt / 0.25)) * amp;
      mL[k] += v; mR[k] += v; verb[k] += v * 0.3;
    }
  }
  // An FM bell; on the music bus for the stars, on the sounds bus for the reveals.
  function bell(t0, f, amp, pan, onMusic = false) {
    const [a, b] = span(t0, 2.6);
    const L = onMusic ? mL : sL, R = onMusic ? mR : sR;
    for (let k = a; k < b; k++) {
      const lt = k / SR - t0;
      const v = fsin(f * lt + 2.2 * Math.exp(-lt / 0.4) * fsin(3.5 * f * lt) / TAU) * Math.exp(-lt / 1.1) * Math.min(1, lt / 0.003) * amp;
      L[k] += v * (1 - pan); R[k] += v * (1 + pan);
      verb[k] += v * 0.5;
    }
  }
}

// Freeverb: eight damped combs in parallel, then four all-passes, per channel (the right one slightly longer).
function freeverb(input) {
  const scale = SR / 44100;
  const combs = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617], alls = [556, 441, 341, 225];
  const out = [];
  for (const spread of [0, 23]) {
    const y = new Float32Array(input.length);
    for (const d0 of combs) {
      const d = Math.round((d0 + spread) * scale), buf = new Float32Array(d);
      let i = 0, store = 0;
      for (let k = 0; k < input.length; k++) {
        const o = buf[i];
        store = o * 0.8 + store * 0.2;
        buf[i] = input[k] * 0.015 + store * 0.84;
        y[k] += o;
        if (++i >= d) i = 0;
      }
    }
    for (const d0 of alls) {
      const d = Math.round((d0 + spread) * scale), buf = new Float32Array(d);
      let i = 0;
      for (let k = 0; k < y.length; k++) {
        const b = buf[i], x = y[k];
        y[k] = -x + b;
        buf[i] = x + b * 0.5;
        if (++i >= d) i = 0;
      }
    }
    out.push(y);
  }
  return out;
}
