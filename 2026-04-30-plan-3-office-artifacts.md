# Plan 3: Microsoft Office Artifacts — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce `office/` containing `office-theme.thmx`, `templates/{deccan.dotx,deccan.potx,deccan.xltx,signature.htm}` plus a README with install paths.

**Architecture:** A single orchestrator `scripts/_09_emit_office.py` calls per-format builder modules in `scripts/lib/` (`office_theme.py`, `office_pptx.py`, `office_docx.py`, `office_xlsx.py`, `office_signature.py`). Each module owns one file format. Theme is built first (foundation); templates are built second and reference the theme. All read inputs from `outputs/palette.json`, `data/logo.png`, `fonts/`. Idempotent re-runs.

**Tech Stack:** Python 3.11+, `python-pptx`, `python-docx`, `openpyxl`, `Pillow`, raw OOXML manipulation via `zipfile`/`lxml` for things the libraries don't expose (font embedding, theme XML).

**Important pragmatic note on font embedding:** `python-docx`/`python-pptx` don't expose font embedding in their public APIs. We post-process the generated OOXML zip to embed IBM Plex Sans/Mono. If this proves too brittle, the fallback is documented in Task 8 (rely on OS-level font install via Plan 5; templates still reference IBM Plex by name).

---

## File Structure

```
swiss_design_at_deccan/
├── pyproject.toml                              # MODIFY: add python-pptx, python-docx, openpyxl, lxml
├── scripts/
│   ├── _09_emit_office.py                      # NEW orchestrator
│   └── lib/
│       ├── office_theme.py                     # NEW .thmx builder
│       ├── office_pptx.py                      # NEW .potx builder
│       ├── office_docx.py                      # NEW .dotx builder
│       ├── office_xlsx.py                      # NEW .xltx builder
│       ├── office_signature.py                 # NEW .htm builder
│       └── office_font_embed.py                # NEW post-processor for font embedding
├── office/                                     # NEW (committed)
│   ├── office-theme.thmx                       # generated
│   ├── templates/
│   │   ├── deccan.dotx                         # generated
│   │   ├── deccan.potx                         # generated
│   │   ├── deccan.xltx                         # generated
│   │   └── signature.htm                       # generated
│   └── README.md                               # install instructions
└── tests/
    └── test_office_emitter.py                  # NEW
```

---

## Phase 1: Setup

### Task 1: Install Office libraries and scaffold

**Files:**
- Modify: `pyproject.toml`
- Create: `scripts/lib/office_theme.py` (empty stub)
- Create: `scripts/lib/office_pptx.py` (empty stub)
- Create: `scripts/lib/office_docx.py` (empty stub)
- Create: `scripts/lib/office_xlsx.py` (empty stub)
- Create: `scripts/lib/office_signature.py` (empty stub)
- Create: `scripts/lib/office_font_embed.py` (empty stub)
- Create: `scripts/_09_emit_office.py` (empty orchestrator stub)
- Create: `office/` directory tree

- [ ] **Step 1: Add dependencies to `pyproject.toml`**

Modify the `[project] dependencies` list to add:

```toml
[project]
dependencies = [
    "pillow>=10.0",
    "scikit-learn>=1.4",
    "numpy>=1.26",
    "colormath>=3.0.0",
    "requests>=2.31",
    "beautifulsoup4>=4.12",
    "python-pptx>=0.6.23",
    "python-docx>=1.1.0",
    "openpyxl>=3.1.2",
    "lxml>=5.0",
]
```

- [ ] **Step 2: Install new deps**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -c "import pptx, docx, openpyxl, lxml; print('OK')"
```

Expected: `OK`.

- [ ] **Step 3: Create directory skeleton**

```powershell
$dirs = @("office", "office/templates")
foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
```

- [ ] **Step 4: Create stub Python files**

Each stub starts with a docstring describing its purpose. Create:

`scripts/lib/office_theme.py`:
```python
"""Build office-theme.thmx (Office 2007+ theme file: ZIP with theme XML)."""
```

`scripts/lib/office_pptx.py`:
```python
"""Build deccan.potx using python-pptx (PowerPoint template with 8 slide masters)."""
```

`scripts/lib/office_docx.py`:
```python
"""Build deccan.dotx using python-docx (Word template with cover page + styles)."""
```

`scripts/lib/office_xlsx.py`:
```python
"""Build deccan.xltx using openpyxl (Excel template with table styles)."""
```

`scripts/lib/office_signature.py`:
```python
"""Build signature.htm Outlook email signature."""
```

`scripts/lib/office_font_embed.py`:
```python
"""Post-process OOXML files to embed IBM Plex fonts (subsets via fontTools optional)."""
```

`scripts/_09_emit_office.py`:
```python
"""Orchestrator: emit office-theme.thmx + 4 templates + signature.htm."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print("scaffold only - implementations come in subsequent tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Smoke test the scaffolding**

```powershell
.\.venv\Scripts\python.exe scripts\_09_emit_office.py
```

Expected: `scaffold only - implementations come in subsequent tasks`

- [ ] **Step 6: Commit**

```powershell
git add pyproject.toml scripts/lib/office_*.py scripts/_09_emit_office.py office/
git status
git commit -m "chore(office): scaffold Office artifact emitter modules"
```

---

## Phase 2: Theme (.thmx)

### Task 2: Build `office-theme.thmx`

**Files:**
- Create: real implementation in `scripts/lib/office_theme.py`
- Modify: `scripts/_09_emit_office.py` to call it
- Will produce: `office/office-theme.thmx`

The `.thmx` file is a ZIP container with this structure:
```
[Content_Types].xml
_rels/.rels
theme/theme1.xml      <- the actual theme definition
theme/_rels/theme1.xml.rels
```

We construct each XML file as a string and zip them together.

- [ ] **Step 1: Implement `scripts/lib/office_theme.py`**

```python
"""Build office-theme.thmx (Office 2007+ theme file: ZIP with theme XML)."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
OUT = ROOT / "office" / "office-theme.thmx"


# Theme color slot mapping. Office theme has 12 slots: bg1, bg2, text1, text2,
# accent1-6, hlink, folHlink. We map our palette as documented in the spec.
def color_map(palette: dict) -> dict[str, str]:
    return {
        "bg1":     "FFFFFF",
        "bg2":     "FAFAF9",
        "text1":   "1C1917",
        "text2":   "44403C",
        "accent1": palette["blue"]["500"]["hex"].lstrip("#"),
        "accent2": palette["blue"]["700"]["hex"].lstrip("#"),
        "accent3": palette["blue"]["300"]["hex"].lstrip("#"),
        "accent4": palette["green"]["500"]["hex"].lstrip("#"),
        "accent5": palette["green"]["700"]["hex"].lstrip("#"),
        "accent6": palette["green"]["300"]["hex"].lstrip("#"),
        "hlink":   palette["blue"]["500"]["hex"].lstrip("#"),
        "folHlink": palette["blue"]["700"]["hex"].lstrip("#"),
    }


THEME_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Deccan Chemicals">
  <a:themeElements>
    <a:clrScheme name="Deccan">
      <a:dk1><a:srgbClr val="{text1}"/></a:dk1>
      <a:lt1><a:srgbClr val="{bg1}"/></a:lt1>
      <a:dk2><a:srgbClr val="{text2}"/></a:dk2>
      <a:lt2><a:srgbClr val="{bg2}"/></a:lt2>
      <a:accent1><a:srgbClr val="{accent1}"/></a:accent1>
      <a:accent2><a:srgbClr val="{accent2}"/></a:accent2>
      <a:accent3><a:srgbClr val="{accent3}"/></a:accent3>
      <a:accent4><a:srgbClr val="{accent4}"/></a:accent4>
      <a:accent5><a:srgbClr val="{accent5}"/></a:accent5>
      <a:accent6><a:srgbClr val="{accent6}"/></a:accent6>
      <a:hlink><a:srgbClr val="{hlink}"/></a:hlink>
      <a:folHlink><a:srgbClr val="{folHlink}"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Deccan">
      <a:majorFont>
        <a:latin typeface="IBM Plex Sans"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="IBM Plex Sans"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:lumMod val="110000"/><a:satMod val="105000"/><a:tint val="67000"/></a:schemeClr></a:gs><a:gs pos="50000"><a:schemeClr val="phClr"><a:lumMod val="105000"/><a:satMod val="103000"/><a:tint val="73000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:lumMod val="105000"/><a:satMod val="109000"/><a:tint val="81000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:satMod val="103000"/><a:lumMod val="102000"/><a:tint val="94000"/></a:schemeClr></a:gs><a:gs pos="50000"><a:schemeClr val="phClr"><a:satMod val="110000"/><a:lumMod val="100000"/><a:shade val="100000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:lumMod val="99000"/><a:satMod val="120000"/><a:shade val="78000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="6350" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:miter lim="800000"/></a:ln>
        <a:ln w="12700" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:miter lim="800000"/></a:ln>
        <a:ln w="19050" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:miter lim="800000"/></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst><a:outerShdw blurRad="57150" dist="19050" dir="5400000" algn="ctr" rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="63000"/></a:srgbClr></a:outerShdw></a:effectLst></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"><a:tint val="95000"/><a:satMod val="170000"/></a:schemeClr></a:solidFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="93000"/><a:satMod val="150000"/><a:shade val="98000"/><a:lumMod val="102000"/></a:schemeClr></a:gs><a:gs pos="50000"><a:schemeClr val="phClr"><a:tint val="98000"/><a:satMod val="130000"/><a:shade val="90000"/><a:lumMod val="103000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:shade val="63000"/><a:satMod val="120000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>
"""

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
</Types>
"""

ROOT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>
"""


def build_theme_xml(palette: dict) -> str:
    return THEME_XML_TEMPLATE.format(**color_map(palette))


def emit_thmx() -> Path:
    palette = json.loads(PALETTE.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    theme_xml = build_theme_xml(palette)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", ROOT_RELS_XML)
        zf.writestr("theme/theme1.xml", theme_xml)
    return OUT
```

- [ ] **Step 2: Wire the theme builder into the orchestrator**

Update `scripts/_09_emit_office.py`:

```python
"""Orchestrator: emit office-theme.thmx + 4 templates + signature.htm."""
from __future__ import annotations
from pathlib import Path

from scripts.lib import office_theme

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    out = office_theme.emit_thmx()
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run and verify**

```powershell
.\.venv\Scripts\python.exe scripts\_09_emit_office.py
```

Expected: prints `Wrote .../office-theme.thmx (NNNN bytes)` with a non-trivial size (~3-5 KB).

```powershell
$bytes = [System.IO.File]::ReadAllBytes("office\office-theme.thmx")
[System.Text.Encoding]::ASCII.GetString($bytes[0..1])  # ZIP magic = "PK"
```

Expected: `PK` (ZIP magic bytes).

- [ ] **Step 4: Inspect the theme XML**

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("office\office-theme.thmx")
$entry = $zip.Entries | Where-Object { $_.FullName -eq "theme/theme1.xml" }
$reader = New-Object System.IO.StreamReader($entry.Open())
$reader.ReadToEnd() | Select-Object -First 20
$reader.Close(); $zip.Dispose()
```

Expected: XML containing all 12 color slot values including `#164999` (as `164999` in `<a:srgbClr val="164999"/>`).

- [ ] **Step 5: Commit**

```powershell
git add scripts/lib/office_theme.py scripts/_09_emit_office.py office/office-theme.thmx
git commit -m "feat(office): generate office-theme.thmx with 12-slot color + IBM Plex fonts"
```

---

## Phase 3: PowerPoint (.potx)

### Task 3: Build `deccan.potx`

**Files:**
- Implement: `scripts/lib/office_pptx.py`
- Modify: `scripts/_09_emit_office.py` to call it
- Will produce: `office/templates/deccan.potx`

`python-pptx` is the right tool. Custom slide layouts beyond the defaults require working with the slide masters directly. We start with a blank presentation, override the theme via the underlying `ppt/theme/theme1.xml`, and add layouts.

- [ ] **Step 1: Implement `scripts/lib/office_pptx.py`**

```python
"""Build deccan.potx using python-pptx (PowerPoint template with brand defaults)."""
from __future__ import annotations

import json
import zipfile
import shutil
from pathlib import Path
from io import BytesIO

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from scripts.lib.office_theme import build_theme_xml

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
LOGO = ROOT / "data" / "logo.png"
OUT = ROOT / "office" / "templates" / "deccan.potx"


def _palette() -> dict:
    return json.loads(PALETTE.read_text(encoding="utf-8"))


def emit_potx() -> Path:
    palette = _palette()
    blue_500 = palette["blue"]["500"]["hex"].lstrip("#")

    # Start from a blank presentation
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Slide 1: Title
    title_layout = prs.slide_layouts[0]  # Title slide
    slide = prs.slides.add_slide(title_layout)
    if slide.shapes.title:
        slide.shapes.title.text = "Title"
        for run in slide.shapes.title.text_frame.paragraphs[0].runs:
            run.font.name = "IBM Plex Sans"
            run.font.size = Pt(44)
            run.font.color.rgb = RGBColor.from_string(blue_500)
    if len(slide.placeholders) > 1:
        sub = slide.placeholders[1]
        sub.text = "Subtitle"
        for run in sub.text_frame.paragraphs[0].runs:
            run.font.name = "IBM Plex Sans"
            run.font.size = Pt(20)

    # Add logo to title slide (top-center, ~1.5 inch wide)
    if LOGO.exists():
        slide.shapes.add_picture(str(LOGO), Inches(0.5), Inches(0.4), width=Inches(1.8))

    # Slide 2: Section divider
    div_layout = prs.slide_layouts[2]  # Section header (or similar)
    div_slide = prs.slides.add_slide(div_layout)
    if div_slide.shapes.title:
        div_slide.shapes.title.text = "Section Title"
        for run in div_slide.shapes.title.text_frame.paragraphs[0].runs:
            run.font.name = "IBM Plex Sans"

    # Slide 3-5: Content (1-col, 2-col, 3-col) using built-in layouts where possible
    for layout_idx, layout_name in [(1, "Content"), (3, "Two Content"), (5, "Title Only")]:
        if layout_idx < len(prs.slide_layouts):
            cs = prs.slides.add_slide(prs.slide_layouts[layout_idx])
            if cs.shapes.title:
                cs.shapes.title.text = layout_name
                for run in cs.shapes.title.text_frame.paragraphs[0].runs:
                    run.font.name = "IBM Plex Sans"
                    run.font.color.rgb = RGBColor.from_string(blue_500)
            # Add small logo bottom-right
            if LOGO.exists():
                cs.shapes.add_picture(str(LOGO), Inches(11.5), Inches(6.8), width=Inches(1.2))

    # Save to temp .pptx then process
    tmp = OUT.with_suffix(".pptx")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(tmp)

    # Replace the theme XML inside the zip with our Deccan theme
    _replace_theme_in_pptx(tmp, build_theme_xml(palette))

    # Convert .pptx → .potx by changing the package's content-type and renaming
    _convert_to_potx(tmp, OUT)
    tmp.unlink()
    return OUT


def _replace_theme_in_pptx(path: Path, theme_xml: str) -> None:
    """Open the .pptx zip and replace ppt/theme/theme1.xml with our theme."""
    buf = BytesIO()
    with zipfile.ZipFile(path, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "ppt/theme/theme1.xml":
                    data = theme_xml.encode("utf-8")
                zout.writestr(item, data)
    path.write_bytes(buf.getvalue())


def _convert_to_potx(src: Path, dst: Path) -> None:
    """Convert .pptx package to .potx by updating [Content_Types].xml."""
    buf = BytesIO()
    with zipfile.ZipFile(src, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    # Change main document type from presentation to template
                    text = text.replace(
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
                        "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml",
                    )
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    dst.write_bytes(buf.getvalue())
```

- [ ] **Step 2: Wire into orchestrator**

Update `scripts/_09_emit_office.py`:

```python
from scripts.lib import office_pptx

def main() -> int:
    thmx = office_theme.emit_thmx()
    print(f"Wrote {thmx} ({thmx.stat().st_size:,} bytes)")
    potx = office_pptx.emit_potx()
    print(f"Wrote {potx} ({potx.stat().st_size:,} bytes)")
    return 0
```

- [ ] **Step 3: Run and verify**

```powershell
.\.venv\Scripts\python.exe scripts\_09_emit_office.py
$bytes = [System.IO.File]::ReadAllBytes("office\templates\deccan.potx")
[System.Text.Encoding]::ASCII.GetString($bytes[0..1])
```

Expected: `Wrote .../deccan.potx (NNNN bytes)` and ZIP magic `PK`.

- [ ] **Step 4: Verify the theme is the Deccan theme inside the .potx**

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("office\templates\deccan.potx")
$entry = $zip.Entries | Where-Object { $_.FullName -eq "ppt/theme/theme1.xml" }
$reader = New-Object System.IO.StreamReader($entry.Open())
$content = $reader.ReadToEnd()
$reader.Close(); $zip.Dispose()
$content -match '164999'  # Expect $true (Deccan blue is in there)
```

Expected: `True`.

- [ ] **Step 5: Commit**

```powershell
git add scripts/lib/office_pptx.py scripts/_09_emit_office.py office/templates/deccan.potx
git commit -m "feat(office): generate deccan.potx PowerPoint template with brand theme + logo"
```

---

## Phase 4: Word (.dotx)

### Task 4: Build `deccan.dotx`

**Files:**
- Implement: `scripts/lib/office_docx.py`
- Modify: `scripts/_09_emit_office.py` to call it
- Will produce: `office/templates/deccan.dotx`

- [ ] **Step 1: Implement `scripts/lib/office_docx.py`**

```python
"""Build deccan.dotx using python-docx (Word template with cover + styles)."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor as DocxRGB
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from scripts.lib.office_theme import build_theme_xml

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
LOGO = ROOT / "data" / "logo.png"
OUT = ROOT / "office" / "templates" / "deccan.dotx"


def _palette() -> dict:
    return json.loads(PALETTE.read_text(encoding="utf-8"))


def _set_run_brand(run, palette, size_pt=11, weight=False):
    run.font.name = "IBM Plex Sans"
    run.font.size = Pt(size_pt)
    if weight:
        run.font.bold = True


def emit_dotx() -> Path:
    palette = _palette()
    blue_500 = palette["blue"]["500"]["hex"].lstrip("#")

    doc = Document()

    # Cover page block
    if LOGO.exists():
        cover_p = doc.add_paragraph()
        cover_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        cover_run = cover_p.add_run()
        cover_run.add_picture(str(LOGO), width=Inches(2.5))

    title_p = doc.add_paragraph()
    title_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_run = title_p.add_run("Document Title")
    title_run.font.name = "IBM Plex Sans"
    title_run.font.size = Pt(36)
    title_run.font.color.rgb = DocxRGB.from_string(blue_500)
    title_run.font.bold = True

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    sub_run = sub_p.add_run("Subtitle / department / date")
    sub_run.font.name = "IBM Plex Sans"
    sub_run.font.size = Pt(14)

    doc.add_page_break()

    # Body styles examples
    h1 = doc.add_heading("Heading 1 example", level=1)
    for run in h1.runs:
        run.font.name = "IBM Plex Sans"
        run.font.color.rgb = DocxRGB.from_string(blue_500)

    h2 = doc.add_heading("Heading 2 example", level=2)
    for run in h2.runs:
        run.font.name = "IBM Plex Sans"

    p = doc.add_paragraph(
        "Body paragraph using the Deccan typography stack. IBM Plex Sans at 11pt "
        "with 1.5 line height. Use opacity (not different colors) for text "
        "hierarchy per the Deccan design system."
    )
    for run in p.runs:
        run.font.name = "IBM Plex Sans"
        run.font.size = Pt(11)

    # Footer
    footer = doc.sections[0].footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    footer_run = footer_p.add_run("Deccan Chemicals - Confidential")
    footer_run.font.name = "IBM Plex Sans"
    footer_run.font.size = Pt(9)

    # Save as .docx, replace theme + content type, rename to .dotx
    tmp = OUT.with_suffix(".docx")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(tmp)

    _replace_theme_in_docx(tmp, build_theme_xml(palette))
    _convert_to_dotx(tmp, OUT)
    tmp.unlink()
    return OUT


def _replace_theme_in_docx(path: Path, theme_xml: str) -> None:
    buf = BytesIO()
    with zipfile.ZipFile(path, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            theme_replaced = False
            for item in zin.namelist():
                data = zin.read(item)
                if item == "word/theme/theme1.xml":
                    data = theme_xml.encode("utf-8")
                    theme_replaced = True
                zout.writestr(item, data)
            if not theme_replaced:
                zout.writestr("word/theme/theme1.xml", theme_xml)
    path.write_bytes(buf.getvalue())


def _convert_to_dotx(src: Path, dst: Path) -> None:
    buf = BytesIO()
    with zipfile.ZipFile(src, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    text = text.replace(
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml",
                    )
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    dst.write_bytes(buf.getvalue())
```

- [ ] **Step 2: Wire into orchestrator**

Add to `scripts/_09_emit_office.py`:

```python
from scripts.lib import office_docx

def main() -> int:
    # ... previous emits ...
    dotx = office_docx.emit_dotx()
    print(f"Wrote {dotx} ({dotx.stat().st_size:,} bytes)")
    return 0
```

- [ ] **Step 3: Run and verify**

```powershell
.\.venv\Scripts\python.exe scripts\_09_emit_office.py
$bytes = [System.IO.File]::ReadAllBytes("office\templates\deccan.dotx")
[System.Text.Encoding]::ASCII.GetString($bytes[0..1])
```

Expected: ZIP magic `PK`, file size > 30KB (logo + content adds heft).

- [ ] **Step 4: Commit**

```powershell
git add scripts/lib/office_docx.py scripts/_09_emit_office.py office/templates/deccan.dotx
git commit -m "feat(office): generate deccan.dotx Word template with cover + styles"
```

---

## Phase 5: Excel (.xltx)

### Task 5: Build `deccan.xltx`

**Files:**
- Implement: `scripts/lib/office_xlsx.py`
- Modify: `scripts/_09_emit_office.py` to call it
- Will produce: `office/templates/deccan.xltx`

- [ ] **Step 1: Implement `scripts/lib/office_xlsx.py`**

```python
"""Build deccan.xltx using openpyxl (Excel template with table styles)."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Color, Fill, Font, PatternFill, Side

from scripts.lib.office_theme import build_theme_xml

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
OUT = ROOT / "office" / "templates" / "deccan.xltx"


def emit_xltx() -> Path:
    palette = json.loads(PALETTE.read_text(encoding="utf-8"))
    blue_500 = palette["blue"]["500"]["hex"].lstrip("#")
    blue_700 = palette["blue"]["700"]["hex"].lstrip("#")
    stone_50 = "FAFAF9"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    # Title row
    ws["A1"] = "Document Title"
    ws["A1"].font = Font(name="IBM Plex Sans", size=18, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=blue_500)
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 36
    ws.merge_cells("A1:F1")

    # Section header
    ws["A3"] = "Section Header"
    ws["A3"].font = Font(name="IBM Plex Sans", size=13, bold=True, color=blue_700)

    # Data table headers
    headers = ["Column A", "Column B", "Column C", "Column D"]
    for i, h in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=i, value=h)
        cell.font = Font(name="IBM Plex Sans", size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=blue_500)
        cell.alignment = Alignment(horizontal="left")

    # Data rows with banded fill
    for row_idx in range(6, 16):
        for col_idx in range(1, 5):
            cell = ws.cell(row=row_idx, column=col_idx, value="")
            cell.font = Font(name="IBM Plex Sans", size=10)
            if row_idx % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=stone_50)

    # Column widths
    for col_letter, width in zip("ABCDEF", [22, 18, 18, 18, 18, 18]):
        ws.column_dimensions[col_letter].width = width

    # Save as .xlsx then convert to .xltx + replace theme
    tmp = OUT.with_suffix(".xlsx")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(tmp)

    _replace_theme_in_xlsx(tmp, build_theme_xml(palette))
    _convert_to_xltx(tmp, OUT)
    tmp.unlink()
    return OUT


def _replace_theme_in_xlsx(path: Path, theme_xml: str) -> None:
    buf = BytesIO()
    with zipfile.ZipFile(path, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "xl/theme/theme1.xml":
                    data = theme_xml.encode("utf-8")
                zout.writestr(item, data)
    path.write_bytes(buf.getvalue())


def _convert_to_xltx(src: Path, dst: Path) -> None:
    buf = BytesIO()
    with zipfile.ZipFile(src, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    text = text.replace(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.template.main+xml",
                    )
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    dst.write_bytes(buf.getvalue())
```

- [ ] **Step 2: Wire into orchestrator**

Add `from scripts.lib import office_xlsx` and `xltx = office_xlsx.emit_xltx()` to `main()`.

- [ ] **Step 3: Run and verify**

```powershell
.\.venv\Scripts\python.exe scripts\_09_emit_office.py
Get-Item office\templates\deccan.xltx | Select-Object Length
```

Expected: file size > 5KB.

- [ ] **Step 4: Commit**

```powershell
git add scripts/lib/office_xlsx.py scripts/_09_emit_office.py office/templates/deccan.xltx
git commit -m "feat(office): generate deccan.xltx Excel template with brand styles"
```

---

## Phase 6: Outlook signature

### Task 6: Build `signature.htm`

**Files:**
- Implement: `scripts/lib/office_signature.py`
- Modify: `scripts/_09_emit_office.py` to call it
- Will produce: `office/templates/signature.htm`

The signature is a static HTML template — it doesn't read the palette dynamically (Outlook strips most styles), but uses inline styles matching the Deccan brand. The logo is referenced via base64 inline data URL so it travels with the email.

- [ ] **Step 1: Implement `scripts/lib/office_signature.py`**

```python
"""Build signature.htm Outlook email signature."""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
LOGO = ROOT / "data" / "logo.png"
OUT = ROOT / "office" / "templates" / "signature.htm"


def emit_signature() -> Path:
    palette = json.loads(PALETTE.read_text(encoding="utf-8"))
    blue_500 = palette["blue"]["500"]["hex"]
    text_color = "#1C1917"
    muted_color = "rgba(28, 25, 23, 0.65)"

    if LOGO.exists():
        logo_b64 = base64.b64encode(LOGO.read_bytes()).decode("ascii")
        logo_src = f"data:image/png;base64,{logo_b64}"
    else:
        logo_src = ""

    html = f"""<!doctype html>
<html><body style="margin:0;padding:0">
<table cellpadding="0" cellspacing="0" border="0" style="font-family: 'IBM Plex Sans', Helvetica, Arial, sans-serif; color:{text_color}; font-size: 13px; line-height: 1.45;">
  <tr>
    <td style="padding-bottom:8px;">
      <img src="{logo_src}" alt="Deccan Chemicals" width="160" style="display:block;border:0;outline:none;text-decoration:none">
    </td>
  </tr>
  <tr>
    <td style="padding:0 0 4px 0; font-weight:600; font-size:14px; color:{blue_500};">
      [Your Name]
    </td>
  </tr>
  <tr>
    <td style="padding:0 0 8px 0; color:{muted_color};">
      [Your Role] | [Department]
    </td>
  </tr>
  <tr>
    <td style="padding-top:6px; border-top: 1px solid #E5E5E4;">
      <span style="color:{muted_color};">M:</span> [+91 XX XXXX XXXX]
      &nbsp;|&nbsp;
      <span style="color:{muted_color};">E:</span>
      <a href="mailto:[your-email]@deccanchemicals.com" style="color:{blue_500}; text-decoration:none;">[your-email]@deccanchemicals.com</a>
    </td>
  </tr>
  <tr>
    <td style="padding-top:4px;">
      <a href="https://www.deccanchemicals.com" style="color:{blue_500}; text-decoration:none;">www.deccanchemicals.com</a>
    </td>
  </tr>
</table>
</body></html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    return OUT
```

- [ ] **Step 2: Wire into orchestrator**

Add `from scripts.lib import office_signature` and call in `main()`.

- [ ] **Step 3: Run and verify by opening the file in a browser**

```powershell
.\.venv\Scripts\python.exe scripts\_09_emit_office.py
Start-Process "office\templates\signature.htm"
```

Expected: a browser window shows a signature block with the Deccan logo, blue name placeholder, and contact info layout.

- [ ] **Step 4: Commit**

```powershell
git add scripts/lib/office_signature.py scripts/_09_emit_office.py office/templates/signature.htm
git commit -m "feat(office): generate signature.htm Outlook email signature template"
```

---

## Phase 7: Tests + idempotency

### Task 7: Write tests for the Office emitter

**Files:**
- Create: `tests/test_office_emitter.py`

- [ ] **Step 1: Implement the test file**

```python
"""Tests for scripts/_09_emit_office.py and per-format builders."""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts.lib import office_theme, office_pptx, office_docx, office_xlsx, office_signature

ROOT = Path(__file__).resolve().parents[1]
OFFICE = ROOT / "office"
TEMPLATES = OFFICE / "templates"


@pytest.fixture(scope="module", autouse=True)
def regenerate_all():
    """Re-emit all artifacts before validations."""
    office_theme.emit_thmx()
    office_pptx.emit_potx()
    office_docx.emit_dotx()
    office_xlsx.emit_xltx()
    office_signature.emit_signature()


def _is_zip(path: Path) -> bool:
    return path.read_bytes()[:2] == b"PK"


def test_thmx_exists_and_is_zip():
    p = OFFICE / "office-theme.thmx"
    assert p.exists()
    assert _is_zip(p)


def test_thmx_contains_deccan_blue():
    p = OFFICE / "office-theme.thmx"
    with zipfile.ZipFile(p) as zf:
        theme = zf.read("theme/theme1.xml").decode("utf-8")
    assert "164999" in theme
    assert "71BF4D" in theme
    assert "IBM Plex Sans" in theme


def test_potx_exists_and_is_zip():
    p = TEMPLATES / "deccan.potx"
    assert p.exists()
    assert _is_zip(p)


def test_potx_uses_deccan_theme():
    p = TEMPLATES / "deccan.potx"
    with zipfile.ZipFile(p) as zf:
        theme = zf.read("ppt/theme/theme1.xml").decode("utf-8")
    assert "164999" in theme


def test_potx_content_type_is_template():
    p = TEMPLATES / "deccan.potx"
    with zipfile.ZipFile(p) as zf:
        ct = zf.read("[Content_Types].xml").decode("utf-8")
    assert "presentationml.template.main+xml" in ct
    assert "presentationml.presentation.main+xml" not in ct


def test_dotx_exists_and_is_zip():
    p = TEMPLATES / "deccan.dotx"
    assert p.exists()
    assert _is_zip(p)


def test_dotx_uses_deccan_theme():
    p = TEMPLATES / "deccan.dotx"
    with zipfile.ZipFile(p) as zf:
        theme = zf.read("word/theme/theme1.xml").decode("utf-8")
    assert "164999" in theme


def test_dotx_content_type_is_template():
    p = TEMPLATES / "deccan.dotx"
    with zipfile.ZipFile(p) as zf:
        ct = zf.read("[Content_Types].xml").decode("utf-8")
    assert "wordprocessingml.template.main+xml" in ct


def test_xltx_exists_and_is_zip():
    p = TEMPLATES / "deccan.xltx"
    assert p.exists()
    assert _is_zip(p)


def test_xltx_uses_deccan_theme():
    p = TEMPLATES / "deccan.xltx"
    with zipfile.ZipFile(p) as zf:
        theme = zf.read("xl/theme/theme1.xml").decode("utf-8")
    assert "164999" in theme


def test_xltx_content_type_is_template():
    p = TEMPLATES / "deccan.xltx"
    with zipfile.ZipFile(p) as zf:
        ct = zf.read("[Content_Types].xml").decode("utf-8")
    assert "spreadsheetml.template.main+xml" in ct


def test_signature_html_has_logo_and_brand():
    p = TEMPLATES / "signature.htm"
    text = p.read_text(encoding="utf-8")
    assert "data:image/png;base64," in text
    assert "#164999" in text
    assert "deccanchemicals.com" in text


def test_emitter_idempotency_thmx():
    """Re-emit twice; bytes should match."""
    office_theme.emit_thmx()
    bytes1 = (OFFICE / "office-theme.thmx").read_bytes()
    office_theme.emit_thmx()
    bytes2 = (OFFICE / "office-theme.thmx").read_bytes()
    assert bytes1 == bytes2


def test_signature_idempotency():
    office_signature.emit_signature()
    text1 = (TEMPLATES / "signature.htm").read_text(encoding="utf-8")
    office_signature.emit_signature()
    text2 = (TEMPLATES / "signature.htm").read_text(encoding="utf-8")
    assert text1 == text2
```

- [ ] **Step 2: Run tests, expect PASS**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_office_emitter.py -v
```

Expected: 13 passed.

If `.dotx`/`.potx`/`.xltx` idempotency fails (it likely will because python-docx/pptx/openpyxl write timestamps into the OOXML), accept that — the bytes-level idempotency only applies to artifacts we control end-to-end (`.thmx` and `signature.htm`). Update the test list accordingly: only test bytes-level idempotency for `.thmx` and `.htm`.

- [ ] **Step 3: Commit**

```powershell
git add tests/test_office_emitter.py
git commit -m "test(office): validate emitter outputs are well-formed and brand-correct"
```

---

## Phase 8: README + tag v0.3.0

### Task 8: Write `office/README.md` and tag v0.3.0

**Files:**
- Create: `office/README.md`
- Modify: top-level `README.md`

- [ ] **Step 1: Write `office/README.md`**

```markdown
# Microsoft Office Artifacts

Generated by `scripts/_09_emit_office.py` from the Plan 1 palette + fonts.

## What's here

- `office-theme.thmx` — Office theme with Deccan colors and IBM Plex Sans typography
- `templates/deccan.dotx` — Word template (cover page, branded styles, header/footer)
- `templates/deccan.potx` — PowerPoint template (title slide, content layouts, brand colors)
- `templates/deccan.xltx` — Excel template (title row, table styles, banded data rows)
- `templates/signature.htm` — Outlook email signature (logo + IBM Plex Sans + brand colors)

## Install (per-user, manual)

The simplest install copies each artifact to the right Office directory.

### Windows PowerShell

```powershell
$Templates = "$env:APPDATA\Microsoft\Templates"
$Themes = "$env:APPDATA\Microsoft\Templates\Document Themes"

if (-not (Test-Path $Themes)) { New-Item -ItemType Directory -Path $Themes -Force | Out-Null }

$root = "C:\path\to\swiss_design_at_deccan\office"
Copy-Item "$root\office-theme.thmx" -Destination $Themes -Force
Copy-Item "$root\templates\deccan.dotx" -Destination $Templates -Force
Copy-Item "$root\templates\deccan.potx" -Destination $Templates -Force
Copy-Item "$root\templates\deccan.xltx" -Destination $Templates -Force
```

### Outlook signature

1. Open Outlook → File → Options → Mail → Signatures
2. Click `New`, name the signature `Deccan`
3. Copy the rendered output of `templates/signature.htm` into the editor (open in browser, select all, copy)
4. Set as default for new messages and replies/forwards
5. Replace the placeholder fields ([Your Name], etc.) with your details

## Fonts required

The templates reference IBM Plex Sans and IBM Plex Mono. For correct rendering,
install these fonts at the OS level. The `fonts/` directory at the project root
contains the TTF files:

```powershell
Get-ChildItem "C:\path\to\swiss_design_at_deccan\fonts" -Recurse -Filter *.ttf |
    ForEach-Object { Start-Process $_.FullName }
```

Each TTF will open the Windows font preview; click `Install`.

(Plan 5 will automate font installation via Group Policy / Intune for corporate fleets.)

## Regenerating

If the Plan 1 palette changes, re-run the emitter:

```powershell
python scripts\_09_emit_office.py
```

This regenerates all 5 artifacts in place.
```

- [ ] **Step 2: Update top-level `README.md` with Plan 3 status**

Use the Edit tool. Add a new "Plan 3 complete (v0.3.0)" section after the existing Plan 2 section, and update the Roadmap.

```markdown
**Plan 3 complete (v0.3.0)** — Microsoft Office artifacts shipped.

- `office/office-theme.thmx` — installable Office theme
- `office/templates/deccan.{dotx,potx,xltx}` — Word/PowerPoint/Excel templates
- `office/templates/signature.htm` — Outlook email signature template
- `office/README.md` — install instructions

See `office/README.md` for per-user install. Plan 5 will automate fleet deployment via Intune/GPO.
```

And update the Roadmap:

```markdown
## Roadmap

- ~~**Plan 2** — modify zeke/swiss-design-skill to consume these tokens~~ **complete (v0.2.0)**
- ~~**Plan 3** — Microsoft Office artifacts (.thmx themes, .dotx/.potx/.xltx templates)~~ **complete (v0.3.0)**
- **Plan 4** — Google Workspace artifacts (Slides/Docs templates, admin gallery)
- **Plan 5** — Enterprise deployment (Intune profiles, Group Policy, font installation)
```

- [ ] **Step 3: Commit**

```powershell
git add README.md office/README.md
git commit -m "docs: mark Plan 3 (Microsoft Office artifacts) complete"
```

- [ ] **Step 4: Tag v0.3.0 (annotated)**

```powershell
git tag -a v0.3.0 -m @'
Plan 3 release: Microsoft Office artifacts

- office-theme.thmx with 12-slot color scheme + IBM Plex Sans theme fonts
- deccan.dotx Word template with cover page, branded styles, footer
- deccan.potx PowerPoint template with title slide + content layouts + logo
- deccan.xltx Excel template with title row, table styles, banded rows
- signature.htm Outlook email signature with logo + brand colors

All templates use Deccan Blue #164999 as accent1 and IBM Plex Sans as theme font.
Per-user install documented in office/README.md.
Fleet deployment (Intune/GPO) deferred to Plan 5.

Built on Plan 1 (v0.1.0) tokens + fonts.
Next: Plan 4 (Google Workspace artifacts).
'@
git push origin main --tags
```

- [ ] **Step 5: Verify the tag is visible on the remote**

```powershell
git ls-remote --tags origin | Select-String v0.3.0
```

Expected: `refs/tags/v0.3.0` line present.

---

## Phase 9: Manual integration smoke test

### Task 9: Open each artifact in real Office

This step requires the user to perform manual verification on a Windows machine with Office installed. The implementer should not skip it — bytes-correctness doesn't equal Office-correctness.

- [ ] **Step 1: Apply the theme**

Open Word. Design tab → Themes → Browse for Themes → select `office\office-theme.thmx`. Confirm theme colors palette shows Deccan Blue, deep navy, cyan-blue, green, dark green, soft green.

- [ ] **Step 2: Open each template**

Double-click `office\templates\deccan.dotx`. Word should open a new untitled document based on the template, showing the cover page, brand title, footer.

Repeat for `deccan.potx` (PowerPoint) and `deccan.xltx` (Excel).

- [ ] **Step 3: Test the email signature**

Open `office\templates\signature.htm` in a browser. Select all, copy. Open Outlook → File → Options → Mail → Signatures → New. Paste into the editor. Save. Compose a new email; verify the signature renders with logo and brand colors.

- [ ] **Step 4: Document any issues**

If any artifact opens with errors or doesn't display brand colors / fonts correctly:
- Note the specific issue
- Check whether IBM Plex Sans is installed on the test machine (most common cause)
- If not installable issue, file a follow-up to refine the emitter

This task has no commit — it's a smoke test, not a code change. Just verify and report.

---

## Self-Review

**Spec coverage:**
- Spec §3 (tooling): Tasks 1-6 (per-format builders + orchestrator)
- Spec §4 (theme): Task 2
- Spec §5 (templates): Tasks 3, 4, 5, 6
- Spec §6 (font embedding): **Reduced scope.** Plan does NOT implement font embedding inside .dotx/.potx/.xltx as originally specified — `python-docx`/`python-pptx` don't expose this and post-processing the OOXML is genuinely complex (font subsetting, custom XML refs). The plan acknowledges this in the architecture note. Templates reference IBM Plex by name; rendering relies on OS-level font install. The `fonts/` directory in the repo root provides the TTFs; Plan 5 will deploy them. The theme `.thmx` does reference IBM Plex Sans. **This is a deviation from spec §6 that the implementer should confirm with the user is acceptable before continuing past Task 1.**
- Spec §7 (output structure): Tasks 1-8
- Spec §8 (testing): Task 7 + Task 9 (manual)
- Spec §10 (success criteria): Task 9 (manual smoke test) verifies items 1-4; idempotency tested in Task 7

**Placeholder scan:** No "TBD"/"TODO"/"add appropriate X". All code blocks are concrete. The font-embedding scope reduction is explicitly called out so the implementer (or a fresh Task 1 subagent) can flag it for user approval.

**Type consistency:** All `emit_*()` functions return `Path`. All `_palette()` helpers return `dict`. All `build_theme_xml()` calls receive `palette: dict`. Library imports consistent: `from scripts.lib.office_theme import build_theme_xml`.

---

## Decision flag for the implementer

Before starting Task 1, **flag to the user:** "Plan 3 spec said templates would embed IBM Plex fonts. Implementing this fully requires deep OOXML manipulation (font subsetting + custom embedded font XML refs) which `python-docx`/`python-pptx` don't expose. The plan reduces scope to: theme references IBM Plex by name; rendering relies on OS-level font install (handled in Plan 5 via Intune). OK to proceed with reduced scope, or do you want me to fully implement font embedding (adds ~3-5 days of OOXML hacking)?"

Wait for user input before starting Task 1.

---

## Out of scope

- True font embedding inside templates (deferred — see decision flag above; or revisit in a future plan)
- Group Policy / Intune deployment (Plan 5)
- Outlook signature auto-population from AD (Plan 5)
- Localization beyond English/Latin
