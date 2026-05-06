"""Color space conversions: hex, RGB, HSL, CMYK + WCAG contrast."""
from __future__ import annotations

import colorsys
from typing import Tuple

RGB = Tuple[int, int, int]
HSL = Tuple[float, float, float]   # H 0-360, S 0-100, L 0-100
CMYK = Tuple[int, int, int, int]   # 0-100 each


def hex_to_rgb(h: str) -> RGB:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(rgb: RGB) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def rgb_to_hsl(rgb: RGB) -> HSL:
    r, g, b = (c / 255 for c in rgb)
    h, light, s = colorsys.rgb_to_hls(r, g, b)
    return (round(h * 360, 1), round(s * 100, 1), round(light * 100, 1))  # Return H, S, L


def hsl_to_rgb(hsl: HSL) -> RGB:
    h, s, light = hsl[0] / 360, hsl[1] / 100, hsl[2] / 100
    r, g, b = colorsys.hls_to_rgb(h, light, s)
    return (round(r * 255), round(g * 255), round(b * 255))


def rgb_to_cmyk(rgb: RGB) -> CMYK:
    r, g, b = (c / 255 for c in rgb)
    k = 1 - max(r, g, b)
    if k >= 1.0:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return (round(c * 100), round(m * 100), round(y * 100), round(k * 100))


def relative_luminance(rgb: RGB) -> float:
    def chan(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb1: RGB, rgb2: RGB) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    lo, hi = sorted((l1, l2))
    return round((hi + 0.05) / (lo + 0.05), 2)
