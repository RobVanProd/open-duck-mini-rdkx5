#!/usr/bin/env python3
"""Freeze the T8 zero-training state-coherent handoff screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
JSON_OUTPUT = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
MARKDOWN_OUTPUT = (
    ANALYSIS / "T8_STATE_COHERENT_HANDOFF_PREREGISTRATION_20260726.md"
)
DEFAULT_ASSET_MANIFEST = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t8_state_coherent_handoff_assets_v2\manifest.json"
)


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


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--asset-manifest", type=Path, default=DEFAULT_ASSET_MANIFEST
    )
    args = parser.parse_args()
    if JSON_OUTPUT.exists() or MARKDOWN_OUTPUT.exists():
        raise FileExistsError("refusing to overwrite the T8 preregistration")

    t6 = json.loads(
        (
            ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    t7 = json.loads(
        (
            ANALYSIS / "t7_universal_response_support_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    t7_result = json.loads(
        (
            ANALYSIS / "t7_universal_response_support_result.json"
        ).read_text(encoding="utf-8")
    )
    t7_audit = json.loads(
        (
            ANALYSIS
            / "t7_universal_response_support_independent_audit.json"
        ).read_text(encoding="utf-8")
    )
    if (
        t7_result["status"] != "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
        or t7_result["decision"]
        != "EARN_STATE_COHERENT_SUPPORT_TO_LOCOMOTION_CPU_SCREEN"
        or t7_audit["status"]
        != "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT_INDEPENDENT_AUDIT"
        or t7_audit["issues"]
    ):
        raise RuntimeError("T7 did not earn T8")

    manifest_path = args.asset_manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_basis = {
        key: value
        for key, value in manifest.items()
        if key != "manifest_sha256"
    }
    if canonical_sha256(manifest_basis) != manifest["manifest_sha256"]:
        raise RuntimeError("T8 asset manifest canonical hash changed")
    if (
        manifest.get("source_candidate") != "V121"
        or len(manifest.get("policies") or []) != 2
        or any(
            not item["parity"]["all_outputs_bit_exact"]
            or not item["parity"]["zero_command_actions_exact_zero"]
            or set(item["parity"]["maximum_abs_errors"].values()) != {0.0}
            for item in manifest["policies"]
        )
    ):
        raise RuntimeError("T8 asset contract is not green")

    repository_inputs = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t8_state_coherent_handoff.py"
        ),
        "independent_auditor": receipt(
            ROOT / "tools" / "audit_t8_state_coherent_handoff.py"
        ),
        "worker": receipt(
            ROOT / "tools" / "evaluate_t8_state_coherent_handoff.py"
        ),
        "adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
        "asset_builder": receipt(
            ROOT / "tools" / "build_t8_state_coherent_handoff_assets.py"
        ),
        "t6_helpers": receipt(
            ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
        ),
        "closed_loop_frozen_source": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
        ),
        "actuator_model": receipt(
            ROOT / "tools" / "actuator_bridge_model.py"
        ),
        "fit_p30": receipt(
            ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
        ),
        "fit_p31_34": receipt(
            ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json"
        ),
        "reference_features": receipt(
            ANALYSIS / "ground_up_projected_reference_feature_table.npz"
        ),
        "t6_preregistration": receipt(
            ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
        ),
        "t6_result": receipt(
            ANALYSIS / "t6_corrected_robustness_screen_result.json"
        ),
        "t7_preregistration": receipt(
            ANALYSIS / "t7_universal_response_support_preregistration.json"
        ),
        "t7_result": receipt(
            ANALYSIS / "t7_universal_response_support_result.json"
        ),
        "t7_independent_audit": receipt(
            ANALYSIS / "t7_universal_response_support_independent_audit.json"
        ),
    }
    if repository_inputs["closed_loop_frozen_source"]["sha256"] != (
        "352ea320936c83801fa47f76e35faea36a68f1d7f45c11b1869292e1955f4114"
    ):
        raise RuntimeError("T8 frozen evaluator source changed")

    playground = {
        "path": t6["playground"]["path"],
        "control_commit": t6["playground"]["control_commit"],
        "required_file_sha256": t6["playground"][
            "required_file_sha256"
        ],
        "composition_manifests": t6["playground"][
            "composition_manifests"
        ],
    }
    playground_path = Path(playground["path"])
    for relative, expected in playground["required_file_sha256"].items():
        if sha256(playground_path / relative) != expected:
            raise RuntimeError(f"T8 Playground source changed: {relative}")

    calibrator = {
        key: t7["frozen_policy"][key]
        for key in ("path", "bytes", "sha256")
    }
    if calibrator["sha256"] != (
        "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576"
    ):
        raise RuntimeError("T8 universal calibrator changed")

    checkpoints = []
    for item in manifest["policies"]:
        if receipt(Path(item["source"]["path"])) != item["source"]:
            raise RuntimeError("T8 source policy receipt changed")
        if receipt(Path(item["wrapped"]["path"])) != item["wrapped"]:
            raise RuntimeError("T8 wrapped policy receipt changed")
        checkpoints.append(
            {
                "checkpoint_id": item["checkpoint_id"],
                "source": item["source"],
                "wrapped": item["wrapped"],
                "parity": item["parity"],
            }
        )
    candidate = {
        "candidate_id": "V121",
        "selection_basis": (
            "first fixed candidate in the T6 order and the intended V121-half "
            "continuation source; T5 reopened the complete nominal pair"
        ),
        "checkpoints": checkpoints,
        "context_input": {
            "name": "calibration_context",
            "shape": [1, 64],
            "T8_behavioral_use": (
                "diagnostic ABI only; wrappers are bit-exact because the "
                "context is unused until a later earned continuation contract"
            ),
        },
    }
    matrix = {
        "checkpoints": 2,
        "fits": ["p30", "p31_34"],
        "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
        "seed": 167931544,
        "frequency_hz": 50,
        "unscored_calibration_ticks": 250,
        "unscored_home_return_ticks": 0,
        "scored_duration_ticks": 600,
        "duration_ticks": 600,
        "blocks": 4,
        "cells_per_block": 4,
        "total_cells": 16,
        "dynamics_override": {
            "torso_com_offset_m": [0.0, 0.0, 0.0]
        },
    }
    handoff_contract = {
        "support_prefix": {
            "calibrator_sha256": calibrator["sha256"],
            "ticks": 250,
            "action_semantics": (
                "the preserved V91/V96 universal support action, proven by T7"
            ),
            "scored": False,
        },
        "boundary": {
            "zero_action_home_return_ticks": 0,
            "preserve_final_support_action_as_policy_previous_action": True,
            "preserve_applied_target_observer_bridge_state": True,
            "policy_hidden_state_exact_zero": True,
            "locomotion_phase_reset": [1.0, 0.0],
            "response_context_shape": [1, 64],
            "response_context_finite_and_immutable": True,
        },
        "locomotion": {
            "graph_authoritative": True,
            "maximum_host_action_delta": 0.0,
            "previous_action_and_hidden_chains_bit_exact": True,
            "full_observation_dim": 115,
            "applied_target_slot": [83, 97],
            "applied_target_slot_matches_prior_bridge_output_float32_exact": True,
            "policy_applied_target_observation": True,
            "reference_start_phase": 0,
        },
        "scope": (
            "T8 tests direct physical/state handoff feasibility only. Its V121 "
            "wrappers ignore context and perform no actor adaptation."
        ),
    }
    behavior_contract = t6["behavior_contract"]
    protection_contract = t6["protection_contract"]
    decision_rule = {
        "partial_results_selection_weight": 0,
        "pass": (
            "all 16 cells pass core gait/stationary behavior, replacement "
            "tracking/rate/saturation quality, corrected manufacturer-duration "
            "protection, exact nominal readback, and every state-handoff check"
        ),
        "pass_next_action": (
            "earn one separately preregistered CPU software contract for a "
            "response-conditioned continuation initialized at V121-half; do "
            "not authorize hosted training"
        ),
        "fail_next_action": (
            "close direct zero-training handoff of the V121 pair and analyze "
            "the transition failure before proposing any new mechanism; do "
            "not train"
        ),
        "both_checkpoints_required": True,
        "both_fits_required": True,
        "all_commands_required": True,
        "no_closest_result_promotion": True,
    }
    authority = {
        "offline_cpu_behavior_screen": True,
        "training_or_hosted_compute": False,
        "policy_or_simulator_training_modification": False,
        "robot_rdkx5_torque_motion": False,
        "gate5": False,
    }
    execution_contract = {
        "cpu_only": True,
        "one_subprocess_per_checkpoint_fit_block": True,
        "raw_logs_external_to_repository": True,
        "cache_root": (
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t8_state_coherent_handoff_v1"
        ),
        "resumable_only_by_exact_block_contract_and_hashes": True,
        "runner_refuses_overwrite": True,
        "training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    causal_basis = {
        "T7": (
            "T7 passed 12/12 and proved the actual training-time universal "
            "support action produces a stable, repeatable, COM-sensitive "
            "64-D response signal on the current composed stack."
        ),
        "historical_mismatch": (
            "the older formal evaluator used the calibrator action head and a "
            "250-tick zero-action return rather than the training wrapper's "
            "universal action; its prefix failure did not test this handoff"
        ),
        "T8_question": (
            "whether locomotion can start directly from that supported "
            "physical state when the action history, applied-target observer, "
            "phase, hidden state, and context boundary are explicit"
        ),
    }
    question = (
        "Can both frozen V121 checkpoints, under both measured actuator fits, "
        "hand off directly from the T7-proven universal support prefix into "
        "the complete nominal 600-tick command matrix without training?"
    )
    assets = {
        "manifest": receipt(manifest_path),
        "manifest_canonical_sha256": manifest["manifest_sha256"],
        "adapter_contract": manifest["adapter"],
        "execution": manifest["execution"],
    }
    basis = {
        "question": question,
        "causal_basis": causal_basis,
        "repository_inputs": repository_inputs,
        "playground": playground,
        "assets": assets,
        "calibrator": calibrator,
        "candidate": candidate,
        "matrix": matrix,
        "handoff_contract": handoff_contract,
        "behavior_contract": behavior_contract,
        "protection_contract": protection_contract,
        "decision_rule": decision_rule,
        "authority": authority,
        "execution_contract": execution_contract,
    }
    payload = {
        "schema_version": (
            "open_duck.t8_state_coherent_handoff_preregistration.v1"
        ),
        "status": "PREREGISTERED_T8_STATE_COHERENT_HANDOFF",
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    JSON_OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T8 state-coherent support-to-locomotion handoff preregistration",
        "",
        f"- Status: `{payload['status']}`",
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`",
        "- Cells: `16` (`2 checkpoints × 2 fits × 4 commands`)",
        "- Training: `0 steps`",
        "- Robot/RDK-X5 access: `forbidden`",
        "",
        "## Question",
        "",
        question,
        "",
        "## Frozen boundary",
        "",
        "Each cell runs 250 unscored universal-support ticks and then starts "
        "V121 locomotion immediately. There is no zero-action home return. "
        "The final support action becomes `previous_action`; the applied-target "
        "observer is preserved; policy hidden state starts at zero; phase resets "
        "to `[1, 0]`; and the response context is finite and immutable.",
        "",
        "The context input is intentionally unused by these bit-exact diagnostic "
        "wrappers. T8 therefore asks only whether a state-coherent physical "
        "handoff is viable before any actor continuation is considered.",
        "",
        "## Decision",
        "",
        f"- Pass: {decision_rule['pass_next_action']}.",
        f"- Fail: {decision_rule['fail_next_action']}.",
        "",
        "A pass does not authorize hosted training, robot/RDK-X5 access, "
        "Gate 5, torque, motion, deployment, or grounded replay.",
    ]
    MARKDOWN_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
