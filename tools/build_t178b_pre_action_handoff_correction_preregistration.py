#!/usr/bin/env python3
"""Freeze the reporting-only T178B pre-action field correction."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t178b_pre_action_handoff_correction.py"
TEST = ROOT / "tests" / "test_t178b_pre_action_handoff_correction.py"
T178_PREREG = ANALYSIS / "t178_positive_z_failure_autopsy_preregistration.json"
T178_RESULT = ANALYSIS / "t178_positive_z_failure_autopsy_result.json"
RECOVERY = ANALYSIS / "t178_analysis_field_provenance_20260730.json"
EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
OUTPUT = (
    ANALYSIS / "t178b_pre_action_handoff_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T178B_PRE_ACTION_HANDOFF_CORRECTION_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T178B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T178B preregistration requires a clean worktree")
    t178_prereg = _load_json(T178_PREREG)
    t178_result = _load_json(T178_RESULT)
    recovery = _load_json(RECOVERY)
    if (
        t178_result.get("result_sha256")
        != "425d90353e3a6c6e7df425f6fe00b74fa2e17778c1226568c6bbd5fbba78e24e"
        or recovery.get("result_sha256")
        != "49b4817911dee113b61705a57679ad9d33cdc33977799e8385fe3ec6e5bf325e"
        or recovery.get("status")
        != "INVALIDATED_T178_HANDOFF_CLASSIFICATION_FIELD_PROVENANCE"
    ):
        raise RuntimeError("T178 source/recovery identity differs")
    if len(t178_prereg["trace_population"]) != 16:
        raise RuntimeError("T178 trace population differs")

    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t178_preregistration": T178_PREREG,
        "t178_invalidated_result": T178_RESULT,
        "t178_field_provenance_recovery": RECOVERY,
        "evaluator_source": EVALUATOR,
    }
    if not all(path.is_file() for path in frozen_paths.values()):
        raise RuntimeError("a frozen T178B input is missing")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t178b_pre_action_handoff_correction_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T178B_PRE_ACTION_HANDOFF_CORRECTION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_t178_contract_sha256": t178_prereg[
            "preregistered_contract_sha256"
        ],
        "source_t178_result_sha256": t178_result["result_sha256"],
        "source_recovery_sha256": recovery["result_sha256"],
        "matrix": t178_prereg["matrix"],
        "trace_population": t178_prereg["trace_population"],
        "field_contract": {
            "read_only_tick_zero": True,
            "pre_action_fields": [
                "policy_calibration_context_sha256",
                "policy_state_input",
                "actual_position_pre_rad",
                "obs_state[0:2]",
                "obs_state[83:97]",
            ],
            "applied_target_observation_slice": [83, 97],
            "phase_observation_slice": [0, 2],
            "excluded_post_action_fields": [
                "applied_target_rad",
                "qpos",
                "qvel",
            ],
            "exact_across_four_commands_within_each_checkpoint_fit": True,
            "blocks": 4,
            "commands_per_block": 4,
            "no_tolerance_or_fitted_threshold": True,
        },
        "decision_rule": {
            "all_four_blocks_exact": (
                "EARN_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB_"
                "PREREGISTRATION_ONLY"
            ),
            "any_true_pre_action_mismatch": (
                "NO_BEHAVIOR_SUCCESSOR_AUTHORIZED"
            ),
            "no_execution_authority_for_t179": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": {
            "tick_zero_rows_read": 16,
            "other_trace_rows_read": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "source_vs_transform_cpu_ab_preregistration": True,
            "source_vs_transform_cpu_ab_execution": False,
            "additional_training": False,
            "colab": False,
            "deployment_contract_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T178B pre-action handoff correction preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Scope: first row only from each of the `16` sealed traces\n"
        "- Compare: context, recurrent input, pre-action joint position, "
        "phase, and `obs[83:97]`\n"
        "- Exclude: current-action applied target and post-step qpos/qvel\n"
        "- Exact comparison; no tolerance or fitted threshold\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n"
        "- A pass earns only T179 CPU A/B preregistration.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
