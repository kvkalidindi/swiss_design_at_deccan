"""Validate palette against WCAG AA and lightness-gap rules."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.lib.color_math import contrast_ratio, rgb_to_hsl

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "data" / "palette.json"

WHITE = (255, 255, 255)
DARK_BG = (15, 15, 15)
MIN_GAP = 12.0
GAP_TOLERANCE = 0.5  # Match tolerance from _03_generate_palette.py
WCAG_AA = 4.5
STEP_ORDER = ("100", "300", "500", "700")


def validate(palette: dict) -> dict:
    warns: list[str] = []
    notes: list[str] = []
    for fam, steps in palette.items():
        present = [(k, rgb_to_hsl(tuple(v["rgb"]))[2]) for k, v in steps.items() if k in STEP_ORDER]
        present.sort(key=lambda kv: STEP_ORDER.index(kv[0]))
        for i in range(len(present) - 1):
            gap = present[i][1] - present[i + 1][1]
            if abs(gap) < MIN_GAP - GAP_TOLERANCE:
                warns.append(
                    f"{fam}-{present[i][0]} -> {fam}-{present[i+1][0]}: "
                    f"lightness gap {gap:.1f}% < {MIN_GAP}%"
                )
        for step, v_step in steps.items():
            if step not in ("500", "700"):
                continue
            rgb = tuple(v_step["rgb"])
            ratio_w = contrast_ratio(rgb, WHITE)
            ratio_d = contrast_ratio(rgb, DARK_BG)
            if ratio_w < WCAG_AA and ratio_d < WCAG_AA:
                warns.append(
                    f"{fam}-{step} ({v_step['hex']}): fails WCAG AA on both white "
                    f"({ratio_w}) and dark ({ratio_d})"
                )
            else:
                notes.append(f"{fam}-{step} contrast - white:{ratio_w} dark:{ratio_d}")
    return {"pass": not warns, "warnings": warns, "notes": notes}


def main() -> int:
    p = json.loads(PALETTE.read_text(encoding="utf-8"))
    report = validate(p)
    print(f"OVERALL: {'PASS' if report['pass'] else 'FAIL'}\n")
    for w in report["warnings"]:
        print(f"  WARN: {w}")
    for n in report["notes"]:
        print(f"  note: {n}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
