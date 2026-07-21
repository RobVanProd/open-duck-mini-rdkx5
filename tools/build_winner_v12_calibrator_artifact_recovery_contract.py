#!/usr/bin/env python3
"""Freeze the read-only recovery of the interrupted Winner-v12 CPU smoke."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/analysis/winner_v12_calibrator_artifact_recovery_contract.json"
MARKDOWN = (
    ROOT
    / "outputs/analysis/WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY_CONTRACT_20260721.md"
)
FAILURE = (
    ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_failure_attribution.json"
)
DOMAIN = (
    ROOT
    / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v12_calibrator_artifact_recovery.py"
WORKFLOW = ROOT / ".github/workflows/winner-v12-calibrator-artifact-recovery.yml"
SOURCE_PATHS = {
    "workflow": (
        ".github/workflows/winner-v12-calibrator-artifact-recovery.yml",
        "lf",
    ),
    "builder": (
        "tools/build_winner_v12_calibrator_artifact_recovery_contract.py",
        "lf",
    ),
    "runner": ("tools/run_winner_v12_calibrator_artifact_recovery.py", "lf"),
    "tests": (
        "tests/test_winner_v12_calibrator_artifact_recovery_contract.py",
        "lf",
    ),
    "failed_smoke_attribution": (
        "outputs/analysis/winner_v12_calibrator_cpu_smoke_failure_attribution.json",
        "lf",
    ),
    "failed_smoke_contract": (
        "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json",
        "lf",
    ),
    "smoke_runner": ("tools/run_winner_v12_calibrator_cpu_smoke.py", "lf"),
    "training_primitives": ("patches/winner_v12_calibrator_training.py", "lf"),
    "decomposed_network": (
        "patches/winner_v12_decomposed_backend_networks.py",
        "lf",
    ),
    "winner_v11_network": (
        "patches/winner_v11_dynamic_calibration_networks.py",
        "lf",
    ),
    "winner_v6_network": (
        "patches/winner_v6_dynamic_calibration_networks.py",
        "lf",
    ),
    "calibrator_preregistration": (
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json",
        "lf",
    ),
    "domain_preregistration": (
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json",
        "lf",
    ),
    "p30_fit": (
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
        "lf",
    ),
    "p31_34_fit": (
        "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
        "lf",
    ),
    "runtime_observer": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py",
        "lf",
    ),
    "runtime_observer_contract": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer_contract.json",
        "lf",
    ),
    "reference_table": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/reference/ground_up_projected_reference_feature_table.npz",
        "raw",
    ),
    "playground_composer": ("tools/compose_winner_v7_playground.py", "lf"),
    "actuator_bridge": ("tools/actuator_bridge_model.py", "lf"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def source_manifest() -> dict[str, dict[str, str]]:
    manifest = {}
    for name, (relative, mode) in SOURCE_PATHS.items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        manifest[name] = {
            "path": relative,
            "hash_mode": mode,
            "sha256": lf_sha256(path) if mode == "lf" else sha256(path),
        }
    return manifest


def main() -> int:
    failure = json.loads(FAILURE.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    runner_source = RUNNER.read_text(encoding="utf-8")
    workflow_source = WORKFLOW.read_text(encoding="utf-8")
    population = domain["evaluation_matrix"]["fixed_anchors"][:16]
    checks = {
        "failed_smoke_exact": failure.get("status")
        == "HOLD_WINNER_V12_CALIBRATOR_CPU_SMOKE_NO_RESULT"
        and failure["github"]["run_id"] == 29802206612
        and failure["github"]["commit"] == "0340ee946a8783434c919fea614b88f199b38a3b",
        "recovered_artifacts_exact": failure["artifact"]["files"][
            "winner_v12_calibrator_smoke_checkpoint.npz"
        ]["sha256"]
        == "5748978f050c222f156d733f709b1ddc76e2b27bebaa00ed726ad53d9fca2288"
        and failure["artifact"]["files"]["winner_v12_calibrator_after_smoke.onnx"][
            "sha256"
        ]
        == "9c0d018cd4d496abf9081584f969a917293ef72ecdcd6047483d6c553389aa4c",
        "failed_checkpoint_counts_exact": failure["checkpoint_readback"][
            "stage1_adam_count"
        ]
        == 1
        and failure["checkpoint_readback"]["stage2_adam_count"] == 1,
        "runner_has_no_optimizer_update": "adam_step(" not in runner_source,
        "runner_writes_no_checkpoint_or_graph": "savez" not in runner_source
        and "save_restore_checkpoint(" not in runner_source
        and "export_calibrator_onnx(" not in runner_source,
        "runner_reconstructs_both_rollouts": "smoke.stage1_rollout(" in runner_source
        and "smoke.stage2_rollout(" in runner_source,
        "runner_reconstructs_gradients_only": runner_source.count("jax.value_and_grad(")
        == 2,
        "runner_checks_stored_moments_and_parameters": "expected_moments("
        in runner_source
        and "parameters_from_moments(" in runner_source
        and '"stage1_moments_reproduce"' in runner_source
        and '"stage2_moments_reproduce"' in runner_source,
        "runner_fixes_only_canary_signature": "p30_plant.step(target, smoke.CONTROL_DT_S)"
        in runner_source
        and "p31_plant.step(target, smoke.CONTROL_DT_S)" in runner_source,
        "runner_protects_artifact_hashes": '"checkpoint_hash_exact_and_unchanged"'
        in runner_source
        and '"graph_hash_exact_and_unchanged"' in runner_source,
        "runner_has_zero_authority": '"optimizer_updates": {"stage1": 0, "stage2": 0}'
        in runner_source
        and '"new_checkpoints_written": 0' in runner_source
        and '"locomotion_behavior_cells": 0' in runner_source
        and '"robot_or_rdk_access": 0' in runner_source,
        "workflow_is_one_shot_branch_path_launch": "push:" in workflow_source
        and "codex/winner-v4-response-contract" in workflow_source
        and ".github/workflows/winner-v12-calibrator-artifact-recovery.yml"
        in workflow_source
        and "workflow_dispatch:" not in workflow_source
        and "run-id: 29802206612" in workflow_source
        and "winner-v12-calibrator-cpu-smoke-29802206612" in workflow_source,
        "population_exact": len(population) == 16
        and [row["id"] for row in population]
        == [
            "MASS_LOW",
            "MASS_HIGH",
            "COM_X_NEG",
            "COM_X_POS",
            "COM_Y_NEG",
            "COM_Y_POS",
            "COM_Z_NEG",
            "COM_Z_POS",
            "INERTIA_X_LOW",
            "INERTIA_X_HIGH",
            "INERTIA_Y_LOW",
            "INERTIA_Y_HIGH",
            "INERTIA_Z_LOW",
            "INERTIA_Z_HIGH",
            "COM_CORNER_00",
            "COM_CORNER_01",
        ],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"artifact recovery contract checks failed: {failed}")
    payload = {
        "schema_version": "winner_v12.calibrator_artifact_recovery_contract.v1",
        "status": "PREREGISTERED_WINNER_V12_READ_ONLY_RECOVERY",
        "decision": "AUTHORIZE_ONE_READ_ONLY_RECOVERY_RUN",
        "causal_scope": (
            "recover the interrupted smoke evidence from the immutable checkpoint "
            "and ONNX; reconstruct deterministic rollouts and gradients only to "
            "compare stored Adam moments/parameters; create no new candidate"
        ),
        "failed_smoke": {
            "run_id": 29802206612,
            "commit": "0340ee946a8783434c919fea614b88f199b38a3b",
            "checkpoint_sha256": "5748978f050c222f156d733f709b1ddc76e2b27bebaa00ed726ad53d9fca2288",
            "graph_sha256": "9c0d018cd4d496abf9081584f969a917293ef72ecdcd6047483d6c553389aa4c",
            "artifact_archive_digest": "sha256:02a2468f22ce5a94e8b552c20c40e42effa1e7cbd637fc516a5b6965dbcd6910",
        },
        "population": {
            "configuration_ids": [row["id"] for row in population],
            "population_sha256": canonical_sha256(population),
            "environment_count": 16,
            "ticks_per_environment": 250,
            "hidden_plants": {
                "P30_ALL_JOINT": 8,
                "P31_34_PITCH_WITH_P30_NONPITCH": 8,
            },
        },
        "required_proofs": [
            "recovered checkpoint and ONNX hashes stay unchanged before/after",
            "checkpoint schema, 40 finite arrays, repeat-load identity, and both Adam counts equal one",
            "deterministically reconstructed Stage-1 normalization, gradients, Adam moments, and checkpoint parameters match",
            "deterministically reconstructed Stage-2 rollout, gradients, Adam moments, and checkpoint parameters match",
            "corrected fixed-P30-observer versus hidden-plant canary passes with explicit 0.02 s dt",
            "all original action/history/support/current/force-range and ONNX-chain checks pass",
            "no protected-policy inference, formal behavior cell, robot access, optimizer update, checkpoint write, or graph write occurs",
        ],
        "software_versions": {
            "python": "3.12.13",
            "jax": "0.7.2",
            "jaxlib": "0.7.2",
            "mujoco": "3.9.0",
            "onnx": "1.22.0",
            "onnxruntime": "1.27.0",
            "numpy": "2.0.2",
        },
        "checks": checks,
        "sources": source_manifest(),
        "authority": {
            "optimizer_updates": 0,
            "new_checkpoint_or_onnx": False,
            "full_calibrator_training": False,
            "formal_behavior_evaluation": False,
            "hosted_gpu_or_igpu": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "robot_clearance": False,
        },
        "pass_authorizes_only": (
            "a separate prospective full-calibrator training preregistration"
        ),
        "failed_smoke_cannot_be_rerun": True,
        "no_retry": True,
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator artifact-recovery contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Failed smoke: `29802206612`",
                "- New optimizer updates: `0`",
                "- New checkpoint/ONNX: `false`",
                "- Formal behavior cells: `0`",
                "- Robot clearance: `false`",
                "",
                "This verifier may only recover evidence for the immutable failed-smoke",
                "artifacts. It cannot rerun training, create a replacement candidate,",
                "evaluate locomotion behavior, or access the robot.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(OUTPUT),
                "output_sha256": sha256(OUTPUT),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
