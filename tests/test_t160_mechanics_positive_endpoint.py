import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t160_preregistration_contract() -> None:
    path = (
        ANALYSIS
        / "t160_mechanics_positive_endpoint_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T160_MECHANICS_POSITIVE_ENDPOINT"
    )
    assert value["failed_checks"] == []
    assert value["condition"]["override"]["torso_com_offset_m"] == [
        0.05,
        0.0,
        0.0,
    ]
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True


def test_t160_result_contract() -> None:
    path = ANALYSIS / "t160_mechanics_positive_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T160_MECHANICS_POSITIVE_ENDPOINT",
        "HOLD_T160_MECHANICS_POSITIVE_ENDPOINT",
    }
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["condition"]["green_cells"] == 16
