"""Render the Office templates to PDF for visual review.

Skips templates that can't be rendered (e.g. when Office holds a lock or
the COM call hangs). Output lands in outputs/template_previews/ which is
gitignored.
"""
from __future__ import annotations

import threading
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "office" / "templates"
OUT = ROOT / "outputs" / "template_previews"
OUT.mkdir(parents=True, exist_ok=True)


def _run_with_timeout(fn, *args, timeout: float = 90.0) -> bool:
    """Run fn(*args) on a thread; return True if it finished within timeout."""
    done = {"ok": False, "err": None}

    def target():
        try:
            fn(*args)
            done["ok"] = True
        except Exception as e:  # noqa: BLE001
            done["err"] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        print(f"  TIMEOUT after {timeout}s")
        return False
    if done["err"]:
        print(f"  ERROR: {done['err']}")
        return False
    return done["ok"]


_TEMPLATE_TO_DOCUMENT = [
    # Word
    ("application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"),
    # PowerPoint
    ("application/vnd.openxmlformats-officedocument.presentationml.template.main+xml",
     "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
    # Excel
    ("application/vnd.openxmlformats-officedocument.spreadsheetml.template.main+xml",
     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"),
]


def _convert_template_to_document(src_template: Path, dst_doc: Path) -> None:
    """Rewrite [Content_Types].xml so a .dotx/.potx/.xltx becomes a .docx/.pptx/.xlsx."""
    buf = BytesIO()
    with zipfile.ZipFile(src_template, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    for tmpl, doc in _TEMPLATE_TO_DOCUMENT:
                        text = text.replace(tmpl, doc)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    dst_doc.write_bytes(buf.getvalue())


def _word_to_pdf(src: Path, dst: Path) -> None:
    import win32com.client
    tmp_docx = dst.with_suffix(".docx")
    _convert_template_to_document(src, tmp_docx)
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(tmp_docx), ReadOnly=False, AddToRecentFiles=False)
        try:
            doc.Fields.Update()
            doc.SaveAs2(str(dst), FileFormat=17)  # wdFormatPDF
        finally:
            doc.Close(SaveChanges=0)
    finally:
        word.Quit()
        tmp_docx.unlink(missing_ok=True)


def _pptx_to_pdf(src: Path, dst: Path) -> None:
    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()
    tmp_pptx = dst.with_suffix(".pptx")
    _convert_template_to_document(src, tmp_pptx)
    pp = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        pres = pp.Presentations.Open(str(tmp_pptx), ReadOnly=True, Untitled=False, WithWindow=False)
        try:
            pres.SaveAs(str(dst), 32)  # ppSaveAsPDF
        finally:
            pres.Close()
    finally:
        pp.Quit()
        tmp_pptx.unlink(missing_ok=True)


def _xlsx_to_pdf(src: Path, dst: Path) -> None:
    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()
    tmp_xlsx = dst.with_suffix(".xlsx")
    _convert_template_to_document(src, tmp_xlsx)
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(str(tmp_xlsx))
        try:
            wb.ExportAsFixedFormat(0, str(dst))  # xlTypePDF
        finally:
            wb.Close(SaveChanges=False)
    finally:
        excel.Quit()
        tmp_xlsx.unlink(missing_ok=True)


def main() -> int:
    jobs = [
        ("Word",       TEMPLATES / "deccan.dotx", OUT / "deccan_dotx_preview.pdf", _word_to_pdf),
        ("PowerPoint", TEMPLATES / "deccan.potx", OUT / "deccan_potx_preview.pdf", _pptx_to_pdf),
        ("Excel",      TEMPLATES / "deccan.xltx", OUT / "deccan_xltx_preview.pdf", _xlsx_to_pdf),
    ]
    rc = 0
    for label, src, dst, fn in jobs:
        print(f"{label}: {src.name} -> {dst.name}")
        if not src.exists():
            print(f"  SKIP: {src} missing")
            rc = 1
            continue
        dst.unlink(missing_ok=True)
        ok = _run_with_timeout(fn, src, dst, timeout=120.0)
        if ok and dst.exists():
            print(f"  OK ({dst.stat().st_size:,} bytes)")
        else:
            print("  FAILED")
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
