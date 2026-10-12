"""Builds the واضح launch ad (decision 044): 30s master + 15s and 6s cutdowns, 1080×1920.

Inputs (all git-ignored, under marketing/assets/):
  screen/   real frames of wadihguide.com from capture_site.mjs
  clips/    shot1.mp4 … shot4.mp4 from Higgsfield (a labelled placeholder is used while missing)
  voice/    l01.mp3 … l09.mp3 from ElevenLabs, one per line in LINES (silent while missing)
  ambience.mp3 (optional) quiet school-courtyard sound under the story shots
Text (captions, end card) is rendered from HTML by the installed Microsoft Edge, so Arabic is shaped
correctly in the site's own fonts. Run from the repo root:
  .venv\\Scripts\\python.exe marketing/src/build_ad.py
"""
import base64
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "marketing"
A = M / "assets"
SCREEN = A / "screen"
WORK = A / "build"
OUT = M / "out"
FONTS = ROOT / "app" / "static" / "fonts"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
W, H, FPS = 1080, 1920, 30

# Brand (decision 035)
IVORY, CHARCOAL, FOREST, LIME = "#F6F4EE", "#101713", "#184B3A", "#D8ED9B"

# The story. Times in seconds on the 30s master.
SHOTS = [  # (name, start, end, kind)
    ("shot1", 0.0, 3.0, "ai"),
    ("shot2", 3.0, 6.4, "ai"),
    ("shot3", 6.4, 9.6, "ai"),
    ("screen", 9.6, 23.6, "screen"),
    ("shot4", 23.6, 27.0, "ai"),
    ("end", 27.0, 30.0, "end"),
]
# (id, start, end, caption, who). The caption is exactly what the voice says.
LINES = [
    ("l01", 0.3, 2.8, "أنا خلاص، بقدّم على أرامكو.", "friend1"),
    ("l02", 3.1, 4.9, "وأنا الرواد… أبي أدرس برّا.", "friend2"),
    ("l03", 4.9, 6.3, "وأنت؟ وش ناوي؟", "friend3"),
    ("l04", 7.4, 9.5, "…ما أدري.", "hero"),
    ("l05", 9.8, 11.2, "لقيت «واضح».", "hero"),
    ("l06", 11.2, 15.0, "اخترت صفّي، وبحثت عن التخصص اللي يعجبني…", "hero"),
    ("l07", 17.4, 21.6, "وكل معلومة معها رابط مصدرها الرسمي.", "hero"),
    ("l08", 23.8, 25.4, "أنا؟ لسّه أقرّر…", "hero"),
    ("l09", 25.4, 27.0, "بس عرفت خطوتي الجاية.", "hero"),
]
AI_NOTE = "مشهد تمثيلي مولَّد بالذكاء الاصطناعي"
SHOT_BRIEF = {
    "shot1": "ساحة مدرسة وقت الفسحة، أربعة طلاب بالثوب من الخلف",
    "shot2": "من فوق كتف صديقه، والطالب في الخلفية غير واضح",
    "shot3": "يدا الطالب والجوال، صمت",
    "shot4": "مع الشلة من الجانب، يدخل الجوال جيبه",
}

# The phone screen sits in a card on forest green: 0.8333 scale → 900×1600 at (90, 110).
CARD_S, CARD_X, CARD_Y = 900 / 1080, 90, 110


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise SystemExit(f"failed: {cmd[0]} …\n{p.stderr[-2000:]}")


def ff(*args):
    run([FFMPEG, "-y", "-v", "error", *args])


def font_face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{data}) format('woff2');font-weight:{weight};}}"


CSS_FONTS = "".join([
    font_face("Plex", "ibm-plex-sans-arabic-arabic-700.woff2", 700),
    font_face("Plex", "ibm-plex-sans-arabic-latin-700.woff2", 700),
    font_face("Plex", "ibm-plex-sans-arabic-arabic-400.woff2", 400),
    font_face("Plex", "ibm-plex-sans-arabic-latin-400.woff2", 400),
    font_face("Naskh", "noto-naskh-arabic-arabic-700.woff2", 700),
])


def render_html(name, body, css="", transparent=True):
    """HTML → 1080×1920 PNG with Edge headless (transparent background unless the page paints one)."""
    html = WORK / f"{name}.html"
    png = WORK / f"{name}.png"
    html.write_text(
        f"<!doctype html><html lang='ar' dir='rtl'><head><meta charset='utf-8'><style>{CSS_FONTS}"
        f"html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:transparent;"
        f"font-family:Plex,sans-serif;}}{css}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )
    run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
         f"--window-size={W},{H}", "--default-background-color=00000000", "--virtual-time-budget=3000",
         f"--screenshot={png}", html.as_uri()])
    with Image.open(png) as im:  # Edge may add a few px; keep exactly 1080×1920
        if im.size != (W, H):
            im.crop((0, 0, W, H)).save(png)
    return png


def caption_png(line_id, text):
    css = (f".cap{{position:absolute;left:50%;transform:translateX(-50%);bottom:{H - 1500}px;"
           f"max-width:880px;width:max-content;box-sizing:border-box;padding:22px 40px 28px;"
           f"background:rgba(16,23,19,.90);color:{IVORY};border-radius:24px;font-weight:700;"
           f"font-size:60px;line-height:1.45;text-align:center;}}")
    return render_html(f"cap_{line_id}", f"<div class='cap'>{text}</div>", css)


def ai_note_png():
    css = (f".n{{position:absolute;top:250px;right:60px;padding:8px 18px;border-radius:12px;"
           f"background:rgba(16,23,19,.70);color:{IVORY};font-size:30px;font-weight:400;}}")
    return render_html("ai_note", f"<div class='n'>{AI_NOTE}</div>", css)


def placeholder_png(name):
    css = (f"body{{background:{CHARCOAL}!important;color:{IVORY};display:flex;flex-direction:column;"
           f"justify-content:center;align-items:center;text-align:center;gap:24px;}}"
           f".t{{font-size:56px;font-weight:700;}} .d{{font-size:40px;opacity:.8;max-width:820px;}}")
    body = f"<div class='t'>لقطة {name[-1]} · بانتظار Higgsfield</div><div class='d'>{SHOT_BRIEF[name]}</div>"
    return render_html(f"ph_{name}", body, css, transparent=False)


def end_card_png():
    svg = (ROOT / "app" / "static" / "favicon.svg").read_text(encoding="utf-8")
    svg = svg.replace('viewBox="0 0 64 64">', 'viewBox="0 0 64 64" width="260" height="260">', 1)
    css = (f"body{{background:{IVORY}!important;color:{CHARCOAL};display:flex;flex-direction:column;"
           f"align-items:center;justify-content:center;text-align:center;}}"
           f".wm{{font-family:Naskh;font-weight:700;font-size:150px;color:{FOREST};line-height:1.2;margin-top:24px;}}"
           f".tag{{font-weight:700;font-size:64px;color:{FOREST};line-height:1.35;margin:8px 80px 0;}}"
           f".url{{margin-top:64px;background:{LIME};color:{CHARCOAL};font-weight:700;font-size:66px;"
           f"padding:18px 48px 24px;border-radius:999px;direction:ltr;}}"
           f".fine{{margin-top:56px;font-size:38px;line-height:1.6;color:{CHARCOAL};max-width:860px;}}")
    body = (f"{svg}<div class='wm'>واضح</div><div class='tag'>مستقبلك بعد الثانوية، بوضوح</div>"
            f"<div class='url'>wadihguide.com</div>"
            f"<div class='fine'>مجاني · بدون تسجيل<br>دليل مستقل، غير تابع لأي جهة حكومية</div>")
    return render_html("end_card", body, css, transparent=False)


def card_assets():
    """Forest background and a rounded mask for the phone-screen card; a tap ring."""
    bg = WORK / "forest.png"
    Image.new("RGB", (W, H), FOREST).save(bg)
    cw, ch = round(W * CARD_S), round(H * CARD_S)
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=44, fill=255)
    mask.save(WORK / "card_mask.png")
    ring = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    d.ellipse((6, 6, 134, 134), fill=(16, 23, 19, 70), outline=(16, 23, 19, 230), width=6)
    d.ellipse((40, 40, 100, 100), fill=(246, 244, 238, 200))
    ring.save(WORK / "tap.png")
    hl = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle((20, 10, W - 20, 250), radius=28, outline=FOREST, width=12)
    hl.save(WORK / "highlight.png")
    return bg


def ease(p):  # smoothstep for scrolls, as an ffmpeg expression of p in [0,1]
    return f"(3*pow({p},2)-2*pow({p},3))"


def screen_part(i, src, dur, scroll=None, tap=None, highlight=None):
    """One sub-shot of the phone screen: a still, a typing frame or a scroll over a full-page image.
    scroll=(y0, y1, t0, t1) in image px; tap=(css_x, css_y, t) in the 390-px viewport;
    highlight=y (px in the 1080×1920 frame) of a lime ring around an official-source line."""
    out = WORK / f"screen_{i:02d}.mp4"
    if scroll:
        y0, y1, t0, t1 = scroll
        p = f"min(1,max(0,(t-{t0})/{t1 - t0}))"
        crop = f"crop={W}:{H}:0:'{y0}+({y1 - y0})*{ease(p)}'"
    else:
        crop = "crop=iw:ih:0:0"  # viewport frames are 1080×1919; the scale below evens it out
    inputs = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(src)]
    chain = f"[0:v]{crop},scale=900:1600,setsar=1,format=rgba[c0]"
    n, c = 1, 0  # next input index, current label number
    if highlight is not None:
        inputs += ["-loop", "1", "-i", str(WORK / "highlight.png")]
        y = round(highlight * CARD_S) - 80
        chain += f";[{n}:v]scale=900:-1[h];[c{c}][h]overlay=0:{y}:enable='gte(t,{dur * 0.55})'[c{c + 1}]"
        n, c = n + 1, c + 1
    if tap:
        x, y, t = tap
        px, py = round(x * 1080 / 390 * CARD_S) - 70, round(y * 1080 / 390 * CARD_S) - 70
        inputs += ["-loop", "1", "-i", str(WORK / "tap.png")]
        chain += f";[c{c}][{n}:v]overlay={px}:{py}:enable='between(t,{t},{t + 0.45})'[c{c + 1}]"
        n, c = n + 1, c + 1
    inputs += ["-loop", "1", "-i", str(WORK / "card_mask.png")]
    chain += f";[{n}:v]format=gray[m];[c{c}][m]alphamerge[c{c + 1}]"
    n, c = n + 1, c + 1
    inputs += ["-loop", "1", "-i", str(WORK / "forest.png")]
    chain += f";[{n}:v][c{c}]overlay={CARD_X}:{CARD_Y}:shortest=1,format=yuv420p[v]"
    ff(*inputs, "-filter_complex", chain, "-map", "[v]", "-t", f"{dur}", "-r", str(FPS),
       "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(out))
    return out


def build_screen():
    r = json.loads((SCREEN / "rects.json").read_text(encoding="utf-8"))
    f = lambda key: SCREEN / (r[key] if isinstance(r[key], str) else r[key]["file"])
    parts = []
    g = r["grade12_tap"]
    parts.append(screen_part(0, f("home"), 1.6, tap=(g["x"], g["y"], 1.05)))
    parts.append(screen_part(1, f("grade12"), 1.4))
    for k, name in enumerate(r["typing"]):
        parts.append(screen_part(2 + k, SCREEN / name, 0.15))
    s = r["suggest_tap"]
    parts.append(screen_part(10, f("typed"), 1.2, tap=(s["x"], s["y"], 0.75)))
    # Results: scroll to the first rows (Harvard near the middle), then tap it.
    top = max(0, round(r["first_uni_pagey"] * r["DSF"]) - 760)
    parts.append(screen_part(11, f("results_full"), 2.4, scroll=(0, top, 0.2, 1.7),
                             tap=(300, (r["first_uni_pagey"] * r["DSF"] - top) / r["DSF"], 1.95)))
    parts.append(screen_part(12, f("uni"), 1.0))
    # University page: scroll down to «المصدر: الدليل الاسترشادي، صفحة …» and ring it.
    src_y = round(r["uni_source_pagey"] * r["DSF"])
    top2 = max(0, src_y - 900)
    parts.append(screen_part(13, f("uni_full"), 3.2, scroll=(0, top2, 0.1, 1.4), highlight=src_y - top2))
    st = r["save_tap"]
    parts.append(screen_part(14, f("uni"), 0.5, tap=(st["x"], st["y"], 0.1)))
    parts.append(screen_part(15, f("uni_saved"), 0.7))
    parts.append(screen_part(16, f("mylist"), 0.8))
    return concat(parts, WORK / "screen.mp4")


def concat(parts, out):
    lst = WORK / (out.stem + "_list.txt")
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out))
    return out


def build_ai(name, dur, note):
    clip = A / "clips" / f"{name}.mp4"
    out = WORK / f"{name}.mp4"
    if clip.exists():
        inputs = ["-i", str(clip)]
        chain = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"fps={FPS},trim=duration={dur},setpts=PTS-STARTPTS[c]")
    else:
        inputs = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(placeholder_png(name))]
        chain = "[0:v]setsar=1[c]"
    if note:
        inputs += ["-loop", "1", "-i", str(WORK / "ai_note.png")]
        chain += ";[c][1:v]overlay=0:0:shortest=1[n]"
    chain += f";[{'n' if note else 'c'}]format=yuv420p[v]"
    ff(*inputs, "-filter_complex", chain, "-map", "[v]", "-t", f"{dur}", "-r", str(FPS),
       "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(out))
    return out


def build_end(dur):
    out = WORK / "end.mp4"
    ff("-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(end_card_png()),
       "-vf", "format=yuv420p", "-r", str(FPS), "-c:v", "libx264", "-crf", "16", str(out))
    return out


def overlay_captions(video, out, lines, offset=0.0):
    inputs = ["-i", str(video)]
    chain, last = "", "0:v"
    for k, (lid, t0, t1, text, _) in enumerate(lines, start=1):
        inputs += ["-i", str(caption_png(lid, text))]
        chain += f"[{last}][{k}:v]overlay=0:0:enable='between(t,{t0 - offset},{t1 - offset})'[v{k}];"
        last = f"v{k}"
    ff(*inputs, "-filter_complex", chain + f"[{last}]format=yuv420p[v]", "-map", "[v]",
       "-c:v", "libx264", "-crf", "17", "-preset", "medium", str(out))
    return out


def build_audio(total, out, lines, offset=0.0, ambience_until=None):
    """Voice lines at their start times + optional ambience, loudness-normalised to −14 LUFS."""
    inputs = ["-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=48000:cl=stereo"]
    chain, mix = "", ["[0:a]"]
    k = 1
    for lid, t0, *_ in lines:
        v = A / "voice" / f"{lid}.mp3"
        if v.exists():
            inputs += ["-i", str(v)]
            ms = max(0, round((t0 - offset) * 1000))
            chain += f"[{k}:a]aresample=48000,adelay={ms}|{ms}[a{k}];"
            mix.append(f"[a{k}]")
            k += 1
    amb = A / "ambience.mp3"
    if amb.exists() and ambience_until:
        inputs += ["-i", str(amb)]
        chain += f"[{k}:a]aresample=48000,atrim=0:{ambience_until},afade=t=out:st={ambience_until - 0.6}:d=0.6,volume=0.18[amb];"
        mix.append("[amb]")
    chain += f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    ff(*inputs, "-filter_complex", chain, "-map", "[a]", "-t", f"{total}", "-c:a", "aac", "-b:a", "192k", str(out))
    return out


def mux(video, audio, out):
    ff("-i", str(video), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
       "-movflags", "+faststart", "-shortest", str(out))


def cut(src, out, segments):
    """Cutdown from the captioned master: segments = [(start, end), …] joined in order."""
    parts = []
    for k, (a, b) in enumerate(segments):
        p = WORK / f"{out.stem}_{k}.mp4"
        ff("-ss", f"{a}", "-to", f"{b}", "-i", str(src), "-c:v", "libx264", "-crf", "17", "-c:a", "aac",
           "-b:a", "192k", "-r", str(FPS), str(p))
        parts.append(p)
    concat(parts, out)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    card_assets()
    ai_note_png()
    clips = []
    for name, t0, t1, kind in SHOTS:
        if kind == "ai":
            clips.append(build_ai(name, round(t1 - t0, 3), note=(name == "shot1")))
        elif kind == "screen":
            clips.append(build_screen())
        else:
            clips.append(build_end(round(t1 - t0, 3)))
    story = concat(clips, WORK / "story.mp4")
    captioned = overlay_captions(story, WORK / "captioned.mp4", LINES)
    audio = build_audio(30.0, WORK / "audio.m4a", LINES, ambience_until=9.6)
    master = OUT / "wadih-ad-30s-9x16.mp4"
    mux(captioned, audio, master)
    # 15s: the question, the answer on the screen, the end card.
    cut(master, OUT / "wadih-ad-15s-9x16.mp4", [(3.0, 6.4), (9.6, 11.2), (13.8, 15.0), (17.4, 21.6), (25.4, 27.0), (27.0, 30.0)])
    # 6s bumper: the friend's question, then the end card.
    cut(master, OUT / "wadih-ad-6s-9x16.mp4", [(4.9, 6.4), (17.9, 19.4), (27.0, 30.0)])
    missing_clips = [n for n, *_ , k in SHOTS if k == "ai" and not (A / "clips" / f"{n}.mp4").exists()]
    missing_voice = [lid for lid, *_ in LINES if not (A / "voice" / f"{lid}.mp3").exists()]
    print("built:", ", ".join(p.name for p in sorted(OUT.glob("*.mp4"))))
    print("placeholders for clips:", missing_clips or "none")
    print("silent voice lines:", missing_voice or "none")


if __name__ == "__main__":
    main()
