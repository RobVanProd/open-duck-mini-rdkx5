#!/usr/bin/env python3
"""Preregister the all-tick correction to the sparse V126 oracle screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
SPARSE_PREREG = (
    ANALYSIS / "winner_v126_exact_oracle_behavior_preregistration.json"
)
SPARSE_RESULT = (
    ANALYSIS / "winner_v126_exact_oracle_behavior_result.json"
)
ISOLATION = ANALYSIS / "winner_v126_evaluator_isolation_amendment.json"
PROJECTOR = ROOT / "tools/exact_torque_oracle.py"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval_v126.py"
OUTPUT = ANALYSIS / "winner_v126_all_tick_oracle_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V126_ALL_TICK_ORACLE_PREREGISTRATION_20260724.md"
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
        raise FileExistsError("refusing to overwrite all-tick preregistration")
    sparse_prereg = json.loads(SPARSE_PREREG.read_text(encoding="utf-8"))
    sparse_result = json.loads(SPARSE_RESULT.read_text(encoding="utf-8"))
    isolation = json.loads(ISOLATION.read_text(encoding="utf-8"))
    if (
        sparse_result.get("status")
        != "PASS_WINNER_V126_EXACT_ORACLE_BEHAVIOR_VALID_RESULT"
        or sparse_result.get("summary", {}).get(
            "teacher_half_all_eight_pass"
        )
        is not True
        or sparse_result.get("summary", {}).get(
            "unscheduled_residual_violations"
        )
        != 5
        or isolation.get("status")
        != "PASS_WINNER_V126_EVALUATOR_ISOLATION_AMENDMENT"
    ):
        raise ValueError("all-tick causal prerequisite changed")

    rows = []
    for source in sparse_prereg["matrix"]["rows"]:
        row = dict(source)
        row["oracle_schedule_ticks"] = None
        rows.append(row)
    payload = {
        "schema_version": (
            "winner_v126.all_tick_exact_oracle_preregistration.v1"
        ),
        "status": "PREREGISTERED_WINNER_V126_ALL_TICK_EXACT_ORACLE",
        "causal_correction": {
            "source_result": {
                "path": str(SPARSE_RESULT.relative_to(ROOT)),
                "sha256": sha256(SPARSE_RESULT),
            },
            "sparse_result_cells": 16,
            "sparse_result_passing_cells": 13,
            "teacher_half_cells": 8,
            "teacher_half_passing_cells": 8,
            "new_unscheduled_residual_violations": 5,
            "diagnosis": (
                "The preregistered sparse optimization was falsified: exact "
                "corrections changed later trajectories and produced five "
                "new torque events outside the frozen event schedule. This "
                "is a scheduling-screen failure, not a policy-training result."
            ),
            "correction": (
                "At every moving-command tick, run one exact simulator "
                "horizon probe. Invoke the already contracted monotone "
                "projection only when that probe predicts an exceedance. "
                "x=0 retains its exact deadband bypass."
            ),
            "not_allowed": (
                "No event-window expansion, iterative schedule repair, "
                "coefficient search, or reuse of a behavior outcome."
            ),
        },
        "nonformal_contract": {
            "checkpoint_id": "V121_TRAIN_MATCHED_FINAL",
            "plant": "P31_34_PITCH_WITH_P30_NONPITCH",
            "command_x_m_s": 0.074,
            "seed": 167931544,
            "duration_ticks": 64,
            "reason": (
                "The sparse trace's first new unscheduled exceedance matured "
                "at tick 59; 64 ticks exercise its last controllable decision."
            ),
            "required": {
                "scheduled_ticks": 64,
                "schedule_bypass_ticks": 0,
                "at_least_one_projection": True,
                "prediction_mismatches": 0,
                "nonempty_residual_violations": 0,
                "unscheduled_residual_violations": 0,
            },
        },
        "matrix": {
            "rows": rows,
            "cells": len(rows),
            "sha256": canonical_sha256(rows),
            "axes": {
                "checkpoints": 2,
                "plants": 2,
                "commands_m_s": [0.0, 0.074, 0.077, 0.08],
                "seed": 167931544,
                "duration_ticks": 600,
            },
        },
        "policies": sparse_prereg["policies"],
        "oracle": {
            **sparse_prereg["oracle"],
            "schedule": None,
            "moving_tick_rule": (
                "one exact base-action horizon rollout at every tick; "
                "projection only on predicted exceedance"
            ),
        },
        "external_inputs": sparse_prereg["external_inputs"],
        "formal_rule": {
            "exact_all_tick_validity": [
                "zero prediction mismatches",
                "zero nonempty residual violations",
                "zero unscheduled residual violations",
                "all action-to-force maps used for projection are monotone",
            ],
            "teacher_requirement": (
                "all eight V121-half cells preserve every frozen behavior "
                "criterion"
            ),
            "final_checkpoint": (
                "evaluated and reported; it has zero checkpoint-selection "
                "weight for earning the continuation"
            ),
            "pass_authorizes_only": (
                "one separately preregistered V127 constrained-continuation "
                "CPU contract"
            ),
        },
        "evidence": {
            "sparse_preregistration": {
                "path": str(SPARSE_PREREG.relative_to(ROOT)),
                "sha256": sha256(SPARSE_PREREG),
            },
            "evaluator_isolation": {
                "path": str(ISOLATION.relative_to(ROOT)),
                "sha256": sha256(ISOLATION),
            },
            "projector": {
                "path": str(PROJECTOR.relative_to(ROOT)),
                "sha256": sha256(PROJECTOR),
            },
            "evaluator": {
                "path": str(EVALUATOR.relative_to(ROOT)),
                "sha256": sha256(EVALUATOR),
            },
        },
        "authority": {
            "nonformal_contract_runs": 1,
            "formal_screen_cells_after_contract_pass": 16,
            "retry_of_sparse_screen": False,
            "training": False,
            "hosted_or_colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# V126 all-tick exact-oracle preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The sparse optimization is closed by its own falsifier: five new "
        "unscheduled torque events. The correction probes the exact simulator "
        "at every moving tick, with no event-window tuning.\n\n"
        "This authorizes one 64-tick CPU contract and, only after a pass, one "
        "frozen 16-cell CPU screen. It authorizes no training or robot work.\n",
        encoding="utf-8",
    )
    print(OUTPUT)
    print(sha256(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
