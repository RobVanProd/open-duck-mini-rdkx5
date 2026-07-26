from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
V4_RUNNER = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v4/"
    "playground/open_duck_mini_v2/runner.py"
)


def test_t19_rate_selector_precedes_inherited_v119_selector() -> None:
    text = V4_RUNNER.read_text(encoding="utf-8")
    t19 = text.index("if args.winner_t19_support_trainthrough:")
    v119 = text.index(
        "if args.winner_v119_train_transition_match",
        t19,
    )
    validator = text.index(
        "winner-v3 selected all-joint velocity vector changed",
        t19,
    )
    assert t19 < v119 < validator
    assert "expected_limits = jp.asarray(" in text[t19:validator]
    assert "RATE_LIMITS_RAD_S, dtype=jp.float32" in text[t19:validator]


def test_rate_selector_correction_is_default_off_for_other_routes() -> None:
    text = PATCH.read_text(encoding="utf-8")
    assert "if args.winner_t19_support_trainthrough:" in text
    assert "else:" in text
    assert "joystick.WINNER_V119_RATE_LIMITS_RAD_S" in text
    assert "winner_v3.CONSERVATIVE_VELOCITY_LIMITS_RAD_S" in text
