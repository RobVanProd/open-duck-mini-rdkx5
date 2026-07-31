from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t247b_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t247b_reporting_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t247b_reporting_recovery.py"
    ).read_text(encoding="utf-8")
    assert "t247_failed_only_two_reporting_assertions" in builder
    assert "real_failed_trace_is_causally_sensitive" in builder
    assert "TARGET_OUTPUT" in runner
    assert "unique output-tuple comparison" in runner
    assert "real_failed_trace_sensitive_and_exact" in runner
    assert '"onnx_inferences": 0' in runner


def test_t247b_result_when_present() -> None:
    path = ANALYSIS / "t247b_reporting_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["onnx_inferences"] == 0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T247B_REPORTING_RECOVERY":
        assert not value["failed_checks"]
        assert all(value["checks"].values())
        assert (
            value["decision"]
            == "EARN_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"]["behavior_matrix_preregistration"]
