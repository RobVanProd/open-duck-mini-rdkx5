from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v12_calibrator_support_gate_launch.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v12_gate_launch", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_zero_cell_result() -> dict:
    independent = {
        "abi_exact": True,
        "all_initializers_finite": True,
        "all_chain_outputs_finite": True,
        "training_only_tensors_absent": True,
        "jax_onnx_at_most_1e_7": True,
        "previous_action_out_equals_action_bit_exact": True,
    }
    return {
        "schema_version": "winner_v12.calibrator_support_gate_cpu_contract_result.v1",
        "status": "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_FROZEN_248_CELL_SUPPORT_GATE_RUN_ONLY",
        "contract_lf_sha256": "a" * 64,
        "checks": {"all_exact": True},
        "failed_checks": [],
        "execution": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "checkpoint_graph_contracts": [
            {
                "label": label,
                "support_runner_chain_ticks": 250,
                "support_runner_all_outputs_finite": True,
                "support_runner_previous_action_chain_bit_exact": True,
                "support_runner_graph_boundary_exact": True,
                "support_runner_jax_onnx_h_max_abs_error": 0.0,
                "support_runner_jax_onnx_h_at_most_1e_7": True,
                "independent_onnx_contract": independent,
            }
            for label in ("half", "final")
        ],
        "transport_primitives": {"all_exact": True},
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": 42,
            "github_run_attempt": 1,
            "github_run_head_sha": "b" * 40,
            "github_artifact_id": 73,
            "github_artifact_name": (
                "winner-v12-calibrator-support-gate-cpu-contract-42"
            ),
            "github_artifact_digest": f"sha256:{'c' * 64}",
            "artifact_zip_sha256": "c" * 64,
            "artifact_zip_bytes": 1,
            "raw_result_sha256": "d" * 64,
            "raw_result_receipt_sha256": "e" * 64,
            "cpu_contract_path": (
                "outputs/analysis/"
                "winner_v12_calibrator_support_gate_cpu_contract.json"
            ),
            "cpu_contract_lf_sha256": "a" * 64,
            "workflow_path": (
                ".github/workflows/"
                "winner-v12-calibrator-support-gate-cpu-contract.yml"
            ),
            "workflow_lf_sha256": "f" * 64,
            "checker_lf_sha256": "1" * 64,
            "importer_lf_sha256": "2" * 64,
        },
    }


def test_exact_zero_cell_result_authorizes_only_formal_gate() -> None:
    builder = load_builder()
    builder.validate_zero_cell_result(valid_zero_cell_result(), "a" * 64)
    assert builder.EXPECTED_ZERO_EXECUTION["formal_support_cells"] == 0


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("execution", "formal_support_cells"), 1),
        (("authority", "robot_clearance"), True),
        (("checkpoint_graph_contracts", 0, "support_runner_chain_ticks"), 249),
    ],
)
def test_launch_rejects_zero_cell_authority_or_graph_drift(
    path: tuple, value: object
) -> None:
    builder = load_builder()
    result = valid_zero_cell_result()
    target = result
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        builder.validate_zero_cell_result(result, "a" * 64)


def test_launch_requires_zero_cell_repository_attribution() -> None:
    builder = load_builder()
    result = valid_zero_cell_result()
    result.pop("repository_attribution")
    with pytest.raises(ValueError, match="repository attribution"):
        builder.validate_zero_cell_result(result, "a" * 64)


def test_formal_workflow_stays_dormant_until_launch_commit() -> None:
    workflow = ROOT / ".github/workflows/winner-v12-calibrator-support-gate.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert workflow.name not in trigger
    assert "winner_v12_calibrator_support_gate_launch.json" in trigger
    assert "--formal-gate-authorized" in source
    assert "--zero-cell-contract-authorized" not in source
