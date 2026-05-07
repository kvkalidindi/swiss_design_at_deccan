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
      <img src="{logo_src}" alt="Deccan Fine Chemicals" width="160" style="display:block;border:0;outline:none;text-decoration:none">
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
