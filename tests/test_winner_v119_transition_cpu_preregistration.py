import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v119_cpu_smoke_is_preregistered_without_training() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v119_transition_cpu_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V119_TRANSITION_CPU_SMOKE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    transition = value["transition"]
    assert transition["default_enabled"] is False
    assert transition["actual_centered_guard_margin_rad"] == 0.165
    assert transition["applied_target_observation"]
    assert transition["x0_deadband_training_support"] is False
    assert transition["x0_deadband_postexport"]
    assert value["objectives"]["new_reward_term"] is False
    assert value["objectives"]["reward_selection"] is False
    assert value["cpu_smoke"]["timesteps"] == 1024
    assert value["cpu_smoke"]["required_exports"] == [0, 1024]
    assert value["authority"]["cpu_smoke_authorized"]
    assert value["authority"]["hosted_training_authorized"] is False
    assert value["authority"]["colab_authorized"] is False
