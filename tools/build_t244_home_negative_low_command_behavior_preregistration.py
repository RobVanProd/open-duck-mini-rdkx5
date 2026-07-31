#!/usr/bin/env python3
"""Preregister one decisive T243 half/P30/x=.074 behavior cell."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T242 = ANALYSIS / "t242_bounded_router_home_offset_preregistration.json"
T243 = ANALYSIS / "t243_home_negative_low_command_floor_preregistration.json"
T243B = ANALYSIS / "t243b_abi_helper_recovery_result.json"
T243C = ANALYSIS / "t243c_random_sensitivity_recovery_result.json"
OUTPUT = (
    ANALYSIS
    / "t244_home_negative_low_command_behavior_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t244_home_negative_low_command_behavior.py"
TEST = ROOT / "tests/test_t244_home_negative_low_command_behavior.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T244 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T244 preregistration requires clean worktree")
    t242 = json.loads(T242.read_text(encoding="utf-8"))
    t243 = json.loads(T243.read_text(encoding="utf-8"))
    t243b = json.loads(T243B.read_text(encoding="utf-8"))
    t243c = json.loads(T243C.read_text(encoding="utf-8"))
    graph = next(row for row in t243b["graphs"] if row["role"] == "half")
    fit = next(row for row in t242["fits"] if row["fit_id"] == "p30")
    checks = {
        "t243c_earns_targeted_behavior_only": (
            t243c["status"]
            == "PASS_T243C_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
            and t243c["decision"]
            == "EARN_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_PREREGISTRATION_ONLY"
            and all(t243c["checks"].values())
        ),
        "t243_half_graph_exact_and_present": (
            graph["step"] == 1_003_520
            and graph["reused_partial_graph"] is True
            and Path(graph["structure"]["transformed"]["path"]).is_file()
            and graph["structure"]["source_abi"]
            == graph["structure"]["transformed_abi"]
        ),
        "single_cell_is_exact_prior_failure": (
            t242["condition"]["id"] == "HOME_JOINT_OFFSET_NEG"
            and t242["condition"]["override"]
            == {"joint_qpos0_offset_rad": -0.03}
            and t243["causal_evidence"]["failed_command_samples"] == 281
        ),
        "frozen_command_seed_duration_and_handoff": (
            t242["seed"] == 167_931_544
            and t242["support_handoff"]["unscored_calibration_ticks"] == 250
            and t242["support_handoff"]["unscored_home_return_ticks"] == 0
            and t242["support_handoff"][
                "preserve_final_support_action_as_previous_action"
            ]
            is True
            and t242["support_handoff"][
                "preserve_applied_target_observer_state"
            ]
            is True
        ),
        "p30_fit_exact_and_present": (
            fit["fit_id"] == "p30" and Path(fit["path"]).is_file()
        ),
        "zero_behavior_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T244 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t244_home_negative_low_command_behavior_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR",
        "question": (
            "Does the T243 half graph complete the exact previously failing "
            "P30, uniform -0.03-rad home-offset, x=.074 cell for 600 ticks "
            "with every frozen behavior, protection, and handoff gate green?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t242_matrix_contract": receipt(T242),
            "t243_graph_contract": receipt(T243),
            "t243b_graph_result": receipt(T243B),
            "t243c_recovery": receipt(T243C),
        },
        "policy": {
            "checkpoint_id": "T243_HOME_NEGATIVE_FLOOR_HALF",
            "step": 1_003_520,
            **graph["structure"]["transformed"],
        },
        "fit": fit,
        "condition": t242["condition"],
        "command_x_m_s": 0.074,
        "seed": t242["seed"],
        "duration_s": 12.0,
        "duration_ticks": 600,
        "calibrator": t242["calibrator"],
        "reference_feature_table": t242["reference_feature_table"],
        "playground": t242["playground"],
        "behavior_contract": t242["behavior_contract"],
        "protection_contract": t242["protection_contract"],
        "support_handoff": t242["support_handoff"],
        "repository_inputs": t242["repository_inputs"],
        "readback_correction": t242["readback_correction"],
        "execution": {
            "fresh_cache": True,
            "cells": 1,
            "formal_t244": True,
            "worker_formal_flag": False,
            "worker_formal_flag_reason": (
                "the inherited worker reserves --formal for its four-command "
                "T27 block; T244 freezes the one-cell command/seed/duration "
                "and evaluates the same trace gates directly"
            ),
            "no_retry": True,
            "stop_on_failure": True,
        },
        "decision_rule": {
            "pass": (
                "EARN_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_HOME_NEGATIVE_LOW_COMMAND_FLOOR",
            "no_retry": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_cpu_behavior_cell": True,
            "remaining_matrix_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T244 home-negative low-command behavior preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Cell: half/P30/home-offset -0.03/x=.074/600 ticks\n"
        "- Fresh cache; no retry; failure closes the mechanism\n"
        "- Optimizer/hosted/robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
