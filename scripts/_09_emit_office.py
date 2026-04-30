"""Orchestrator: emit office-theme.thmx + 4 templates + signature.htm."""
from __future__ import annotations
from pathlib import Path

from scripts.lib import office_theme, office_pptx, office_docx, office_xlsx, office_signature

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    thmx = office_theme.emit_thmx()
    print(f"Wrote {thmx} ({thmx.stat().st_size:,} bytes)")
    potx = office_pptx.emit_potx()
    print(f"Wrote {potx} ({potx.stat().st_size:,} bytes)")
    dotx = office_docx.emit_dotx()
    print(f"Wrote {dotx} ({dotx.stat().st_size:,} bytes)")
    xltx = office_xlsx.emit_xltx()
    print(f"Wrote {xltx} ({xltx.stat().st_size:,} bytes)")
    sig = office_signature.emit_signature()
    print(f"Wrote {sig} ({sig.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
