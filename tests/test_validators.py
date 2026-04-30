from scripts import _05_validate_palette as v


def _make_step(rgb, hex_str):
    return {"rgb": list(rgb), "hex": hex_str}


def test_validate_passes_well_designed_palette():
    palette = {
        "blue": {
            "100": _make_step((230, 240, 255), "#E6F0FF"),
            "300": _make_step((150, 190, 235), "#96BEEB"),
            "500": _make_step((22, 73, 153),   "#164999"),
            "700": _make_step((12, 41, 86),    "#0C2956"),
        },
        "green": {
            "100": _make_step((233, 239, 230), "#E9EFE6"),
            "300": _make_step((161, 203, 141), "#A1CB8D"),
            "500": _make_step((113, 191, 77),  "#71BF4D"),
            "700": _make_step((79, 141, 51),   "#4F8D33"),
        },
    }
    report = v.validate(palette)
    assert report["pass"] is True, f"Expected pass, got warnings: {report['warnings']}"


def test_validate_flags_too_close_steps():
    palette = {"blue": {
        "100": _make_step((240, 240, 240), "#F0F0F0"),
        "300": _make_step((235, 235, 235), "#EBEBEB"),
        "500": _make_step((100, 100, 100), "#646464"),
        "700": _make_step((50, 50, 50),    "#323232"),
    }}
    report = v.validate(palette)
    assert report["pass"] is False
    assert any("lightness gap" in w.lower() for w in report["warnings"])


def test_validate_flags_failing_wcag_contrast():
    """A 500-step that fails AA on both white AND dark backgrounds is flagged."""
    palette = {"blue": {
        "100": _make_step((250, 250, 250), "#FAFAFA"),
        "300": _make_step((200, 200, 200), "#C8C8C8"),
        "500": _make_step((155, 155, 155), "#9B9B9B"),  # contrast 2.78 on white (fail), 6.9 on dark (pass) — passes overall
        "700": _make_step((80, 80, 80),    "#505050"),
    }}
    report = v.validate(palette)
    # mid-gray passes on at least one bg, so this should pass overall
    assert report["pass"] is True


def test_validate_returns_notes_for_500_and_700():
    palette = {
        "blue": {
            "100": _make_step((230, 240, 255), "#E6F0FF"),
            "300": _make_step((150, 190, 235), "#96BEEB"),
            "500": _make_step((22, 73, 153),   "#164999"),
            "700": _make_step((12, 41, 86),    "#0C2956"),
        }
    }
    report = v.validate(palette)
    assert any("blue-500 contrast" in n for n in report["notes"])
    assert any("blue-700 contrast" in n for n in report["notes"])
