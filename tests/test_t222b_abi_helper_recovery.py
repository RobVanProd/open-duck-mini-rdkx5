from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t222b_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t222b_abi_helper_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t222b_abi_helper_recovery.py"
    ).read_text(encoding="utf-8")
    assert "abi_path_call_defect_exact" in builder
    assert "failure_occurs_after_graph_save_before_contract_result" in builder
    assert "partial_graph_must_match_regenerated_half_sha256" in builder
    assert "path_aware_abi" in runner
    assert "t222.abi = path_aware_abi" in runner
    assert "partial_half_graph_matches_regenerated_exactly" in runner
    assert '"behavior": False' in runner


def test_t222b_result_when_present() -> None:
    path = ANALYSIS / "t222b_abi_helper_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T222B_ABI_HELPER_RECOVERY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "RECOVER_T222_AND_EARN_T223_GLOBAL_PLATEAU_"
        "NOMINAL_MATRIX_PREREGISTRATION_ONLY"
    )
    assert (
        value["recovery_kind"]
        == "PATH_TO_MODELPROTO_ABI_HELPER_ADAPTER_ONLY"
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
