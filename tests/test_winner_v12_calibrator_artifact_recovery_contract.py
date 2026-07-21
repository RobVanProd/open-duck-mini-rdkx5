from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_calibrator_artifact_recovery_contract.json"
)
RUNNER = ROOT / "tools/run_winner_v12_calibrator_artifact_recovery.py"
WORKFLOW = ROOT / ".github/workflows/winner-v12-calibrator-artifact-recovery.yml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_contract_is_read_only_recovery_with_zero_training_authority() -> None:
    contract = load_contract()
    assert contract["status"] == "PREREGISTERED_WINNER_V12_READ_ONLY_RECOVERY"
    assert contract["decision"] == "AUTHORIZE_ONE_READ_ONLY_RECOVERY_RUN"
    assert contract["authority"] == {
        "optimizer_updates": 0,
        "new_checkpoint_or_onnx": False,
        "full_calibrator_training": False,
        "formal_behavior_evaluation": False,
        "hosted_gpu_or_igpu": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }
    assert contract["no_retry"] is True
    assert contract["failed_smoke_cannot_be_rerun"] is True
    assert contract["pass_authorizes_only"] == (
        "a separate prospective full-calibrator training preregistration"
    )


def test_failed_artifact_identity_and_population_are_exact() -> None:
    contract = load_contract()
    failed = contract["failed_smoke"]
    assert failed["run_id"] == 29802206612
    assert failed["commit"] == "0340ee946a8783434c919fea614b88f199b38a3b"
    assert failed["checkpoint_sha256"] == (
        "5748978f050c222f156d733f709b1ddc76e2b27bebaa00ed726ad53d9fca2288"
    )
    assert failed["graph_sha256"] == (
        "9c0d018cd4d496abf9081584f969a917293ef72ecdcd6047483d6c553389aa4c"
    )
    population = contract["population"]
    assert population["environment_count"] == 16
    assert population["ticks_per_environment"] == 250
    assert population["hidden_plants"] == {
        "P30_ALL_JOINT": 8,
        "P31_34_PITCH_WITH_P30_NONPITCH": 8,
    }
    assert "COM_X_NEG" in population["configuration_ids"]
    assert not any(
        name.startswith("HELDOUT") for name in population["configuration_ids"]
    )


def test_runner_cannot_update_or_write_a_candidate() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "savez" not in source
    assert "save_restore_checkpoint(" not in source
    assert "export_calibrator_onnx(" not in source
    assert source.count("jax.value_and_grad(") == 2
    assert "smoke.stage1_rollout(" in source
    assert "smoke.stage2_rollout(" in source
    assert '"optimizer_updates": {"stage1": 0, "stage2": 0}' in source
    assert '"new_checkpoints_written": 0' in source
    assert '"new_onnx_graphs_written": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_behavior_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source


def test_runner_repairs_only_the_failed_canary_and_proves_artifact_identity() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "p30_plant.step(target, smoke.CONTROL_DT_S)" in source
    assert "p31_plant.step(target, smoke.CONTROL_DT_S)" in source
    assert '"checkpoint_hash_exact_and_unchanged"' in source
    assert '"graph_hash_exact_and_unchanged"' in source
    assert '"stage1_moments_reproduce"' in source
    assert '"stage2_moments_reproduce"' in source
    assert '"stage1_parameters_reproduce"' in source
    assert '"stage2_parameters_reproduce"' in source
    assert "smoke.onnx_contract(" in source


def test_workflow_is_reviewable_but_not_launchable_from_this_branch_yet() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in source
    assert "push:" not in source
    assert "run-id: 29802206612" in source
    assert "winner-v12-calibrator-cpu-smoke-29802206612" in source
    assert "run_winner_v12_calibrator_artifact_recovery.py" in source


def test_every_execution_source_hash_reproduces() -> None:
    contract = load_contract()
    assert all(contract["checks"].values())
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = lf_sha256(path) if item["hash_mode"] == "lf" else sha256(path)
        assert observed == item["sha256"], item["path"]
