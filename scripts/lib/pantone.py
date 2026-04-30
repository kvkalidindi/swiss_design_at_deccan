"""Approximate Pantone matching via ΔE-2000 in CIE Lab space."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Tuple

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# colormath uses numpy.asscalar removed in numpy 1.16+; patch if needed
try:
    import numpy as np
    if not hasattr(np, "asscalar"):
        np.asscalar = lambda a: a.item()
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "pantone-solid-coated.csv"

_TABLE = None


def _load_table():
    rows = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            h = r["hex"].lstrip("#")
            rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
            rows.append((r["code"], rgb))
    return rows


def _table():
    global _TABLE
    if _TABLE is None:
        _TABLE = _load_table()
    return _TABLE


def _to_lab(rgb: Tuple[int, int, int]) -> LabColor:
    s = sRGBColor(*rgb, is_upscaled=True)
    return convert_color(s, LabColor)


def nearest_pantone(rgb: Tuple[int, int, int]) -> tuple[str, float]:
    """Return (PMS code, ΔE) for nearest Solid Coated match."""
    target = _to_lab(rgb)
    best, best_de = None, float("inf")
    for code, ref_rgb in _table():
        de = delta_e_cie2000(target, _to_lab(ref_rgb))
        if de < best_de:
            best, best_de = code, de
    return best, round(float(best_de), 2)
