"""K-means color extraction from logo, with white/transparent filtering."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from scripts.lib.color_math import rgb_to_hex, rgb_to_hsl

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "data" / "logo.png"
OUT = ROOT / "data" / "candidates.json"
N_CLUSTERS = 12  # over-extract; we curate later in Task 4


def extract_pixels(img: Image.Image) -> np.ndarray:
    """Extract logo-relevant pixels: drop transparent, near-white, near-black."""
    img = img.convert("RGBA")
    arr = np.array(img).reshape(-1, 4)
    arr = arr[arr[:, 3] > 200]
    rgb = arr[:, :3]
    mask = ~((rgb > 240).all(axis=1) | (rgb < 20).all(axis=1))
    return rgb[mask]


def cluster_colors(pixels: np.ndarray, n: int) -> list[dict]:
    km = KMeans(n_clusters=n, n_init=10, random_state=42).fit(pixels)
    centers = km.cluster_centers_.round().astype(int)
    counts = np.bincount(km.labels_, minlength=n)
    total = counts.sum()
    out = []
    for c, n_pix in zip(centers, counts):
        rgb = (int(c[0]), int(c[1]), int(c[2]))
        h, s, light = rgb_to_hsl(rgb)
        out.append({
            "rgb": list(rgb),
            "hex": rgb_to_hex(rgb),
            "hsl": [h, s, light],
            "pixel_count": int(n_pix),
            "pixel_share": round(float(n_pix / total), 4),
        })
    return sorted(out, key=lambda x: -x["pixel_share"])


def categorize(cands: list[dict]) -> list[dict]:
    for c in cands:
        h = c["hsl"][0]
        s = c["hsl"][1]
        if s < 8:
            c["family"] = "neutral"
        elif 180 <= h <= 260:
            c["family"] = "blue"
        elif 80 <= h <= 170:
            c["family"] = "green"
        else:
            c["family"] = "other"
    return cands


def main() -> int:
    if not LOGO.exists():
        raise SystemExit(f"Missing logo: {LOGO}.")
    img = Image.open(LOGO)
    pixels = extract_pixels(img)
    print(f"Extracted {len(pixels)} non-bg/non-text pixels from logo.")
    cands = categorize(cluster_colors(pixels, N_CLUSTERS))
    OUT.write_text(json.dumps(cands, indent=2))
    print(f"\nWrote {len(cands)} candidates to {OUT}")
    print("\nTop candidates by pixel share:")
    print(f"{'#':<3} {'hex':<8} {'family':<8} {'H':>5} {'S':>5} {'L':>5} {'share':>7}")
    for i, c in enumerate(cands[:12], 1):
        h, s, light = c["hsl"]
        print(f"{i:<3} {c['hex']:<8} {c['family']:<8} {h:>5.1f} {s:>5.1f} {light:>5.1f} {c['pixel_share']:>7.2%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
