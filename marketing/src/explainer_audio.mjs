// The explainer's soundtrack from free Mixkit files (decision 094; the list, licence and levels: explainer_audio.json).
// The music is one instrumental track, kept quiet under the picture and edited to it the way an editor would: it
// starts with the film (its soft opening under the question, its full band arriving as the logo lands), loses eight
// bars inside وضّاح's night (a whole phrase, cut on a downbeat, so the seam can't be heard), and its own soft ending
// plays under the end card. Every action in the picture (timeline.mjs's events) gets one quiet, real sound.
import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const SR = 48000;

function decode(file, channels = 2) {
  const raw = execFileSync("ffmpeg", ["-v", "error", "-i", file, "-f", "f32le", "-ac", String(channels), "-ar", String(SR), "-"], { maxBuffer: 1 << 30 });
  const x = new Float32Array(raw.buffer, raw.byteOffset, raw.byteLength / 4);
  if (channels === 1) return [x, x];
  const n = x.length / 2, L = new Float32Array(n), R = new Float32Array(n);
  for (let k = 0; k < n; k++) { L[k] = x[2 * k]; R[k] = x[2 * k + 1]; }
  return [L, R];
}

// The track's beat grid: tempo and phase from an onset envelope (two bands, log-energy rises), then the downbeat as
// the beat of the bar where the low band hits hardest.
function grid(L, R) {
  const hop = 512, N = Math.floor(L.length / hop), fr = SR / hop;
  const lo = new Float32Array(N), hi = new Float32Array(N);
  let lp = 0;
  for (let i = 0; i < N; i++) {
    let sl = 0, sh = 0;
    for (let k = 0; k < hop; k++) { const v = (L[i * hop + k] + R[i * hop + k]) / 2; lp += 0.03 * (v - lp); sl += lp * lp; sh += (v - lp) * (v - lp); }
    lo[i] = Math.log(1e-7 + sl); hi[i] = Math.log(1e-7 + sh);
  }
  const on = new Float32Array(N), onLo = new Float32Array(N);
  for (let i = 1; i < N; i++) { onLo[i] = Math.max(0, lo[i] - lo[i - 1]); on[i] = onLo[i] + Math.max(0, hi[i] - hi[i - 1]); }
  let best = [0, -1];
  for (let bpm = 80; bpm <= 140; bpm += 0.05) {
    const lag = (fr * 60) / bpm;
    let s = 0;
    for (let i = Math.ceil(lag); i < N; i++) { const a = i - lag, j = Math.floor(a), u = a - j; s += on[i] * (on[j] * (1 - u) + on[j + 1] * u); }
    if (s > best[1]) best = [bpm, s];
  }
  const beat = 60 / best[0], lag = beat * fr;
  let ph = [0, -1];
  for (let o = 0; o < lag; o += 0.25) { let s = 0; for (let t = o; t < N; t += lag) s += on[Math.round(t)] || 0; if (s > ph[1]) ph = [o, s]; }
  const first = ph[0] / fr;
  const sums = [0, 0, 0, 0];
  for (let k = 0; first + k * beat < L.length / SR; k++) { const i = Math.round((first + k * beat) * fr); for (let j = -2; j <= 2; j++) sums[k % 4] += onLo[i + j] || 0; }
  const down = sums.indexOf(Math.max(...sums));
  return { bpm: best[0], beat, bar: 4 * beat, downbeat: first + down * beat };
}

// One sound file, normalised to its peak, with the moment it starts (its first sample above a tenth of the peak).
function sample(file) {
  const [L, R] = decode(file);
  let peak = 1e-9;
  for (let k = 0; k < L.length; k++) peak = Math.max(peak, Math.abs(L[k]), Math.abs(R[k]));
  const g = 0.89 / peak;
  for (let k = 0; k < L.length; k++) { L[k] *= g; R[k] *= g; }
  let onset = 0;
  while (onset < L.length && Math.max(Math.abs(L[onset]), Math.abs(R[onset])) < 0.089) onset++;
  return { L, R, onset: Math.max(0, onset - Math.round(0.004 * SR)) };
}

function writeWav(to, L, R) {
  const n = L.length, buf = Buffer.alloc(44 + n * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write("WAVE", 8); buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(n * 4, 40);
  for (let k = 0; k < n; k++) {
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[k])) * 32767), 44 + k * 4);
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[k])) * 32767), 46 + k * 4);
  }
  writeFileSync(to, buf);
}

// Integrated loudness (ffmpeg's EBU R128 meter, which reports on stderr).
function integratedLufs(file) {
  const r = spawnSync("ffmpeg", ["-hide_banner", "-nostats", "-i", file, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], { encoding: "utf8" });
  return Number((/I:\s+(-?[\d.]+) LUFS/.exec(r.stderr || "") || [])[1]);
}

export function mixkitSoundtrack(plan, events, { fmt, cfg, dir, file, sfxOnly, log = console.log }) {
  const n = Math.ceil((plan.total + 1.0) * SR);
  const S = Object.fromEntries(plan.scenes.map((s) => [s.id, s]));
  const mL = new Float32Array(n), mR = new Float32Array(n), sL = new Float32Array(n), sR = new Float32Array(n);

  // ---- the music, edited to the picture ----
  const [tL, tR] = decode(join(dir, cfg.music.file));
  const g = grid(tL, tR);
  const bars = 8, delta = bars * g.bar;
  // The cut: the downbeat nearest the start of وضّاح's night, where the picture changes world too.
  const k = Math.round((S.waddah.start - g.downbeat) / g.bar);
  const cut = g.downbeat + k * g.bar, xf = 0.12;
  for (let i = 0; i < n; i++) {
    const v = i / SR;
    const a = v < cut + xf ? Math.min(1, Math.max(0, (cut + xf - v) / (2 * xf))) : 0;   // before the cut
    const b = 1 - a;
    let l = 0, r = 0;
    for (const [w, tt] of [[a, v], [b, v + delta]]) {
      if (w <= 0) continue;
      const x = tt * SR, j = Math.floor(x), u = x - j;
      if (j + 1 >= tL.length) continue;
      const ww = Math.sqrt(w);  // equal power
      l += ww * (tL[j] * (1 - u) + tL[j + 1] * u); r += ww * (tR[j] * (1 - u) + tR[j + 1] * u);
    }
    const fade = Math.min(1, v / 0.04) * Math.min(1, Math.max(0, (plan.total + 0.9 - v) / 1.6));
    mL[i] = l * fade; mR[i] = r * fade;
  }
  // Quiet: the music sits about 6 dB under the sounds' peaks (its level is set against the whole mix below).
  let sq = 0;
  for (let i = 0; i < n; i++) sq += mL[i] * mL[i] + mR[i] * mR[i];
  const mg = 0.075 / Math.sqrt(sq / (2 * n) || 1);
  for (let i = 0; i < n; i++) { mL[i] *= mg; mR[i] *= mg; }

  // ---- the sounds ----
  const files = {}, byRole = {};
  for (const s of cfg.sfx) {
    const f = ["wav", "mp3"].map((e) => join(dir, "sfx", `${s.id}.${e}`)).find(existsSync);
    if (!f) throw new Error(`missing Mixkit sound ${s.id} (${s.title}): run explainer.mjs again to download it`);
    files[s.id] = files[s.id] || sample(f);
    (byRole[s.role] = byRole[s.role] || []).push({ ...s, smp: files[s.id] });
  }
  const put = (t, smp, gain, { dur = null, pan = 0 } = {}) => {
    const i0 = Math.round(t * SR), len = dur ? Math.round(dur * SR) : smp.L.length - smp.onset, fo = Math.round(0.03 * SR);
    for (let j = 0; j < len; j++) {
      const i = i0 + j, src = smp.onset + j;
      if (i < 0 || i >= n || src >= smp.L.length) continue;
      const env = dur ? Math.min(1, j / fo, (len - j) / fo) : 1;
      sL[i] += smp.L[src] * gain * env * (1 - pan); sR[i] += smp.R[src] * gain * env * (1 + pan);
    }
  };
  const count = {};
  const typing = [];
  for (const e of events) {
    if (e.type === "type") {
      const last = typing[typing.length - 1];
      if (last && e.t - last[1] < 0.3) last[1] = e.t; else typing.push([e.t, e.t]);
      continue;
    }
    if (e.type === "word") {
      // A word lands: a deep, short hit under it (our own; no file needed).
      const i0 = Math.round(e.t * SR);
      let ph = 0;
      for (let j = 0; j < 0.5 * SR && i0 + j < n; j++) { const lt = j / SR; ph += (55 + 45 * Math.exp(-lt / 0.04)) / SR; const v = Math.sin(2 * Math.PI * ph) * Math.exp(-lt / 0.2) * 0.12; sL[i0 + j] += v; sR[i0 + j] += v; }
      continue;
    }
    const list = byRole[e.type];
    if (!list) continue;
    if (e.type === "twinkle" && e.v !== 0) continue;   // the stars: one sparkle, not one each
    const c = (count[e.type] = (count[e.type] || 0) + 1) - 1;
    const s = list[c % list.length];
    // A run of the same sound gets a little quieter each time, so it never sounds like a machine gun.
    const fadeRun = e.type === "paper" ? 1 - 0.035 * c : 1;
    put(e.t, s.smp, s.gain * fadeRun, { pan: e.type === "paper" ? ((c % 5) - 2) * 0.15 : 0 });
  }
  const typ = byRole[`type-${fmt}`]?.[0];
  if (typ) for (const [a, b] of typing) put(a - 0.02, typ.smp, typ.gain, { dur: b - a + 0.14 });

  // ---- mix, then level it: -16 LUFS, peaks under -1 dB ----
  const tmp = file.replace(/\.wav$/, ".raw.wav"), tmpS = file.replace(/\.wav$/, ".sfx.raw.wav");
  const L = new Float32Array(n), R = new Float32Array(n);
  for (let i = 0; i < n; i++) { L[i] = mL[i] + sL[i]; R[i] = mR[i] + sR[i]; }
  writeWav(tmp, L, R);
  writeWav(tmpS, sL, sR);
  const I = integratedLufs(tmp);
  const gain = Number.isFinite(I) ? -16 - I : 0;
  for (const [from, to] of [[tmp, file], [tmpS, sfxOnly]]) {
    if (!to) continue;
    execFileSync("ffmpeg", ["-y", "-v", "error", "-i", from, "-af", `volume=${gain.toFixed(2)}dB,alimiter=limit=0.89:level=disabled`, "-ar", String(SR), "-c:a", "pcm_s16le", to]);
  }
  rmSync(tmp, { force: true }); rmSync(tmpS, { force: true });
  log(`music: ${cfg.music.title} (${g.bpm.toFixed(2)} BPM), cut ${bars} bars at ${cut.toFixed(2)} s; mix ${Number.isFinite(I) ? I.toFixed(1) : "?"} LUFS → -16 LUFS`);
}
