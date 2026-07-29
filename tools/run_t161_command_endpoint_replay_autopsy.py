#!/usr/bin/env python3
"""Autopsy T160 and falsify a checkpoint-endpoint command replay repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T160 = ANALYSIS / "t160_mechanics_positive_endpoint_result.json"
RESULT = ANALYSIS / "t161_command_endpoint_replay_autopsy.json"
MARKDOWN = ANALYSIS / "T161_COMMAND_ENDPOINT_REPLAY_AUTOPSY_20260729.md"

COMMANDS = (0.0, 0.074, 0.077, 0.080)
ENDPOINT_BY_CHECKPOINT = {
    "T159_MECHANICS_HALF": 0.080,
    "T159_MECHANICS_FINAL": 0.074,
}


def canonical_sha256(value: Any) -> str:
    import hashlib

    payload = json.dumps(
        value,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T161 output")
    source = json.loads(T160.read_text(encoding="utf-8"))
    if source["status"] != "HOLD_T160_MECHANICS_POSITIVE_ENDPOINT":
        raise RuntimeError("T160 is not the frozen hold result")

    cells = []
    indexed: dict[tuple[str, str, float], dict[str, Any]] = {}
    for block in source["blocks"]:
        checkpoint = block["checkpoint_id"]
        fit = block["fit_id"]
        for cell in block["result"]["cells"]:
            command = float(cell["command_x_m_s"])
            indexed[(checkpoint, fit, command)] = cell
            behavior = cell["behavior"]
            failure_reasons = [
                key
                for key, passed in {
                    **behavior["core_checks"],
                    **behavior["replacement_quality_checks"],
                }.items()
                if not passed
            ]
            cells.append(
                {
                    "checkpoint_id": checkpoint,
                    "fit_id": fit,
                    "command_x_m_s": command,
                    "cell_green": bool(cell["cell_green"]),
                    "failure_reasons": failure_reasons,
                    "samples": int(behavior["samples"]),
                    "termination_reason": behavior["termination_reason"],
                    "mean_velocity_x_m_s": behavior[
                        "mean_local_vx_m_s"
                    ],
                    "forward_command_tracking_ratio": behavior[
                        "track_ratio"
                    ],
                    "tracking_p95_rad": behavior[
                        "pitch_tracking_p95_rad"
                    ],
                    "action_saturation_pct": behavior[
                        "action_saturation_pct"
                    ],
                    "rate_excess_rad_s": max(
                        behavior["instant_rate_excess_rad_s"],
                        behavior["p95_rate_excess_rad_s"],
                    ),
                }
            )

    projected = []
    failed_checks = []
    for checkpoint, endpoint in ENDPOINT_BY_CHECKPOINT.items():
        for fit in ("p30", "p31_34"):
            source_cell = indexed[(checkpoint, fit, endpoint)]
            if not source_cell["cell_green"]:
                failed_checks.append(
                    f"selected endpoint is not green: {checkpoint}:{fit}"
                )
            source_metrics = source_cell["behavior"]
            source_vx = float(source_metrics["mean_local_vx_m_s"])
            for external_command in COMMANDS:
                if external_command == 0.0:
                    replay_cell = indexed[(checkpoint, fit, 0.0)]
                    projected_green = bool(replay_cell["cell_green"])
                    projected_ratio = None
                    selected_command = 0.0
                else:
                    replay_cell = source_cell
                    projected_ratio = source_vx / external_command
                    projected_green = bool(
                        replay_cell["behavior"]["samples"] == 600
                        and replay_cell["behavior"]["termination_reason"]
                        == "duration_complete"
                        and replay_cell["behavior"][
                            "left_contact_transitions"
                        ]
                        > 0
                        and replay_cell["behavior"][
                            "right_contact_transitions"
                        ]
                        > 0
                        and projected_ratio >= 0.25
                        and replay_cell["behavior"][
                            "pitch_tracking_p95_rad"
                        ]
                        <= 0.2
                        and replay_cell["behavior"]["action_saturation_pct"]
                        <= 0.0
                        and replay_cell["behavior"][
                            "instant_rate_excess_rad_s"
                        ]
                        <= 0.0
                        and replay_cell["behavior"]["p95_rate_excess_rad_s"]
                        <= 0.0
                    )
                    selected_command = endpoint
                projected.append(
                    {
                        "checkpoint_id": checkpoint,
                        "fit_id": fit,
                        "external_command_x_m_s": external_command,
                        "policy_command_x_m_s": selected_command,
                        "source_cell_green": bool(
                            replay_cell["cell_green"]
                        ),
                        "source_mean_velocity_x_m_s": float(
                            replay_cell["behavior"]["mean_local_vx_m_s"]
                        ),
                        "projected_forward_tracking_ratio": projected_ratio,
                        "projected_cell_green_under_behavior_replay": (
                            projected_green
                        ),
                        "replay_limit": (
                            "This is an algebraic screen over a frozen "
                            "behavior trace. It does not assert that an ONNX "
                            "command rewrite reproduces the trace until an "
                            "exact graph contract and behavior rerun pass."
                        ),
                    }
                )
                if not projected_green:
                    failed_checks.append(
                        "projected replay is not green: "
                        f"{checkpoint}:{fit}:x={external_command:.3f}"
                    )

    nonzero_map = {
        checkpoint: endpoint
        for checkpoint, endpoint in ENDPOINT_BY_CHECKPOINT.items()
    }
    status = (
        "PASS_T161_COMMAND_ENDPOINT_REPLAY_AUTOPSY"
        if not failed_checks
        else "HOLD_T161_COMMAND_ENDPOINT_REPLAY_AUTOPSY"
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t161_command_endpoint_replay_autopsy.v1"
        ),
        "status": status,
        "source": {
            "path": str(T160),
            "result_sha256": source["result_sha256"],
        },
        "observed_cells": cells,
        "mechanism": {
            "external_command_unchanged": True,
            "x0_policy_command_x_m_s": 0.0,
            "moving_policy_command_by_checkpoint_x_m_s": nonzero_map,
            "selection_rule": (
                "For each frozen checkpoint, select its unique moving "
                "support endpoint that is green under both measured "
                "actuator fits: HALF=max support 0.080; FINAL=min support "
                "0.074. No interpolated scalar is introduced."
            ),
            "policy_support_preserved": True,
            "environment_command_preserved": True,
            "runtime_abi_preserved": True,
        },
        "projected_replay_cells": projected,
        "checks": {
            "all_selected_endpoint_cells_green": not any(
                item.startswith("selected endpoint")
                for item in failed_checks
            ),
            "all_16_projected_replay_cells_green": not any(
                item.startswith("projected replay")
                for item in failed_checks
            ),
            "no_scalar_search": True,
            "zero_behavior_executions": True,
            "zero_training_or_hosted_compute": True,
        },
        "failed_checks": failed_checks,
        "decision": (
            "EARN_T162_EXACT_COMMAND_ENDPOINT_GRAPH_CONTRACT_ONLY"
            if not failed_checks
            else "CLOSE_COMMAND_ENDPOINT_REPLAY_REPAIR"
        ),
        "authority": {
            "graph_contract": not failed_checks,
            "behavior_rerun": False,
            "full_r2": False,
            "training": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    ratios = [
        item["projected_forward_tracking_ratio"]
        for item in projected
        if item["projected_forward_tracking_ratio"] is not None
    ]
    MARKDOWN.write_text(
        "# T161 command-endpoint replay autopsy\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Behavior/training/hosted executions: `0/0/0`\n"
        f"- Projected green cells: "
        f"`{sum(item['projected_cell_green_under_behavior_replay'] for item in projected)}/16`\n"
        f"- Minimum projected moving forward ratio: `{min(ratios):.9f}`\n"
        "- This is an algebraic falsifier, not behavior evidence. It only "
        "authorizes an exact graph contract.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
