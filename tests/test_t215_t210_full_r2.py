from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t215_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t215_t210_full_r2_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t215_t210_full_r2.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T214_T210_TARGETED_Y_NEGATIVE" in builder
    assert '"maximum_cells": 320' in builder
    assert '"maximum_new_conditions_per_invocation": 1' in builder
    assert '"stop_after_first_failed_condition": True' in builder
    assert "choices=[1]" in runner
    assert "first_failed" in runner
    assert "IN_PROGRESS_T215_T210_FULL_R2" in runner
    assert "gate5_hardware_authorized" in runner


def test_t215_result_when_present() -> None:
    path = ANALYSIS / "t215_t210_full_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T215_T210_FULL_R2"
    assert value["summary"]["completed_conditions"] == 20
    assert value["summary"]["completed_cells"] == 320
    assert value["summary"]["green_cells"] == 320
    assert value["summary"]["first_failed_condition"] is None
    assert (
        value["decision"]
        == "EARN_T216_T210_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
        "PREREGISTRATION_ONLY"
    )
    assert value["authority"]["gate5_hardware_authorized"] is False
