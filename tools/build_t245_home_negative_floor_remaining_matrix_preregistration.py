#!/usr/bin/env python3
"""Preregister completion of T243's remaining home-negative matrix."""

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
T242B = ANALYSIS / "t242b_interrupted_reporter_recovery_result.json"
T243B = ANALYSIS / "t243b_abi_helper_recovery_result.json"
T243C = ANALYSIS / "t243c_random_sensitivity_recovery_result.json"
T244 = ANALYSIS / "t244_home_negative_low_command_behavior_result.json"
OUTPUT = (
    ANALYSIS
    / "t245_home_negative_floor_remaining_matrix_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t245_home_negative_floor_remaining_matrix.py"
TEST = ROOT / "tests/test_t245_home_negative_floor_remaining_matrix.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T245 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T245 preregistration requires clean worktree")
    t242 = json.loads(T242.read_text(encoding="utf-8"))
    t242b = json.loads(T242B.read_text(encoding="utf-8"))
    t243b = json.loads(T243B.read_text(encoding="utf-8"))
    t243c = json.loads(T243C.read_text(encoding="utf-8"))
    t244 = json.loads(T244.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T243_HOME_NEGATIVE_FLOOR_{row['role'].upper()}",
            "step": int(row["step"]),
            **row["structure"]["transformed"],
        }
        for row in t243b["graphs"]
    ]
    policies.sort(key=lambda row: row["step"])
    inherited = [
        cell
        for cell in t242b["block"]["result"]["cells"]
        if float(cell["command_x_m_s"]) != 0.074
    ]
    checks = {
        "t244_earns_remaining_matrix_only": (
            t244["status"]
            == "PASS_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR"
            and t244["decision"]
            == "EARN_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX_PREREGISTRATION_ONLY"
            and t244["cell"]["cell_green"]
            and t244["cell"]["behavior"]["samples"] == 600
        ),
        "three_non_target_half_p30_cells_are_inheritable": (
            len(inherited) == 3
            and {float(cell["command_x_m_s"]) for cell in inherited}
            == {0.0, 0.077, 0.080}
            and all(cell["cell_green"] for cell in inherited)
            and all(
                graph["inference"]["all_non_targets_exact_source"]
                for graph in t243b["graphs"]
            )
        ),
        "t243c_closes_only_reporting_sensitivity": (
            t243c["status"]
            == "PASS_T243C_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
            and all(t243c["checks"].values())
        ),
        "two_complete_t243_graphs_present": (
            len(policies) == 2
            and [row["step"] for row in policies]
            == [1_003_520, 2_007_040]
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "matrix_reuses_four_and_runs_only_twelve": True,
        "both_checkpoints_and_fits_still_mandatory": (
            t242["matrix"]["both_checkpoints_required"]
            and len(t242["fits"]) == 2
        ),
        "zero_behavior_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T245 preregistration checks failed: {failed}")
    copied = {
        name: t242[name]
        for name in (
            "fits",
            "calibrator",
            "reference_feature_table",
            "playground",
            "commands_x_m_s",
            "seed",
            "support_handoff",
            "behavior_contract",
            "protection_contract",
            "repository_inputs",
            "readback_correction",
        )
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t245_home_negative_floor_remaining_matrix_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX"
        ),
        "question": (
            "After reusing the four fully proven half/P30 cells, do the "
            "remaining half/P31-34, final/P30, and final/P31-34 blocks pass "
            "the unchanged 16-cell negative-home-offset matrix?"
        ),
        **copied,
        "condition": t242["condition"],
        "policies": policies,
        "matrix": {
            "cells_total": 16,
            "cells_reused": 4,
            "cells_new_maximum": 12,
            "blocks_reused": 1,
            "blocks_new_maximum": 3,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "stop_at_first_failed_new_block": True,
            "no_retry": True,
            "fresh_cache_for_new_blocks": True,
        },
        "reused_evidence": {
            "source_non_target_block_manifest": t242b["block"]["manifest"],
            "target_cell_manifest": t244["manifest"],
            "source_non_target_commands": [0.0, 0.077, 0.080],
            "target_command": 0.074,
            "non_target_graph_equivalence": (
                "T243B proves all non-target context/commands exact source"
            ),
        },
        "ordered_new_blocks": [
            {
                "checkpoint_id": "T243_HOME_NEGATIVE_FLOOR_HALF",
                "fit_id": "p31_34",
                "cells": 4,
            },
            {
                "checkpoint_id": "T243_HOME_NEGATIVE_FLOOR_FINAL",
                "fit_id": "p30",
                "cells": 4,
            },
            {
                "checkpoint_id": "T243_HOME_NEGATIVE_FLOOR_FINAL",
                "fit_id": "p31_34",
                "cells": 4,
            },
        ],
        "decision_rule": {
            "pass": (
                "EARN_T246_HOME_NEGATIVE_FLOOR_FULL_R2_"
                "PRESERVATION_PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_HOME_NEGATIVE_LOW_COMMAND_FLOOR",
            "no_retry": True,
        },
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t242_contract": receipt(T242),
            "t242b_recovery": receipt(T242B),
            "t243b_graph_result": receipt(T243B),
            "t243c_recovery": receipt(T243C),
            "t244_behavior": receipt(T244),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells_reused": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "reuse_four_cells": True,
            "run_only_remaining_blocks": True,
            "full_r2_preservation_preregistration": False,
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
        "# T245 home-negative floor remaining matrix preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reuse/new maximum: `4/12` cells\n"
        "- Order: half/P31-34, final/P30, final/P31-34\n"
        "- Stop at first failed block; no retry\n"
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
