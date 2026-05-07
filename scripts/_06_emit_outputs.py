"""Emit final design-system tokens in multiple formats."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.lib.ase_writer import write_ase

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "data" / "palette.json"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

USE_CASES = {
    "100": "Background washes; subtle hover fills; subtle highlights.",
    "300": "Borders; dividers; secondary accents; chart fill tints.",
    "500": "**Anchor** - primary buttons, links, brand identity, default chart series color.",
    "700": "Hover/pressed states; text on light backgrounds; emphasis; chart series 2.",
}


def emit_json(p: dict) -> None:
    (OUT / "palette.json").write_text(json.dumps(p, indent=2), encoding="utf-8")


def emit_css(p: dict) -> None:
    lines = [":root {"]
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            lines.append(f"  --accent-{fam}-{step}: {e['hex']};")
    lines.append("}")
    lines.append("")
    lines.append("/* Tailwind config snippet:")
    lines.append("module.exports = {")
    lines.append("  theme: { extend: { colors: {")
    for fam in ("blue", "green"):
        lines.append(f"    {fam}: {{")
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            lines.append(f"      '{step}': '{e['hex']}',")
        lines.append("    },")
    lines.append("  } } }")
    lines.append("} */")
    (OUT / "palette.css").write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_ase(p: dict) -> None:
    swatches = []
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            swatches.append((f"{fam}-{step}", tuple(e["rgb"])))
    write_ase(OUT / "palette.ase", "Deccan Fine Chemicals - Accent", swatches)


def emit_html(p: dict) -> None:
    sections = []
    for fam in ("blue", "green"):
        cells = []
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            text_color = "#fff" if e["hsl"][2] < 55 else "#111"
            pms = e.get("pantone", {}).get("code", "-")
            de = e.get("pantone", {}).get("delta_e", 0)
            de_label = "exact" if de < 2 else ("close" if de < 5 else "verify")
            cells.append(
                f'<div class="sw" style="background:{e["hex"]};color:{text_color}">'
                f'<div class="step">{fam}-{step}</div>'
                f'<div class="hex">{e["hex"]}</div>'
                f'<div class="pms">{pms} <span class="de">DeltaE {de} ({de_label})</span></div>'
                f'</div>'
            )
        sections.append(f'<section><h2>{fam.title()}</h2><div class="row">{"".join(cells)}</div></section>')
    html = (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        "<title>Deccan Fine Chemicals - Accent Palette</title>\n"
        "<style>\n"
        "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; color: #222; }\n"
        "  h1 { font-weight: 400; letter-spacing: -.02em; }\n"
        "  h2 { font-weight: 500; letter-spacing: -.01em; margin-top: 32px; }\n"
        "  section { margin: 24px 0; }\n"
        "  .row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }\n"
        "  .sw { padding: 24px 16px; border-radius: 4px; min-height: 110px; }\n"
        "  .step { font-size: 12px; opacity: .9; }\n"
        "  .hex  { font-size: 18px; font-weight: 600; margin-top: 4px; font-family: ui-monospace, monospace; }\n"
        "  .pms  { font-size: 11px; opacity: .85; margin-top: 18px; }\n"
        "  .de   { opacity: .7; }\n"
        "</style></head>\n"
        "<body>\n"
        "  <h1>Deccan Fine Chemicals - Accent Palette</h1>\n"
        f"  {''.join(sections)}\n"
        "  <p style=\"opacity:.6;font-size:12px\">Generated from corporate logo at deccanchemicals.com.</p>\n"
        "</body></html>\n"
    )
    (OUT / "palette-swatches.html").write_text(html, encoding="utf-8")


def emit_md(p: dict) -> None:
    out: list[str] = [
        "# Deccan Fine Chemicals - Accent Color Palette",
        "",
        "Generated from the corporate logo at https://deccanchemicals.com.",
        "Anchor steps (`-500`) are exact colors taken from the logo. Other steps",
        "are derived to maintain visual progression and accessibility.",
        "",
        "## Palette",
        "",
    ]
    for fam in ("blue", "green"):
        out.append(f"### {fam.title()}")
        out.append("")
        out.append("| Step | Hex | RGB | HSL | CMYK | Pantone (approx) | DeltaE | Use |")
        out.append("|---|---|---|---|---|---|---|---|")
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            r, g, b = e["rgb"]
            h, s, light = e["hsl"]
            c, m, y, k = e["cmyk"]
            pms = e["pantone"]["code"]
            de = e["pantone"]["delta_e"]
            de_note = "ok" if de < 2 else ("close" if de < 5 else "**verify**")
            out.append(
                f"| `{fam}-{step}` | `{e['hex']}` | rgb({r}, {g}, {b}) | hsl({h}, {s}%, {light}%) | "
                f"C{c} M{m} Y{y} K{k} | {pms} | {de} ({de_note}) | {USE_CASES[step]} |"
            )
        out.append("")
    out += [
        "## Pantone matching note",
        "",
        "Pantone values are algorithmic Delta-E 2000 nearest neighbors against a Solid Coated reference table.",
        "Steps marked **verify** (DeltaE > 5) should be confirmed against a professional Pantone Bridge guide",
        "before being used in print production. The 100-tints (very light) and the algorithmically lightened",
        "green-300 are the most likely to need professional verification.",
        "",
        "## Accessibility",
        "",
        "Anchor (`-500`) and dark (`-700`) steps are validated against WCAG AA (>= 4.5:1) on at least",
        "one of white or dark backgrounds. See `scripts/_05_validate_palette.py` for the validation routine.",
        "",
        "Important: green-500 only achieves ~2.3:1 contrast on white backgrounds, so it should be used as a",
        "fill / icon color on light backgrounds rather than as text. Use green-700 for dark text contrast on",
        "white, or use green-500 for text on dark backgrounds (where it contrasts ~8.5:1).",
        "",
        "## Status indicator colors are out of scope",
        "",
        "This palette covers brand accents only. Status colors (success / warning / info / error) follow",
        "a separate traditional multi-colored palette defined elsewhere in the design system.",
        "",
    ]
    (OUT / "palette.md").write_text("\n".join(out), encoding="utf-8")


def main() -> int:
    p = json.loads(PALETTE.read_text(encoding="utf-8"))
    emit_json(p)
    emit_css(p)
    emit_ase(p)
    emit_html(p)
    emit_md(p)
    print("Wrote outputs/palette.json, palette.css, palette.ase, palette-swatches.html, palette.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
