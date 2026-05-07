# Deccan Fine Chemicals - Accent Color Palette

Generated from the corporate logo at https://deccanchemicals.com.
Anchor steps (`-500`) are exact colors taken from the logo. Other steps
are derived to maintain visual progression and accessibility.

## Palette

### Blue

| Step | Hex | RGB | HSL | CMYK | Pantone (approx) | DeltaE | Use |
|---|---|---|---|---|---|---|---|
| `blue-100` | `#E0E8F5` | rgb(224, 232, 245) | hsl(217.1, 51.2%, 92.0%) | C9 M5 Y0 K4 | PMS 649 C | 3.0 (close) | Background washes; subtle hover fills; subtle highlights. |
| `blue-300` | `#0EA3DD` | rgb(14, 163, 221) | hsl(196.8, 88.1%, 46.1%) | C94 M26 Y0 K13 | PMS 639 C | 4.72 (close) | Borders; dividers; secondary accents; chart fill tints. |
| `blue-500` | `#164999` | rgb(22, 73, 153) | hsl(216.6, 74.9%, 34.3%) | C86 M52 Y0 K40 | PMS 2175 C | 1.7 (ok) | **Anchor** - primary buttons, links, brand identity, default chart series color. |
| `blue-700` | `#0C2956` | rgb(12, 41, 86) | hsl(216.5, 75.5%, 19.2%) | C86 M52 Y0 K66 | PMS 295 C | 1.26 (ok) | Hover/pressed states; text on light backgrounds; emphasis; chart series 2. |

### Green

| Step | Hex | RGB | HSL | CMYK | Pantone (approx) | DeltaE | Use |
|---|---|---|---|---|---|---|---|
| `green-100` | `#E9EFE6` | rgb(233, 239, 230) | hsl(100.0, 22.0%, 92.0%) | C3 M0 Y4 K6 | PMS 649 C | 8.45 (**verify**) | Background washes; subtle hover fills; subtle highlights. |
| `green-300` | `#A1CB8D` | rgb(161, 203, 141) | hsl(100.6, 37.3%, 67.5%) | C21 M0 Y31 K20 | PMS 366 C | 6.26 (**verify**) | Borders; dividers; secondary accents; chart fill tints. |
| `green-500` | `#71BF4D` | rgb(113, 191, 77) | hsl(101.1, 47.1%, 52.5%) | C41 M0 Y60 K25 | PMS 360 C | 1.1 (ok) | **Anchor** - primary buttons, links, brand identity, default chart series color. |
| `green-700` | `#4F8D33` | rgb(79, 141, 51) | hsl(101.3, 46.9%, 37.6%) | C44 M0 Y64 K45 | PMS 362 C | 2.56 (close) | Hover/pressed states; text on light backgrounds; emphasis; chart series 2. |

## Pantone matching note

Pantone values are algorithmic Delta-E 2000 nearest neighbors against a Solid Coated reference table.
Steps marked **verify** (DeltaE > 5) should be confirmed against a professional Pantone Bridge guide
before being used in print production. The 100-tints (very light) and the algorithmically lightened
green-300 are the most likely to need professional verification.

## Accessibility

Anchor (`-500`) and dark (`-700`) steps are validated against WCAG AA (>= 4.5:1) on at least
one of white or dark backgrounds. See `scripts/_05_validate_palette.py` for the validation routine.

Important: green-500 only achieves ~2.3:1 contrast on white backgrounds, so it should be used as a
fill / icon color on light backgrounds rather than as text. Use green-700 for dark text contrast on
white, or use green-500 for text on dark backgrounds (where it contrasts ~8.5:1).

## Status indicator colors are out of scope

This palette covers brand accents only. Status colors (success / warning / info / error) follow
a separate traditional multi-colored palette defined elsewhere in the design system.
