from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v12_calibrator_support_gate_cpu_contract.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v12_gate_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_identity(builder, label: str) -> dict:
    update = {"half": 50, "final": 100}[label]
    return {
        "label": label,
        "update": update,
        "checkpoint": {
            "file": f"winner_v12_calibrator_{label}.npz",
            "sha256": "1" * 64,
            "bytes": 10,
        },
        "onnx": {
            "file": f"winner_v12_calibrator_{label}.onnx",
            "sha256": "2" * 64,
            "bytes": 20,
            "inputs": builder.EXPECTED_INPUTS,
            "outputs": builder.EXPECTED_OUTPUTS,
            "abi_exact": True,
            "all_initializers_finite": True,
            "all_chain_outputs_finite": True,
            "training_only_tensors_absent": True,
            "jax_onnx_max_abs_error": 0.0,
            "jax_onnx_at_most_1e_7": True,
            "previous_action_out_equals_action_bit_exact": True,
        },
        "receipt": {
            "file": f"winner_v12_calibrator_{label}_receipt.json",
            "sha256": "3" * 64,
            "bytes": 30,
        },
    }


def valid_artifact_check(builder) -> dict:
    return {
        "schema_version": "winner_v12.full_calibrator_training_artifact_check.v1",
        "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK",
        "decision": "AUTHORIZE_FROZEN_124_CELL_CALIBRATOR_GATE_ONLY",
        "checks": {"all_exact": True},
        "failed_checks": [],
        "artifact_zip": {
            "path": "/evidence/artifact.zip",
            "sha256": "4" * 64,
            "bytes": 1000,
            "member_count": 415,
        },
        "training_result_sha256": "5" * 64,
        "verified_checkpoints": {
            label: valid_identity(builder, label) for label in ("half", "final")
        },
        "execution": {
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "artifact_verification_only": True,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "support gate",
        },
    }


def test_accepts_only_exact_green_artifact_check() -> None:
    builder = load_builder()
    builder.validate_artifact_check(valid_artifact_check(builder))


@pytest.mark.parametrize(
    ("field", "value"),
    [("status", "HOLD"), ("failed_checks", ["failed"]), ("checks", {"x": False})],
)
def test_rejects_artifact_check_that_is_not_fully_green(
    field: str, value: object
) -> None:
    builder = load_builder()
    artifact = valid_artifact_check(builder)
    artifact[field] = value
    with pytest.raises(ValueError):
        builder.validate_artifact_check(artifact)


def test_rejects_wrong_checkpoint_abi_or_boundary() -> None:
    builder = load_builder()
    artifact = valid_artifact_check(builder)
    wrong_abi = copy.deepcopy(artifact)
    wrong_abi["verified_checkpoints"]["half"]["onnx"]["inputs"][0]["shape"] = [
        1,
        101,
    ]
    with pytest.raises(ValueError, match="ONNX"):
        builder.validate_artifact_check(wrong_abi)
    wrong_boundary = copy.deepcopy(artifact)
    wrong_boundary["verified_checkpoints"]["final"]["update"] = 99
    with pytest.raises(ValueError, match="boundary"):
        builder.validate_artifact_check(wrong_boundary)


def test_bind_training_files_requires_verifier_hashes(tmp_path: Path) -> None:
    builder = load_builder()
    artifact = valid_artifact_check(builder)
    work = tmp_path / builder.EXPECTED_WORK_ROOT_NAME
    work.mkdir()
    for label in ("half", "final"):
        identity = artifact["verified_checkpoints"][label]
        for kind in ("checkpoint", "onnx", "receipt"):
            path = work / identity[kind]["file"]
            path.write_bytes(kind.encode())
            identity[kind]["sha256"] = builder.sha256(path)
            identity[kind]["bytes"] = path.stat().st_size
    bound = builder.bind_training_files(work, artifact["verified_checkpoints"])
    assert set(bound) == {"half", "final"}
    assert bound["half"]["onnx"]["sha256"] == builder.sha256(
        work / "winner_v12_calibrator_half.onnx"
    )
    (work / "winner_v12_calibrator_final.onnx").write_bytes(b"changed")
    with pytest.raises(ValueError, match="differs"):
        builder.bind_training_files(work, artifact["verified_checkpoints"])
