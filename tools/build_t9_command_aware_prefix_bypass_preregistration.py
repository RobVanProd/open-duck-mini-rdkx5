#!/usr/bin/env python3
"""Freeze the T9 command-aware x=0 response-prefix bypass screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
JSON_OUTPUT = ANALYSIS / "t9_command_aware_prefix_bypass_preregistration.json"
MARKDOWN_OUTPUT = (
    ANALYSIS / "T9_COMMAND_AWARE_PREFIX_BYPASS_PREREGISTRATION_20260726.md"
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
    if JSON_OUTPUT.exists() or MARKDOWN_OUTPUT.exists():
        raise FileExistsError("refusing to overwrite the T9 preregistration")
    t8_prereg = json.loads(
        (
            ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    t8_result = json.loads(
        (
            ANALYSIS / "t8_state_coherent_handoff_result.json"
        ).read_text(encoding="utf-8")
    )
    t8_audit = json.loads(
        (
            ANALYSIS / "t8_state_coherent_handoff_independent_audit_v2.json"
        ).read_text(encoding="utf-8")
    )
    failure = json.loads(
        (
            ANALYSIS / "t8_state_coherent_handoff_failure_analysis.json"
        ).read_text(encoding="utf-8")
    )
    if (
        t8_result["status"] != "HOLD_T8_STATE_COHERENT_HANDOFF"
        or t8_result["passing_cells"] != 12
        or t8_audit["status"]
        != "PASS_T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT"
        or t8_audit["issues"]
        or failure["status"]
        != "T8_FAILURE_LOCALIZED_X0_PREFIX_TRANSITION"
        or not all(failure["checks"].values())
        or failure["selected_next_falsifier"]["mechanism"]
        != "COMMAND_AWARE_X0_CALIBRATION_PREFIX_BYPASS"
    ):
        raise RuntimeError("T8 did not earn the exact T9 mechanism")

    repository_inputs = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t9_command_aware_prefix_bypass.py"
        ),
        "worker": receipt(
            ROOT / "tools" / "evaluate_t9_x0_prefix_bypass.py"
        ),
        "independent_auditor": receipt(
            ROOT / "tools" / "audit_t9_command_aware_prefix_bypass.py"
        ),
        "adapter": receipt(
            ROOT / "tools" / "t9_command_aware_eval_adapter.py"
        ),
        "t8_adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
        "t6_helpers": receipt(
            ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
        ),
        "closed_loop_frozen_source": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
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
        "t8_preregistration": receipt(
            ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
        ),
        "t8_result": receipt(
            ANALYSIS / "t8_state_coherent_handoff_result.json"
        ),
        "t8_independent_audit": receipt(
            ANALYSIS / "t8_state_coherent_handoff_independent_audit_v2.json"
        ),
        "t8_failure_analysis": receipt(
            ANALYSIS / "t8_state_coherent_handoff_failure_analysis.json"
        ),
        "t8_asset_manifest": receipt(
            Path(t8_prereg["assets"]["manifest"]["path"])
        ),
    }
    playground = t8_prereg["playground"]
    playground_root = Path(playground["path"])
    for relative, expected in playground["required_file_sha256"].items():
        if sha256(playground_root / relative) != expected:
            raise RuntimeError(f"T9 Playground source changed: {relative}")
    candidate = {
        "candidate_id": "V121",
        "checkpoints": [
            {
                "checkpoint_id": item["checkpoint_id"],
                "source": item["source"],
                "wrapped": item["wrapped"],
                "parity": item["parity"],
            }
            for item in t8_prereg["candidate"]["checkpoints"]
        ],
        "selection_basis": (
            "identical V121 pair and context-ABI wrappers used in T8; no "
            "policy weights or graph behavior change"
        ),
    }
    matrix = {
        "new_command_x_m_s": 0.0,
        "checkpoints": 2,
        "fits": ["p30", "p31_34"],
        "seed": 167931544,
        "frequency_hz": 50,
        "duration_ticks": 600,
        "new_cells": 4,
        "reused_t8_moving_cells": 12,
        "combined_cells": 16,
        "dynamics_override": {
            "torso_com_offset_m": [0.0, 0.0, 0.0]
        },
    }
    bypass_contract = {
        "selection": {
            "only_when_command_x_equals_zero": True,
            "deployment_alignment": (
                "startup is paused at home; exact-zero command requires no "
                "configuration excitation"
            ),
        },
        "x0_path": {
            "response_calibration_ticks": 0,
            "home_return_ticks": 0,
            "initial_physical_state": "home-support reset",
            "calibration_context": "immutable float32 zeros [1,64]",
            "policy_hidden_state": "exact zeros [1,64]",
            "previous_action": "exact zeros [1,14]",
            "reference_phase": [1.0, 0.0],
            "policy_action": "exact zero on every scored tick",
            "graph_authoritative": True,
            "maximum_host_action_delta": 0.0,
            "applied_target_observation": True,
            "applied_target_slot": [83, 97],
            "state_context_and_applied_target_chains_exact": True,
        },
        "moving_path": {
            "change_from_T8": "none",
            "reused_cells": 12,
            "commands_x_m_s": [0.074, 0.077, 0.08],
            "green_and_independently_audited": True,
        },
        "default_off": (
            "the versioned evaluator flag defaults false; the T8 response "
            "prefix remains unchanged outside the x=0 branch"
        ),
    }
    reused_t8_evidence = {
        "result": repository_inputs["t8_result"],
        "independent_audit": repository_inputs["t8_independent_audit"],
        "failure_analysis": repository_inputs["t8_failure_analysis"],
        "green_moving_cells": 12,
        "reuse_rule": (
            "the mechanism makes no change to moving commands, so their exact "
            "immutable T8 traces carry decision weight without rerun"
        ),
    }
    behavior_contract = t8_prereg["behavior_contract"]
    protection_contract = t8_prereg["protection_contract"]
    decision_rule = {
        "partial_results_selection_weight": 0,
        "pass": (
            "all four new x=0 cells pass stationary behavior, replacement "
            "tracking/rate/saturation, corrected servo-duration protection, "
            "exact nominal readback, zero-context bypass, and every recurrent/"
            "applied-target chain; combined with all twelve audited T8 moving "
            "cells this must be 16/16"
        ),
        "pass_next_action": (
            "earn one separately preregistered response-conditioned V121 "
            "continuation CPU software contract; do not authorize hosted "
            "training yet"
        ),
        "fail_next_action": (
            "close the command-aware prefix-bypass mechanism and do not train"
        ),
        "new_x0_cells_required": 4,
        "reused_moving_cells_required": 12,
        "combined_cells_required": 16,
        "no_closest_result_promotion": True,
    }
    authority = {
        "offline_cpu_behavior_screen": True,
        "training_or_hosted_compute": False,
        "policy_weight_or_simulator_modification": False,
        "robot_rdkx5_torque_motion": False,
        "gate5": False,
    }
    execution_contract = {
        "cpu_only": True,
        "one_subprocess_per_checkpoint_fit_cell": True,
        "raw_logs_external_to_repository": True,
        "cache_root": (
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t9_command_aware_prefix_bypass_v1"
        ),
        "resumable_only_by_exact_block_contract_and_hashes": True,
        "runner_refuses_overwrite": True,
        "new_simulator_behavior_cells": 4,
        "reused_behavior_cells": 12,
        "training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    causal_basis = {
        "T8_localization": failure["causal_conclusion"],
        "one_variable": (
            "change only whether the response-support prefix executes when "
            "command x is exactly zero"
        ),
        "why_no_training": (
            "the failed transition is deterministic startup orchestration, "
            "not actor behavior or credit assignment"
        ),
        "why_reuse_moving": (
            "T9 does not change their prefix, policy, state, context, dynamics, "
            "or gate; rerunning would add compute without new evidence"
        ),
    }
    question = (
        "Does bypassing response excitation only while paused/x=0 eliminate "
        "T8's single transition-rate failure while preserving the immutable "
        "12/12 green moving handoff evidence?"
    )
    basis = {
        "question": question,
        "causal_basis": causal_basis,
        "repository_inputs": repository_inputs,
        "playground": playground,
        "candidate": candidate,
        "matrix": matrix,
        "bypass_contract": bypass_contract,
        "behavior_contract": behavior_contract,
        "protection_contract": protection_contract,
        "reused_t8_evidence": reused_t8_evidence,
        "decision_rule": decision_rule,
        "authority": authority,
        "execution_contract": execution_contract,
    }
    payload = {
        "schema_version": (
            "open_duck.t9_command_aware_prefix_bypass_preregistration.v1"
        ),
        "status": "PREREGISTERED_T9_COMMAND_AWARE_PREFIX_BYPASS",
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    JSON_OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T9 command-aware x=0 prefix-bypass preregistration",
        "",
        f"- Status: `{payload['status']}`",
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`",
        "- New cells: `4` (`2 checkpoints × 2 fits × x=0`)",
        "- Reused T8 moving cells: `12`",
        "- Training: `0 steps`",
        "- Robot/RDK-X5 access: `forbidden`",
        "",
        "## Question",
        "",
        question,
        "",
        "## One-variable mechanism",
        "",
        "At paused/x=0, stay at home, skip response excitation, and pass an "
        "immutable zero context to the unchanged context-ABI V121 graph. At "
        "moving commands, change nothing and reuse the twelve audited T8 cells.",
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
