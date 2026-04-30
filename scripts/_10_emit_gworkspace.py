"""Orchestrator: emit Google Workspace artifacts (currently just the Gmail signature)."""
from __future__ import annotations
from pathlib import Path

from scripts.lib import gmail_signature

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sig = gmail_signature.emit_gmail_signature()
    size = sig.stat().st_size
    print(f"Wrote {sig} ({size:,} bytes)")
    if size > 10000:
        print(f"  WARN: exceeds Gmail 10 KB signature limit")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
