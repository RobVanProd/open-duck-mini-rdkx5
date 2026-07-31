#!/usr/bin/env python3
"""Freeze the T179 source-versus-T175 positive-Z CPU behavior A/B."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t179_source_vs_t175_positive_z.py"
TEST = ROOT / "tests" / "test_t179_source_vs_t175_positive_z.py"
T175 = ANALYSIS / "t175_head_prefix_mean_result.json"
T177_PREREG = ANALYSIS / "t177_head_prefix_mean_full_r2_preregistration.json"
T177_RESULT = ANALYSIS / "t177_head_prefix_mean_full_r2_result.json"
T178_PREREG = ANALYSIS / "t178_positive_z_failure_autopsy_preregistration.json"
T178B = ANALYSIS / "t178b_pre_action_handoff_correction_result.json"
OUTPUT = ANALYSIS / "t179_source_vs_t175_positive_z_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T179_SOURCE_VS_T175_POSITIVE_Z_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    matrix_plan,
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
            raise FileExistsError(f"refusing to overwrite T179: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T179 preregistration requires a clean worktree")
    t175 = _load_json(T175)
    t177_prereg = _load_json(T177_PREREG)
    t177_result = _load_json(T177_RESULT)
    t178_prereg = _load_json(T178_PREREG)
    t178b = _load_json(T178B)
    if (
        t175.get("status") != "PASS_T175_HEAD_PREFIX_MEAN"
        or t177_result.get("result_sha256")
        != "59d0d3c73d808ff258e73f9cef0d0ff1734900776ab58c22d59e4ae8ae9219b2"
        or t178b.get("status") != "PASS_T178B_PRE_ACTION_HANDOFF_EXACT"
        or t178b.get("result_sha256")
        != "7c6a48b8e955f8633052c092002b12c12bba731709a2d27f932b418c69c2242c"
    ):
        raise RuntimeError("T179 source evidence identity differs")
    condition = next(
        item
        for item in t177_prereg["conditions"]
        if item["id"] == "TORSO_COM_Z_POS"
    )
    graphs = {item["checkpoint_id"]: item for item in t175["graphs"]}
    half_members = graphs["T175_HEAD_MEAN_HALF"]["structure"]["members"]
    final_members = graphs["T175_HEAD_MEAN_FINAL"]["structure"]["members"]
    source_policies = [
        {
            "checkpoint_id": "T170_SOURCE_HALF",
            "step": 1_003_520,
            **half_members[1],
        },
        {
            "checkpoint_id": "T170_SOURCE_FINAL",
            "step": 2_007_040,
            **final_members[2],
        },
    ]
    for policy in source_policies:
        verify_receipt(policy, policy["checkpoint_id"])
    transformed_blocks = []
    for block in t177_result["blocks"]:
        if block["condition_id"] != "TORSO_COM_Z_POS":
            continue
        verify_receipt(
            block["manifest"],
            f"{block['checkpoint_id']}:{block['fit_id']}",
        )
        manifest = _load_json(Path(block["manifest"]["path"]))
        traces = []
        for command, trace in zip(
            t177_prereg["commands_x_m_s"], manifest["traces"], strict=True
        ):
            verify_receipt(trace, f"transformed:{command:.3f}")
            traces.append({"command_x_m_s": float(command), **trace})
        transformed_blocks.append({**block, "traces": traces})
    if len(transformed_blocks) != 4:
        raise RuntimeError("T179 transformed block population differs")
    if sum(
        int(cell["cell_green"])
        for block in transformed_blocks
        for cell in block["result"]["cells"]
    ) != 11:
        raise RuntimeError("T179 transformed green count differs")
    checkpoint_pairs = [
        {
            "source_checkpoint_id": "T170_SOURCE_HALF",
            "transformed_checkpoint_id": "T175_HEAD_MEAN_HALF",
        },
        {
            "source_checkpoint_id": "T170_SOURCE_FINAL",
            "transformed_checkpoint_id": "T175_HEAD_MEAN_FINAL",
        },
    ]
    source_plan = matrix_plan(
        [condition],
        source_policies,
        t177_prereg["fits"],
        t177_prereg["commands_x_m_s"],
        int(t177_prereg["seed"]),
    )
    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t175_transform": T175,
        "t177_preregistration": T177_PREREG,
        "t177_terminal_result": T177_RESULT,
        "t178_preregistration": T178_PREREG,
        "t178b_exact_handoff": T178B,
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t179_source_vs_t175_positive_z_preregistration.v1"
        ),
        "status": "PREREGISTERED_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "condition": condition,
        "conditions": [condition],
        "source_policies": source_policies,
        "policies": source_policies,
        "checkpoint_pairs": checkpoint_pairs,
        "transformed_blocks": transformed_blocks,
        "fits": t177_prereg["fits"],
        "commands_x_m_s": t177_prereg["commands_x_m_s"],
        "seed": t177_prereg["seed"],
        "calibrator": t177_prereg["calibrator"],
        "reference_feature_table": t177_prereg["reference_feature_table"],
        "playground": t177_prereg["playground"],
        "support_handoff": t177_prereg["support_handoff"],
        "behavior_contract": t177_prereg["behavior_contract"],
        "protection_contract": t177_prereg["protection_contract"],
        "repository_inputs": t177_prereg["repository_inputs"],
        "matrix": {
            "new_source_cells": 16,
            "reused_transformed_cells": 16,
            "transformed_reruns": 0,
            "source_plan_sha256": canonical_sha256(source_plan),
            "fresh_source_cache": True,
        },
        "comparison_contract": {
            "primary": "green-cell count and exact failed-cell identity",
            "secondary": "full JSONL file SHA/byte identity for all 16 pairs",
            "no_threshold_change": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": {
            "source_16_of_16": (
                "T175_HEAD_PREFIX_MEAN_INTRODUCED_POSITIVE_Z_REGRESSION"
            ),
            "source_greener_than_t175": (
                "T175_HEAD_PREFIX_MEAN_NET_POSITIVE_Z_REGRESSION"
            ),
            "same_failures_all_traces_exact": (
                "T175_NO_EFFECT_POSITIVE_Z_FAILURE_PREDATES_TRANSFORM"
            ),
            "same_failures_traces_differ": (
                "T175_NONCAUSAL_SHARED_POSITIVE_Z_FAILURE_MATRIX"
            ),
            "source_worse_than_t175": (
                "T175_PARTIAL_POSITIVE_Z_IMPROVEMENT_INSUFFICIENT"
            ),
            "no_training_or_deployment_authority": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": {
            "new_behavior_cells": 16,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "t180_cpu_preregistration": True,
            "t180_execution": False,
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
        "# T179 source versus T175 positive-Z CPU A/B preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- New source cells: `16`; reused transformed cells: `16`\n"
        "- Source: untransformed T170 half/final checkpoints\n"
        "- Comparator: sealed T177 T175 half/final positive-Z cells\n"
        "- Primary: green count and exact failure cells\n"
        "- Secondary: full JSONL SHA/byte identity\n"
        "- Optimizer / hosted compute / robot: `0/0/0`\n"
        "- No outcome authorizes training, deployment audit, Gate 5, or "
        "hardware.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
