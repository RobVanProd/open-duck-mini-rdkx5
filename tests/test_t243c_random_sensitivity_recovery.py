from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t243c_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t243c_random_sensitivity_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t243c_random_sensitivity_recovery.py"
    ).read_text(encoding="utf-8")
    assert "t243b_sole_failure_is_random_sensitivity" in builder
    assert "real_failed_state_population_is_fully_sensitive" in builder
    assert "all_real_failed_states_change_exactly_to_x0077" in runner
    assert '"onnx_inferences": 0' in runner
    assert '"simulator_steps": 0' in runner


def test_t243c_result_when_present() -> None:
    path = ANALYSIS / "t243c_random_sensitivity_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["onnx_inferences"] == 0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if (
        value["status"]
        == "PASS_T243C_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
    ):
        assert not value["failed_checks"]
        assert all(value["checks"].values())
        assert value["classification"]["real_failed_state_rows"] == 281
        assert (
            value["classification"]["real_failed_state_changed_rows"]
            == 281
        )
        assert (
            value["decision"]
            == "EARN_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_"
            "PREREGISTRATION_ONLY"
        )
