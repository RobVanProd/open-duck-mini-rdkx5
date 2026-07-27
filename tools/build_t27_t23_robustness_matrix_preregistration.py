#!/usr/bin/env python3
"""Freeze T23's sequential 20-condition R2 robustness matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from run_t27_t23_robustness_matrix import matrix_plan


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T27_T23_ROBUSTNESS_MATRIX_PREREGISTRATION_20260726.md"
)
R2 = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"
T26 = ANALYSIS / "t26_t23_corrected_nominal_result.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
T24 = ANALYSIS / "t24_t23_postexport_result.json"
T8 = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
T6 = ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
POLICY_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t25_t23_nominal_policies_v1"
)
PLAYGROUND = Path(
    r"D:\CodexProjects\Open_Duck_Playground-composed-t19-v6"
)

REPOSITORY_INPUTS = {
    "runner": ROOT / "tools" / "run_t27_t23_robustness_matrix.py",
    "worker": ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py",
    "adapter": ROOT / "tools" / "t27_state_coherent_eval_adapter.py",
    "base_evaluator": ROOT / "tools" / "closed_loop_sim_eval.py",
    "t6_helpers": ROOT / "tools" / "run_t6_corrected_robustness_screen.py",
    "t8_helpers": ROOT / "tools" / "run_t8_state_coherent_handoff.py",
    "r2_source": R2,
    "t26_nominal_result": T26,
    "t27_runner_contract": T27_CONTRACT,
    "t24_postexport_result": T24,
    "t8_support_preregistration": T8,
    "t6_corrected_gate_preregistration": T6,
}


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
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T27 preregistration")
    missing = [
        name for name, path in REPOSITORY_INPUTS.items() if not path.is_file()
    ]
    r2 = load_json(R2) if R2.is_file() else {}
    t26 = load_json(T26) if T26.is_file() else {}
    contract = load_json(T27_CONTRACT) if T27_CONTRACT.is_file() else {}
    t24 = load_json(T24) if T24.is_file() else {}
    t8 = load_json(T8) if T8.is_file() else {}
    t6 = load_json(T6) if T6.is_file() else {}

    conditions = [
        {
            "condition_index": index,
            "id": item["id"],
            "override": item["override"],
        }
        for index, item in enumerate(
            r2.get("conditions_in_strict_order", []), start=1
        )
    ]
    policy_specs = [
        {
            "checkpoint_id": "T23_SUPPORT_HALF",
            "step": 1_003_520,
            **receipt(POLICY_ROOT / "T23_SUPPORT_1003520.onnx"),
        },
        {
            "checkpoint_id": "T23_SUPPORT_FINAL",
            "step": 2_007_040,
            **receipt(POLICY_ROOT / "T23_SUPPORT_2007040.onnx"),
        },
    ]
    fit_specs = [
        {
            "fit_id": "p30",
            **receipt(
                ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
            ),
        },
        {
            "fit_id": "p31_34",
            **receipt(
                ANALYSIS
                / "fixed_target_p31_34_actuator_fit_20260712.json"
            ),
        },
    ]
    calibrator = t8.get("calibrator") or {}
    reference = receipt(
        ANALYSIS / "ground_up_projected_reference_feature_table.npz"
    )
    playground_manifest = receipt(
        PLAYGROUND / "T19_COMPOSED_SOURCE_MANIFEST.json"
    )
    commands = [0.0, 0.074, 0.077, 0.08]
    seed = 167931544
    plan = matrix_plan(
        conditions, policy_specs, fit_specs, commands, seed
    )
    checks = {
        "t26_nominal_persistence_passed": (
            t26.get("status")
            == "PASS_T26_T23_CORRECTED_NOMINAL_PERSISTENCE"
            and t26.get("authority", {}).get(
                "robustness_preregistration_authorized"
            )
            is True
        ),
        "runner_contract_passed": (
            contract.get("status")
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and not contract.get("failed_checks")
        ),
        "t24_postexport_passed": (
            t24.get("status") == "PASS_T24_T23_POSTEXPORT_TRANSFORM"
        ),
        "r2_has_exact_twenty_conditions": len(conditions) == 20,
        "r2_order_and_overrides_exact": (
            conditions
            == [
                {
                    "condition_index": index,
                    "id": item["id"],
                    "override": item["override"],
                }
                for index, item in enumerate(
                    r2.get("conditions_in_strict_order", []), start=1
                )
            ]
        ),
        "matrix_is_exact_320_cells": len(plan) == 320,
        "both_t23_policies_exact": all(
            path["sha256"]
            == t24["deployments"][str(path["step"])]["wrapped"][
                "sha256"
            ]
            for path in policy_specs
        )
        if t24
        else False,
        "calibrator_exists_and_matches_t8": (
            bool(calibrator)
            and Path(calibrator["path"]).is_file()
            and sha256(Path(calibrator["path"])) == calibrator["sha256"]
        ),
        "all_repository_inputs_present": not missing,
        "playground_manifest_present": playground_manifest["bytes"] > 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX"
        if not failed
        else "HOLD_T27_T23_ROBUSTNESS_MATRIX_PREREGISTRATION"
    )
    payload = {
        "schema_version": (
            "open_duck.t27_t23_robustness_matrix_preregistration.v1"
        ),
        "status": status,
        "question": (
            "Do both frozen T23 checkpoints pass the unchanged 20-condition "
            "R2 ladder under both measured actuator fits and all four "
            "commands when entered through the exact trained 250-tick "
            "support handoff?"
        ),
        "checks": checks,
        "failed_checks": failed,
        "repository_inputs": {
            name: receipt(path)
            for name, path in REPOSITORY_INPUTS.items()
            if path.is_file()
        },
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "manifest": playground_manifest,
        },
        "policies": policy_specs,
        "fits": fit_specs,
        "calibrator": calibrator,
        "reference_feature_table": reference,
        "conditions": conditions,
        "commands_x_m_s": commands,
        "seed": seed,
        "support_handoff": {
            "unscored_calibration_ticks": 250,
            "unscored_home_return_ticks": 0,
            "preserve_final_support_action_as_previous_action": True,
            "preserve_applied_target_observer_state": True,
            "locomotion_phase_reset": [1.0, 0.0],
            "locomotion_hidden_zero": True,
            "context_input_name": "calibration_context",
            "context_is_diagnostic_only": True,
            "source": (
                "T22/T24 exact support-train-through deployment chain and "
                "green T27 one-tick runner contract"
            ),
        },
        "behavior_contract": t6.get("behavior_contract"),
        "protection_contract": t6.get("protection_contract"),
        "matrix": {
            "conditions": 20,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 320,
            "plan_sha256": canonical_sha256(plan),
            "strictly_sequential_conditions": True,
            "complete_each_16_cell_condition_before_decision": True,
            "stop_after_first_failed_condition": True,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
        },
        "decision_rule": {
            "pass": (
                "all 320 cells across all 20 conditions are green under "
                "core behavior, replacement-quality, exact handoff/readback, "
                "zero full-vector rate excess, and T5 duration protection"
            ),
            "pass_decision": "EARN_T23_GATE5_PACKAGE_PREREGISTRATION",
            "fail_decision": (
                "STOP_T23_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE"
            ),
            "training_reward_selection_weight": 0,
        },
        "authority": {
            "one_sequential_cpu_matrix_authorized": not failed,
            "maximum_formal_behavior_cells": 320,
            "additional_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_hardware_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    basis = dict(payload)
    payload["preregistered_contract_sha256"] = canonical_sha256(basis)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T27 T23 sequential R2 robustness preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: "
        f"`{payload['preregistered_contract_sha256']}`\n"
        "- Matrix: 20 frozen R2 conditions × 2 checkpoints × 2 measured "
        "fits × 4 commands = at most 320 cells.\n"
        "- Execution is strictly sequential and stops after the first "
        "complete failed 16-cell condition.\n"
        "- Each cell uses the exact 250-tick support handoff, T5 duration "
        "protection, and unchanged behavior/quality gates.\n"
        "- No training, checkpoint selection, Gate 5, RDK-X5, robot access, "
        "torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"plan_sha256={payload['matrix']['plan_sha256']}")
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
