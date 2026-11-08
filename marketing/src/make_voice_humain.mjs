// The explainer's Arabic voice from HUMAIN Voice (marketing/README.md §9). Reads each line of explainer_script.json
// in one voice (its "say" when it has one: the same words with vowel marks, so «تتقدّم» isn't read «تَقَدَّمَ») and saves
// marketing/assets/explainer/voice/ar/<folder>/<id>.wav; `explainer.mjs --voice <folder>` then fits each scene to its clip.
// Uses HUMAIN's own SDK (`npm install --prefix marketing @humain-voice/sdk@0.18.0`), per docs.voice.humain.com
// (recipe "text-to-speech to file", read 2026-11-07). The key stays in your terminal: this script never prints it.
//
//   $env:HUMAIN_API_KEY = "<your key>"                       (PowerShell, this window only)
//   node marketing/src/make_voice_humain.mjs --list           the voices, with their dialect
//   node marketing/src/make_voice_humain.mjs --voice <id> --out nourah            every line, into voice/ar/nourah/
//   node marketing/src/make_voice_humain.mjs --voice <id> --out nourah --line 06  one line, to audition or redo

import { createRequire } from "node:module";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const argv = process.argv.slice(2);
const opt = (name) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : null; };
const key = process.env.HUMAIN_API_KEY;
if (!key) { console.error("Set HUMAIN_API_KEY in this terminal first (see the top of this file)."); process.exit(1); }

let sdk;
try { sdk = createRequire(join(ROOT, "marketing", "package.json"))("@humain-voice/sdk"); }
catch { console.error("Install HUMAIN's SDK first:  npm install --prefix marketing @humain-voice/sdk@0.18.0"); process.exit(1); }
const { TTSClient, TtsModel, getSampleRate } = sdk;

const client = new TTSClient({ api_url: process.env.HUMAIN_API_URL || "https://api.voice.humain.com", api_key: key });
try {
  if (argv.includes("--list")) {
    const voices = await client.listVoices({ timeoutSeconds: 10 });
    for (const v of voices) {
      const sp = v.profile?.speaker || {};
      console.log(`${v.id}\t${v.label || ""}\t${sp.gender || "?"}\t${sp.dialect || "?"}\t${(v.profile?.languages || []).join(",")}`);
    }
  } else {
    const voice = opt("voice");
    if (!voice) throw new Error("say which voice: --voice <id> (see --list)");
    const script = JSON.parse(readFileSync(join(ROOT, "marketing", "src", "explainer_script.json"), "utf8"));
    const only = opt("line");
    const lines = script.scenes.flatMap((s) => s.lines).filter((l) => !only || l.id === only);
    const out = opt("out");
    if (!out || !/^[a-z0-9_-]+$/i.test(out)) throw new Error("say which folder: --out <name> (letters, digits, - or _), e.g. --out nourah");
    const dir = join(ROOT, "marketing", "assets", "explainer", "voice", "ar", out);
    mkdirSync(dir, { recursive: true });
    const rate = getSampleRate(TtsModel.Nebula);
    for (const l of lines) {
      const text = (l.say || l.text).replace(/\*/g, "");
      const pcm = Buffer.from(await client.synthesize(text, {
        voice_id: voice, model: TtsModel.Nebula, timeoutSeconds: 30,
        onError: (e) => console.error(`line ${l.id}:`, e?.message || e),
      }));
      // The SDK gives raw PCM16 mono; a 44-byte WAV header makes it a file.
      const h = Buffer.alloc(44);
      h.write("RIFF", 0); h.writeUInt32LE(36 + pcm.length, 4); h.write("WAVE", 8); h.write("fmt ", 12);
      h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22); h.writeUInt32LE(rate, 24);
      h.writeUInt32LE(rate * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34); h.write("data", 36); h.writeUInt32LE(pcm.length, 40);
      writeFileSync(join(dir, `${l.id}.wav`), Buffer.concat([h, pcm]));
      console.log(`${l.id}.wav  ${(pcm.length / 2 / rate).toFixed(1)} s  ${text}`);
    }
  }
} finally {
  client.close();
}
