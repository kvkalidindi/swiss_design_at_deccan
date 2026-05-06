import pytest
from scripts.lib import color_math as cm

@pytest.mark.parametrize("hex_in,rgb_out", [
    ("#000000", (0, 0, 0)),
    ("#FFFFFF", (255, 255, 255)),
    ("#FF0000", (255, 0, 0)),
    ("#1E5BBE", (30, 91, 190)),
])
def test_hex_to_rgb(hex_in, rgb_out):
    assert cm.hex_to_rgb(hex_in) == rgb_out

def test_rgb_to_hex_uppercase():
    assert cm.rgb_to_hex((30, 91, 190)) == "#1E5BBE"

def test_rgb_to_hsl_round_trip():
    rgb = (30, 91, 190)
    h, s, light = cm.rgb_to_hsl(rgb)
    rgb2 = cm.hsl_to_rgb((h, s, light))
    assert all(abs(a - b) <= 1 for a, b in zip(rgb, rgb2))

def test_rgb_to_cmyk_pure_red():
    c, m, y, k = cm.rgb_to_cmyk((255, 0, 0))
    assert (c, m, y, k) == (0, 100, 100, 0)

def test_rgb_to_cmyk_pure_black():
    assert cm.rgb_to_cmyk((0, 0, 0)) == (0, 0, 0, 100)

def test_contrast_ratio_black_on_white():
    # Should be 21:1
    assert cm.contrast_ratio((0, 0, 0), (255, 255, 255)) == 21.0
