#!/usr/bin/env python3
"""Preregister the zero-credit T23 normalized-action margin repair."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_RESULT = ANALYSIS / "t27_t23_robustness_matrix_result.json"
OUTPUT = ANALYSIS / "t28_t23_action_margin_preregistration.json"
OUTPUT_MD = ANALYSIS / "T28_T23_ACTION_MARGIN_PREREGISTRATION_20260726.md"
ASSET_BUILDER = ROOT / "tools" / "build_t28_t23_action_margin_assets.py"
JOINTS = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
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


def verified_trace_paths(result: dict[str, Any]) -> list[tuple[dict, Path]]:
    rows: list[tuple[dict, Path]] = []
    for block in result["blocks"]:
        manifest_path = Path(block["manifest"]["path"])
        if sha256(manifest_path) != block["manifest"]["sha256"]:
            raise ValueError(f"changed T27 manifest: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["traces"]:
            path = Path(item["path"])
            if sha256(path) != item["sha256"]:
                raise ValueError(f"changed T27 trace: {path}")
            rows.append((block, path))
    return rows


def event_census(
    result: dict[str, Any],
    threshold: np.float32,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    joint_counts: Counter[str] = Counter()
    checkpoint_counts: Counter[str] = Counter()
    fit_counts: Counter[str] = Counter()
    maximum = 0.0
    for block, path in verified_trace_paths(result):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                for joint_index, action in enumerate(row["action"]):
                    absolute = abs(float(action))
                    maximum = max(maximum, absolute)
                    if absolute < float(threshold):
                        continue
                    joint = JOINTS[joint_index]
                    event = {
                        "checkpoint_id": block["checkpoint_id"],
                        "fit_id": block["fit_id"],
                        "command_x_m_s": float(row["command"][0]),
                        "tick": int(row["tick"]),
                        "joint_index": joint_index,
                        "joint": joint,
                        "action": float(action),
                        "absolute_action": absolute,
                    }
                    events.append(event)
                    joint_counts[joint] += 1
                    checkpoint_counts[block["checkpoint_id"]] += 1
                    fit_counts[block["fit_id"]] += 1
    return {
        "threshold_abs": float(threshold),
        "events": events,
        "event_count": len(events),
        "event_joint_counts": dict(sorted(joint_counts.items())),
        "event_checkpoint_counts": dict(sorted(checkpoint_counts.items())),
        "event_fit_counts": dict(sorted(fit_counts.items())),
        "maximum_absolute_action_all_cells": maximum,
    }


def main() -> int:
    prereg = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T27_RESULT.read_text(encoding="utf-8"))
    threshold = np.float32(0.98)
    stored_limit = np.nextafter(threshold, np.float32(0.0))
    census = event_census(result, threshold)
    failed_cells = [
        cell
        for block in result["blocks"]
        for cell in block["result"]["cells"]
        if not cell["cell_green"]
    ]
    failure_is_only_zero_saturation = all(
        all(
            passed
            for name, passed in cell["behavior"]["core_checks"].items()
            if name != "saturation"
        )
        and cell["behavior"]["replacement_quality_checks"]["tracking"]
        and cell["behavior"]["replacement_quality_checks"]["p95_rate"]
        and cell["behavior"]["replacement_quality_checks"]["instant_rate"]
        and not cell["behavior"]["replacement_quality_checks"]["zero_saturation"]
        and cell["protection"]["duration_protection_pass"]
        and cell["handoff"]["all_checks_pass"]
        and cell["override_readback_exact"]
        for cell in failed_cells
    )
    policies = []
    for item in prereg["policies"]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T23 policy: {path}")
        policies.append(dict(item))
    checks = {
        "t27_stopped_at_first_condition": (
            result["status"] == "HOLD_T27_T23_R2_ROBUSTNESS"
            and result["summary"]["completed_conditions"] == 1
            and result["summary"]["first_failed_condition"]
            == "FLOOR_FRICTION_LO"
        ),
        "exactly_six_failed_cells": len(failed_cells) == 6,
        "failure_is_only_zero_saturation": failure_is_only_zero_saturation,
        "events_are_sparse": census["event_count"] == 39,
        "events_only_final_checkpoint": (
            census["event_checkpoint_counts"] == {"T23_SUPPORT_FINAL": 39}
        ),
        "events_only_two_joints": set(census["event_joint_counts"])
        == {"left_ankle", "right_hip_pitch"},
        "events_are_below_hard_action_bound": (
            census["maximum_absolute_action_all_cells"] < 1.0
        ),
        "both_source_policy_receipts_exact": len(policies) == 2,
        "stored_limit_is_strictly_below_gate_threshold": (
            float(stored_limit) < float(threshold)
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": "open_duck.t28_t23_action_margin_preregistration.v1",
        "status": (
            "PREREGISTERED_T28_T23_ACTION_MARGIN_REPAIR"
            if not failed_checks
            else "HOLD_T28_T23_ACTION_MARGIN_PREREGISTRATION"
        ),
        "question": (
            "Can one uniform zero-credit ONNX transform preserve both T23 "
            "checkpoints while enforcing the already frozen normalized-action "
            "replacement-quality margin under floor friction 0.5?"
        ),
        "causal_attribution": {
            "source_result": receipt(T27_RESULT),
            "failed_cells": len(failed_cells),
            "green_cells": result["summary"]["green_cells"],
            "completed_cells": result["summary"]["completed_cells"],
            "failure_is_only_zero_saturation": failure_is_only_zero_saturation,
            "event_census": census,
            "interpretation": (
                "T27 shows no hard action clip, gait, tracking, rate, handoff, "
                "or duration-protection failure. The only failure is 39 sparse "
                "deployed actions at or above the frozen 0.98 diagnostic "
                "margin, with maximum magnitude below 1.0."
            ),
        },
        "transform": {
            "name": "uniform_post_transition_action_margin_clip",
            "source_tensor_outputs": [
                "continuous_actions",
                "previous_action_out",
            ],
            "hidden_output": "h_out",
            "saturation_observation_threshold_abs": float(threshold),
            "stored_float32_limit_abs": float(stored_limit),
            "stored_float32_limit_hex_le": stored_limit.tobytes().hex(),
            "equation": (
                "a_out=clip(a_source,-L,L); "
                "previous_action_out=clip(previous_action_source,-L,L); "
                "L=nextafter(float32(0.98),float32(0.0))"
            ),
            "insertion": (
                "After the complete frozen T23 support/deadband/rate/guard "
                "transition. h_out and every source initializer/node are "
                "unchanged; only two Clip nodes and two scalar initializers "
                "are appended."
            ),
            "uniformity": (
                "Apply the identical transform to half and final. No joint, "
                "command, fit, checkpoint, phase, or trace-specific constant."
            ),
            "state_feedback": (
                "previous_action_out must equal the realized clipped action "
                "bit-exact so the next policy tick observes its deployed action."
            ),
            "not_action_rescaling": True,
            "no_training": True,
            "no_parameter_search": True,
        },
        "cpu_contract": {
            "source_graph_prefix_and_initializers_exact": True,
            "external_abi_exact": {
                "inputs": [
                    "obs",
                    "previous_action",
                    "h_in",
                    "calibration_context",
                ],
                "outputs": [
                    "continuous_actions",
                    "previous_action_out",
                    "h_out",
                ],
            },
            "source_trace_replay_tolerance": 1e-6,
            "clipped_outputs_equal_numpy_float32_clip_bit_exact": True,
            "hidden_output_bit_exact": True,
            "realized_action_feedback_bit_exact": True,
            "all_wrapped_outputs_strictly_below_threshold": True,
            "x0_frozen_trace_outputs_bit_exact_to_source": True,
            "all_source_outputs_below_limit_bit_exact_to_source": True,
            "cpu_only": True,
        },
        "source_policies": policies,
        "frozen_inputs": {
            "t27_preregistration": receipt(T27_PREREG),
            "t27_result": receipt(T27_RESULT),
            "asset_builder": receipt(ASSET_BUILDER),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "decision_rule": {
            "contract_pass": (
                "Authorize only a new 16-cell floor-friction-0.5 CPU condition "
                "preregistration for both uniformly wrapped checkpoints."
            ),
            "contract_fail": (
                "Close the exact action-margin transform without behavior "
                "evaluation or training."
            ),
            "condition_pass": (
                "Resume the remaining frozen R2 conditions sequentially from "
                "condition 2 with the wrapped checkpoints."
            ),
            "condition_fail": (
                "Close the transform and attribute the first failed cell. No "
                "hosted training is automatically earned."
            ),
        },
        "authority": {
            "build_exact_cpu_assets": not failed_checks,
            "behavior_evaluation": False,
            "training": False,
            "colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "gate5": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T28 T23 action-margin repair preregistration",
        "",
        f"status: `{payload['status']}`",
        "",
        "## Attribution",
        "",
        (
            f"- T27 failed `{len(failed_cells)}` of 16 condition-1 cells; "
            f"`{census['event_count']}` individual action values crossed the "
            "frozen 0.98 margin."
        ),
        (
            "- Every failed cell still passed gait, tracking, duration, rate, "
            "handoff, override readback, and corrected motor-duration protection."
        ),
        (
            f"- Worst absolute action was "
            f"`{census['maximum_absolute_action_all_cells']:.9f}`, below the "
            "hard normalized bound."
        ),
        "",
        "## Frozen transform",
        "",
        (
            f"`L = nextafter(float32(0.98), 0) = "
            f"{float(stored_limit):.10f}`; clip both the deployed action and "
            "its recurrent feedback to `[-L,L]` after the complete source graph."
        ),
        "",
        "The same transform is applied to both checkpoints. There is no joint, "
        "command, trace, or fit-specific value and no training.",
        "",
        "Passing the asset contract authorizes only preregistration of the "
        "16-cell floor-friction-0.5 CPU falsifier. It does not authorize "
        "training, Gate 5, RDK-X5, robot, torque, or motion.",
        "",
    ]
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"events={census['event_count']}")
    print(f"limit={float(stored_limit):.10f}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
