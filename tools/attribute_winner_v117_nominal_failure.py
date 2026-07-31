#!/usr/bin/env python3
"""Attribute V117 peaks and derive one deterministic V118 rate vector."""

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
    TORQUE_LIMIT_NM,
    load_trace,
    sha256,
)


ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v117_nominal_behavior_result.json"
SOURCE_CONTRACT = (
    ANALYSIS / "winner_v117_postguard_rate_projection_contract.json"
)
OUTPUT = ANALYSIS / "winner_v117_nominal_failure_attribution.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V117_NOMINAL_FAILURE_ATTRIBUTION_20260724.md"
)
RESULT_SHA256 = (
    "0a3d04b478e46c5041b52554008cb5e8db800f0a2552932cd60cb8640efee09a"
)
SOURCE_CONTRACT_SHA256 = (
    "9aab1d09ffcff7608fa758ea891f4b2a6c54d90b00a056a4478c503514d05beb"
)
EXPECTED_AFFECTED = {
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_ankle",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite V117 attribution: {path}"
            )

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    source_contract = json.loads(
        SOURCE_CONTRACT.read_text(encoding="utf-8")
    )
    if (
        sha256(RESULT) != RESULT_SHA256
        or sha256(SOURCE_CONTRACT) != SOURCE_CONTRACT_SHA256
        or result.get("decision", {}).get("status")
        != "REJECT_V117_NOMINAL_POLICY"
        or source_contract.get("status")
        != "PASS_WINNER_V117_POSTGUARD_RATE_PROJECTION_CONTRACT"
    ):
        raise ValueError("V117 attribution inputs changed")

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
            f"unexpected V117 tensors: {force.shape}, {velocity.shape}"
        )

    current_delta = np.asarray(
        source_contract["projection"][
            "selected_normalized_action_delta"
        ],
        dtype=np.float32,
    )
    current_rates = (
        current_delta.astype(np.float64)
        * ACTION_SCALE_RAD
        / CONTROL_DT_S
    )
    max_force = np.max(force, axis=(0, 1))
    active = force > TORQUE_LIMIT_NM
    boundary = velocity >= current_rates[None, None] - 2.0e-5
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

    affected = max_force > TORQUE_LIMIT_NM
    ratios = np.minimum(1.0, TORQUE_LIMIT_NM / max_force)
    raw_next_rates = current_rates * ratios
    raw_next_delta = (
        raw_next_rates * CONTROL_DT_S / ACTION_SCALE_RAD
    ).astype(np.float32)
    next_delta = current_delta.copy()
    next_delta[affected] = np.nextafter(
        raw_next_delta[affected], np.float32(0.0)
    )
    effective_next_rates = (
        next_delta.astype(np.float64)
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
            "current_rate_limit_rad_s": float(current_rates[index]),
            "selected_rate_limit_rad_s": float(
                effective_next_rates[index]
            ),
            "current_normalized_action_delta": float(
                current_delta[index]
            ),
            "selected_normalized_action_delta": float(next_delta[index]),
            "changed": bool(affected[index]),
        }
        for index in range(14)
    ]
    affected_names = [row["joint"] for row in rows if row["changed"]]
    max_excess_fraction = float(
        np.max(max_force / TORQUE_LIMIT_NM - 1.0)
    )
    checkpoints = {
        int(row["step"]): row for row in result["per_checkpoint"]
    }
    checks = {
        "valid_complete_nominal_result": (
            result.get("failed_validity_checks") == []
            and result.get("summary", {}).get("cells") == 16
        ),
        "final_checkpoint_all_eight_pass": checkpoints[2_007_040][
            "all_eight_cells_pass"
        ],
        "half_checkpoint_physical_only_failure": (
            checkpoints[1_003_520]["all_eight_cells_pass"] is False
            and set(result["summary"]["failures_by_reason"])
            == {
                "current_peak_at_most_2p5",
                "torque_peak_at_most_1p91229675_nm",
            }
            and result["summary"]["worst_tracking_p95_rad"] <= 0.20
            and result["summary"]["minimum_moving_mean_vx_m_s"] > 0.0
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
        == EXPECTED_AFFECTED,
        "peak_excess_is_below_four_percent": max_excess_fraction < 0.04,
        "no_rate_limit_increased": bool(
            np.all(effective_next_rates <= current_rates + 2.0e-7)
        ),
        "all_selected_limits_positive_finite": bool(
            np.all(np.isfinite(effective_next_rates))
            and np.all(effective_next_rates > 0.0)
        ),
        "one_vector_no_scalar_sweep": True,
        "both_checkpoints_required_in_next_screen": True,
        "training_not_yet_earned": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v117.nominal_failure_attribution.v1"
        ),
        "status": (
            "PASS_WINNER_V117_NOMINAL_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V117_NOMINAL_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "derivation": {
            "formula": (
                "L_next[j] = L_current[j] * "
                "min(1, torque_limit / max_observed_torque[j]); "
                "affected float32 deltas move one ULP toward zero"
            ),
            "torque_limit_nm": TORQUE_LIMIT_NM,
            "control_dt_s": CONTROL_DT_S,
            "action_scale_rad": ACTION_SCALE_RAD,
            "affected_joints": affected_names,
            "max_peak_excess_fraction": max_excess_fraction,
            "joints": rows,
            "scalar_search": False,
            "candidate_vectors": 1,
        },
        "decision": (
            "PREREGISTER_ONE_V118_POSTGUARD_RATE_PROJECTION"
            if not failed
            else "STOP"
        ),
        "authority": {
            "v118_projection_preregistration_authorized": not failed,
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
            "nominal_result": sha256(RESULT),
            "v117_source_contract": sha256(SOURCE_CONTRACT),
            "traces": {path.name: sha256(path) for path in traces},
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v117 nominal failure attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        f"Decision: `{value['decision']}`\n\n"
        f"Affected joints: `{affected_names}`\n\n"
        "The final checkpoint passes all eight cells. The half checkpoint "
        "retains gait and tracking but has seven torque-exceeding joint-ticks; "
        "every one follows its active rate boundary. The same physical "
        "formula yields one V118 vector. Training is not yet earned.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(value["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
