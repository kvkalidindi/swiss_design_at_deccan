"""Adobe Swatch Exchange (ASE) binary writer - minimal RGB-only.

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
    swatches = list(swatches)
    blocks = [_group_open(group)]
    for name, rgb in swatches:
        blocks.append(_color_block(name, rgb))
    blocks.append(_group_close())
    n_blocks = len(blocks)
    header = b"ASEF" + struct.pack(">HH", 1, 0) + struct.pack(">I", n_blocks)
    path.write_bytes(header + b"".join(blocks))
