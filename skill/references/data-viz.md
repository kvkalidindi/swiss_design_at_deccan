# Data Visualization — Deccan Palette

This document covers a deliberate exception to the **"one accent per project"** Swiss design rule (`design-system.md`). Charts and data visualizations follow different rules: they need multiple distinct colors to encode different series, and a single-color palette would be unreadable.

## When to use

This guidance applies ONLY to:
- Multi-series charts (line, bar, stacked area)
- Categorical encodings (heatmaps, treemaps, choropleths)
- Dashboards displaying numeric series

It does NOT apply to:
- UI chrome (buttons, links, navigation, surfaces)
- Single-value indicators (use the single Deccan Blue accent at appropriate opacity)
- Status indicators (use a separate traditional success/warning/error palette)

## The 8-step palette

Pulled from `outputs/palette.json` at the project root:

| Step | Hex | Role |
|------|-----|------|
| `blue-100`  | `#E0E8F5` | Background tint, fill |
| `blue-300`  | `#0EA3DD` | Bright cyan series, callout |
| `blue-500`  | `#164999` | Primary brand series, hero data |
| `blue-700`  | `#0C2956` | Dark emphasis series |
| `green-100` | `#E9EFE6` | Background tint, fill |
| `green-300` | `#A1CB8D` | Soft green series |
| `green-500` | `#71BF4D` | Secondary brand series |
| `green-700` | `#4F8D33` | Dark emphasis series |

## Recommended series order

For a 2-series chart: `blue-500`, `green-500`.
For a 4-series chart: `blue-500`, `green-500`, `blue-700`, `green-700`.
For an 8-series chart: cycle through all 8 in lightness order: `blue-500`, `green-500`, `blue-700`, `green-700`, `blue-300`, `green-300`, `blue-100`, `green-100`.

## Accessibility for charts

Color alone is never sufficient encoding for accessibility. Pair color with:
- Direct labels on series
- Distinct line styles (solid / dashed / dotted)
- Distinct marker shapes
- Pattern fills for grayscale-printed dashboards

Sources for the canonical palette: `outputs/palette.json` (machine-readable), `outputs/palette.css` (CSS variables), `outputs/palette.md` (documentation).
