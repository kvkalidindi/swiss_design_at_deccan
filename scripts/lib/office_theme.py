"""Build office-theme.thmx (Office 2007+ theme file: ZIP with theme XML)."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "outputs" / "palette.json"
OUT = ROOT / "office" / "office-theme.thmx"


def color_map(palette: dict) -> dict[str, str]:
    """Map palette to Office's 12 theme color slots.

    Office theme has these slots: bg1, bg2, text1, text2,
    accent1-6, hlink, folHlink. Hex values returned without "#" prefix.
    """
    return {
        "bg1":      "FFFFFF",
        "bg2":      "FAFAF9",
        "text1":    "1C1917",
        "text2":    "44403C",
        "accent1":  palette["blue"]["500"]["hex"].lstrip("#"),
        "accent2":  palette["blue"]["700"]["hex"].lstrip("#"),
        "accent3":  palette["blue"]["300"]["hex"].lstrip("#"),
        "accent4":  palette["green"]["500"]["hex"].lstrip("#"),
        "accent5":  palette["green"]["700"]["hex"].lstrip("#"),
        "accent6":  palette["green"]["300"]["hex"].lstrip("#"),
        "hlink":    palette["blue"]["500"]["hex"].lstrip("#"),
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
