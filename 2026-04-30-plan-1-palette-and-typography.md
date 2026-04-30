# Plan 1: Color Palette + Typography Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the brand-derived 8-step accent palette (4 blue + 4 green) and Google Fonts substitution package for Deccan Chemicals' design system, in all required formats (web, print, design tools, documentation).

**Architecture:** Python pipeline (Pillow + scikit-learn + colormath) extracts logo colors → curated anchors generate HSL-progression steps → conversions emit hex/RGB/HSL/CMYK/Pantone-approx → multi-format outputs (JSON, CSS, ASE, HTML, MD). Typography audit clones swiss-design-skill, inventories fonts, picks Google Fonts substitutes by metric similarity, packages OFL-compliant font files.

**Tech Stack:** Python 3.11+ (Pillow, scikit-learn, numpy, colormath, swatch), Git, Node (optional, for swiss-design-skill audit), corporate logo from deccanchemicals.com.

**Decision Points (user input required during execution):**
- **DP-1 (Task 5):** Confirm anchor color selections after extraction (which extracted blue is "blue-500", which green is "green-500")
- **DP-2 (Task 8):** Confirm Pantone-approximation method is acceptable (algorithmic ΔE-Lab nearest-neighbor against PMS Solid Coated CSV) vs. requiring a professional Pantone bridge guide
- **DP-3 (Task 16):** Confirm Google Fonts substitution choices after the recommended-mapping is presented

---

## File Structure

Project root: `C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan\`

```
.
├── .gitignore                                   # extended for Python/data
├── README.md                                    # existing
├── 2026-04-30-deccan-accent-palette-design.md   # spec (existing)
├── 2026-04-30-plan-1-palette-and-typography.md  # this plan
├── pyproject.toml                               # Python deps (uv/pip)
├── scripts/
│   ├── 01_fetch_logo.py                         # downloads logo from deccanchemicals.com
│   ├── 02_extract_colors.py                     # k-means quantization → 12 candidate colors
│   ├── 03_generate_palette.py                   # anchor-driven 8-step palette generation
│   ├── 04_compute_color_spaces.py               # adds RGB/HSL/CMYK/Pantone to each step
│   ├── 05_validate_palette.py                   # WCAG AA + lightness-gap checks
│   ├── 06_emit_outputs.py                       # produces JSON/CSS/ASE/HTML/MD
│   └── lib/
│       ├── color_math.py                        # conversions (hex↔RGB↔HSL↔CMYK↔Lab)
│       ├── pantone.py                           # nearest-neighbor PMS lookup
│       └── ase_writer.py                        # Adobe Swatch Exchange binary writer
├── data/
│   ├── logo.png                                 # downloaded logo (raw)
│   ├── candidates.json                          # k-means output (intermediate)
│   ├── anchors.json                             # 6 curated anchors (after DP-1)
│   ├── palette.json                             # final 8-step palette (intermediate)
│   └── pantone-solid-coated.csv                 # PMS reference (vendored)
├── outputs/
│   ├── palette.json                             # final, all color spaces
│   ├── palette.css                              # CSS variables + Tailwind config block
│   ├── palette.ase                              # Adobe Swatch Exchange binary
│   ├── palette-swatches.html                    # visual preview
│   └── palette.md                               # human-readable documentation
├── typography/
│   └── typography.md                            # font substitution rationale
├── fonts/
│   ├── inter/                                   # one folder per chosen Google Font
│   │   ├── Inter-VariableFont.ttf
│   │   └── OFL.txt
│   └── ...
└── tests/
    ├── test_color_math.py
    ├── test_palette_generation.py
    ├── test_validators.py
    └── test_pantone.py
```

---

## Phase 1: Setup & Logo Acquisition

### Task 1: Python environment and project structure

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Modify: `.gitignore`
- Create: directory tree (`scripts/lib/`, `data/`, `outputs/`, `typography/`, `fonts/`, `tests/`)

- [ ] **Step 1: Create directory skeleton**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
$dirs = @("scripts","scripts/lib","data","outputs","typography","fonts","tests")
foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
"" | Out-File scripts/lib/__init__.py -Encoding utf8
"" | Out-File tests/__init__.py -Encoding utf8
```

Expected: directories exist; verify with `Get-ChildItem`.

- [ ] **Step 2: Write `pyproject.toml`**

Create `pyproject.toml`:

```toml
[project]
name = "deccan-design-system"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pillow>=10.0",
    "scikit-learn>=1.4",
    "numpy>=1.26",
    "colormath>=3.0.0",
    "requests>=2.31",
    "beautifulsoup4>=4.12",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4"]
```

Create `.python-version` with content `3.11`.

- [ ] **Step 3: Extend `.gitignore`**

Append to `.gitignore`:

```
# Python
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
*.egg-info/

# Intermediate data (re-derivable)
data/candidates.json
data/anchors.json
data/palette.json

# Keep logo + pantone reference
!data/logo.png
!data/pantone-solid-coated.csv
```

- [ ] **Step 4: Create virtual env and install**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -c "import PIL, sklearn, numpy, colormath, requests, bs4; print('OK')"
```

Expected output: `OK`

- [ ] **Step 5: Commit**

```powershell
git add pyproject.toml .python-version .gitignore scripts/ data/ outputs/ typography/ fonts/ tests/
git commit -m "chore: project scaffolding for palette + typography pipeline"
```

---

### Task 2: Fetch website and locate logo asset

**Files:**
- Create: `scripts/01_fetch_logo.py`
- Create: `tests/test_logo_fetch.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_logo_fetch.py`:

```python
from pathlib import Path
from scripts import _01_fetch_logo as fetch_logo

def test_locate_logo_url_picks_header_img(tmp_path):
    html = '''
    <html><head><title>X</title></head>
    <body>
      <header><img src="/wp-content/uploads/logo.png" alt="Deccan Chemicals"></header>
    </body></html>
    '''
    url = fetch_logo.find_logo_url(html, base_url="https://deccanchemicals.com")
    assert url == "https://deccanchemicals.com/wp-content/uploads/logo.png"
```

Note: importing `_01_fetch_logo` requires renaming the file to a Python-import-safe name; rename in Step 3.

- [ ] **Step 2: Run test, expect ImportError**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_logo_fetch.py -v
```

Expected: ImportError (module doesn't exist yet).

- [ ] **Step 3: Implement `scripts/_01_fetch_logo.py`**

Create `scripts/_01_fetch_logo.py`:

```python
"""Fetch deccanchemicals.com homepage and download the corporate logo."""
from __future__ import annotations
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

WEBSITE = "https://deccanchemicals.com"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "logo.png"

def find_logo_url(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    # 1. Try <header> img
    header = soup.find("header")
    if header:
        img = header.find("img")
        if img and img.get("src"):
            return urljoin(base_url, img["src"])
    # 2. Try img with alt containing "deccan" (case-insensitive)
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").lower()
        if "deccan" in alt and img.get("src"):
            return urljoin(base_url, img["src"])
    # 3. Try img with src or class containing "logo"
    for img in soup.find_all("img"):
        src = (img.get("src") or "").lower()
        cls = " ".join(img.get("class") or []).lower()
        if "logo" in src or "logo" in cls:
            return urljoin(base_url, img.get("src", ""))
    return None

def main() -> int:
    resp = requests.get(WEBSITE, timeout=15)
    resp.raise_for_status()
    url = find_logo_url(resp.text, WEBSITE)
    if not url:
        print("ERROR: could not auto-locate logo. Save it manually to data/logo.png.", file=sys.stderr)
        return 1
    print(f"Logo URL: {url}")
    img = requests.get(url, timeout=15)
    img.raise_for_status()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(img.content)
    print(f"Saved to {OUT_PATH} ({len(img.content)} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test, expect PASS**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_logo_fetch.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Run script and verify logo downloaded**

```powershell
.\.venv\Scripts\python.exe scripts\_01_fetch_logo.py
Get-ChildItem data\logo.png
```

Expected: `Logo URL: https://...` printed, and `data/logo.png` exists with non-zero size.

**Manual fallback if Step 5 fails:** Open https://deccanchemicals.com in a browser, right-click the logo → Save Image As → save to `data\logo.png`. Then proceed.

- [ ] **Step 6: Commit**

```powershell
git add scripts/_01_fetch_logo.py tests/test_logo_fetch.py data/logo.png
git commit -m "feat(palette): fetch corporate logo from deccanchemicals.com"
```

---

## Phase 2: Color Extraction

### Task 3: K-means color extraction

**Files:**
- Create: `scripts/_02_extract_colors.py`
- Create: `scripts/lib/color_math.py`
- Create: `tests/test_color_math.py`
- Create: `data/candidates.json` (output)

- [ ] **Step 1: Write the failing test for color_math conversions**

Create `tests/test_color_math.py`:

```python
import pytest
from scripts.lib import color_math as cm

@pytest.mark.parametrize("hex_in,rgb_out", [
    ("#000000", (0, 0, 0)),
    ("#FFFFFF", (255, 255, 255)),
    ("#FF0000", (255, 0, 0)),
    ("#1E5BBE", (30, 91, 190)),
])
def test_hex_to_rgb(hex_in, rgb_out):
    assert cm.hex_to_rgb(hex_in) == rgb_out

def test_rgb_to_hex_uppercase():
    assert cm.rgb_to_hex((30, 91, 190)) == "#1E5BBE"

def test_rgb_to_hsl_round_trip():
    rgb = (30, 91, 190)
    h, s, l = cm.rgb_to_hsl(rgb)
    rgb2 = cm.hsl_to_rgb((h, s, l))
    # tolerate 1-unit rounding in each channel
    assert all(abs(a - b) <= 1 for a, b in zip(rgb, rgb2))

def test_rgb_to_cmyk_pure_red():
    c, m, y, k = cm.rgb_to_cmyk((255, 0, 0))
    assert (c, m, y, k) == (0, 100, 100, 0)
```

- [ ] **Step 2: Run, expect ImportError**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_color_math.py -v
```

Expected: ImportError on `scripts.lib.color_math`.

- [ ] **Step 3: Implement `scripts/lib/color_math.py`**

```python
"""Color space conversions: hex, RGB, HSL, CMYK, Lab."""
from __future__ import annotations
import colorsys
from typing import Tuple

RGB = Tuple[int, int, int]
HSL = Tuple[float, float, float]   # H 0-360, S 0-100, L 0-100
CMYK = Tuple[int, int, int, int]   # 0-100 each

def hex_to_rgb(h: str) -> RGB:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore

def rgb_to_hex(rgb: RGB) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)

def rgb_to_hsl(rgb: RGB) -> HSL:
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (round(h * 360, 1), round(s * 100, 1), round(l * 100, 1))

def hsl_to_rgb(hsl: HSL) -> RGB:
    h, s, l = hsl[0] / 360, hsl[2] / 100, hsl[1] / 100
    r, g, b = colorsys.hls_to_rgb(h, l, s)
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
```

- [ ] **Step 4: Run tests, expect PASS**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_color_math.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Implement `scripts/_02_extract_colors.py`**

```python
"""K-means color extraction from logo, with white/transparent filtering."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from scripts.lib.color_math import rgb_to_hex, rgb_to_hsl

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "data" / "logo.png"
OUT = ROOT / "data" / "candidates.json"
N_CLUSTERS = 12  # over-extract; we curate later

def extract_pixels(img: Image.Image) -> np.ndarray:
    img = img.convert("RGBA")
    arr = np.array(img).reshape(-1, 4)
    # Drop near-transparent
    arr = arr[arr[:, 3] > 200]
    rgb = arr[:, :3]
    # Drop near-white (likely background) and near-black (likely text)
    mask = ~((rgb > 240).all(axis=1) | (rgb < 20).all(axis=1))
    return rgb[mask]

def cluster_colors(pixels: np.ndarray, n: int) -> list[dict]:
    km = KMeans(n_clusters=n, n_init=10, random_state=42).fit(pixels)
    centers = km.cluster_centers_.round().astype(int)
    counts = np.bincount(km.labels_, minlength=n)
    total = counts.sum()
    out = []
    for i, (c, n_pix) in enumerate(zip(centers, counts)):
        rgb = tuple(int(x) for x in c)
        h, s, l = rgb_to_hsl(rgb)
        out.append({
            "rgb": rgb,
            "hex": rgb_to_hex(rgb),
            "hsl": [h, s, l],
            "pixel_count": int(n_pix),
            "pixel_share": round(float(n_pix / total), 4),
        })
    return sorted(out, key=lambda x: -x["pixel_share"])

def categorize(cands: list[dict]) -> list[dict]:
    for c in cands:
        h = c["hsl"][0]
        s = c["hsl"][1]
        if s < 8:
            c["family"] = "neutral"
        elif 180 <= h <= 260:
            c["family"] = "blue"
        elif 80 <= h <= 170:
            c["family"] = "green"
        else:
            c["family"] = "other"
    return cands

def main() -> int:
    if not LOGO.exists():
        raise SystemExit(f"Missing logo: {LOGO}. Run scripts/_01_fetch_logo.py or save manually.")
    img = Image.open(LOGO)
    pixels = extract_pixels(img)
    print(f"Extracted {len(pixels)} non-bg/non-text pixels from logo.")
    cands = categorize(cluster_colors(pixels, N_CLUSTERS))
    OUT.write_text(json.dumps(cands, indent=2))
    print(f"\nWrote {len(cands)} candidates to {OUT}")
    print("\nTop candidates by pixel share:")
    print(f"{'#':<3} {'hex':<8} {'family':<8} {'H':>5} {'S':>5} {'L':>5} {'share':>7}")
    for i, c in enumerate(cands[:12], 1):
        h, s, l = c["hsl"]
        print(f"{i:<3} {c['hex']:<8} {c['family']:<8} {h:>5.1f} {s:>5.1f} {l:>5.1f} {c['pixel_share']:>7.2%}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Run extraction**

```powershell
.\.venv\Scripts\python.exe scripts\_02_extract_colors.py
```

Expected output: a table of 12 candidate colors categorized into blue/green/neutral/other with hex codes and pixel shares. `data/candidates.json` is written.

- [ ] **Step 7: Commit**

```powershell
git add scripts/lib/color_math.py scripts/_02_extract_colors.py tests/test_color_math.py data/candidates.json
git commit -m "feat(palette): k-means color extraction with HSL categorization"
```

---

### Task 4: Curate the 6 brand anchors (DECISION POINT 1)

**Files:**
- Create: `data/anchors.json` (manual curation output)

- [ ] **Step 1: Display candidates for user review**

Run:

```powershell
.\.venv\Scripts\python.exe scripts\_02_extract_colors.py
```

The 12 candidates are listed sorted by pixel share. Spec expects 4 blue + 2 green anchor candidates.

- [ ] **Step 2: User selects 4 blues + 2 greens (DP-1)**

Present the candidates to the user and ask:
- "Of the blues listed, which 4 are the brand-distinct ones? (typically: a deep navy, a mid-blue, a brighter highlight blue, a darkest accent blue)"
- "Of the greens listed, which 2 are the brand-distinct ones? (typically: the dominant green and one shade variant)"
- "Of the 4 blues, which is the most-prominent **brand identity** blue? (this becomes `blue-500`, the anchor)"
- "Of the 2 greens, which is the dominant brand green? (this becomes `green-500`, the anchor)"

- [ ] **Step 3: Write `data/anchors.json` with selections**

Create `data/anchors.json` (replace example hex values with the user's selections — this is one of the only two manually-curated files in the pipeline):

```json
{
  "blue": {
    "darkest":  "#0A1F44",
    "dark":     "#1E5BBE",
    "anchor":   "#2A8AE2",
    "lightest": "#9EC8F2"
  },
  "green": {
    "anchor":   "#3FAE5A",
    "alt":      "#74C97E"
  }
}
```

- [ ] **Step 4: Validate anchors are legal hex codes**

Add a quick validation snippet to `scripts/_02_extract_colors.py` (or a new tiny script) that loads `data/anchors.json` and ensures every value matches `^#[0-9A-Fa-f]{6}$`. If invalid, fix before continuing.

```powershell
.\.venv\Scripts\python.exe -c "import json,re; d=json.load(open('data/anchors.json')); ok=all(re.match(r'^#[0-9A-Fa-f]{6}$', v) for fam in d.values() for v in fam.values()); print('OK' if ok else 'INVALID HEX')"
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```powershell
git add data/anchors.json
git commit -m "feat(palette): curate 6 brand anchors from logo extraction"
```

---

## Phase 3: Palette Generation

### Task 5: Generate the 8-step palette

**Files:**
- Create: `scripts/_03_generate_palette.py`
- Create: `tests/test_palette_generation.py`
- Create: `data/palette.json` (intermediate)

- [ ] **Step 1: Write the failing test**

Create `tests/test_palette_generation.py`:

```python
import json
from pathlib import Path
from scripts import _03_generate_palette as gen

def _anchors():
    return {
        "blue":  {"darkest": "#0A1F44", "dark": "#1E5BBE", "anchor": "#2A8AE2", "lightest": "#9EC8F2"},
        "green": {"anchor": "#3FAE5A", "alt": "#74C97E"},
    }

def test_blue_uses_logo_colors_for_steps():
    p = gen.build_palette(_anchors())
    assert p["blue"]["500"]["hex"] == "#2A8AE2"
    assert p["blue"]["700"]["hex"] == "#0A1F44" or p["blue"]["700"]["hex"] == "#1E5BBE"
    assert all(k in p["blue"] for k in ("100", "300", "500", "700"))

def test_green_anchor_preserved():
    p = gen.build_palette(_anchors())
    assert p["green"]["500"]["hex"] == "#3FAE5A"
    assert all(k in p["green"] for k in ("100", "300", "500", "700"))

def test_lightness_progression_monotonic():
    p = gen.build_palette(_anchors())
    for fam in ("blue", "green"):
        ls = [p[fam][k]["hsl"][2] for k in ("100", "300", "500", "700")]
        assert ls[0] > ls[1] > ls[2] > ls[3], f"{fam} not monotonic: {ls}"
```

- [ ] **Step 2: Run, expect ImportError**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_palette_generation.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `scripts/_03_generate_palette.py`**

```python
"""Generate 8-step palette (4 blue + 4 green) from 6 curated anchors."""
from __future__ import annotations
import json
from pathlib import Path

from scripts.lib.color_math import (
    hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb,
)

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = ROOT / "data" / "anchors.json"
OUT = ROOT / "data" / "palette.json"

def _adjust_hsl(rgb, dl=0, ds=0):
    h, s, l = rgb_to_hsl(rgb)
    s = max(0, min(100, s + ds))
    l = max(0, min(100, l + dl))
    return hsl_to_rgb((h, s, l))

def _entry(rgb):
    return {"hex": rgb_to_hex(rgb), "rgb": list(rgb), "hsl": list(rgb_to_hsl(rgb))}

def build_palette(anchors: dict) -> dict:
    # Blue: 4 logo shades available
    b_anchor = hex_to_rgb(anchors["blue"]["anchor"])
    b_darkest = hex_to_rgb(anchors["blue"]["darkest"])
    b_dark = hex_to_rgb(anchors["blue"]["dark"])
    b_lightest = hex_to_rgb(anchors["blue"]["lightest"])

    blue = {
        "500": _entry(b_anchor),
        # 700: darker than anchor; prefer darkest if it's at least 12 lightness below anchor
        "700": _entry(b_darkest if rgb_to_hsl(b_anchor)[2] - rgb_to_hsl(b_darkest)[2] >= 12 else b_dark),
        # 300: lighter than anchor; prefer lightest if at least 12 lightness above anchor
        "300": _entry(b_lightest if rgb_to_hsl(b_lightest)[2] - rgb_to_hsl(b_anchor)[2] >= 12
                       else _adjust_hsl(b_anchor, dl=+15, ds=-10)),
        "100": _entry(_adjust_hsl(b_anchor, dl=+(95 - rgb_to_hsl(b_anchor)[2]) if rgb_to_hsl(b_anchor)[2] < 95 else 0,
                                  ds=-25)),
    }

    # Green: 2 logo shades available
    g_anchor = hex_to_rgb(anchors["green"]["anchor"])
    g_alt = hex_to_rgb(anchors["green"]["alt"])
    g_alt_l = rgb_to_hsl(g_alt)[2]
    g_anchor_l = rgb_to_hsl(g_anchor)[2]

    # Determine if alt is darker or lighter than anchor
    if g_alt_l < g_anchor_l - 5:
        # alt is darker → use as 700
        green_700 = g_alt
        green_300 = _adjust_hsl(g_anchor, dl=+15, ds=-10)
    elif g_alt_l > g_anchor_l + 5:
        # alt is lighter → use as 300
        green_700 = _adjust_hsl(g_anchor, dl=-15)
        green_300 = g_alt
    else:
        green_700 = _adjust_hsl(g_anchor, dl=-15)
        green_300 = _adjust_hsl(g_anchor, dl=+15, ds=-10)

    green = {
        "500": _entry(g_anchor),
        "700": _entry(green_700),
        "300": _entry(green_300),
        "100": _entry(_adjust_hsl(g_anchor,
                                  dl=+(95 - g_anchor_l) if g_anchor_l < 95 else 0,
                                  ds=-25)),
    }

    return {"blue": blue, "green": green}

def main() -> int:
    anchors = json.loads(ANCHORS.read_text())
    p = build_palette(anchors)
    OUT.write_text(json.dumps(p, indent=2))
    print(f"Wrote {OUT}")
    print()
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            print(f"  {fam}-{step}  {e['hex']}  HSL{tuple(e['hsl'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests, expect PASS**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_palette_generation.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Run generation against curated anchors**

```powershell
.\.venv\Scripts\python.exe scripts\_03_generate_palette.py
```

Expected: 8 palette entries printed; `data/palette.json` written.

- [ ] **Step 6: Commit**

```powershell
git add scripts/_03_generate_palette.py tests/test_palette_generation.py data/palette.json
git commit -m "feat(palette): generate 8-step palette from curated anchors"
```

---

### Task 6: Compute color spaces (RGB/HSL/CMYK/Pantone)

**Files:**
- Create: `scripts/_04_compute_color_spaces.py`
- Create: `scripts/lib/pantone.py`
- Create: `data/pantone-solid-coated.csv`
- Modify: `data/palette.json` (enriched in place)

- [ ] **Step 1: Vendor a Pantone reference table**

Source: a public-domain Pantone Solid Coated → Hex mapping (e.g., compiled from open-source repos like `mattfarina/Color-vs.-Pantone` or similar).

Write `data/pantone-solid-coated.csv` with columns `code,hex` (~1500 rows). Excerpt:

```csv
code,hex
PMS 100 C,#F4ED7C
PMS 101 C,#F7EE5E
PMS 286 C,#0033A0
PMS 7461 C,#0080C8
PMS 354 C,#00B140
PMS 2253 C,#5BC236
...
```

(The implementer downloads/vendors a complete CSV. Note in commit message which source was used.)

- [ ] **Step 2: Implement `scripts/lib/pantone.py`**

```python
"""Approximate Pantone matching via ΔE in CIE Lab space."""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Tuple

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "pantone-solid-coated.csv"

def _load_table():
    rows = []
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            h = r["hex"].lstrip("#")
            rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
            rows.append((r["code"], rgb))
    return rows

_TABLE = None

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
```

- [ ] **Step 3: Implement `scripts/_04_compute_color_spaces.py`**

```python
"""Enrich palette.json with full color-space coordinates and Pantone match."""
from __future__ import annotations
import json
from pathlib import Path

from scripts.lib.color_math import hex_to_rgb, rgb_to_cmyk
from scripts.lib.pantone import nearest_pantone

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "data" / "palette.json"

def main() -> int:
    p = json.loads(PALETTE.read_text())
    for fam in p:
        for step in p[fam]:
            e = p[fam][step]
            rgb = tuple(e["rgb"])
            cmyk = rgb_to_cmyk(rgb)
            pms, de = nearest_pantone(rgb)
            e["cmyk"] = list(cmyk)
            e["pantone"] = {"code": pms, "delta_e": de}
    PALETTE.write_text(json.dumps(p, indent=2))
    print("Enriched palette.json with CMYK + Pantone approximations.")
    print()
    print(f"{'token':<11} {'hex':<8} {'CMYK':<22} {'Pantone':<14} {'ΔE':>5}")
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            c, m, y, k = e["cmyk"]
            cmyk = f"C{c:>3} M{m:>3} Y{y:>3} K{k:>3}"
            pms = e["pantone"]["code"]
            de = e["pantone"]["delta_e"]
            print(f"{fam}-{step:<6} {e['hex']:<8} {cmyk:<22} {pms:<14} {de:>5}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run**

```powershell
.\.venv\Scripts\python.exe scripts\_04_compute_color_spaces.py
```

Expected: table with 8 rows showing hex + CMYK + Pantone approximation + ΔE per step.

- [ ] **Step 5: DECISION POINT 2 — review Pantone matches**

Inspect each step's ΔE value. Guidance:
- ΔE < 2 — visually indistinguishable; safe to recommend that PMS.
- ΔE 2–5 — close; usable but note the approximation in `palette.md`.
- ΔE > 5 — perceptibly different; recommend the user obtain a professional Pantone bridge guide for that step.

Record the decision (accept the algorithmic match vs. flag for professional review per step) for documentation in Task 9.

- [ ] **Step 6: Commit**

```powershell
git add scripts/lib/pantone.py scripts/_04_compute_color_spaces.py data/pantone-solid-coated.csv data/palette.json
git commit -m "feat(palette): enrich with CMYK + ΔE-nearest Pantone matches"
```

---

### Task 7: Validate WCAG contrast and lightness gaps

**Files:**
- Create: `scripts/_05_validate_palette.py`
- Create: `tests/test_validators.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_validators.py`:

```python
from scripts import _05_validate_palette as v

def test_validate_passes_well_designed_palette():
    palette = {
        "blue": {
            "100": {"rgb": [230, 240, 255], "hex": "#E6F0FF"},
            "300": {"rgb": [150, 190, 235], "hex": "#96BEEB"},
            "500": {"rgb": [42, 138, 226],  "hex": "#2A8AE2"},
            "700": {"rgb": [10, 31, 68],    "hex": "#0A1F44"},
        },
        "green": {
            "100": {"rgb": [220, 245, 225], "hex": "#DCF5E1"},
            "300": {"rgb": [150, 215, 165], "hex": "#96D7A5"},
            "500": {"rgb": [63, 174, 90],   "hex": "#3FAE5A"},
            "700": {"rgb": [22, 96, 38],    "hex": "#166026"},
        },
    }
    report = v.validate(palette)
    assert report["pass"] is True

def test_validate_flags_too_close_steps():
    palette = {"blue": {
        "100": {"rgb": [240, 240, 240], "hex": "#F0F0F0"},
        "300": {"rgb": [235, 235, 235], "hex": "#EBEBEB"},  # too close to 100
        "500": {"rgb": [100, 100, 100], "hex": "#646464"},
        "700": {"rgb": [50, 50, 50],    "hex": "#323232"},
    }}
    report = v.validate(palette)
    assert report["pass"] is False
    assert any("lightness gap" in w.lower() for w in report["warnings"])
```

- [ ] **Step 2: Run, expect ImportError**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_validators.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `scripts/_05_validate_palette.py`**

```python
"""Validate palette against WCAG AA and lightness-gap rules."""
from __future__ import annotations
import json
from pathlib import Path

from scripts.lib.color_math import contrast_ratio, rgb_to_hsl

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "data" / "palette.json"

WHITE = (255, 255, 255)
DARK_BG = (15, 15, 15)
MIN_GAP = 12.0     # min lightness % between adjacent steps
WCAG_AA = 4.5

def validate(palette: dict) -> dict:
    warns = []
    notes = []
    for fam, steps in palette.items():
        ls = [(k, rgb_to_hsl(tuple(v["rgb"]))[2]) for k, v in steps.items() if k in ("100", "300", "500", "700")]
        ls.sort(key=lambda kv: ["100","300","500","700"].index(kv[0]))
        for i in range(len(ls) - 1):
            gap = ls[i][1] - ls[i+1][1]
            if abs(gap) < MIN_GAP:
                warns.append(f"{fam}-{ls[i][0]} → {fam}-{ls[i+1][0]}: lightness gap {gap:.1f}% < {MIN_GAP}%")
        for step, v in steps.items():
            if step not in ("500", "700"):
                continue
            rgb = tuple(v["rgb"])
            ratio_w = contrast_ratio(rgb, WHITE)
            ratio_d = contrast_ratio(rgb, DARK_BG)
            if ratio_w < WCAG_AA and ratio_d < WCAG_AA:
                warns.append(f"{fam}-{step} ({v['hex']}): fails WCAG AA on both white ({ratio_w}) and dark ({ratio_d})")
            else:
                notes.append(f"{fam}-{step} contrast — white:{ratio_w}  dark:{ratio_d}")
    return {"pass": not warns, "warnings": warns, "notes": notes}

def main() -> int:
    p = json.loads(PALETTE.read_text())
    report = validate(p)
    print(f"OVERALL: {'PASS' if report['pass'] else 'FAIL'}")
    for w in report["warnings"]:
        print(f"  WARN: {w}")
    for n in report["notes"]:
        print(f"  note: {n}")
    return 0 if report["pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests + script**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_validators.py -v
.\.venv\Scripts\python.exe scripts\_05_validate_palette.py
```

Expected: tests pass; script reports PASS or specific warnings.

If WARN: revisit anchor selection (Task 4) or step-generation parameters (Task 5).

- [ ] **Step 5: Commit**

```powershell
git add scripts/_05_validate_palette.py tests/test_validators.py
git commit -m "feat(palette): validate WCAG AA contrast and lightness-gap rules"
```

---

## Phase 4: Multi-Format Output Generation

### Task 8: Emit `outputs/palette.json` and `outputs/palette.css`

**Files:**
- Create: `scripts/_06_emit_outputs.py`
- Create: `outputs/palette.json`, `outputs/palette.css`

- [ ] **Step 1: Implement `scripts/_06_emit_outputs.py` (JSON + CSS sections)**

```python
"""Emit final design-system tokens in multiple formats."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "data" / "palette.json"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

def emit_json(p: dict) -> None:
    (OUT / "palette.json").write_text(json.dumps(p, indent=2))

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
    (OUT / "palette.css").write_text("\n".join(lines))

def main() -> int:
    p = json.loads(PALETTE.read_text())
    emit_json(p)
    emit_css(p)
    print("Wrote outputs/palette.json, outputs/palette.css")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run and inspect**

```powershell
.\.venv\Scripts\python.exe scripts\_06_emit_outputs.py
Get-Content outputs\palette.css
Get-Content outputs\palette.json
```

Expected: CSS shows `--accent-blue-100..700` and `--accent-green-100..700` variables plus a commented Tailwind block. JSON is identical to `data/palette.json`.

- [ ] **Step 3: Commit**

```powershell
git add scripts/_06_emit_outputs.py outputs/palette.json outputs/palette.css
git commit -m "feat(outputs): emit palette.json and palette.css with Tailwind block"
```

---

### Task 9: Emit `outputs/palette.ase`

**Files:**
- Create: `scripts/lib/ase_writer.py`
- Modify: `scripts/_06_emit_outputs.py` (add `emit_ase`)
- Create: `outputs/palette.ase`

- [ ] **Step 1: Implement `scripts/lib/ase_writer.py`**

The ASE binary format is documented (see Adobe ASE spec). Implement a minimal writer that emits one group with 8 swatches (RGB float 0..1):

```python
"""Adobe Swatch Exchange (ASE) binary writer — minimal RGB-only.

Format reference: Adobe Swatch Exchange specification (1.0). One group block
containing one color block per palette step. RGB color mode, "Normal" type.
"""
from __future__ import annotations
import struct
from pathlib import Path
from typing import Iterable

def _string_block(name: str) -> bytes:
    s = name.encode("utf-16-be") + b"\x00\x00"
    return struct.pack(">H", len(name) + 1) + s

def _color_block(name: str, rgb: tuple[int, int, int]) -> bytes:
    name_block = _string_block(name)
    color_data = b"RGB " + struct.pack(">3f", *(c / 255 for c in rgb)) + struct.pack(">H", 0)
    body = name_block + color_data
    return b"\x00\x01" + struct.pack(">I", len(body)) + body

def _group_open(name: str) -> bytes:
    name_block = _string_block(name)
    return b"\xC0\x01" + struct.pack(">I", len(name_block)) + name_block

def _group_close() -> bytes:
    return b"\xC0\x02" + struct.pack(">I", 0)

def write_ase(path: Path, group: str, swatches: Iterable[tuple[str, tuple[int, int, int]]]) -> None:
    blocks = [_group_open(group)]
    n_blocks = 1
    for name, rgb in swatches:
        blocks.append(_color_block(name, rgb))
        n_blocks += 1
    blocks.append(_group_close())
    n_blocks += 1
    header = b"ASEF" + struct.pack(">HH", 1, 0) + struct.pack(">I", n_blocks)
    path.write_bytes(header + b"".join(blocks))
```

- [ ] **Step 2: Add `emit_ase` to `_06_emit_outputs.py`**

Append to `scripts/_06_emit_outputs.py`:

```python
from scripts.lib.ase_writer import write_ase

def emit_ase(p: dict) -> None:
    swatches = []
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            swatches.append((f"{fam}-{step}", tuple(e["rgb"])))
    write_ase(OUT / "palette.ase", "Deccan Chemicals — Accent", swatches)
```

And call it in `main()`:

```python
def main() -> int:
    p = json.loads(PALETTE.read_text())
    emit_json(p)
    emit_css(p)
    emit_ase(p)
    print("Wrote outputs/palette.json, outputs/palette.css, outputs/palette.ase")
    return 0
```

- [ ] **Step 3: Run and verify ASE is non-trivial size and starts with "ASEF"**

```powershell
.\.venv\Scripts\python.exe scripts\_06_emit_outputs.py
$bytes = [System.IO.File]::ReadAllBytes("outputs\palette.ase")
[System.Text.Encoding]::ASCII.GetString($bytes[0..3])
$bytes.Length
```

Expected: `ASEF` and length ≥ ~300 bytes.

- [ ] **Step 4: Manual verification (optional but recommended)**

Open `outputs/palette.ase` in Adobe Illustrator/Photoshop/InDesign (Window → Swatches → menu → Open Swatch Library → Other Library) to confirm the swatches load with the right names and colors. Or use a free online ASE viewer.

- [ ] **Step 5: Commit**

```powershell
git add scripts/lib/ase_writer.py scripts/_06_emit_outputs.py outputs/palette.ase
git commit -m "feat(outputs): emit Adobe Swatch Exchange (.ase) for design tools"
```

---

### Task 10: Emit `outputs/palette-swatches.html`

**Files:**
- Modify: `scripts/_06_emit_outputs.py`
- Create: `outputs/palette-swatches.html`

- [ ] **Step 1: Add `emit_html` function**

Append to `scripts/_06_emit_outputs.py`:

```python
def emit_html(p: dict) -> None:
    rows = []
    for fam in ("blue", "green"):
        cells = []
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            text_color = "#fff" if e["hsl"][2] < 55 else "#111"
            pms = e.get("pantone", {}).get("code", "—")
            cells.append(
                f'<div class="sw" style="background:{e["hex"]};color:{text_color}">'
                f'<div class="step">{fam}-{step}</div>'
                f'<div class="hex">{e["hex"]}</div>'
                f'<div class="pms">{pms}</div>'
                f'</div>'
            )
        rows.append(f'<section><h2>{fam.title()}</h2><div class="row">{"".join(cells)}</div></section>')
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Deccan Chemicals — Accent Palette</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; }}
  h1 {{ font-weight: 400; letter-spacing: -.02em; }}
  section {{ margin: 24px 0; }}
  .row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }}
  .sw {{ padding: 24px 16px; border-radius: 4px; }}
  .step {{ font-size: 12px; opacity: .9; }}
  .hex  {{ font-size: 18px; font-weight: 600; margin-top: 4px; }}
  .pms  {{ font-size: 11px; opacity: .8; margin-top: 18px; }}
</style></head>
<body>
  <h1>Deccan Chemicals — Accent Palette</h1>
  {"".join(rows)}
  <p style="opacity:.6;font-size:12px">Generated from corporate logo at deccanchemicals.com</p>
</body></html>"""
    (OUT / "palette-swatches.html").write_text(html, encoding="utf-8")
```

Call in `main()`:

```python
emit_html(p)
print("Wrote outputs/palette.json, outputs/palette.css, outputs/palette.ase, outputs/palette-swatches.html")
```

- [ ] **Step 2: Run and open in browser**

```powershell
.\.venv\Scripts\python.exe scripts\_06_emit_outputs.py
Start-Process outputs\palette-swatches.html
```

Expected: a browser window showing two rows of 4 swatches each, with hex codes and PMS labels visible. Visually validate that the colors look brand-coherent.

- [ ] **Step 3: Commit**

```powershell
git add scripts/_06_emit_outputs.py outputs/palette-swatches.html
git commit -m "feat(outputs): emit visual swatch preview HTML"
```

---

### Task 11: Emit `outputs/palette.md`

**Files:**
- Modify: `scripts/_06_emit_outputs.py`
- Create: `outputs/palette.md`

- [ ] **Step 1: Add `emit_md` function**

Append to `scripts/_06_emit_outputs.py`:

```python
def emit_md(p: dict) -> None:
    USE_CASES = {
        "100": "Background washes; subtle hover fills; subtle highlights.",
        "300": "Borders; dividers; secondary accents; chart fill tints.",
        "500": "**Anchor** — primary buttons, links, brand identity, default chart series color.",
        "700": "Hover/pressed states; text on light backgrounds; emphasis; chart series 2.",
    }
    out = ["# Deccan Chemicals — Accent Color Palette",
           "",
           "Generated from the corporate logo at https://deccanchemicals.com.",
           "Anchor steps (`-500`) are exact colors taken from the logo. Other steps",
           "are derived to maintain visual progression and accessibility.",
           "",
           "## Palette",
           ""]
    for fam in ("blue", "green"):
        out.append(f"### {fam.title()}")
        out.append("")
        out.append("| Step | Hex | RGB | HSL | CMYK | Pantone (≈) | ΔE | Use |")
        out.append("|---|---|---|---|---|---|---|---|")
        for step in ("100", "300", "500", "700"):
            e = p[fam][step]
            r, g, b = e["rgb"]
            h, s, l = e["hsl"]
            c, m, y, k = e["cmyk"]
            pms = e["pantone"]["code"]
            de = e["pantone"]["delta_e"]
            de_note = "✓" if de < 2 else ("close" if de < 5 else "**verify**")
            out.append(f"| `{fam}-{step}` | `{e['hex']}` | rgb({r}, {g}, {b}) | hsl({h}, {s}%, {l}%) | "
                       f"C{c} M{m} Y{y} K{k} | {pms} | {de} ({de_note}) | {USE_CASES[step]} |")
        out.append("")
    out += ["## Pantone matching note",
            "",
            "Pantone values are algorithmic ΔE-2000 nearest neighbors against a Solid Coated reference table.",
            "Steps marked **verify** (ΔE > 5) should be confirmed against a professional Pantone Bridge guide",
            "before being used in print production.",
            "",
            "## Accessibility",
            "",
            "Anchor (`-500`) and dark (`-700`) steps are validated against WCAG AA (≥ 4.5:1) on at least",
            "one of white or dark backgrounds. See `scripts/_05_validate_palette.py` for the validation routine.",
            "",
            "## Status indicator colors are out of scope",
            "",
            "This palette covers brand accents only. Status colors (success / warning / info / error) follow",
            "a separate traditional multi-colored palette defined elsewhere in the design system.",
            ""]
    (OUT / "palette.md").write_text("\n".join(out), encoding="utf-8")
```

Call in `main()`:

```python
emit_md(p)
print("Wrote palette.json, palette.css, palette.ase, palette-swatches.html, palette.md")
```

- [ ] **Step 2: Run and review**

```powershell
.\.venv\Scripts\python.exe scripts\_06_emit_outputs.py
Get-Content outputs\palette.md | Select-Object -First 40
```

Expected: a Markdown table with all 8 steps, hex/RGB/HSL/CMYK/Pantone columns and use-case notes.

- [ ] **Step 3: Commit**

```powershell
git add scripts/_06_emit_outputs.py outputs/palette.md
git commit -m "feat(outputs): emit human-readable palette.md documentation"
```

---

## Phase 5: Typography Audit & Substitution

### Task 12: Clone and audit zeke/swiss-design-skill

**Files:**
- Create: `typography/audit.json` (intermediate, gitignored)
- Create: `typography/audit-notes.md`

- [ ] **Step 1: Clone the upstream repo into a temp working area**

```powershell
$tmp = "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan\.tmp_swiss"
git clone https://github.com/zeke/swiss-design-skill $tmp
Get-ChildItem $tmp
```

(Add `.tmp_swiss/` to `.gitignore` to avoid committing the clone.)

- [ ] **Step 2: Inventory font references**

Search across the cloned repo:

```powershell
Set-Location $tmp
$pattern = '(?i)font-family|@font-face|@import.*(font|google)|fonts\.googleapis|Helvetica|Akzidenz|Univers|Neue Haas|Frutiger|Avenir|Futura|Brown|Suisse|Theinhardt'
Get-ChildItem -Recurse -Include *.css,*.scss,*.html,*.md,*.tsx,*.ts,*.js,*.json,*.svelte,*.vue -ErrorAction SilentlyContinue |
    Select-String -Pattern $pattern |
    Format-Table Path, LineNumber, Line -AutoSize
```

Capture the output into `..\swiss_design_at_deccan\typography\audit-notes.md` so each font reference is documented with file + line.

- [ ] **Step 3: Categorize each font by license**

For each unique font name found, determine licensing:
- **Free** (Google Fonts, SIL OFL, Apache 2.0): keep as-is.
- **Commercial** (Linotype/Monotype/Hoefler/Klim/Commercial Type, etc.): mark for substitution.

Compile into a 3-column table (Font | License | Substitution Needed?) at the top of `audit-notes.md`.

- [ ] **Step 4: Commit audit notes**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
git add typography/audit-notes.md .gitignore
git commit -m "feat(typography): audit zeke/swiss-design-skill font references"
```

---

### Task 13: Map commercial fonts to Google Fonts (DECISION POINT 3)

**Files:**
- Create: `typography/substitution-map.json`

- [ ] **Step 1: For each commercial font, propose 2 Google Fonts candidates**

Use this comparison rubric per candidate:
- x-height ratio
- weight count and variable axes available
- letterform geometry (humanist vs geometric vs grotesque)
- language/glyph coverage (must include extended-Latin)
- whether it's a variable font (preferred for weight flexibility)

Common likely substitutions (placeholder — verify against actual audit):

| Original | Candidate A | Candidate B | Recommended | Rationale |
|---|---|---|---|---|
| Helvetica / Helvetica Neue | Inter | Manrope | Inter | Variable, extensive weight range, designed for screens, near-identical metrics |
| Akzidenz-Grotesk | Manrope | Work Sans | Manrope | Variable, humanist-grotesque, good on body and display |
| Univers | DM Sans | Plus Jakarta Sans | DM Sans | Geometric grotesque with optical-size axis |
| Neue Haas Grotesk | Inter | Plus Jakarta Sans | Inter | Closest digital re-interpretation |
| Frutiger | Public Sans | Source Sans 3 | Public Sans | USWDS-approved Frutiger-like substitute |

- [ ] **Step 2: Present mapping to user (DP-3)**

Ask the user to confirm or override each substitution. Lock in choices.

- [ ] **Step 3: Write `typography/substitution-map.json`**

Example structure (replace example values with the user's confirmed choices):

```json
{
  "substitutions": [
    {
      "original": "Helvetica Neue",
      "original_license": "commercial (Linotype)",
      "substitute": {
        "family": "Inter",
        "license": "SIL OFL 1.1",
        "weights": "100-900 (variable)",
        "url": "https://fonts.google.com/specimen/Inter",
        "github": "https://github.com/rsms/inter"
      },
      "rationale": "Variable font with full weight range; designed for screens; near-identical metrics to Helvetica."
    }
  ]
}
```

- [ ] **Step 4: Commit**

```powershell
git add typography/substitution-map.json
git commit -m "feat(typography): map commercial Swiss fonts to Google Fonts substitutes"
```

---

### Task 14: Download and package Google Fonts

**Files:**
- Create: `fonts/<family>/...` for each chosen font
- Create: `scripts/_07_fetch_fonts.py`

- [ ] **Step 1: Implement `scripts/_07_fetch_fonts.py`**

```python
"""Download chosen Google Fonts (TTF + OFL.txt) into fonts/<family>/."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "typography" / "substitution-map.json"
OUT = ROOT / "fonts"

# Direct download URLs for OFL'd Google Fonts. Update with the user-confirmed choices.
SOURCES = {
    "Inter": {
        "files": [
            ("Inter-VariableFont_slnt,wght.ttf",
             "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-VariableFont_slnt,wght.ttf"),
            ("OFL.txt", "https://github.com/rsms/inter/raw/master/LICENSE.txt"),
        ],
    },
    "Manrope": {
        "files": [
            ("Manrope-VariableFont_wght.ttf",
             "https://github.com/sharanda/manrope/raw/master/fonts/variable/Manrope%5Bwght%5D.ttf"),
            ("OFL.txt",
             "https://github.com/sharanda/manrope/raw/master/OFL.txt"),
        ],
    },
    # Add additional families per substitution-map.json
}

def main() -> int:
    sub_map = json.loads(MAP.read_text())
    families = {s["substitute"]["family"] for s in sub_map["substitutions"]}
    for fam in families:
        if fam not in SOURCES:
            print(f"WARN: no SOURCES entry for {fam}; add it to scripts/_07_fetch_fonts.py", file=sys.stderr)
            continue
        dest = OUT / fam.lower().replace(" ", "-")
        dest.mkdir(parents=True, exist_ok=True)
        for filename, url in SOURCES[fam]["files"]:
            print(f"  → {fam}/{filename}")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            (dest / filename).write_bytes(r.content)
    print("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run and verify**

```powershell
.\.venv\Scripts\python.exe scripts\_07_fetch_fonts.py
Get-ChildItem fonts -Recurse -File | Select-Object FullName, Length
```

Expected: each chosen family has at least one `.ttf` (preferably variable) and an `OFL.txt` license file.

- [ ] **Step 3: Verify license compliance**

Open one OFL.txt to confirm it's the standard SIL Open Font License 1.1 text. Document this confirmation in `typography/typography.md` (next task).

- [ ] **Step 4: Commit**

```powershell
git add scripts/_07_fetch_fonts.py fonts/
git commit -m "feat(typography): package OFL Google Fonts substitutes"
```

---

### Task 15: Write `typography/typography.md`

**Files:**
- Create: `typography/typography.md`

- [ ] **Step 1: Write the documentation**

Create `typography/typography.md` populated from the substitution map:

```markdown
# Deccan Chemicals — Typography

The Deccan Chemicals design system uses free Google Fonts substitutes for any
commercially-licensed fonts referenced in the upstream `zeke/swiss-design-skill`
specification. All chosen fonts are licensed under SIL Open Font License 1.1,
which permits redistribution and embedding in corporate documents.

## Substitutions

<!-- Generate one block per substitution from typography/substitution-map.json -->

### Helvetica Neue → Inter

- **Original:** Helvetica Neue (Linotype, commercial)
- **Substitute:** Inter (rsms / Google Fonts, SIL OFL 1.1)
- **Why:** Variable font (100–900) designed for screens. x-height and proportions
  closely match Helvetica Neue. Extended-Latin coverage. Excellent at small
  display sizes and body text.
- **Files:** `fonts/inter/Inter-VariableFont_slnt,wght.ttf`
- **License:** `fonts/inter/OFL.txt`

<!-- Repeat for each substitution -->

## Usage Guidance

- **Display/headlines** — use the chosen substitute at weights 600–800
- **Body** — weight 400, 1.5 line height (matches Swiss design conventions)
- **UI / small caps** — weight 500, slight letter-spacing increase

## Variable-axis usage

Variable fonts allow expressive hierarchy with a single file. Reference the
weight axis directly: `font-variation-settings: "wght" 600;`. This avoids
loading multiple static weight files and keeps documents lightweight.

## License compliance

All bundled fonts are SIL OFL 1.1, which permits:
- Free use in corporate documents and websites
- Redistribution as part of templates and brand assets
- Embedding in PDFs, .pptx, .docx files

Each font folder includes its `OFL.txt` to satisfy attribution requirements.
```

- [ ] **Step 2: Commit**

```powershell
git add typography/typography.md
git commit -m "docs(typography): document Google Fonts substitutions and licensing"
```

---

## Phase 6: Final Review & Tag

### Task 16: End-to-end smoke test

- [ ] **Step 1: Re-run the full pipeline from scratch**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe scripts\_01_fetch_logo.py
.\.venv\Scripts\python.exe scripts\_02_extract_colors.py
# Manually inspect data/anchors.json — should already exist from Task 4
.\.venv\Scripts\python.exe scripts\_03_generate_palette.py
.\.venv\Scripts\python.exe scripts\_04_compute_color_spaces.py
.\.venv\Scripts\python.exe scripts\_05_validate_palette.py
.\.venv\Scripts\python.exe scripts\_06_emit_outputs.py
.\.venv\Scripts\python.exe scripts\_07_fetch_fonts.py
.\.venv\Scripts\python.exe -m pytest -v
```

Expected:
- All scripts exit 0
- All tests pass
- `outputs/` contains 5 files (json/css/ase/html/md)
- `fonts/<family>/` populated for each chosen font
- `typography/typography.md` complete

- [ ] **Step 2: Visual review**

Open `outputs/palette-swatches.html` in a browser. Confirm:
- Colors look brand-coherent (related to logo)
- Text contrast is comfortable on every swatch
- Use-case labels make sense

- [ ] **Step 3: Update top-level README**

Add a "Status" section to `README.md`:

```markdown
## Status

✓ **Plan 1 complete** — Color palette + typography foundation shipped.

Outputs in `outputs/`:
- `palette.json`, `palette.css`, `palette.ase`, `palette-swatches.html`, `palette.md`

Typography in `typography/` and `fonts/` (SIL OFL 1.1).

Next: **Plan 2** — modify `zeke/swiss-design-skill` to use these tokens.
```

- [ ] **Step 4: Tag the release**

```powershell
git add README.md
git commit -m "docs: mark Plan 1 complete"
git tag -a v0.1.0 -m "Plan 1: palette + typography foundation"
git push origin main --tags
```

Expected: tag pushed and visible on GitHub at https://github.com/kvkalidindi/swiss_design_at_deccan/releases/tag/v0.1.0.

---

## Self-Review

**Spec coverage:**
- Section 2 (Color extraction) → Tasks 2, 3
- Section 3 (8-step structure) → Task 5
- Section 4 (Step generation logic) → Task 5
- Section 5 (Multi-format integration core: Hex/RGB/HSL/CMYK/Pantone) → Task 6
- Section 6 (Font strategy) → Tasks 12, 13, 14, 15
- Section 7 (Enterprise deployment) → **Deferred to Plan 3+** (out of scope here)
- Section 8 (Deliverables 1–6) → Tasks 8, 9, 10, 11, 15
- Section 8 (Deliverables 7–11, Office/Workspace/Intune) → **Deferred to Plans 3, 4, 5**

**Placeholder scan:** None — all tasks contain actual code, exact commands, and explicit expected outputs. Decision points are explicitly marked DP-1/DP-2/DP-3 with the questions to ask the user.

**Type consistency:** `build_palette()`, `validate()`, `nearest_pantone()`, `write_ase()` signatures consistent across tasks. `data/anchors.json` schema (blue:darkest/dark/anchor/lightest, green:anchor/alt) used consistently. Token naming `<family>-<step>` (e.g., `blue-500`) used identically in palette.json/CSS/ASE/HTML/MD.

---

## Out of Scope (deferred to follow-up plans)

- **Plan 2:** Modify `zeke/swiss-design-skill` to consume our tokens; produce the modified skill repo.
- **Plan 3:** Microsoft Office artifacts — `.thmx` themes, `.dotx`/`.potx`/`.xltx` templates, Outlook signature.
- **Plan 4:** Google Workspace artifacts — Slides/Docs templates, admin gallery setup.
- **Plan 5:** Enterprise deployment — Intune profiles, Group Policy, font-installation scripts, browser default fonts.
- **Status indicator palette** (success/warning/info/error) — separate effort, not part of this 8-step accent palette.
