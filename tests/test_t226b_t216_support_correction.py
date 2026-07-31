from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t226b_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t226b_t216_support_correction_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t226b_t216_support_correction.py"
    ).read_text(encoding="utf-8")
    assert "t226_passed_but_contains_support_claim_to_supersede" in builder
    assert "t217_confirms_t98_and_eight_strata" in builder
    assert "t67_endpoint_only_family_was_closed" in builder
    assert "repeat exact-COM-only T66/T67 training" in builder
    assert "t170_replaces_predecessor_with_t98" in runner
    assert "composed_runner_wraps_t98_with_endpoint_bank" in runner
    assert "endpoint_bank_has_exact_upper_z_and_eight_categories" in runner
    assert "command_support_remains_continuous_without_atoms" in runner
    assert '"simulator_transitions": 0' in runner
    assert '"optimizer_steps": 0' in runner
    assert '"hosted_compute_units": 0' in runner


def test_t226b_result_when_present() -> None:
    path = ANALYSIS / "t226b_t216_support_correction_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T226B_T216_SUPPORT_CORRECTION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T227_COMMAND_ATOM_X_EXISTING_COM_BANK_CPU_"
        "CONTRACT_PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]
        == "LOW_COMMAND_BOUNDARY_NOT_DETERMINISTICALLY_COVERED_"
        "WITH_EXACT_UPPER_Z_STRATUM_AND_LATE_ABI_FEASIBILITY"
    )
    support = value["training_support"]
    assert support["configuration_strata"] == 8
    assert support["environments_per_configuration_stratum"] == 32
    assert support["exact_upper_z_stratum"] is True
    assert support["deterministic_command_atoms"] == 0
    assert (
        value["supersedes"]["corrected_claims"][
            "upper_z_exact_training_environments"
        ]["correct"]
        == 32
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
