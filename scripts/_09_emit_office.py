"""Orchestrator: emit office-theme.thmx + 4 templates + signature.htm."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print("scaffold only - implementations come in subsequent tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
