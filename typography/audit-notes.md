# Font Audit: zeke/swiss-design-skill

**Audit date:** 2026-04-30  
**Source:** https://github.com/zeke/swiss-design-skill (cloned to `.tmp_swiss/`)  
**Purpose:** Identify any commercially-licensed fonts that block enterprise-wide deployment, so we can substitute them with Google Fonts equivalents in Task 13.

## Summary

| # | Font | License | Substitution needed? |
|---|------|---------|----------------------|
| 1 | IBM Plex Sans | FREE (Apache 2.0) | No |
| 2 | IBM Plex Mono | FREE (Apache 2.0) | No |
| 3 | Hanken Grotesk | FREE (SIL OFL) | No |
| 4 | Barlow | FREE (SIL OFL) | No |
| 5 | Host Grotesk | FREE (SIL OFL) | No |
| 6 | DM Sans | FREE (SIL OFL) | No |
| 7 | Fira Code | FREE (SIL OFL) | No |
| 8 | Helvetica Neue | COMMERCIAL (Linotype) | Yes — reference only |
| 9 | Akzidenz-Grotesk | COMMERCIAL (Berthold/Linotype) | Yes — reference only |
| 10 | Univers | COMMERCIAL (Linotype) | Yes — reference only |
| 11 | Neue Haas Grotesk | COMMERCIAL (Commercial Type) | Yes — reference only |

## Detailed reference inventory

### IBM Plex Sans

**License:** Apache 2.0 (Free)  
**Status:** Primary font for the system. Deployed from Google Fonts.

Found in:
- `swiss-design/SKILL.md:27` — "`**Primary font:** IBM Plex Sans (Google Fonts)`"
- `swiss-design/SKILL.md:46` — "`font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', system-ui, sans-serif;`"
- `swiss-design/references/design-system.md:10` — "`--font-sans: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', system-ui, sans-serif;`"
- `website/src/index.tsx:37` — "`sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],`"
- `website/src/index.tsx:29` — "`<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:...display=swap" rel="stylesheet">`"
- Multiple references in `SKILL.md`, `README.md`, component patterns, and demo website

**Impact:** Actively used. No substitution needed.

---

### IBM Plex Mono

**License:** Apache 2.0 (Free)  
**Status:** Monospace font for code blocks and technical content. Deployed from Google Fonts.

Found in:
- `swiss-design/references/design-system.md:11` — "`--font-mono: 'IBM Plex Mono', 'Fira Code', monospace;`"
- `website/src/index.tsx:38` — "`mono: ['IBM Plex Mono', 'monospace'],`"
- `website/src/index.tsx:29` — "`<link href="https://fonts.googleapis.com/css2?family=...IBM+Plex+Mono:wght@400;500&...display=swap" rel="stylesheet">`"
- Multiple CSS class references: `font-mono`

**Impact:** Actively used for code/technical content. No substitution needed.

---

### Hanken Grotesk

**License:** SIL OFL (Free)  
**Status:** Fallback font #1. Deployed from Google Fonts.

Found in:
- `swiss-design/SKILL.md:39` — "`| Hanken Grotesk | Google Fonts | Closest to Neue Haas Grotesk lineage |`"
- `swiss-design/SKILL.md:46` — "`font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', ...`"
- `swiss-design/references/design-system.md:10` — "`--font-sans: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', system-ui, sans-serif;`"
- `website/src/index.tsx:36–39` — Tailwind config fallback chain
- `tailwind-config.md` — Comprehensive fallback chain documentation

**Impact:** Used as fallback. No substitution needed.

---

### Barlow

**License:** SIL OFL (Free)  
**Status:** Fallback font #2. Deployed from Google Fonts.

Found in:
- `swiss-design/SKILL.md:40` — "`| Barlow | Google Fonts | Condensed Swiss-grid proportions, strong vertical rhythm |`"
- `swiss-design/SKILL.md:46` — "`font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', ...`"
- `swiss-design/references/design-system.md:10` — "`--font-sans: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', system-ui, sans-serif;`"
- `website/src/index.tsx:36–39` — Tailwind config fallback chain
- `website/src/index.tsx` — Table data: "`['Barlow', 'Jeremy Tribby', '2017', 'Google Fonts', '88', false],`"
- `tailwind-config.md` — Comprehensive fallback chain documentation

**Impact:** Used as fallback. No substitution needed.

---

### Host Grotesk

**License:** SIL OFL (Free)  
**Status:** Fallback font #3. Deployed from Google Fonts.

Found in:
- `swiss-design/SKILL.md:41` — "`| Host Grotesk | Google Fonts | Warm grotesque, good at all sizes |`"
- `swiss-design/SKILL.md:46` — "`font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', system-ui, sans-serif;`"
- `website/src/index.tsx:36–39` — Tailwind config fallback chain
- `website/src/index.tsx` — Table data: "`['Host Grotesk', 'Fraunhofer IAIS', '2018', 'Google Fonts', '84', false],`"
- `tailwind-config.md` — Comprehensive fallback chain documentation

**Impact:** Used as fallback. No substitution needed.

---

### DM Sans

**License:** SIL OFL (Free)  
**Status:** Fallback font #4. Deployed from Google Fonts.

Found in:
- `swiss-design/SKILL.md:42` — "`| DM Sans | Google Fonts | Clean neo-grotesque fallback |`"
- `swiss-design/SKILL.md:46` — "`font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', system-ui, sans-serif;`"
- `swiss-design/references/design-system.md:10` — "`--font-sans: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', system-ui, sans-serif;`"
- `website/src/index.tsx:36–39` — Tailwind config fallback chain
- `website/src/index.tsx` — Table data: "`['DM Sans', 'Colophon Foundry', '2019', 'Google Fonts', '79', false],`"
- `tailwind-config.md` — Comprehensive fallback chain documentation

**Impact:** Used as fallback. No substitution needed.

---

### Fira Code

**License:** SIL OFL (Free)  
**Status:** Monospace fallback. Deployed from Google Fonts.

Found in:
- `swiss-design/references/design-system.md:11` — "`--font-mono: 'IBM Plex Mono', 'Fira Code', monospace;`"
- `tailwind-config.md:22` — "`'Fira Code',`"

**Impact:** Used as monospace fallback. No substitution needed.

---

### Helvetica Neue

**License:** COMMERCIAL (Linotype/Monotype)  
**Status:** Historical reference only (not deployed).

Found in:
- `swiss-design/references/components.md:255` — "`<td class="py-4 pr-8 text-stone-900 dark:text-stone-50">Helvetica Neue</td>`" (in example table: shows Year 1983, Origin Switzerland)
- `website/src/index.tsx` — Comments and historical discussion referencing Helvetica

**Context:** Helvetica (released 1957 as Neue Haas Grotesk, renamed 1960) is mentioned in the website's inspiration/education section about International Typographic Style history, but is NOT used in the actual design system.

**Impact:** Reference/educational content only. No substitution needed — this is historical documentation, not a deployed font.

---

### Akzidenz-Grotesk

**License:** COMMERCIAL (Berthold/now Linotype)  
**Status:** Historical reference only (not deployed).

Found in:
- `website/scripts/fetch-inspiration.mjs:2` — "`{ keywords: ['akzidenz', 'berthold'],`"
- `website/scripts/fetch-inspiration.mjs:5` — "`{ q: 'Akzidenz-Grotesk Helvetica grotesque type specimen', category: 'Typography' },`"
- `website/scripts/generate-preview.mjs` — Metadata for sourcing design inspiration images
- `website/src/index.tsx` — Comments: "`// Akzidenz-Grotesk 1896 — Berthold ✓ (preceded Swiss Style, influenced it)`"
- `website/public/inspiration/manifest.json` — Query parameters for inspiration image fetching

**Context:** Akzidenz-Grotesk is mentioned as historical/inspirational reference for the Swiss International Style (precursor to Helvetica), but is NOT used in the actual design system. It's part of the educational/cultural context in the demo website.

**Impact:** Reference/educational content only, used to fetch inspiration images. No substitution needed.

---

### Univers

**License:** COMMERCIAL (Linotype)  
**Status:** Historical reference only (not deployed).

Found in:
- `website/scripts/fetch-inspiration.mjs:1` — "`{ keywords: ['adrian frutiger', 'frutiger', 'univers'],`"
- `website/src/index.tsx` — Comments: "`// Univers 1957 — Frutiger ✓`" and "`// Univers: Frutiger, also 1957 — favored by Basel school`"
- `website/src/index.tsx` — Table data: "`{ name: 'Univers', year: '1957', designer: 'Adrian Frutiger' },`"

**Context:** Univers is mentioned in the educational section about International Typographic Style history (favored by Basel school designers), but is NOT used in the actual design system.

**Impact:** Reference/educational content only. No substitution needed.

---

### Neue Haas Grotesk

**License:** COMMERCIAL (Commercial Type, which now holds the digital rights; original Linotype)  
**Status:** Historical reference only (not deployed).

Found in:
- `swiss-design/SKILL.md:39` — "`| Hanken Grotesk | Google Fonts | Closest to Neue Haas Grotesk lineage |`" (mentioned as comparison for Hanken Grotesk)
- `website/src/index.tsx` — Extensive comments and data:
  - "`// Neue Haas Grotesk: launched 1957 as 'Neue Haas Grotesk', renamed Helvetica 1960`"
  - "`// Neue Haas Grotesk: Miedinger designed letterforms, Hoffmann (Haas) directed/commissioned — both credited`"
  - "`{ name: 'Neue Haas Grotesk', year: '1957', designer: 'Miedinger & Hoffmann' },`"
  - Table row: "`['Neue Haas Grotesk', 'Miedinger & Hoffmann', '1957', 'Linotype', '100', false],`"
  - "`desc: 'Max Miedinger and Eduard Hoffmann's neutral grotesque, designed at the Haas Type Foundry in Münchenbuchsee. Renamed Helvetica in 1960.',`"

**Context:** Neue Haas Grotesk is presented as the original (1957) name for Helvetica. Referenced in educational/historical sections and used for comparison to justify Hanken Grotesk as a free fallback, but is NOT used in the actual design system.

**Impact:** Reference/educational/historical content only. No substitution needed.

---

## Conclusion

### Summary Statistics

- **FREE fonts actively deployed:** 7
  - IBM Plex Sans (Apache 2.0)
  - IBM Plex Mono (Apache 2.0)
  - Hanken Grotesk (SIL OFL)
  - Barlow (SIL OFL)
  - Host Grotesk (SIL OFL)
  - DM Sans (SIL OFL)
  - Fira Code (SIL OFL)

- **COMMERCIAL fonts mentioned:** 4
  - Helvetica Neue (Linotype/Monotype) — **reference only, not deployed**
  - Akzidenz-Grotesk (Berthold/Linotype) — **reference only, not deployed**
  - Univers (Linotype) — **reference only, not deployed**
  - Neue Haas Grotesk (Commercial Type/Linotype) — **reference only, not deployed**

### Key Finding

**The zeke/swiss-design-skill repo uses ONLY free, open-source fonts in its actual deployed design system.** All commercial typeface mentions are:

1. **Educational/historical references** in documentation and comments
2. **Inspirational content** used to source design principle images (Akzidenz-Grotesk, Univers, Helvetica)
3. **Comparison justifications** (e.g., noting that Hanken Grotesk is the closest free alternative to Neue Haas Grotesk)

**No commercial fonts are embedded, loaded via CDN, or required for deployment.**

### Next Step

**Task 13 (DECISION POINT 3):** Since the system already uses only free Google Fonts, no font substitutions are required. The entire font stack is production-ready and license-compliant for enterprise-wide deployment.

---

## Upstream Repository License

The zeke/swiss-design-skill repository is licensed under **MIT** (per LICENSE file and SKILL.md metadata). All documentation and code are freely available. The Google Fonts it references are independently licensed under SIL OFL and Apache 2.0.
