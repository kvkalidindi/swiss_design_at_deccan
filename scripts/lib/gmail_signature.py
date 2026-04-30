"""Gmail-optimized email signature builder.

Gmail signatures are limited to ~10 KB. Plan 3's signature (with full-resolution
logo base64-embedded) is ~13.8 KB and exceeds this. We downsample the logo to
120x40 px (visually identical at rendered size), keeping the file under budget.
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
LOGO = ROOT / "data" / "logo.png"
OUT = ROOT / "gworkspace" / "gmail-signature.htm"

# Gmail enforces ~10 KB on signatures. We target well under to leave headroom.
LOGO_WIDTH = 100
LOGO_HEIGHT = 33


def _resize_logo_to_b64() -> str:
    img = Image.open(LOGO).convert("RGBA")
    img = img.resize((LOGO_WIDTH, LOGO_HEIGHT), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def emit_gmail_signature() -> Path:
    palette = json.loads(PALETTE.read_text(encoding="utf-8"))
    blue_500 = palette["blue"]["500"]["hex"]
    text_color = "#1C1917"
    muted = "rgba(28, 25, 23, 0.65)"

    logo_b64 = _resize_logo_to_b64() if LOGO.exists() else ""
    logo_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

    html = f"""<!doctype html>
<html><body style="margin:0;padding:0">
<table cellpadding="0" cellspacing="0" border="0" style="font-family: 'IBM Plex Sans', Helvetica, Arial, sans-serif; color:{text_color}; font-size: 13px; line-height: 1.45;">
  <tr>
    <td style="padding-bottom:6px;">
      <img src="{logo_src}" alt="Deccan Chemicals" width="{LOGO_WIDTH}" height="{LOGO_HEIGHT}" style="display:block;border:0;outline:none;text-decoration:none">
    </td>
  </tr>
  <tr>
    <td style="padding:0 0 4px 0; font-weight:600; font-size:14px; color:{blue_500};">[Your Name]</td>
  </tr>
  <tr>
    <td style="padding:0 0 6px 0; color:{muted};">[Your Role] | [Department]</td>
  </tr>
  <tr>
    <td style="padding-top:6px; border-top: 1px solid #E5E5E4;">
      <span style="color:{muted};">M:</span> [+91 XX XXXX XXXX]
      &nbsp;|&nbsp;
      <span style="color:{muted};">E:</span>
      <a href="mailto:[your-email]@deccanchemicals.com" style="color:{blue_500}; text-decoration:none;">[your-email]@deccanchemicals.com</a>
    </td>
  </tr>
  <tr>
    <td style="padding-top:3px;">
      <a href="https://www.deccanchemicals.com" style="color:{blue_500}; text-decoration:none;">www.deccanchemicals.com</a>
    </td>
  </tr>
</table>
</body></html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    return OUT
