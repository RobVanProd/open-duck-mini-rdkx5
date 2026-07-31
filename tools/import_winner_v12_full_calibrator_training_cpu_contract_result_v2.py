#!/usr/bin/env python3
"""Import the corrected Winner-v12 full-trainer CPU-contract result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract.json"
OUTPUT_JSON = (
    ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract_result_v2.json"
)
OUTPUT_MD = (
    ANALYSIS / "WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_RESULT_V2_20260721.md"
)
EXPECTED_RAW_SHA256 = "d0d035123122bc37462c2a6e83cb6a8bc82081f34cfdd3317fd79db3fbbc010e"
EXPECTED_CONTRACT_LF_SHA256 = (
    "6288b4f9bc1919ecb2638fe1bc1f6908f7e720f40f7721b4677c81f151cb9505"
)
EXPECTED_RUN_ID = 29808349887
EXPECTED_RUN_COMMIT = "35069ead37433e1b8d98c3082d4b163e06ec5fef"
EXPECTED_ARTIFACT_ID = 8486408542
EXPECTED_ARTIFACT_DIGEST = (
    "sha256:f02a902412abf23ef08832c3d73e3faee13f5af53cfe977bb3832c4b13fe853c"
)
HEX64_RE = re.compile(r"[0-9a-f]{64}")
EXPECTED_CHECKS = frozenset(
    {
        "cpu_only_jax",
        "fractional_terminal_mask_rejected",
        "fresh_adam_counts_zero",
        "full_population_exact",
        "full_rollout_action_boundary_exact",
        "heldout_excluded",
        "independent_normalizer_lineage_rejects_tamper",
        "independent_stage1_lineage_rejects_tamper",
        "initial_parameter_tree_exact",
        "logical_run_claim_repeat_exact",
        "malformed_realized_action_rejected",
        "nonzero_onnx_chain_passes",
        "observation_bank_nonzero_finite",
        "older_resume_rejected",
        "optimizer_updates_zero",
        "pending_recovery_exact",
        "plants_balanced",
        "playground_tree_exact",
        "sample_accounting_valid",
        "second_fresh_root_claim_rejected",
        "snapshot_archive_schema_rejects_extra",
        "snapshot_metadata_schema_rejects_extra",
        "snapshot_metric_schema_rejects_extra",
        "snapshot_self_hash_rejects_tamper",
        "snapshot_transition_order_exact",
        "software_versions_exact",
        "stage1_action_chain_exact",
        "stage1_final_checkpoint_exact",
        "stage1_fixed_p30_slot_exact",
        "stage1_full_shape",
        "stage1_mixed_type_normalization_receipt_exact",
        "stage1_normalizer_independently_recomputed_exact",
        "stage1_objective_and_gradients_finite",
        "stage1_receipts_exact",
        "stage2_full_shape",
        "stage2_objective_and_gradients_finite",
        "stage2_receipts_exact",
        "stage2_terminal_masks_exact",
        "stale_latest_repaired",
    }
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def validate_checkpoint(value: Mapping[str, Any], *, array_count: int) -> None:
    if set(value) != {"array_count", "bit_exact_readback", "bytes", "path", "sha256"}:
        raise ValueError("CPU-contract checkpoint schema changed")
    if (
        value["array_count"] != array_count
        or value["bit_exact_readback"] is not True
        or type(value["bytes"]) is not int
        or value["bytes"] <= 0
    ):
        raise ValueError("CPU-contract checkpoint proof changed")
    require_sha256(value["sha256"], "checkpoint")


def validate(raw: dict[str, Any]) -> None:
    if set(raw) != {
        "authority",
        "checks",
        "contract_lf_sha256",
        "decision",
        "environment",
        "execution",
        "failed_checks",
        "persistence_contract",
        "rollouts",
        "schema_version",
        "status",
    }:
        raise ValueError("raw corrected full-training CPU result schema changed")
    if raw["schema_version"] != (
        "winner_v12.full_calibrator_training_cpu_contract_result.v1"
    ):
        raise ValueError("raw corrected full-training CPU result version changed")
    if raw["status"] != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT":
        raise ValueError("corrected full-training CPU contract did not pass")
    if raw["decision"] != (
        "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY"
    ):
        raise ValueError("corrected full-training CPU authority changed")
    if raw["contract_lf_sha256"] != EXPECTED_CONTRACT_LF_SHA256:
        raise ValueError("raw result is not bound to the corrected contract")
    if lf_sha256(CONTRACT) != EXPECTED_CONTRACT_LF_SHA256:
        raise ValueError("repository corrected CPU contract changed")

    checks = raw["checks"]
    if not isinstance(checks, dict) or set(checks) != EXPECTED_CHECKS:
        raise ValueError("corrected CPU check schema changed")
    if not all(type(value) is bool for value in checks.values()):
        raise ValueError("corrected CPU checks must be strict JSON booleans")
    failed = sorted(name for name, passed in checks.items() if not passed)
    if raw["failed_checks"] != failed or failed:
        raise ValueError("raw corrected PASS requires every exact check to pass")

    versions = {
        "jax": "0.7.2",
        "jaxlib": "0.7.2",
        "mujoco": "3.9.0",
        "numpy": "2.0.2",
        "onnx": "1.22.0",
        "onnxruntime": "1.27.0",
        "python": "3.12.13",
    }
    if raw["environment"] != {
        "jax_devices": ["TFRT_CPU_0"],
        "software_versions": {
            "exact": True,
            "expected": versions,
            "observed": versions,
        },
    }:
        raise ValueError("formal corrected CPU environment changed")
    if raw["execution"] != {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("corrected zero-update CPU authority was exceeded")
    if raw["authority"] != {
        "formal_support_gate_executed": False,
        "full_calibrator_training_executed": False,
        "locomotion_training_or_behavior_executed": False,
        "pass_authorizes_only": "one frozen seed-120120 full calibrator training run",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("raw corrected authority block changed")

    if set(raw["rollouts"]) != {"stage1", "stage2"}:
        raise ValueError("corrected rollout schema changed")
    for stage in ("stage1", "stage2"):
        rollout = raw["rollouts"][stage]
        if set(rollout) != {
            "attempted_transition_samples",
            "environments",
            "receipt_sha256",
            "scheduled_tick_slots",
            "valid_transitions",
        }:
            raise ValueError(f"{stage} corrected rollout receipt schema changed")
        if rollout["environments"] != 80 or rollout["scheduled_tick_slots"] != 20_000:
            raise ValueError(f"{stage} corrected rollout population changed")
        if not (
            0
            < rollout["valid_transitions"]
            <= rollout["attempted_transition_samples"]
            <= rollout["scheduled_tick_slots"]
        ):
            raise ValueError(f"{stage} corrected rollout accounting changed")
        require_sha256(rollout["receipt_sha256"], f"{stage} receipt")

    persistence = raw["persistence_contract"]
    if set(persistence) != {"half", "newest_snapshot", "recovery", "stage1_final"}:
        raise ValueError("corrected persistence-contract schema changed")
    stage1 = persistence["stage1_final"]
    if set(stage1) != {"checkpoint", "label", "source_snapshot", "update"}:
        raise ValueError("corrected Stage-1 receipt schema changed")
    if stage1["label"] != "stage1_final" or stage1["update"] != 100:
        raise ValueError("corrected Stage-1 checkpoint boundary changed")
    validate_checkpoint(stage1["checkpoint"], array_count=30)
    if set(stage1["source_snapshot"]) != {"path", "sha256"}:
        raise ValueError("corrected Stage-1 source receipt schema changed")
    require_sha256(stage1["source_snapshot"]["sha256"], "Stage-1 source")
    if stage1["source_snapshot"]["sha256"] != stage1["checkpoint"]["sha256"]:
        raise ValueError("corrected Stage-1 checkpoint copy changed")

    half = persistence["half"]
    if set(half) != {
        "checkpoint",
        "graph",
        "label",
        "onnx_observation_bank",
        "source_snapshot",
        "update",
    }:
        raise ValueError("corrected Stage-2 half receipt schema changed")
    if half["label"] != "half" or half["update"] != 50:
        raise ValueError("corrected Stage-2 half boundary changed")
    validate_checkpoint(half["checkpoint"], array_count=26)
    if set(half["source_snapshot"]) != {"path", "sha256"}:
        raise ValueError("corrected Stage-2 source receipt schema changed")
    require_sha256(half["source_snapshot"]["sha256"], "Stage-2 source")
    if half["source_snapshot"]["sha256"] != half["checkpoint"]["sha256"]:
        raise ValueError("corrected Stage-2 checkpoint copy changed")

    graph = half["graph"]
    if graph["inputs"] != [
        {"name": "obs", "shape": [1, 115]},
        {"name": "previous_action", "shape": [1, 14]},
        {"name": "h_in", "shape": [1, 64]},
    ] or graph["outputs"] != [
        {"name": "calibration_actions", "shape": [1, 14]},
        {"name": "previous_action_out", "shape": [1, 14]},
        {"name": "h_out", "shape": [1, 64]},
    ]:
        raise ValueError("corrected calibrator ONNX ABI changed")
    if not all(
        (
            graph["abi_exact"],
            graph["all_chain_outputs_finite"],
            graph["all_initializers_finite"],
            graph["jax_onnx_at_most_1e_7"],
            graph["previous_action_out_equals_action_bit_exact"],
            graph["training_only_tensors_absent"],
            graph["jax_onnx_max_abs_error"] <= 1.0e-7,
            not graph["forbidden_training_or_privileged_tokens"],
        )
    ):
        raise ValueError("corrected calibrator ONNX proof changed")
    require_sha256(graph["sha256"], "corrected calibrator ONNX")
    bank = half["onnx_observation_bank"]
    if (
        bank["shape"] != [250, 115]
        or bank["all_finite"] is not True
        or bank["nonzero_values"] <= 0
    ):
        raise ValueError("corrected nonzero ONNX observation bank changed")
    require_sha256(bank["sha256"], "corrected ONNX observation bank")

    newest = persistence["newest_snapshot"]
    if set(newest) != {"path", "sha256"}:
        raise ValueError("corrected newest-snapshot receipt schema changed")
    if newest["sha256"] != half["source_snapshot"]["sha256"]:
        raise ValueError("corrected newest snapshot is not Stage-2 update 50")
    recovery = persistence["recovery"]
    if (
        set(recovery) != {"entries", "policy", "schema_version"}
        or recovery["schema_version"] != "winner_v12.full_calibrator_recovery_event.v1"
        or len(recovery["entries"]) != 4
    ):
        raise ValueError("corrected pending-artifact recovery proof changed")
    for entry in recovery["entries"]:
        if set(entry) != {
            "bytes",
            "final_target",
            "final_target_exists",
            "original_path",
            "quarantined_path",
            "sha256",
        }:
            raise ValueError("corrected recovery-entry schema changed")
        require_sha256(entry["sha256"], "corrected recovery entry")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("corrected full-training CPU result is already imported")
    raw_path = args.raw_result.resolve()
    if sha256(raw_path) != EXPECTED_RAW_SHA256:
        raise ValueError("raw corrected full-training CPU result hash changed")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    validate(raw)
    payload = dict(raw)
    payload["repository_attribution"] = {
        "github_artifact_digest": EXPECTED_ARTIFACT_DIGEST,
        "github_artifact_id": EXPECTED_ARTIFACT_ID,
        "github_run_attempt": 1,
        "github_run_commit": EXPECTED_RUN_COMMIT,
        "github_run_id": EXPECTED_RUN_ID,
        "raw_result_sha256": EXPECTED_RAW_SHA256,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 corrected full-calibrator CPU-contract result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run: `{EXPECTED_RUN_ID}` (attempt `1`)",
                f"- Commit: `{EXPECTED_RUN_COMMIT}`",
                f"- Artifact digest: `{EXPECTED_ARTIFACT_DIGEST}`",
                f"- Raw result SHA-256: `{EXPECTED_RAW_SHA256}`",
                f"- Stage-1 attempted/valid: `{payload['rollouts']['stage1']['attempted_transition_samples']}` / `{payload['rollouts']['stage1']['valid_transitions']}`",
                f"- Stage-2 attempted/valid: `{payload['rollouts']['stage2']['attempted_transition_samples']}` / `{payload['rollouts']['stage2']['valid_transitions']}`",
                "- Optimizer updates: `0`",
                "- Formal support cells: `0`",
                "- Robot access/clearance: `0` / `false`",
                "",
                "Every exact corrected zero-update check passed in the pinned CPU",
                "environment, including the mixed-type normalization proof and strict",
                "snapshot archive/metadata/metric rejection tests. This authorizes only",
                "one separately hash-bound seed-120120 full-calibrator training run.",
                "It does not authorize the 124-cell gate, locomotion training, deployment",
                "selection, Gate 5, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
