#!/usr/bin/env python3
"""Preregister T247's final-only home-negative behavior matrix."""

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
T245 = ANALYSIS / "t245_home_negative_floor_remaining_matrix_result.json"
T247 = ANALYSIS / "t247_home_negative_half_adapter_route_result.json"
T247B = ANALYSIS / "t247b_reporting_recovery_result.json"
OUTPUT = (
    ANALYSIS / "t248_home_negative_half_adapter_matrix_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t248_home_negative_half_adapter_matrix.py"
TEST = ROOT / "tests/test_t248_home_negative_half_adapter_matrix.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T248 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T248 preregistration requires clean worktree")
    t242 = json.loads(T242.read_text(encoding="utf-8"))
    t245 = json.loads(T245.read_text(encoding="utf-8"))
    t247 = json.loads(T247.read_text(encoding="utf-8"))
    t247b = json.loads(T247B.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": (
                f"T247_HOME_NEGATIVE_HALF_ADAPTER_{row['role'].upper()}"
            ),
            "step": int(row["step"]),
            **row["structure"]["transformed"],
        }
        for row in t247["graphs"]
    ]
    policies.sort(key=lambda row: row["step"])
    reused_blocks = [
        block
        for block in t245["blocks"]
        if block["checkpoint_id"] == "T243_HOME_NEGATIVE_FLOOR_HALF"
    ]
    half_contract = next(
        row for row in t247["graphs"] if row["role"] == "half"
    )
    checks = {
        "t247b_earns_behavior_matrix_only": (
            t247b["status"] == "PASS_T247B_REPORTING_RECOVERY"
            and t247b["decision"]
            == "EARN_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX_PREREGISTRATION_ONLY"
            and all(t247b["checks"].values())
        ),
        "half_transform_is_output_exact_source": (
            half_contract["inference"]["all_outputs_bit_exact"]
            and half_contract["inference"]["all_non_tail_exact_source"]
            and half_contract["inference"]["all_tail_exact_half_source"]
            and half_contract["inference"]["tail_changed_samples"] == 0
        ),
        "eight_half_cells_green_and_reusable": (
            len(reused_blocks) == 2
            and {block["fit_id"] for block in reused_blocks}
            == {"p30", "p31_34"}
            and all(
                block["result"]["block_green"]
                and all(
                    cell["cell_green"]
                    for cell in block["result"]["cells"]
                )
                for block in reused_blocks
            )
        ),
        "two_complete_t247_graphs_present": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "run_only_two_final_blocks_fresh_no_retry": True,
        "zero_behavior_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T248 preregistration checks failed: {failed}")
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
            "open_duck.t248_home_negative_half_adapter_matrix_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX",
        "question": (
            "After inheriting the eight output-exact green half cells, do "
            "the T247 final graph's P30 and P31-34 blocks complete the "
            "unchanged 16-cell negative-home-offset gate?"
        ),
        **copied,
        "condition": t242["condition"],
        "policies": policies,
        "matrix": {
            "cells_total": 16,
            "cells_reused": 8,
            "cells_new_maximum": 8,
            "blocks_reused": 2,
            "blocks_new_maximum": 2,
            "both_checkpoints_required": True,
            "stop_at_first_failed_new_block": True,
            "fresh_cache": True,
            "no_retry": True,
        },
        "ordered_new_blocks": [
            {
                "checkpoint_id": (
                    "T247_HOME_NEGATIVE_HALF_ADAPTER_FINAL"
                ),
                "fit_id": "p30",
                "cells": 4,
            },
            {
                "checkpoint_id": (
                    "T247_HOME_NEGATIVE_HALF_ADAPTER_FINAL"
                ),
                "fit_id": "p31_34",
                "cells": 4,
            },
        ],
        "reused_evidence": {
            "t245_result": receipt(T245),
            "checkpoint_id": "T243_HOME_NEGATIVE_FLOOR_HALF",
            "fit_ids": ["p30", "p31_34"],
            "graph_equivalence": (
                "T247 half outputs are bit-exact to T243 half for every "
                "frozen context and command"
            ),
            "rerun": False,
        },
        "decision_rule": {
            "pass": (
                "EARN_T249_HOME_NEGATIVE_REPAIR_FULL_R2_"
                "PRESERVATION_PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_HOME_NEGATIVE_HALF_ADAPTER_ROUTE",
            "no_retry": True,
        },
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t242_contract": receipt(T242),
            "t245_behavior": receipt(T245),
            "t247_graph_result": receipt(T247),
            "t247b_recovery": receipt(T247B),
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
            "reuse_eight_half_cells": True,
            "run_only_final_blocks": True,
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
        "# T248 home-negative half-adapter matrix preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reuse/new maximum: `8/8` cells\n"
        "- Execute: final/P30 then final/P31-34; stop at first failure\n"
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
