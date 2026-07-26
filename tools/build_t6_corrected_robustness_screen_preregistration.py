#!/usr/bin/env python3
"""Freeze the corrected-gate torso-COM robustness screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T6_CORRECTED_ROBUSTNESS_SCREEN_PREREGISTRATION_20260725.md"
)
PLAYGROUND = Path(
    r"D:\CodexProjects\Open_Duck_Playground-composed-v175"
)
ARTIFACTS = Path(r"D:\CodexArtifacts\open-duck-mini-rdkx5")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "path": str(resolved),
        "sha256": sha256(resolved),
        "bytes": resolved.stat().st_size,
    }


def candidate_pair(
    candidate_id: str,
    nominal_result: Path,
    checkpoints: list[tuple[str, Path]],
) -> dict[str, Any]:
    nominal = json.loads(nominal_result.read_text(encoding="utf-8"))
    expected = nominal["input_hashes"]["policies"]
    rows = []
    for checkpoint_id, path in checkpoints:
        digest = sha256(path)
        if digest != expected[checkpoint_id]:
            raise RuntimeError(
                f"{candidate_id} policy hash does not match nominal evidence: "
                f"{checkpoint_id}"
            )
        rows.append(
            {
                "checkpoint_id": checkpoint_id,
                "path": str(path.resolve()),
                "sha256": digest,
                "bytes": path.stat().st_size,
            }
        )
    return {
        "candidate_id": candidate_id,
        "role": "T5_REOPENED_COMPLETE_NOMINAL_PAIR",
        "nominal_result": file_record(nominal_result),
        "checkpoints": rows,
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T6 preregistration")
    repository_paths = {
        "runner": ROOT / "tools/run_t6_corrected_robustness_screen.py",
        "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
        "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
        "actuator_model": ROOT / "tools/actuator_bridge_model.py",
        "reference_features": (
            ANALYSIS / "ground_up_projected_reference_feature_table.npz"
        ),
        "fit_p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
        "fit_p31_34": (
            ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json"
        ),
        "r2_matrix": (
            ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"
        ),
        "prior_r2_condition7": (
            ANALYSIS / "winner_v10_r2_condition7_result.json"
        ),
        "t4_baseline_result": (
            ANALYSIS / "t4_baseline_all_gates_result.json"
        ),
        "t5_protection_result": (
            ANALYSIS / "t5_actuator_protection_reanalysis_result.json"
        ),
    }
    repository_inputs = {
        name: file_record(path) for name, path in repository_paths.items()
    }
    t4 = json.loads(
        repository_paths["t4_baseline_result"].read_text(encoding="utf-8")
    )
    t5 = json.loads(
        repository_paths["t5_protection_result"].read_text(encoding="utf-8")
    )
    prior = json.loads(
        repository_paths["prior_r2_condition7"].read_text(encoding="utf-8")
    )
    r2 = json.loads(
        repository_paths["r2_matrix"].read_text(encoding="utf-8")
    )
    if (
        t4["status"] != "BASELINE_FAILS_CURRENT_FEASIBILITY_GATES"
        or t5["decision"] != "REOPEN_V121_V175_CAMPAIGN_CLOSURES"
        or prior["condition"]["id"] != "TORSO_COM_X_NEG"
        or prior["status"] != "HOLD_WINNER_V10_R2_CONDITION7_TORSO_COM_X_NEG"
    ):
        raise RuntimeError("T6 causal prerequisites do not match")
    condition = r2["conditions_in_strict_order"][6]
    if condition != prior["condition"]:
        raise RuntimeError("T6 condition differs from the frozen R2 endpoint")

    candidate_pairs = [
        candidate_pair(
            "V121",
            ANALYSIS / "winner_v121_nominal_behavior_result.json",
            [
                (
                    "V121_TRAIN_MATCHED_HALF",
                    ARTIFACTS
                    / "winner-v121-deployment-policies-20260724"
                    / "V121_DEPLOYMENT_1003520.onnx",
                ),
                (
                    "V121_TRAIN_MATCHED_FINAL",
                    ARTIFACTS
                    / "winner-v121-deployment-policies-20260724"
                    / "V121_DEPLOYMENT_2007040.onnx",
                ),
            ],
        ),
        candidate_pair(
            "V123",
            ANALYSIS / "winner_v123_nominal_behavior_result.json",
            [
                (
                    "V123_EPISODE_PEAK_HALF",
                    ARTIFACTS
                    / "winner-v123-deployment-policies-20260724"
                    / "winner_v123_episode_peak_half.onnx",
                ),
                (
                    "V123_EPISODE_PEAK_FINAL",
                    ARTIFACTS
                    / "winner-v123-deployment-policies-20260724"
                    / "winner_v123_episode_peak_final.onnx",
                ),
            ],
        ),
        candidate_pair(
            "V128",
            ANALYSIS / "winner_v128_nominal_behavior_result.json",
            [
                (
                    "V128_CONSTRAINED_HALF",
                    ARTIFACTS
                    / "winner-v128-deployment-policies-20260724"
                    / "winner_v128_constrained_half.onnx",
                ),
                (
                    "V128_CONSTRAINED_FINAL",
                    ARTIFACTS
                    / "winner-v128-deployment-policies-20260724"
                    / "winner_v128_constrained_final.onnx",
                ),
            ],
        ),
        candidate_pair(
            "V177",
            ANALYSIS / "winner_v177_nominal_behavior_result.json",
            [
                (
                    "V176_TANGENT_HALF",
                    ARTIFACTS
                    / "winner-v176-deployment-policies-20260725"
                    / "winner_v176_tangent_half.onnx",
                ),
                (
                    "V176_TANGENT_FINAL",
                    ARTIFACTS
                    / "winner-v176-deployment-policies-20260725"
                    / "winner_v176_tangent_final.onnx",
                ),
            ],
        ),
    ]
    old_condition_prereg = json.loads(
        (
            ANALYSIS / "winner_v10_r2_condition7_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    required_files = list(
        old_condition_prereg["playground"]["required_file_hashes"]
    )
    observed_files = {
        relative: sha256(PLAYGROUND / relative)
        for relative in required_files
    }
    manifest_paths = {
        "base_v98": PLAYGROUND / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "constrained_v127": (
            PLAYGROUND / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "tangent_v173": (
            PLAYGROUND / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"
        ),
    }
    composition_manifests = {
        name: file_record(path) for name, path in manifest_paths.items()
    }
    base_manifest = json.loads(
        manifest_paths["base_v98"].read_text(encoding="utf-8")
    )
    if (
        base_manifest["control_commit"]
        != "b9be205ac64488c23504ca42e5ec790337adeec3"
    ):
        raise RuntimeError("T6 composed Playground has the wrong control commit")

    behavior_contract = {
        "interpretation": {
            "core": (
                "minimum physical/semantic validity; thresholds passed by the "
                "T4 baseline where comparable"
            ),
            "replacement_quality": (
                "explicit stretch goals for replacing the behaviorally bad "
                "baseline; T4 showed the baseline can fail some of these"
            ),
            "evaluator_candidate_gate_status": (
                "diagnostic only because T4 invalidated its use as an "
                "unqualified feasibility classifier"
            ),
        },
        "x0_core": {
            "samples": 600,
            "maximum_absolute_mean_local_vx_m_s": 0.02,
            "maximum_body_pitch_p95_rad": 0.25,
            "minimum_base_height_m": 0.12,
            "maximum_action_saturation_pct": 1.0,
        },
        "moving_core": {
            "samples": 600,
            "bilateral_transitions": True,
            "positive_mean_local_velocity": True,
            "minimum_track_ratio": 0.25,
            "maximum_body_pitch_p95_rad": 0.25,
            "minimum_base_height_m": 0.12,
            "maximum_action_saturation_pct": 1.0,
        },
        "x0_replacement_quality": {
            "maximum_pitch_tracking_p95_rad": 0.20,
            "maximum_rate_excess_rad_s": 0.0,
            "maximum_action_saturation_pct": 0.0,
        },
        "moving_replacement_quality": {
            "maximum_pitch_tracking_p95_rad": 0.20,
            "maximum_rate_excess_rad_s": 0.0,
            "maximum_action_saturation_pct": 0.0,
        },
    }
    protection_contract = {
        "source": "T5 manufacturer-derived duration rules",
        "motor_constant_nm_per_a": 0.784532,
        "overcurrent_threshold_a": 2.0,
        "overload_threshold_nm": 1.5298374,
        "trip_ticks": 100,
        "pass_max_consecutive_ticks": 99,
        "strict_comparison": True,
        "instantaneous_stall_current_and_torque": "diagnostic_only",
        "simulator_force_limit_abs_nm": 3.23,
        "force_limit_tolerance_nm": 5.0e-6,
        "simulator_force_limit_hits": "diagnostic_only",
    }
    matrix = {
        "candidate_pairs": 4,
        "checkpoints_per_candidate": 2,
        "fits": ["p30", "p31_34"],
        "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
        "seed": 167931544,
        "duration_ticks": 600,
        "frequency_hz": 50,
        "blocks_per_candidate": 4,
        "cells_per_candidate": 16,
        "total_blocks": 16,
        "total_cells": 64,
    }
    decision_rule = {
        "run_all_candidates": True,
        "no_early_stop_between_candidates": True,
        "survivor": (
            "all 16 cells pass core behavior, explicit replacement-quality "
            "goals, corrected duration protection, exact trace validity, and "
            "the requested dynamics readback"
        ),
        "selection_order_if_multiple_survive": [
            "lowest worst strict-overload run",
            "lowest worst strict-overcurrent run",
            "lowest worst tracking p95",
            "highest minimum moving velocity",
            "fixed candidate order",
        ],
        "fixed_tiebreak_order": ["V121", "V123", "V128", "V177"],
        "survivor_next_action": (
            "advance only the selected survivor to the complete sequential R2 "
            "revalidation; no training"
        ),
        "no_survivor_next_action": (
            "earn automatic configuration-response mechanism review and its "
            "CPU contract; do not automatically authorize hosted training"
        ),
        "selection_weight_of_partial_result": 0,
    }
    execution_contract = {
        "why_condition_selected": (
            "the pre-existing minus-0.05 m torso-COM endpoint was the first R2 "
            "failure of the previous winner after six sequential R2 passes; "
            "it is selected before observing any reopened candidate here"
        ),
        "offline_cpu_only": True,
        "one_subprocess_per_checkpoint_fit_block": True,
        "resumable_only_by_exact_block_contract_and_hashes": True,
        "early_termination_is_valid_failure_evidence": (
            "trace rows must match reported samples and remain contiguous; an "
            "early fall fails behavior but does not invalidate the evidence"
        ),
        "policy_or_model_modification": False,
        "training_steps": 0,
    }
    playground = {
        "path": str(PLAYGROUND.resolve()),
        "control_commit": base_manifest["control_commit"],
        "composition_manifests": composition_manifests,
        "required_file_sha256": observed_files,
    }
    payload = {
        "schema_version": (
            "open_duck.t6_corrected_robustness_screen_preregistration.v1"
        ),
        "status": "PREREGISTERED_T6_CORRECTED_ROBUSTNESS_SCREEN",
        "question": (
            "Does any T5-reopened frozen policy pair preserve the corrected "
            "behavior and servo-protection contract at the known torso-COM "
            "robustness discriminator?"
        ),
        "causal_basis": {
            "t4": (
                "baseline-failed gates are explicit replacement-quality goals, "
                "not generic feasibility claims"
            ),
            "t5": (
                "replace one-tick stall rejection with the documented "
                "per-joint 100-tick overcurrent and overload rules"
            ),
            "prior_r2": (
                "TORSO_COM_X_NEG was the first failure after conditions 1-6 "
                "passed"
            ),
        },
        "repository_inputs": repository_inputs,
        "candidate_pairs": candidate_pairs,
        "playground": playground,
        "condition": condition,
        "matrix": matrix,
        "behavior_contract": behavior_contract,
        "protection_contract": protection_contract,
        "decision_rule": decision_rule,
        "execution_contract": execution_contract,
        "authority": {
            "offline_cpu_behavior_screen": True,
            "hosted_compute_or_training": False,
            "robot_rdkx5_gate5_torque_motion": False,
            "policy_selected_before_result": False,
        },
    }
    basis = {
        key: payload[key]
        for key in (
            "repository_inputs",
            "candidate_pairs",
            "playground",
            "condition",
            "matrix",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "execution_contract",
        )
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(basis)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T6 corrected-gate robustness screen preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        "- Population: `V121`, `V123`, `V128`, and `V177`; both frozen "
        "checkpoints, both measured fits, four commands.\n"
        "- Frozen condition: `TORSO_COM_X_NEG`, torso COM x offset `-0.05 m`.\n"
        "- Matrix: `64` CPU-only cells in `16` resumable blocks.\n"
        "- Protection: strict `>2 A` and strict `>1.5298374 N.m`, each "
        "passing only below `100` consecutive 50 Hz ticks.\n"
        "- T4-baseline failures are explicitly replacement-quality stretch "
        "goals, not generic feasibility claims.\n"
        "- No training, hosted compute, policy selection, robot access, "
        "Gate 5, torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"CONTRACT_SHA256={payload['preregistered_contract_sha256']}")
    print(f"FILE_SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
