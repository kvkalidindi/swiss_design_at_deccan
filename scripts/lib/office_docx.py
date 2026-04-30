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

    tmp = OUT.with_suffix(".docx")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(tmp)

    _replace_theme_in_docx(tmp, build_theme_xml(palette))
    _convert_to_dotx(tmp, OUT)
    tmp.unlink()
    return OUT


def _replace_theme_in_docx(path: Path, theme_xml: str) -> None:
    """Replace word/theme/theme1.xml in the .docx zip with our theme."""
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
                # python-docx older versions sometimes omit the theme file;
                # add it if missing.
                zout.writestr("word/theme/theme1.xml", theme_xml)
    path.write_bytes(buf.getvalue())


def _convert_to_dotx(src: Path, dst: Path) -> None:
    """Convert .docx package to .dotx by updating [Content_Types].xml."""
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
