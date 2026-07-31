from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from tools.import_winner_v12_zero_ppo_decomposed_backend import (
    validate_legacy_record_only,
    validate_frozen_checks,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "outputs/analysis/winner_v12_zero_ppo_decomposed_backend_preregistration.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v12_is_distinct_and_keeps_v11_closed() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PREREGISTERED_NOT_RUN"
    assert artifact["decision"] == (
        "AUTHORIZE_ONE_EXACT_WINNER_V12_DECOMPOSED_BACKEND_CPU_RUN"
    )
    assert artifact["contract_id"] == "winner-v12-decomposed-backend-r64"
    assert artifact["closed_winner_v11"] == {
        "remains_closed": True,
        "status": "HOLD_WINNER_V11_ZERO_PPO_CPU_MECHANICS",
        "result_sha256_lf": (
            "f946b79b16a6769c87ebf31e4134d1c80c83bc6071bbeb5d61ecade387895a0a"
        ),
        "rerun_or_reclassification": False,
        "old_full_protected_jax_onnx_quantity": "record only; never gating",
    }
    change = artifact["distinct_change"]
    assert change["new_branch_tolerance"] == 1.0e-7
    assert change["tolerance_changed"] is False
    assert change["protected_policy_changed"] is False
    assert change["runtime_or_deployable_abi_changed"] is False
    assert change["debug_output_is_deployable"] is False
    assert artifact["explicit_non_gate"]["still_recorded"] is True


def test_v12_preserves_protected_hashes_and_abi() -> None:
    artifact = load(ARTIFACT)
    v11 = load(
        ROOT / "outputs/analysis/winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
    )
    assert artifact["protected_policies"] == v11["protected_policies"]
    assert artifact["expected_abi"] == v11["expected_abi"]


def test_v12_population_is_zero_ppo_cpu_only() -> None:
    artifact = load(ARTIFACT)
    assert artifact["test_population"] == {
        "step_zero_cases": 66,
        "calibration_ticks": 250,
        "default_off_identity_cases_per_checkpoint": 66,
        "default_off_x0_ticks_per_checkpoint": 32,
        "physical_chain_ticks_per_checkpoint": 32,
        "default_response_cases_per_checkpoint": 66,
        "enabled_response_cases_per_checkpoint": 256,
        "enabled_full_graph_cases_per_checkpoint": 256,
        "invalid_policy_handoff_cases": 9,
        "phase_period_ticks": 27,
        "action_history_lags": [2, 3, 4],
        "applied_target_source": "exact frozen P30 forward observer",
        "new_branch_numeric_tolerance": 1.0e-7,
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
    }
    assert artifact["authority"] == {
        "one_exact_cpu_only_run": True,
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
        "training_or_ppo": False,
        "colab_hosted_gpu_or_igpu": False,
        "runtime_implementation": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "gate5_deployment_or_robot_clearance": False,
    }


def test_v12_sources_are_present_and_frozen() -> None:
    artifact = load(ARTIFACT)
    required = {
        "network_source",
        "winner_v11_network_source",
        "closed_winner_v11_result",
        "winner_v11_numeric_attribution",
        "winner_v2_observer_source",
        "winner_v2_p30_fit",
        "winner_v2_reference_table",
        "winner_v2_golden_evidence",
        "winner_v2_handoff_manifest",
    }
    assert required.issubset(artifact["sources"])
    for source in artifact["sources"].values():
        path = ROOT / source["path"]
        assert path.is_file()
        observed = (
            raw_sha256(path)
            if source["hash_mode"] == "raw sha256"
            else lf_sha256(path)
        )
        assert observed == source["sha256"]
    markdown = (
        ROOT
        / "outputs/analysis/"
        "WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_PREREGISTRATION_20260720.md"
    )
    assert lf_sha256(ARTIFACT) in markdown.read_text(encoding="utf-8")


def test_checker_checks_exactly_match_preregistration() -> None:
    checker = (
        ROOT / "tools/check_winner_v12_zero_ppo_decomposed_backend.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(checker)
    observed = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "checks"
            for target in node.targets
        ):
            observed = [ast.literal_eval(key) for key in node.value.keys]
            break
    assert observed == load(ARTIFACT)["expected_result_checks"]
    assert 'parser.add_argument("--policy-half"' in checker
    assert 'parser.add_argument("--policy-final"' in checker
    assert '"gating": False' in checker
    assert '"zero_optimizer_steps_and_behavior_cells": True' in checker


def test_debug_output_is_checker_only_and_exporter_is_delegated() -> None:
    checker = (
        ROOT / "tools/check_winner_v12_zero_ppo_decomposed_backend.py"
    ).read_text(encoding="utf-8")
    network = (
        ROOT / "patches/winner_v12_decomposed_backend_networks.py"
    ).read_text(encoding="utf-8")
    assert "model.graph.output.extend" in checker
    assert "v6_adapter_delta" in checker
    assert "base.export_locomotion_onnx(" in network
    assert "return Path(v11_path).read_bytes() == Path(v12_path).read_bytes()" in network
    assert "helper.make_tensor_value_info" not in network


def test_importer_rejects_omitted_added_and_non_boolean_checks() -> None:
    expected = load(ARTIFACT)["expected_result_checks"]
    valid = {name: True for name in expected}
    assert validate_frozen_checks(valid, expected) == []
    with pytest.raises(ValueError, match="check names"):
        validate_frozen_checks({}, expected)
    with pytest.raises(ValueError, match="check names"):
        validate_frozen_checks({**valid, "forged": True}, expected)
    missing = dict(valid)
    missing.pop(expected[0])
    with pytest.raises(ValueError, match="check names"):
        validate_frozen_checks(missing, expected)
    invalid = dict(valid)
    invalid[expected[0]] = 1
    with pytest.raises(ValueError, match="named booleans"):
        validate_frozen_checks(invalid, expected)


def test_importer_requires_both_non_gating_legacy_rows() -> None:
    rows = [
        {
            "protected_label": label,
            "max_action_error": 4.76837158203125e-7,
            "max_hidden_error": 8.940696716308594e-8,
            "gating": False,
            "reason": "closed Winner-v11 quantity; protected ONNX is authoritative",
        }
        for label in ("half", "final")
    ]
    validate_legacy_record_only(rows)
    with pytest.raises(ValueError, match="two rows"):
        validate_legacy_record_only([])
    with pytest.raises(ValueError, match="half and final"):
        validate_legacy_record_only([rows[0], rows[0]])
    changed = [dict(row) for row in rows]
    changed[0]["gating"] = True
    with pytest.raises(ValueError, match="non-gating"):
        validate_legacy_record_only(changed)
