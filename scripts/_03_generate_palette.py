"""Generate 8-step palette (4 blue + 4 green) from 6 curated anchors.

Algorithm:
  - For each step that needs lightening/darkening from the anchor, prefer a
    logo color that already has the required ~12% lightness gap. This keeps
    the palette brand-authentic. If no logo color qualifies, derive the step
    algorithmically from the anchor (HSL adjustment).
  - The -100 tint is always algorithmically derived (close to white).
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.lib.color_math import (
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
    hsl_to_rgb,
)

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = ROOT / "data" / "anchors.json"
OUT = ROOT / "data" / "palette.json"

MIN_GAP = 12.0          # required lightness gap between adjacent steps
GAP_TOLERANCE = 0.5     # allow 0.5% tolerance for floating-point precision
DARKEN_DELTA = 15.0     # algorithmic darken/lighten amount when no logo color fits
LIGHTEN_DELTA = 15.0
DESAT_ON_LIGHTEN = 10.0
TINT_LIGHTNESS = 92.0   # target lightness for the -100 tint
TINT_DESAT = 25.0


def _adjust_hsl(rgb, dl=0.0, ds=0.0):
    h, s, l = rgb_to_hsl(rgb)
    s = max(0.0, min(100.0, s + ds))
    l = max(0.0, min(100.0, l + dl))
    return hsl_to_rgb((h, s, l))


def _set_lightness(rgb, target_l, ds=0.0):
    h, s, _ = rgb_to_hsl(rgb)
    s = max(0.0, min(100.0, s + ds))
    return hsl_to_rgb((h, s, target_l))


def _entry(rgb):
    return {"hex": rgb_to_hex(rgb), "rgb": list(rgb), "hsl": list(rgb_to_hsl(rgb))}


def _pick_darker(anchor_rgb, *candidates):
    """Return a logo candidate that's ≥MIN_GAP darker, else algorithmically darken anchor."""
    anchor_l = rgb_to_hsl(anchor_rgb)[2]
    for c in candidates:
        if anchor_l - rgb_to_hsl(c)[2] >= MIN_GAP - GAP_TOLERANCE:
            return c
    return _adjust_hsl(anchor_rgb, dl=-DARKEN_DELTA)


def _pick_lighter(anchor_rgb, *candidates):
    """Return a logo candidate that's ≥MIN_GAP lighter, else algorithmically lighten + desaturate anchor."""
    anchor_l = rgb_to_hsl(anchor_rgb)[2]
    for c in candidates:
        if rgb_to_hsl(c)[2] - anchor_l >= MIN_GAP - GAP_TOLERANCE:
            return c
    return _adjust_hsl(anchor_rgb, dl=+LIGHTEN_DELTA, ds=-DESAT_ON_LIGHTEN)


def build_palette(anchors: dict) -> dict:
    # Blue
    b_anchor = hex_to_rgb(anchors["blue"]["anchor"])
    b_darkest = hex_to_rgb(anchors["blue"]["darkest"])
    b_dark = hex_to_rgb(anchors["blue"]["dark"])
    b_lightest = hex_to_rgb(anchors["blue"]["lightest"])

    blue = {
        "500": _entry(b_anchor),
        "700": _entry(_pick_darker(b_anchor, b_darkest, b_dark)),
        "300": _entry(_pick_lighter(b_anchor, b_lightest, b_dark)),
        "100": _entry(_set_lightness(b_anchor, TINT_LIGHTNESS, ds=-TINT_DESAT)),
    }

    # Green (only 2 logo shades available)
    g_anchor = hex_to_rgb(anchors["green"]["anchor"])
    g_alt = hex_to_rgb(anchors["green"]["alt"])

    green = {
        "500": _entry(g_anchor),
        "700": _entry(_pick_darker(g_anchor, g_alt)),
        "300": _entry(_pick_lighter(g_anchor, g_alt)),
        "100": _entry(_set_lightness(g_anchor, TINT_LIGHTNESS, ds=-TINT_DESAT)),
    }

    return {"blue": blue, "green": green}


def main() -> int:
    anchors = json.loads(ANCHORS.read_text(encoding="utf-8"))
    p = build_palette(anchors)
    OUT.write_text(json.dumps(p, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}\n")
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            h, s, l = e["hsl"]
            print(f"  {fam}-{step}  {e['hex']}  H={h:>5.1f} S={s:>5.1f} L={l:>5.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
