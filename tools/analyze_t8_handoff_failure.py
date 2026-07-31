#!/usr/bin/env python3
"""Localize the completed T8 handoff failure from immutable raw traces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = ANALYSIS / "t8_state_coherent_handoff_result.json"
AUDIT = ANALYSIS / "t8_state_coherent_handoff_independent_audit_v2.json"
OUTPUT = ANALYSIS / "t8_state_coherent_handoff_failure_analysis.json"
MARKDOWN = (
    ANALYSIS / "T8_STATE_COHERENT_HANDOFF_FAILURE_ANALYSIS_20260726.md"
)
JOINT_NAMES = [
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
UNIVERSAL_ACTION = np.asarray(
    [
        0.0,
        0.0,
        -0.5,
        0.25,
        0.25,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.5,
        0.25,
        0.25,
    ],
    dtype=np.float32,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T8 failure analysis")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if (
        result["status"] != "HOLD_T8_STATE_COHERENT_HANDOFF"
        or result["passing_cells"] != 12
        or audit["status"]
        != "PASS_T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT"
        or audit["issues"]
    ):
        raise RuntimeError("T8 result/audit basis is not final")

    x0 = []
    moving = []
    physical_hashes: dict[str, list[str]] = {}
    for block in result["blocks"]:
        for cell in block["result"]["cells"]:
            if cell["command_x_m_s"] > 0.0:
                moving.append(
                    {
                        "checkpoint_id": block["checkpoint_id"],
                        "fit_id": block["fit_id"],
                        "command_x_m_s": cell["command_x_m_s"],
                        "green": cell["cell_green"],
                    }
                )
                continue
            path = Path(cell["protection"]["path"])
            if sha256(path) != cell["protection"]["sha256"]:
                raise RuntimeError(f"T8 raw trace changed: {path}")
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            actions = np.asarray(
                [row["action"] for row in rows], dtype=np.float32
            )
            previous = np.asarray(
                [
                    row["policy_state_input"]["previous_action"][0]
                    for row in rows
                ],
                dtype=np.float32,
            )
            velocity = np.asarray(
                [row["sent_target_velocity_rad_s"] for row in rows],
                dtype=np.float64,
            )
            sent_excess = np.asarray(
                [row["sent_target_rate_excess_rad_s"] for row in rows],
                dtype=np.float64,
            )
            conservative_excess = np.asarray(
                [row["conservative_rate_excess_rad_s"] for row in rows],
                dtype=np.float64,
            )
            maximum_excess = np.maximum(sent_excess, conservative_excess)
            excess_ticks = np.flatnonzero(
                np.max(maximum_excess, axis=1) > 0.0
            ).astype(int)
            affected = np.flatnonzero(
                np.max(maximum_excess, axis=0) > 0.0
            ).astype(int)
            physical = np.concatenate(
                [
                    np.asarray(
                        [row[key] for row in rows], dtype=np.float32
                    ).ravel()
                    for key in (
                        "action",
                        "sent_target_rad",
                        "applied_target_rad",
                        "actual_position_rad",
                        "actuator_force_nm",
                    )
                ]
            )
            physical_hash = hashlib.sha256(physical.tobytes()).hexdigest()
            physical_hashes.setdefault(block["fit_id"], []).append(
                physical_hash
            )
            non_rate_checks = {
                "core_behavior": cell["behavior"]["core_pass"],
                "replacement_quality_summary": cell["behavior"][
                    "replacement_quality_pass"
                ],
                "duration_protection": cell["protection"][
                    "duration_protection_pass"
                ],
                "state_handoff": cell["handoff"]["all_checks_pass"],
                "nominal_readback": cell["nominal_com_readback_exact"],
            }
            x0.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "trace": {
                        "path": str(path),
                        "sha256": sha256(path),
                    },
                    "cell_green": cell["cell_green"],
                    "all_policy_actions_exact_zero": (
                        np.count_nonzero(actions) == 0
                    ),
                    "first_previous_action_matches_universal": (
                        np.array_equal(previous[0], UNIVERSAL_ACTION)
                    ),
                    "excess_ticks": excess_ticks.tolist(),
                    "affected_joints": [
                        {
                            "joint_index": int(index),
                            "joint_name": JOINT_NAMES[index],
                            "maximum_sent_target_velocity_rad_s": float(
                                np.max(velocity[:, index])
                            ),
                            "maximum_rate_excess_rad_s": float(
                                np.max(maximum_excess[:, index])
                            ),
                        }
                        for index in affected
                    ],
                    "maximum_rate_excess_rad_s": float(
                        np.max(maximum_excess)
                    ),
                    "physical_trace_sha256": physical_hash,
                    "non_rate_checks": non_rate_checks,
                }
            )

    checks = {
        "moving_cells_all_green": len(moving) == 12
        and all(item["green"] for item in moving),
        "exactly_four_x0_failures": len(x0) == 4
        and all(not item["cell_green"] for item in x0),
        "x0_actions_exact_zero": all(
            item["all_policy_actions_exact_zero"] for item in x0
        ),
        "x0_starts_from_universal_previous_action": all(
            item["first_previous_action_matches_universal"] for item in x0
        ),
        "x0_excess_confined_to_first_scored_tick": all(
            item["excess_ticks"] == [0] for item in x0
        ),
        "x0_non_rate_checks_all_green": all(
            all(item["non_rate_checks"].values()) for item in x0
        ),
        "x0_physics_checkpoint_independent_per_fit": all(
            len(set(values)) == 1 for values in physical_hashes.values()
        ),
        "same_six_pitch_joints_affected": all(
            [joint["joint_index"] for joint in item["affected_joints"]]
            == [2, 3, 4, 11, 12, 13]
            for item in x0
        ),
        "same_worst_excess_all_x0": all(
            item["maximum_rate_excess_rad_s"] == 3.989999294281006
            for item in x0
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"T8 failure did not localize exactly: {checks}")
    basis = {
        "schema_version": "open_duck.t8_handoff_failure_analysis.v1",
        "status": "T8_FAILURE_LOCALIZED_X0_PREFIX_TRANSITION",
        "result_file_sha256": sha256(RESULT),
        "result_canonical_sha256": result["result_sha256"],
        "audit_file_sha256": sha256(AUDIT),
        "audit_canonical_sha256": audit["audit_sha256"],
        "checks": checks,
        "moving_cells": moving,
        "x0_cells": x0,
        "causal_conclusion": (
            "T8's direct physical/state handoff is viable for every moving "
            "cell. At x=0 only, the graph's exact deadband action changes from "
            "the universal support action to exact zero on the first scored "
            "tick. That single commanded-target transition exceeds all six "
            "measured pitch-chain envelopes; no later tick fails."
        ),
        "selected_next_falsifier": {
            "mechanism": "COMMAND_AWARE_X0_CALIBRATION_PREFIX_BYPASS",
            "reason": (
                "x=0 requires no configuration excitation because the frozen "
                "deadband output is context-independent exact zero; startup is "
                "already paused at home. Bypassing the support prefix only for "
                "x=0 removes the proven transition while leaving all 12 green "
                "moving cells bit-for-bit unchanged."
            ),
            "new_behavior_cells_required": 4,
            "reuse_existing_green_moving_cells": 12,
            "training_steps": 0,
        },
        "authority": {
            "preregister_command_aware_zero_training_screen": True,
            "training_or_hosted_compute": False,
            "robot_rdkx5_gate5_torque_motion": False,
        },
    }
    payload = {**basis, "analysis_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T8 state-coherent handoff failure analysis",
        "",
        f"- Status: `{payload['status']}`",
        f"- Analysis SHA-256: `{payload['analysis_sha256']}`",
        "- Moving cells: `12/12 green`",
        "- x=0 cells: `0/4 green`",
        "- Training: `0 steps`",
        "",
        "All four x=0 cells complete 600 ticks, remain stationary and upright, "
        "clear tracking and servo-duration protection, preserve the response/"
        "recurrent/applied-target handoff, and command exact-zero policy action "
        "on every scored tick. Their only failed quantity is one rate event at "
        "tick 0: the previous action is the universal support vector, while the "
        "x=0 deadband output is exact zero.",
        "",
        "The same six pitch joints exceed their measured envelopes in all four "
        "cells; the worst excess is `3.989999294281006 rad/s`. From tick 1 "
        "through tick 599, excess is exactly zero. Physical x=0 traces are "
        "checkpoint-independent within each actuator fit.",
        "",
        "The next earned falsifier is therefore a command-aware startup branch: "
        "while paused/x=0, remain at home and bypass response excitation; for "
        "moving commands, retain the already-green direct T8 handoff. It needs "
        "four new x=0 CPU cells and reuses the twelve immutable audited moving "
        "cells. It earns no training by itself.",
    ]
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"analysis_sha256={payload['analysis_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
