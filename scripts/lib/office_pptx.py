"""Build deccan.potx using python-pptx (PowerPoint template with brand defaults)."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

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

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Slide 1: Title
    title_layout = prs.slide_layouts[0]
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

    if LOGO.exists():
        slide.shapes.add_picture(str(LOGO), Inches(0.5), Inches(0.4), width=Inches(1.8))

    # Slide 2: Section divider
    if len(prs.slide_layouts) > 2:
        div_slide = prs.slides.add_slide(prs.slide_layouts[2])
        if div_slide.shapes.title:
            div_slide.shapes.title.text = "Section Title"
            for run in div_slide.shapes.title.text_frame.paragraphs[0].runs:
                run.font.name = "IBM Plex Sans"
                run.font.color.rgb = RGBColor.from_string(blue_500)

    # Slides 3-5: Content layouts (1-col, 2-col, title-only)
    for layout_idx, layout_label in [(1, "Content"), (3, "Two Content"), (5, "Title Only")]:
        if layout_idx < len(prs.slide_layouts):
            cs = prs.slides.add_slide(prs.slide_layouts[layout_idx])
            if cs.shapes.title:
                cs.shapes.title.text = layout_label
                for run in cs.shapes.title.text_frame.paragraphs[0].runs:
                    run.font.name = "IBM Plex Sans"
                    run.font.color.rgb = RGBColor.from_string(blue_500)
            if LOGO.exists():
                cs.shapes.add_picture(str(LOGO), Inches(11.5), Inches(6.8), width=Inches(1.2))

    tmp = OUT.with_suffix(".pptx")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(tmp)

    _replace_theme_in_pptx(tmp, build_theme_xml(palette))
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
                    text = text.replace(
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
                        "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml",
                    )
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    dst.write_bytes(buf.getvalue())
