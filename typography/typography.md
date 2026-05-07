# Deccan Fine Chemicals — Typography

The Deccan Fine Chemicals design system inherits its typography from
[zeke/swiss-design-skill](https://github.com/zeke/swiss-design-skill), whose
font stack is 100% license-compliant (SIL Open Font License 1.1). **No
substitutions were required.** The audit at `typography/audit-notes.md`
documents the verification.

## Stack

### Primary

| Family | Role | License | Files |
|---|---|---|---|
| **IBM Plex Sans** | Sans-serif (display, body, UI) | SIL OFL 1.1 | `fonts/ibm-plex-sans/` |
| **IBM Plex Mono** | Monospace (code, technical) | SIL OFL 1.1 | `fonts/ibm-plex-mono/` |

### Fallbacks

| Family | Role | License | Files |
|---|---|---|---|
| Hanken Grotesk | Sans alternative | SIL OFL 1.1 | `fonts/hanken-grotesk/` |
| Barlow | Sans alternative | SIL OFL 1.1 | `fonts/barlow/` |
| Host Grotesk | Sans alternative | SIL OFL 1.1 | `fonts/host-grotesk/` |
| DM Sans | Sans alternative | SIL OFL 1.1 | `fonts/dm-sans/` |
| Fira Code | Monospace alternative | SIL OFL 1.1 | `fonts/fira-code/` |

## Usage Guidance

### Display & Headlines

- Family: **IBM Plex Sans**
- Weight: 600 (SemiBold) for H1/H2; 500 (Medium) for H3/H4
- Tracking: -0.01em to -0.02em on display sizes for tighter optical density
  (Swiss design convention)
- Line height: 1.1–1.2 on headlines

### Body & Paragraph

- Family: **IBM Plex Sans**
- Weight: 400 (Regular)
- Line height: 1.5
- Measure (line length): 50–75 characters

### UI & Small Caps

- Family: **IBM Plex Sans**
- Weight: 500 (Medium)
- Tracking: +0.02em on small UI labels (12px and below)

### Code & Technical

- Family: **IBM Plex Mono**
- Weight: 400 (Regular)
- Line height: 1.45

## Variable-axis usage

If your runtime supports variable fonts, prefer the variable build:
`font-variation-settings: "wght" 600;`. This loads one file per family and
exposes the entire weight range, keeping documents lighter than embedding
multiple static weight files. Static weight files are bundled here for
runtimes that don't support variable fonts (e.g., older Office versions).

## License compliance

All bundled fonts are SIL OFL 1.1, which permits:

- Free use in corporate documents and websites
- Redistribution as part of templates and brand assets
- Embedding in PDFs, .pptx, .docx files
- Commercial use without royalty

Each `fonts/<family>/` folder contains an `OFL.txt` reproducing the license
to satisfy attribution requirements.

## CSS / Web setup

Quick CSS snippet to load the primary fonts:

```css
@font-face {
  font-family: "IBM Plex Sans";
  src: url("/fonts/ibm-plex-sans/IBMPlexSans-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "IBM Plex Sans";
  src: url("/fonts/ibm-plex-sans/IBMPlexSans-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "IBM Plex Mono";
  src: url("/fonts/ibm-plex-mono/IBMPlexMono-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

body {
  font-family: "IBM Plex Sans", "Hanken Grotesk", system-ui, sans-serif;
}

code, pre, kbd {
  font-family: "IBM Plex Mono", "Fira Code", ui-monospace, monospace;
}
```

For production, convert TTFs to WOFF2 using a tool like `fonttools` for
~30–50% smaller delivery on the web.

## Microsoft Office setup

Office must have the fonts installed at the OS level to use them in themes.
Plan 3 (Microsoft Office artifacts) covers Group Policy / Intune deployment.
Until then, manually install by double-clicking each `.ttf` file under
`fonts/<family>/` on the target Windows 11 PC.

## Fallback strategy

The Swiss International Style tradition emphasizes a careful fallback chain,
ensuring typographic consistency even when preferred fonts are unavailable.
Use the following CSS font-family chain:

```css
/* For sans-serif / UI */
font-family: "IBM Plex Sans", "Hanken Grotesk", "Barlow", "Host Grotesk",
  "DM Sans", system-ui, sans-serif;

/* For monospace / code */
font-family: "IBM Plex Mono", "Fira Code", "Monaco", "Courier New", monospace;
```

Each fallback is geometrically similar to the primary font, maintaining
line breaks and layout integrity across environments.
