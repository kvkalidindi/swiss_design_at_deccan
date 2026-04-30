"""Build deccan.xltx using openpyxl (Excel template with table styles)."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

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
            theme_replaced = False
            for item in zin.namelist():
                data = zin.read(item)
                if item == "xl/theme/theme1.xml":
                    data = theme_xml.encode("utf-8")
                    theme_replaced = True
                zout.writestr(item, data)
            if not theme_replaced:
                zout.writestr("xl/theme/theme1.xml", theme_xml)
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
