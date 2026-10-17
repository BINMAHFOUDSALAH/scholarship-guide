"""The design system's colour rules, written as code (decisions 035, 062).

Every text colour must be readable on the backgrounds it's used on (WCAG 1.4.3: 4.5:1 for text),
and borders and focus rings must stand out from the page (WCAG 1.4.11: 3:1). Both themes.
"""

import re

import pytest

import app.main as main

CSS = (main.APP_DIR / "static" / "style.css").read_text(encoding="utf-8")


def tokens(selector):
    """The --name: #hex tokens of the first CSS block that starts with `selector {`."""
    start = CSS.index(selector + " {")
    block = CSS[start:CSS.index("}", start)]
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", block))


LIGHT = tokens(":root")
DARK = {**LIGHT, **tokens(':root[data-theme="dark"]')}


def rgb(hex_color):
    return [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]


def mix(color, percent, base):
    """CSS color-mix(in srgb, color percent%, base): a straight blend of the sRGB values."""
    a, b = rgb(color), rgb(base)
    return "#" + "".join(f"{round(x * percent / 100 + y * (100 - percent) / 100):02x}" for x, y in zip(a, b))


def luminance(hex_color):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def test_contrast_formula():
    assert round(contrast("#000000", "#ffffff"), 1) == 21.0
    assert round(contrast("#777777", "#ffffff"), 2) == 4.48


def text_pairs(t):
    """(text colour, background, where it's used) for every text pair the CSS uses (decision 062 names)."""
    return [
        (t["ink"], t["paper"], "body text and headings"),
        (t["ink"], t["surface"], "text on panels"),
        (t["ink"], t["surface-strong"], "text in inputs, menus and the summary sheet"),
        (t["ink-muted"], t["paper"], "secondary text"),
        (t["ink-muted"], t["surface"], "secondary text on panels"),
        (t["ink-muted"], t["surface-strong"], "hints in the suggestions panel"),
        (t["action"], t["paper"], "links"),
        (t["action"], t["surface"], "links on panels"),
        (t["action"], t["surface-strong"], "links in menus and the summary sheet"),
        (t["on-action"], t["action"], "primary button text"),
        (t["on-lime"], t["lime"], "«مفتوح الآن», the next step, the chosen country"),
        (t["amber"], t["paper"], "restriction and «لم يفتح بعد» text"),
        (t["amber"], mix(t["amber"], 12, t["paper"]), "«ماجستير فقط» tags"),
        (t["action"], mix(t["action"], 10, t["surface-strong"]), "a highlighted suggestion"),
        # The forest stage (the homepage's start, the universities search) and the footer.
        (t["on-stage"], t["stage"], "titles and text on the stage"),
        (t["on-stage-muted"], t["stage"], "secondary text on the stage"),
        (t["stage-amber"], t["stage"], "«لم يفتح بعد» on the stage"),
        (t["stage"], t["on-stage"], "a primary button on the stage (forest text on ivory)"),
        (t["on-stage"], t["stage-deep"], "footer titles"),
        (t["on-stage-muted"], t["stage-deep"], "footer links and the copyright line"),
    ]


@pytest.mark.parametrize("theme, t", [("light", LIGHT), ("dark", DARK)])
def test_text_is_readable_in_both_themes(theme, t):
    for fg, bg, where in text_pairs(t):
        assert contrast(fg, bg) >= 4.5, f"{theme}: {where} ({fg} on {bg}) is {contrast(fg, bg):.2f}:1"


@pytest.mark.parametrize("theme, t", [("light", LIGHT), ("dark", DARK)])
def test_controls_and_focus_ring_stand_out(theme, t):
    for fg, bg, where in [
        (t["control-border"], t["surface-strong"], "input border"),
        (t["control-border"], t["paper"], "input border against the page"),
        (t["focus"], t["paper"], "focus ring"),
        (t["focus"], t["surface"], "focus ring on panels"),
        (t["action"], t["paper"], "secondary button border"),
        (t["lime"], t["stage"], "focus ring and the lit diamond on the stage"),
        (t["lime"], t["stage-deep"], "focus ring in the footer"),
    ]:
        assert contrast(fg, bg) >= 3, f"{theme}: {where} ({fg} on {bg}) is {contrast(fg, bg):.2f}:1"


def test_fields_stand_out_on_the_stage():
    """A search box on forest: white on forest by day; at night the field keeps its border (decision 062)."""
    assert contrast(LIGHT["surface-strong"], LIGHT["stage"]) >= 3
    assert "--stage-field-border: transparent" in CSS.split(':root[data-theme="dark"] {')[0]
    assert contrast(DARK["stage-field-border"], DARK["stage"]) >= 3


def test_no_text_smaller_than_the_scale_floor():
    """Small Arabic text is hard to read: nothing under --text-xs (13px)."""
    sizes = re.findall(r"font-size:\s*([0-9.]+)rem", CSS)
    too_small = [s for s in sizes if float(s) < 0.8125]
    assert not too_small, f"font sizes below 0.8125rem: {too_small}"
