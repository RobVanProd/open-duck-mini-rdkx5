#!/usr/bin/env python3
"""Freeze the formal 16-cell V126 sparse exact-oracle behavior screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
SCHEDULE = ANALYSIS / "winner_v126_sparse_oracle_schedule_preregistration.json"
CONTRACT = ANALYSIS / "winner_v126_sparse_oracle_schedule_cpu_contract.json"
V2 = ANALYSIS / "winner_v126_exact_oracle_cpu_contract_v2.json"
AUDIT = ANALYSIS / "winner_v126_v115_linear_price_clipping_audit.json"
PROJECTOR = ROOT / "tools/exact_torque_oracle.py"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval.py"
OUTPUT = ANALYSIS / "winner_v126_exact_oracle_behavior_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V126_EXACT_ORACLE_BEHAVIOR_PREREGISTRATION_20260724.md"
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
        raise FileExistsError("refusing to overwrite V126 behavior preregistration")
    schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if (
        schedule.get("status")
        != "PREREGISTERED_WINNER_V126_SPARSE_ORACLE_SCHEDULE"
        or contract.get("status")
        != "PASS_WINNER_V126_SPARSE_ORACLE_SCHEDULE_CPU_CONTRACT"
        or contract.get("formal_behavior_cells_executed") != 0
        or contract.get("authority", {}).get("formal_screen_cells") != 16
        or v2.get("status")
        != "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_OPTIMIZED"
        or audit.get("status")
        != "PASS_WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT"
    ):
        raise ValueError("V126 formal-screen prerequisites changed")
    rows = schedule["matrix"]["rows"]
    if len(rows) != 16 or canonical_sha256(rows) != schedule["matrix"]["sha256"]:
        raise ValueError("V126 sparse matrix changed")
    payload = {
        "schema_version": "winner_v126.exact_oracle_behavior_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V126_EXACT_ORACLE_BEHAVIOR",
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
        "policies": schedule["policies"],
        "oracle": schedule["oracle"],
        "external_inputs": schedule["external_inputs"],
        "screen_rule": {
            "uniform_mechanism": (
                "the same V124-event-scheduled exact simulator projector wraps "
                "both V121 checkpoints; rows without frozen events have an "
                "explicit empty schedule and therefore exact pass-through"
            ),
            "teacher_checkpoint": "V121_TRAIN_MATCHED_HALF",
            "teacher_requirement": (
                "all eight half cells pass the unchanged duration, candidate "
                "gait, bilateral transition, signed motion, tracking, x=0, "
                "saturation, rate, guard, dwell, trace, readback, and CPU checks"
            ),
            "peak_exception": (
                "a peak torque/current failure is permitted only when its "
                "matured source decision was explicitly empty or the event was "
                "finite-horizon prehistory; dwell remains unchanged"
            ),
            "oracle_validity": [
                "zero prediction mismatches",
                "zero nonempty residual violations",
                "zero unscheduled residual violations",
                "all scheduled maps monotone",
            ],
            "final_checkpoint": (
                "evaluated and reported with zero selection weight for earning "
                "the constrained continuation"
            ),
            "stop": (
                "if any teacher-half cell fails, close the constrained "
                "continuation without hosted training"
            ),
        },
        "decision": {
            "required_teacher_checkpoint_id": "V121_TRAIN_MATCHED_HALF",
            "required_teacher_cells": 8,
            "pass_authorizes_only": (
                "one separately preregistered constrained-continuation CPU contract"
            ),
        },
        "evidence": {
            "schedule_preregistration": {
                "path": str(SCHEDULE.relative_to(ROOT)),
                "sha256": sha256(SCHEDULE),
            },
            "schedule_cpu_contract": {
                "path": str(CONTRACT.relative_to(ROOT)),
                "sha256": sha256(CONTRACT),
            },
            "optimized_cpu_contract": {
                "path": str(V2.relative_to(ROOT)),
                "sha256": sha256(V2),
            },
            "v115_price_audit": {
                "path": str(AUDIT.relative_to(ROOT)),
                "sha256": sha256(AUDIT),
                "removed_fraction": audit["summary"]["removed_fraction"],
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
            "formal_screen_cells": 16,
            "retry": False,
            "training": False,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
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
        "# Winner-v126 exact-oracle behavior preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The frozen 16 cells wrap both V121 checkpoints with the same sparse "
        "exact simulator mechanism. All eight V121-half cells must preserve "
        "the full behavior gate. Any new unscheduled torque event fails.\n\n"
        "This authorizes one CPU-only, no-retry screen. It authorizes no "
        "training, hosted compute, Gate 5, RDK-X5, robot, torque, or motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "matrix_sha256": payload["matrix"]["sha256"],
                "output_sha256": sha256(OUTPUT),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
