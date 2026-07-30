#!/usr/bin/env python3
"""Freeze T180's CPU-only source/T175 route attribution."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t180_transform_route_attribution.py"
TEST = ROOT / "tests" / "test_t180_transform_route_attribution.py"
T175_PREREG = ANALYSIS / "t175_head_prefix_mean_preregistration.json"
T175_RESULT = ANALYSIS / "t175_head_prefix_mean_result.json"
T173 = ANALYSIS / "t173_t170_targeted_y_negative_result.json"
T176 = ANALYSIS / "t176_head_prefix_mean_targeted_result.json"
T177 = ANALYSIS / "t177_head_prefix_mean_full_r2_result.json"
T179 = ANALYSIS / "t179_source_vs_t175_positive_z_result.json"
OUTPUT = ANALYSIS / "t180_transform_route_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T180_TRANSFORM_ROUTE_ATTRIBUTION_PREREGISTRATION_20260730.md"
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


def _trace_for(
    block: Mapping[str, Any],
    command: float,
    commands: list[float],
) -> dict[str, Any]:
    manifest_receipt = block["manifest"]
    verify_receipt(manifest_receipt, "manifest")
    manifest = _load_json(Path(manifest_receipt["path"]))
    index = commands.index(command)
    trace = manifest["traces"][index]
    verify_receipt(trace, f"trace:{command:.3f}")
    return trace


def _block_for(
    result: Mapping[str, Any],
    checkpoint_id: str,
    fit_id: str,
) -> Mapping[str, Any]:
    return next(
        block
        for block in result["blocks"]
        if block["checkpoint_id"] == checkpoint_id
        and block["fit_id"] == fit_id
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T180: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T180 preregistration requires a clean worktree")
    t175_prereg = _load_json(T175_PREREG)
    t175_result = _load_json(T175_RESULT)
    t173 = _load_json(T173)
    t176 = _load_json(T176)
    t177 = _load_json(T177)
    t179 = _load_json(T179)
    if (
        t179.get("classification")
        != "T175_HEAD_PREFIX_MEAN_NET_POSITIVE_Z_REGRESSION"
        or t179.get("result_sha256")
        != "97256b78b85e851a8aedaaa24b0c2125cf99594df9c995ea1a9a87620ef07a30"
        or t173.get("status") != "HOLD_T173_T170_TARGETED_Y_NEGATIVE"
        or t176.get("status") != "PASS_T176_HEAD_PREFIX_MEAN_TARGETED"
    ):
        raise RuntimeError("T180 source evidence identity differs")
    commands = [0.0, 0.074, 0.077, 0.08]
    contexts = {
        (row["condition_id"], row["fit_id"]): row
        for row in t175_prereg["contexts"]
    }
    graph_rows = {
        row["checkpoint_id"]: row for row in t175_result["graphs"]
    }
    graph_pairs = {
        "half": {
            "source_graph": graph_rows["T175_HEAD_MEAN_HALF"]["structure"][
                "members"
            ][1],
            "transformed_graph": graph_rows["T175_HEAD_MEAN_HALF"][
                "structure"
            ]["transformed"],
        },
        "final": {
            "source_graph": graph_rows["T175_HEAD_MEAN_FINAL"]["structure"][
                "members"
            ][2],
            "transformed_graph": graph_rows["T175_HEAD_MEAN_FINAL"][
                "structure"
            ]["transformed"],
        },
    }
    case_specs = [
        {
            "case_id": "Y_NEG_RESCUE_FINAL_P30_X080",
            "family": "negative_y_rescue",
            "condition_id": "TORSO_COM_Y_NEG",
            "checkpoint_pair": "final",
            "fit_id": "p30",
            "command_x_m_s": 0.08,
            "source_result": t173,
            "source_checkpoint": "T170_COMPOSED_FINAL",
            "transformed_result": t176,
            "transformed_checkpoint": "T175_HEAD_MEAN_FINAL",
            "source_cell_green": False,
            "transformed_cell_green": True,
        },
        {
            "case_id": "Z_POS_REGRESS_HALF_P30_X077",
            "family": "positive_z_regression",
            "condition_id": "TORSO_COM_Z_POS",
            "checkpoint_pair": "half",
            "fit_id": "p30",
            "command_x_m_s": 0.077,
            "source_result": t179,
            "source_checkpoint": "T170_SOURCE_HALF",
            "transformed_result": t177,
            "transformed_checkpoint": "T175_HEAD_MEAN_HALF",
            "source_cell_green": True,
            "transformed_cell_green": False,
        },
        {
            "case_id": "Z_POS_REGRESS_HALF_P31_X074",
            "family": "positive_z_regression",
            "condition_id": "TORSO_COM_Z_POS",
            "checkpoint_pair": "half",
            "fit_id": "p31_34",
            "command_x_m_s": 0.074,
            "source_result": t179,
            "source_checkpoint": "T170_SOURCE_HALF",
            "transformed_result": t177,
            "transformed_checkpoint": "T175_HEAD_MEAN_HALF",
            "source_cell_green": True,
            "transformed_cell_green": False,
        },
        {
            "case_id": "Z_POS_REGRESS_FINAL_P30_X074",
            "family": "positive_z_regression",
            "condition_id": "TORSO_COM_Z_POS",
            "checkpoint_pair": "final",
            "fit_id": "p30",
            "command_x_m_s": 0.074,
            "source_result": t179,
            "source_checkpoint": "T170_SOURCE_FINAL",
            "transformed_result": t177,
            "transformed_checkpoint": "T175_HEAD_MEAN_FINAL",
            "source_cell_green": True,
            "transformed_cell_green": False,
        },
        {
            "case_id": "Z_POS_REGRESS_FINAL_P30_X077",
            "family": "positive_z_regression",
            "condition_id": "TORSO_COM_Z_POS",
            "checkpoint_pair": "final",
            "fit_id": "p30",
            "command_x_m_s": 0.077,
            "source_result": t179,
            "source_checkpoint": "T170_SOURCE_FINAL",
            "transformed_result": t177,
            "transformed_checkpoint": "T175_HEAD_MEAN_FINAL",
            "source_cell_green": True,
            "transformed_cell_green": False,
        },
        {
            "case_id": "Z_POS_SHARED_HALF_P31_X077",
            "family": "positive_z_shared_failure",
            "condition_id": "TORSO_COM_Z_POS",
            "checkpoint_pair": "half",
            "fit_id": "p31_34",
            "command_x_m_s": 0.077,
            "source_result": t179,
            "source_checkpoint": "T170_SOURCE_HALF",
            "transformed_result": t177,
            "transformed_checkpoint": "T175_HEAD_MEAN_HALF",
            "source_cell_green": False,
            "transformed_cell_green": False,
        },
    ]
    cases = []
    for spec in case_specs:
        context = contexts[(spec["condition_id"], spec["fit_id"])]
        source_block = _block_for(
            spec["source_result"],
            spec["source_checkpoint"],
            spec["fit_id"],
        )
        transformed_block = _block_for(
            spec["transformed_result"],
            spec["transformed_checkpoint"],
            spec["fit_id"],
        )
        graph_pair = graph_pairs[spec["checkpoint_pair"]]
        case = {
            key: spec[key]
            for key in (
                "case_id",
                "family",
                "condition_id",
                "checkpoint_pair",
                "fit_id",
                "command_x_m_s",
                "source_cell_green",
                "transformed_cell_green",
            )
        }
        case.update(
            {
                "context": context["context"],
                "context_sha256": context["context_sha256"],
                "source_graph": graph_pair["source_graph"],
                "transformed_graph": graph_pair["transformed_graph"],
                "source_trace": _trace_for(
                    source_block, spec["command_x_m_s"], commands
                ),
                "transformed_trace": _trace_for(
                    transformed_block, spec["command_x_m_s"], commands
                ),
            }
        )
        cases.append(case)
    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t175_preregistration": T175_PREREG,
        "t175_transform_result": T175_RESULT,
        "t173_source_y_negative": T173,
        "t176_transformed_y_negative": T176,
        "t177_transformed_positive_z": T177,
        "t179_source_positive_z": T179,
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t180_transform_route_attribution_preregistration.v1"
        ),
        "status": "PREREGISTERED_T180_TRANSFORM_ROUTE_ATTRIBUTION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "cases": cases,
        "analysis_contract": {
            "prefix_ticks": 162,
            "gait_period_ticks": 27,
            "banks_per_case": ["source_trace", "transformed_trace"],
            "own_graph_replay_tolerance": 1.0e-6,
            "nonzero_action_delta_threshold": 1.0e-7,
            "shared_direction_cosine_threshold": 0.90,
            "shared_direction_rule": (
                "helpful and harmful families have the same dominant joint and "
                "absolute signed-mean cosine >= 0.90"
            ),
            "no_fitted_threshold_or_behavior_selection": True,
        },
        "decision_rule": {
            "invalid_replay": "NO_SUCCESSOR_AUTHORIZED",
            "shared_direction": (
                "EARN_T181_ONE_DIMENSIONAL_HEAD_INTERPOLATION_"
                "FEASIBILITY_PREREGISTRATION_ONLY"
            ),
            "distributed_direction": (
                "EARN_T181_CONTEXT_GATED_HEAD_FEASIBILITY_"
                "PREREGISTRATION_ONLY"
            ),
            "no_graph_change_or_behavior_authority": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": {
            "saved_trace_banks": 12,
            "saved_trace_rows": 1944,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "t181_cpu_preregistration": True,
            "t181_execution": False,
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
        "# T180 transform-route attribution preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Cases: `6`; frozen banks: `12`; prefix: `162` ticks\n"
        "- Families: one negative-Y rescue, four positive-Z regressions, one "
        "shared positive-Z failure\n"
        "- Method: exact source/T175 CPU inference on identical recorded states\n"
        "- Replay tolerance: `1e-6`; shared-direction cosine: `0.90`\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n"
        "- No result directly authorizes a graph change or behavior test.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
