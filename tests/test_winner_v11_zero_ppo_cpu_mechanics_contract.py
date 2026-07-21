from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from tools.import_winner_v11_zero_ppo_cpu_mechanics import validate_frozen_checks


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "outputs/analysis/winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
RECEIPT = ROOT / "outputs/analysis/winner_v11_runtime_rereview_receipt.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_runtime_rereview_receipt_authorizes_only_zero_ppo_mechanics() -> None:
    receipt = load(RECEIPT)
    assert receipt["status"] == "PASS_WINNER_V11_LF_BINDING_HOLD_ZERO_PPO_ONLY"
    assert receipt["decision"] == (
        "AUTHORIZE_POLICY_WINNER_V11_ZERO_PPO_CPU_MECHANICS_CONTRACT_ONLY"
    )
    assert receipt["review_commit"] == (
        "b91bf86e1e0dfa4aa2ba1c6eb8755b5edbad6fe1"
    )
    assert receipt["artifact_sha256"] == (
        "6c4f05830d2f1b661bd27297a40e05da5256c701427d929cf1a480d731bfcf57"
    )
    assert receipt["authority"] == {
        "formal_behavior_cells": 0,
        "optimizer_steps": 0,
        "policy_freeze_and_run_zero_ppo_cpu_mechanics_contract": True,
        "rdkx5_robot_torque_motion_gate5_deployment": False,
        "robot_clearance": False,
        "runtime_implementation": False,
        "training_or_optimizer": False,
    }


def test_winner_v11_contract_is_frozen_on_exact_winner_v10_hashes() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PREREGISTERED_NOT_RUN"
    assert artifact["decision"] == (
        "AUTHORIZE_ONE_EXACT_WINNER_V11_ZERO_PPO_CPU_MECHANICS_RUN"
    )
    assert artifact["contract_id"] == "winner-v11-zero-ppo-mechanics-r64"
    assert artifact["protected_policies"] == {
        "half": {
            "sha256": "cf001269908d86e47eaa145ffda1d87e946a314ecf51056dc086c4cf10164ab6",
            "role": "exact Winner-v10 protected half checkpoint",
            "committed_binary": False,
        },
        "final": {
            "sha256": "d52b63241340d9d56671b95c58bb0fc72af0998fd47d4684719f6cd44f244a10",
            "role": "exact Winner-v10 protected final checkpoint",
            "committed_binary": False,
        },
    }
    assert artifact["not_a_v6_or_v6b_retry"]["both_closed_results_preserved"]
    assert artifact["not_a_v6_or_v6b_retry"]["distinct_protected_base"] == (
        "Winner-v10 inward-torque representation"
    )


def test_winner_v11_contract_preserves_exact_reviewed_abis() -> None:
    interface = load(
        ROOT / "outputs/analysis/winner_v11_dynamic_calibration_interface_preregistration.json"
    )["requested_interface"]
    artifact = load(ARTIFACT)
    assert artifact["expected_abi"] == {
        "calibrator": interface["calibrator"],
        "locomotion": interface["locomotion"],
    }


def test_winner_v11_contract_is_zero_optimizer_zero_behavior_cpu_only() -> None:
    artifact = load(ARTIFACT)
    population = artifact["test_population"]
    assert population["calibration_ticks"] == 250
    assert population["optimizer_steps"] == 0
    assert population["formal_behavior_cells"] == 0
    assert population["invalid_handoff_cases"] == 9
    assert population["invalid_handoff_scope"] == (
        "policy-side calibration context validation only"
    )
    assert population["phase_period_ticks"] == 27
    assert population["action_history_lags"] == [2, 3, 4]
    assert population["applied_target_source"] == (
        "exact frozen P30 forward observer"
    )
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


def test_winner_v11_sequence_and_action_boundary_are_explicit() -> None:
    artifact = load(ARTIFACT)
    sequence = artifact["exact_sequence"]
    assert sequence["frequency_hz"] == 50
    assert sequence["calibration_ticks"] == 250
    assert sequence["calibration_command"] == "exact float32 zeros[7]"
    assert sequence["calibration_phase"] == [1.0, 0.0]
    assert sequence["calibration_phase_advances"] is False
    assert sequence["context_session_local_immutable_nonpersistent"] is True
    assert sequence["runtime_remains_paused_after_handoff"] is True
    boundary = artifact["action_boundary"]
    assert boundary["new_graphs_use_inward_delta"] is True
    assert boundary["strict_maximum_excess"] == 0.0
    assert boundary["host_projection_or_limiter"] is False
    assert boundary["inward_torque_is_plant_xml_semantics"] is True
    assert artifact["recurrent_state_precondition"] == {
        "previous_action_shape": [1, 14],
        "previous_action_dtype": "float32",
        "previous_action_finite": True,
        "previous_action_bounds_inclusive": [-1.0, 1.0],
        "source": (
            "exact zero at reset, then the immediately preceding validated "
            "previous_action_out from the same graph"
        ),
        "out_of_range_runtime_input": "reject before inference; not graph-clamped",
    }
    assert artifact["mechanics_scope_boundary"] == {
        "policy_graph_handoff_executed": True,
        "runtime_process_persistence_executed": False,
        "runtime_paused_hold_executed": False,
        "runtime_arming_or_torque_off_executed": False,
        "physical_support_mode_defined_or_executed": False,
        "runtime_fail_closed_rules_executed": False,
    }


def test_winner_v11_sources_are_lf_stable_and_present() -> None:
    artifact = load(ARTIFACT)
    assert {
        "base_v6_checker",
        "base_v6_network_source",
        "winner_v2_observer_source",
        "winner_v2_p30_fit",
        "winner_v2_reference_table",
        "winner_v2_policy_contract",
        "winner_v2_observation_map",
    }.issubset(artifact["sources"])
    for source in artifact["sources"].values():
        path = ROOT / source["path"]
        assert path.is_file()
        if source["hash_mode"] == "raw sha256":
            assert raw_sha256(path) == source["sha256"]
        else:
            assert source["hash_mode"] == "sha256 after CRLF-to-LF normalization"
            assert lf_sha256(path) == source["sha256"]
    markdown = ROOT / "outputs/analysis/WINNER_V11_ZERO_PPO_CPU_MECHANICS_PREREGISTRATION_20260720.md"
    assert lf_sha256(ARTIFACT) in markdown.read_text(encoding="utf-8")


def test_winner_v11_checker_requires_external_exact_policy_paths() -> None:
    checker = (ROOT / "tools/check_winner_v11_zero_ppo_cpu_mechanics.py").read_text(
        encoding="utf-8"
    )
    assert 'parser.add_argument("--policy-half"' in checker
    assert 'parser.add_argument("--policy-final"' in checker
    assert '"zero_optimizer_steps_and_behavior_cells": True' in checker
    assert "MAX_ACTION_DELTA" in checker
    assert "INTERNAL_ACTION_DELTA" in checker
    tree = ast.parse(checker)
    observed_check_names = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if any(isinstance(target, ast.Name) and target.id == "checks" for target in node.targets):
            observed_check_names = [ast.literal_eval(key) for key in node.value.keys]
            break
    assert observed_check_names == load(ARTIFACT)["expected_result_checks"]


def test_winner_v11_exporter_renames_protected_consumers_and_producers() -> None:
    source = (ROOT / "patches/winner_v11_dynamic_calibration_networks.py").read_text(
        encoding="utf-8"
    )
    assert "for index, name in enumerate(node.input)" in source
    assert "for index, name in enumerate(node.output)" in source
    assert '"continuous_actions": "protected_continuous_actions"' in source
    assert "onnx.checker.check_model(protected)" in source


def test_winner_v11_importer_is_fail_closed() -> None:
    importer = (ROOT / "tools/import_winner_v11_zero_ppo_cpu_mechanics.py").read_text(
        encoding="utf-8"
    )
    for required in (
        "expected_top_level",
        "source_hashes",
        "protected_policy_hashes",
        "observed_test_population",
        "PASS requires every frozen check to be true",
        "raw result authority exceeds the mechanics-only boundary",
        '"cpu" in str(device).lower()',
    ):
        assert required in importer

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
    invalid_type = dict(valid)
    invalid_type[expected[0]] = 1
    with pytest.raises(ValueError, match="named booleans"):
        validate_frozen_checks(invalid_type, expected)
