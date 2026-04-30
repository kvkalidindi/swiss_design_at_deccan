"""Enrich palette.json with full color-space coordinates and Pantone match."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.lib.color_math import rgb_to_cmyk
from scripts.lib.pantone import nearest_pantone

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "data" / "palette.json"


def main() -> int:
    p = json.loads(PALETTE.read_text(encoding="utf-8"))
    for fam in p:
        for step in p[fam]:
            e = p[fam][step]
            rgb = tuple(e["rgb"])
            cmyk = rgb_to_cmyk(rgb)
            pms, de = nearest_pantone(rgb)
            e["cmyk"] = list(cmyk)
            e["pantone"] = {"code": pms, "delta_e": de}
    PALETTE.write_text(json.dumps(p, indent=2), encoding="utf-8")
    print("Enriched palette.json with CMYK + Pantone approximations.\n")
    print(f"{'token':<12} {'hex':<8} {'CMYK':<24} {'Pantone':<14} {'DeltaE':>7} {'note':<10}")
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            c, m, y, k = e["cmyk"]
            cmyk = f"C{c:>3} M{m:>3} Y{y:>3} K{k:>3}"
            pms = e["pantone"]["code"]
            de = e["pantone"]["delta_e"]
            if de < 2:
                note = "exact"
            elif de < 5:
                note = "close"
            else:
                note = "VERIFY"
            print(f"{fam}-{step:<7} {e['hex']:<8} {cmyk:<24} {pms:<14} {de:>7.2f} {note:<10}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
