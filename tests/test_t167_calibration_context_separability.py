import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t167_preregistration_contract() -> None:
    path = (
        ANALYSIS
        / "t167_calibration_context_separability_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T167_CALIBRATION_CONTEXT_SEPARABILITY"
    )
    assert value["failed_checks"] == []
    assert value["population"]["cells"] == 40
    assert value["population"]["diagnostic_locomotion_ticks"] == 1
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t167_result_contract() -> None:
    path = ANALYSIS / "t167_calibration_context_separability_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T167_CALIBRATION_CONTEXT_SEPARABILITY",
        "HOLD_T167_CALIBRATION_CONTEXT_SEPARABILITY",
    }
    assert value["execution"]["calibration_prefixes"] == 40
    assert value["execution"]["diagnostic_locomotion_ticks"] == 40
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["summary"]["prior_hash_matches"] == 18
        assert value["summary"]["combined_correct"] == "40/40"
        assert value["summary"]["combined_margin"] > 0.0
