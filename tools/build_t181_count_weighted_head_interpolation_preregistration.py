#!/usr/bin/env python3
"""Freeze the one evidence-derived T181 interpolation coefficient."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t181_count_weighted_head_interpolation.py"
TEST = ROOT / "tests" / "test_t181_count_weighted_head_interpolation.py"
T175_PREREG = ANALYSIS / "t175_head_prefix_mean_preregistration.json"
T175_RESULT = ANALYSIS / "t175_head_prefix_mean_result.json"
T173 = ANALYSIS / "t173_t170_targeted_y_negative_result.json"
T179 = ANALYSIS / "t179_source_vs_t175_positive_z_result.json"
T180B = ANALYSIS / "t180b_transform_route_attribution_result.json"
OUTPUT = (
    ANALYSIS / "t181_count_weighted_head_interpolation_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T181_COUNT_WEIGHTED_HEAD_INTERPOLATION_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
    verify_receipt,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T181: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T181 preregistration requires a clean worktree")
    t175_prereg = _load_json(T175_PREREG)
    t175_result = _load_json(T175_RESULT)
    t173 = _load_json(T173)
    t179 = _load_json(T179)
    t180b = _load_json(T180B)
    if (
        t180b.get("classification")
        != "SHARED_HEAD_DIRECTION_CONTEXT_AMPLITUDE_TRADEOFF"
        or t180b.get("result_sha256")
        != "7dcdd2e29190c804869a3757ef6aaae922840ad073918890410f3143abbea3c9"
        or t179["summary"]["source_failure_count"] != 1
        or t179["summary"]["transformed_failure_count"] != 5
    ):
        raise RuntimeError("T181 source evidence identity differs")
    y_negative_source_failures = sum(
        int(not cell["cell_green"])
        for block in t173["blocks"]
        for cell in block["result"]["cells"]
    )
    if y_negative_source_failures != 1:
        raise RuntimeError("T181 rescue count differs")
    rescue_count = 1
    regression_count = (
        int(t179["summary"]["transformed_failure_count"])
        - int(t179["summary"]["source_failure_count"])
    )
    alpha = rescue_count / (rescue_count + regression_count)
    if alpha != 0.2:
        raise RuntimeError("T181 derived alpha differs")
    graph_rows = {
        item["checkpoint_id"]: item for item in t175_result["graphs"]
    }
    graph_pairs = [
        {
            "checkpoint_id": "T181_ALPHA_0P2_HALF",
            "step": 1_003_520,
            "source": graph_rows["T175_HEAD_MEAN_HALF"]["structure"]["members"][1],
            "transformed_endpoint": graph_rows["T175_HEAD_MEAN_HALF"][
                "structure"
            ]["transformed"],
        },
        {
            "checkpoint_id": "T181_ALPHA_0P2_FINAL",
            "step": 2_007_040,
            "source": graph_rows["T175_HEAD_MEAN_FINAL"]["structure"]["members"][2],
            "transformed_endpoint": graph_rows["T175_HEAD_MEAN_FINAL"][
                "structure"
            ]["transformed"],
        },
    ]
    for pair in graph_pairs:
        verify_receipt(pair["source"], f"{pair['checkpoint_id']}:source")
        verify_receipt(
            pair["transformed_endpoint"],
            f"{pair['checkpoint_id']}:transformed",
        )
    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t175_preregistration": T175_PREREG,
        "t175_transform_result": T175_RESULT,
        "t173_source_y_negative": T173,
        "t179_source_vs_t175_positive_z": T179,
        "t180b_route_attribution": T180B,
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t181_count_weighted_head_interpolation_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T181_COUNT_WEIGHTED_HEAD_INTERPOLATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "graph_pairs": graph_pairs,
        "contexts": t175_prereg["contexts"],
        "interpolation": {
            "alpha": alpha,
            "formula": (
                "rescue_count / (rescue_count + regression_count)"
            ),
            "rescue_count": rescue_count,
            "regression_count": regression_count,
            "source_endpoint_alpha": 0.0,
            "t175_endpoint_alpha": 1.0,
            "arithmetic": (
                "float64 source + alpha*(T175-source), one float32 cast"
            ),
            "head_initializers": t175_prereg["transform"][
                "head_initializers"
            ],
            "scalar_search": False,
            "alternative_alphas": [],
        },
        "inference_seed": 181_2026_0730,
        "checks": {
            "only_two_head_initializers_change": True,
            "all_nodes_and_other_initializers_source_exact": True,
            "x0_and_inactive_routes_source_exact": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "EARN_T182_SHARED_FAILURE_SINGLE_CELL_PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_COUNT_WEIGHTED_HEAD_INTERPOLATION_WITHOUT_BEHAVIOR"
            ),
            "no_retry_or_alpha_sweep": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "t182_single_cell_preregistration": True,
            "t182_execution": False,
            "additional_interpolation_alpha": False,
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
        "# T181 count-weighted head interpolation preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Alpha: `1 / (1 + 4) = 0.20`\n"
        "- Inputs: source and T175 half/final graph pairs\n"
        "- Changed tensors: the same two nominal adapter-head initializers\n"
        "- Scalar search / alternative alpha: `false / none`\n"
        "- Behavior / optimizer / hosted compute / robot: `0/0/0/0`\n"
        "- A green graph contract earns only T182 single-cell "
        "preregistration.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
