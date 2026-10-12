"""Generates the ad's voice lines with ElevenLabs (decision 044) → marketing/assets/voice/l01.mp3 … l09.mp3.

Needs:
  1. a restricted ElevenLabs API key (Text to Speech only, with a credit limit) saved in
     %USERPROFILE%\\.wadih\\elevenlabs.key: outside the repo, never printed, never committed;
  2. marketing/voices.json with the voice IDs the owner picked after listening, e.g.
     {"hero": "…", "friend1": "…", "friend2": "…", "friend3": "…"}.
Run from the repo root:  .venv\\Scripts\\python.exe marketing/src/make_voice.py [l04 l09 …]
(no arguments = all lines; pass line ids to redo only some takes).
"""
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))
from build_ad import LINES  # the captions are the script: one source of truth  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
KEY_FILE = Path.home() / ".wadih" / "elevenlabs.key"
VOICES = ROOT / "marketing" / "voices.json"
OUT = ROOT / "marketing" / "assets" / "voice"
# Most expressive first; the first one the account can use for text to speech wins.
# voices.json may pin one: {"model": "eleven_multilingual_v2", …}
MODEL_PREFERENCE = ["eleven_v4", "eleven_v3", "eleven_multilingual_v2"]

# How each line should sound, as [audio tags]. Off unless voices.json says {"audio_tags": true}:
# only some models read them as hints, and others would say them out loud.
DELIVERY = {
    "l01": "[casual, confident]",
    "l02": "[excited]",
    "l03": "[curious, friendly]",
    "l04": "[quietly, unsure]",
    "l05": "[relieved]",
    "l06": "[calm]",
    "l07": "[calm, reassuring]",
    "l08": "[thoughtful]",
    "l09": "[quiet smile]",
}


def main():
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    voices = json.loads(VOICES.read_text(encoding="utf-8"))
    only = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    tags = voices.get("audio_tags", False)
    with httpx.Client(timeout=120, headers={"xi-api-key": key}) as client:
        model = voices.get("model")
        if not model:
            r = client.get("https://api.elevenlabs.io/v1/models")
            r.raise_for_status()
            usable = {m["model_id"] for m in r.json() if m.get("can_do_text_to_speech")}
            model = next((m for m in MODEL_PREFERENCE if m in usable), "eleven_multilingual_v2")
        print("model:", model)
        for lid, _t0, _t1, text, who in LINES:
            if only and lid not in only:
                continue
            body = {"text": f"{DELIVERY[lid]} {text}" if tags else text, "model_id": model}
            if model != "eleven_multilingual_v2":  # that model rejects language_code
                body["language_code"] = "ar"
            r = client.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voices[who]}",
                            params={"output_format": "mp3_44100_128"}, json=body)
            if r.status_code != 200:
                raise SystemExit(f"{lid}: ElevenLabs answered {r.status_code}: {r.text[:300]}")
            (OUT / f"{lid}.mp3").write_bytes(r.content)
            print(f"{lid} ({who}): {len(r.content) // 1024} KB")


if __name__ == "__main__":
    main()
