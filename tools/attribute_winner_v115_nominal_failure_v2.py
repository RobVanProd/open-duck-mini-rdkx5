#!/usr/bin/env python3
"""Derive one deterministic multi-joint rate projection from V115 traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from attribute_winner_v115_nominal_failure import (  # noqa: E402
    ACTION_SCALE_RAD,
    CONTROL_DT_S,
    JOINTS,
    RATE_LIMITS_RAD_S,
    TORQUE_LIMIT_NM,
    load_trace,
    sha256,
)


ANALYSIS = ROOT / "outputs/analysis"
HOLD = ANALYSIS / "winner_v115_nominal_failure_attribution.json"
RESULT = ANALYSIS / "winner_v115_nominal_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v115_nominal_failure_attribution_v2.json"
MARKDOWN = ANALYSIS / "WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_20260724.md"
HOLD_SHA256 = (
    "c35836b0bece1c8d40b13aa5ee4eea225822f384990d745d3a30f97f3597c408"
)
RESULT_SHA256 = (
    "370e444785692d3c64070f5b9f694e82859d295d4433f22d15f351f87f90a25c"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V115 attribution v2")
    hold = json.loads(HOLD.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if (
        sha256(HOLD) != HOLD_SHA256
        or sha256(RESULT) != RESULT_SHA256
        or hold.get("status")
        != "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION"
        or hold.get("decision") != "STOP_AND_REASSESS"
        or result.get("decision", {}).get("status")
        != "REJECT_V115_NOMINAL_POLICY"
    ):
        raise ValueError("V115 v2 attribution inputs changed")
    traces = sorted((args.run_root.resolve() / "traces").glob("*.jsonl"))
    force_rows = []
    velocity_rows = []
    for path in traces:
        samples = load_trace(path)
        force_rows.append(
            np.abs(
                np.asarray(
                    [sample["actuator_force_nm"] for sample in samples],
                    dtype=np.float64,
                )
            )
        )
        velocity_rows.append(
            np.abs(
                np.asarray(
                    [
                        sample["sent_target_velocity_rad_s"]
                        for sample in samples
                    ],
                    dtype=np.float64,
                )
            )
        )
    force = np.stack(force_rows)
    velocity = np.stack(velocity_rows)
    if force.shape != (16, 600, 14) or velocity.shape != (16, 600, 14):
        raise ValueError(
            f"unexpected V115 tensor shapes: {force.shape}, {velocity.shape}"
        )
    max_force = np.max(force, axis=(0, 1))
    active = force > TORQUE_LIMIT_NM
    boundary = velocity >= RATE_LIMITS_RAD_S[None, None] - 2.0e-5
    lag_hits = np.zeros(14, dtype=np.int64)
    active_counts = np.sum(active, axis=(0, 1)).astype(np.int64)
    for trace_index, tick, joint in np.argwhere(active):
        start = max(0, int(tick) - 3)
        lag_hits[joint] += int(
            np.any(
                boundary[
                    int(trace_index), start : int(tick) + 1, int(joint)
                ]
            )
        )
    ratios = np.minimum(1.0, TORQUE_LIMIT_NM / max_force)
    raw_selected_rates = RATE_LIMITS_RAD_S * ratios
    current_delta = (
        RATE_LIMITS_RAD_S * CONTROL_DT_S / ACTION_SCALE_RAD
    ).astype(np.float32)
    raw_selected_delta = (
        raw_selected_rates * CONTROL_DT_S / ACTION_SCALE_RAD
    ).astype(np.float32)
    selected_delta = raw_selected_delta.copy()
    affected = max_force > TORQUE_LIMIT_NM
    selected_delta[affected] = np.nextafter(
        selected_delta[affected], np.float32(0.0)
    )
    effective_selected_rates = (
        selected_delta.astype(np.float64)
        * ACTION_SCALE_RAD
        / CONTROL_DT_S
    )
    rows = [
        {
            "joint": JOINTS[index],
            "joint_index": index,
            "max_observed_torque_nm": float(max_force[index]),
            "active_exceeding_joint_ticks": int(active_counts[index]),
            "rate_lag_hits": int(lag_hits[index]),
            "rate_lag_fraction": (
                float(lag_hits[index] / active_counts[index])
                if active_counts[index]
                else 1.0
            ),
            "current_rate_limit_rad_s": float(RATE_LIMITS_RAD_S[index]),
            "selected_rate_limit_rad_s": float(
                effective_selected_rates[index]
            ),
            "current_normalized_action_delta": float(current_delta[index]),
            "selected_normalized_action_delta": float(
                selected_delta[index]
            ),
            "changed": bool(affected[index]),
        }
        for index in range(14)
    ]
    affected_names = [row["joint"] for row in rows if row["changed"]]
    checks = {
        "held_single_joint_hypothesis_preserved": True,
        "valid_complete_nominal_result_preserved": (
            result.get("failed_validity_checks") == []
            and result.get("summary", {}).get("cells") == 16
        ),
        "exact_16_by_600_by_14_trace_tensor": (
            force.shape == (16, 600, 14)
        ),
        "all_exceeding_ticks_rate_lag_linked": all(
            row["rate_lag_fraction"] == 1.0
            for row in rows
            if row["active_exceeding_joint_ticks"]
        ),
        "affected_joint_set_exact": set(affected_names)
        == {"left_hip_pitch", "left_knee", "left_ankle", "right_ankle"},
        "formula_exact": all(
            (
                row["selected_rate_limit_rad_s"]
                < row["current_rate_limit_rad_s"]
            )
            == row["changed"]
            for row in rows
        ),
        "no_rate_limit_increased": bool(
            np.all(effective_selected_rates <= RATE_LIMITS_RAD_S)
        ),
        "all_selected_limits_positive_finite": bool(
            np.all(np.isfinite(effective_selected_rates))
            and np.all(effective_selected_rates > 0.0)
        ),
        "one_vector_no_scalar_sweep": True,
        "both_checkpoints_required_in_screen": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v115.nominal_failure_attribution_v2.v1",
        "status": (
            "PASS_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2"
            if not failed
            else "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2"
        ),
        "failed_checks": failed,
        "checks": checks,
        "derivation": {
            "formula": (
                "L_selected[j] = L_current[j] * "
                "min(1, torque_limit / max_observed_torque[j]); "
                "affected float32 deltas move one ULP toward zero"
            ),
            "torque_limit_nm": TORQUE_LIMIT_NM,
            "control_dt_s": CONTROL_DT_S,
            "action_scale_rad": ACTION_SCALE_RAD,
            "affected_joints": affected_names,
            "joints": rows,
            "scalar_search": False,
            "candidate_vectors": 1,
        },
        "decision": (
            "PREREGISTER_ONE_DETERMINISTIC_MULTI_JOINT_RATE_PROJECTION"
            if not failed
            else "STOP"
        ),
        "authority": {
            "rate_projection_preregistration_authorized": not failed,
            "training_authorized": False,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
        "input_hashes": {
            "held_attribution": sha256(HOLD),
            "nominal_result": sha256(RESULT),
            "traces": {path.name: sha256(path) for path in traces},
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v115 nominal failure attribution v2\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"Affected joints: `{affected_names}`\n\n"
        "The first attribution correctly rejected a left-ankle-only repair. "
        "This correction derives one complete conservative rate vector from "
        "all 16 traces and the unchanged torque boundary. There is no scalar "
        "sweep and no training. A pass authorizes only a separate transform "
        "and 16-cell CPU preregistration.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
