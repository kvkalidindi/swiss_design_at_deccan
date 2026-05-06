from scripts import _03_generate_palette as gen


def _real_anchors():
    """The user's actual chosen anchors (from data/anchors.json)."""
    return {
        "blue":  {"darkest": "#223D7A", "dark": "#325FAC", "anchor": "#164999", "lightest": "#0EA3DD"},
        "green": {"anchor": "#71BF4D", "alt": "#A6CF4E"},
    }


def test_blue_500_is_user_anchor():
    p = gen.build_palette(_real_anchors())
    assert p["blue"]["500"]["hex"] == "#164999"


def test_green_500_is_user_anchor():
    p = gen.build_palette(_real_anchors())
    assert p["green"]["500"]["hex"] == "#71BF4D"


def test_all_four_steps_present():
    p = gen.build_palette(_real_anchors())
    for fam in ("blue", "green"):
        for step in ("100", "300", "500", "700"):
            assert step in p[fam], f"{fam}-{step} missing"


def test_lightness_progression_strictly_monotonic():
    """100 (lightest) → 700 (darkest); each step must be strictly darker."""
    p = gen.build_palette(_real_anchors())
    for fam in ("blue", "green"):
        ls = [p[fam][k]["hsl"][2] for k in ("100", "300", "500", "700")]
        assert ls[0] > ls[1] > ls[2] > ls[3], f"{fam} not monotonic: {ls}"


def test_blue_700_has_minimum_gap_from_500():
    """Algorithmic darkening must produce ≥12% gap even when no logo color qualifies."""
    p = gen.build_palette(_real_anchors())
    l_500 = p["blue"]["500"]["hsl"][2]
    l_700 = p["blue"]["700"]["hsl"][2]
    assert l_500 - l_700 >= 12, f"blue-700 ({l_700}) only {l_500 - l_700:.1f}% darker than blue-500 ({l_500})"


def test_green_700_has_minimum_gap_from_500():
    p = gen.build_palette(_real_anchors())
    l_500 = p["green"]["500"]["hsl"][2]
    l_700 = p["green"]["700"]["hsl"][2]
    assert l_500 - l_700 >= 12, f"green-700 ({l_700}) only {l_500 - l_700:.1f}% darker than green-500 ({l_500})"


def test_green_300_has_minimum_gap_from_500():
    p = gen.build_palette(_real_anchors())
    l_500 = p["green"]["500"]["hsl"][2]
    l_300 = p["green"]["300"]["hsl"][2]
    assert l_300 - l_500 >= 12, f"green-300 ({l_300}) only {l_300 - l_500:.1f}% lighter than green-500 ({l_500})"


def test_100_is_very_light_tint():
    """blue-100 and green-100 should be tints (lightness ~88-95%)."""
    p = gen.build_palette(_real_anchors())
    for fam in ("blue", "green"):
        light = p[fam]["100"]["hsl"][2]
        assert 85 <= light <= 96, f"{fam}-100 lightness {light} outside 85-96 tint range"


def test_blue_300_uses_logo_color_when_gap_sufficient():
    """If a logo color has the required gap, use it directly (preserves brand)."""
    p = gen.build_palette(_real_anchors())
    # blue.lightest = #0EA3DD has 12% gap from blue.anchor #164999 — should be used directly
    assert p["blue"]["300"]["hex"] == "#0EA3DD"


def test_blue_700_algorithmic_when_logo_gap_insufficient():
    """When no logo color provides enough gap, algorithmic darkening of anchor."""
    p = gen.build_palette(_real_anchors())
    # No logo blue is ≥12% darker than #164999, so blue-700 ≠ any logo color
    logo_blues = {"#223D7A", "#325FAC", "#164999", "#0EA3DD"}
    assert p["blue"]["700"]["hex"] not in logo_blues, (
        f"Expected algorithmic darken; got logo color {p['blue']['700']['hex']}"
    )
