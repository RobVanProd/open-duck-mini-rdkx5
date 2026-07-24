#!/usr/bin/env python3
"""Freeze the V124-event-scheduled V126 exact-oracle screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V126 = ANALYSIS / "winner_v126_exact_oracle_preregistration.json"
V126_V2 = ANALYSIS / "winner_v126_exact_oracle_cpu_contract_v2.json"
V115_AUDIT = ANALYSIS / "winner_v126_v115_linear_price_clipping_audit.json"
V124 = ANALYSIS / "winner_v124_predictive_torque_s0_s2_compact_result.json"
PROJECTOR = ROOT / "tools/exact_torque_oracle.py"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval.py"
OUTPUT = ANALYSIS / "winner_v126_sparse_oracle_schedule_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V126_SPARSE_ORACLE_SCHEDULE_PREREGISTRATION_20260724.md"
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
        raise FileExistsError("refusing to overwrite sparse-oracle preregistration")
    base = json.loads(V126.read_text(encoding="utf-8"))
    contract = json.loads(V126_V2.read_text(encoding="utf-8"))
    audit = json.loads(V115_AUDIT.read_text(encoding="utf-8"))
    v124 = json.loads(V124.read_text(encoding="utf-8"))
    if (
        contract.get("status")
        != "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_OPTIMIZED"
        or audit.get("status")
        != "PASS_WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT"
        or v124.get("status")
        != "HOLD_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
        or v124.get("s1", {}).get("pass") is not True
    ):
        raise ValueError("sparse-oracle prerequisites changed")
    events = v124["s1"]["event_summary"]["v121_all_events"]
    schedule_by_filename: dict[str, set[int]] = {}
    for event in events:
        schedule_by_filename.setdefault(event["filename"], set()).add(
            int(event["decision_tick"])
        )
    if len(events) != 15:
        raise ValueError("V124 event population changed")
    rows = []
    for source in base["formal_screen"]["matrix"]["rows"]:
        checkpoint = (
            "half"
            if source["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
            else "final"
        )
        plant = str(source["plant"]).lower()
        filename = (
            f"v121_train_matched_{checkpoint}_{plant}_"
            f"x{float(source['command_x_m_s']):.3f}_"
            f"seed{int(source['seed'])}.jsonl"
        )
        rows.append(
            {
                **source,
                "oracle_schedule_ticks": sorted(
                    schedule_by_filename.get(filename, set())
                ),
            }
        )
    scheduled = sum(len(row["oracle_schedule_ticks"]) for row in rows)
    if scheduled != len({(event["filename"], event["decision_tick"]) for event in events}):
        raise ValueError("V124 event schedule did not map exactly to V121 matrix")
    payload = {
        "schema_version": "winner_v126.sparse_oracle_schedule_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V126_SPARSE_ORACLE_SCHEDULE",
        "causal_selection": {
            "source": "all 15 V121 torque events frozen by V124 S1",
            "schedule": (
                "run the exact simulator projection only at each event's "
                "already frozen source decision tick"
            ),
            "not_scheduled": (
                "pass the policy action through exactly; any resulting torque "
                "exceedance outside a matured scheduled prediction is an "
                "unscheduled residual and fails the screen"
            ),
            "reason": (
                "this is a zero-credit compute optimization, not a safety "
                "assumption: it can reject on a new event but cannot hide one"
            ),
            "events": events,
            "unique_scheduled_decisions": scheduled,
        },
        "oracle": base["oracle"],
        "matrix": {
            "rows": rows,
            "cells": len(rows),
            "sha256": canonical_sha256(rows),
        },
        "policies": base["formal_screen"]["policies"],
        "external_inputs": base["external_inputs"],
        "nonformal_schedule_contract": {
            "checkpoint_id": "V121_TRAIN_MATCHED_FINAL",
            "plant": "P30_ALL_JOINT",
            "command_x_m_s": 0.077,
            "seed": 167931544,
            "duration_ticks": 32,
            "schedule_ticks": [18, 27, 28],
            "required": [
                "at least one exact projection",
                "zero prediction mismatches",
                "zero nonempty residual violations",
                "zero unscheduled residual violations",
                "duration complete on CPU",
            ],
        },
        "evidence": {
            "optimized_cpu_contract": {
                "path": str(V126_V2.relative_to(ROOT)),
                "sha256": sha256(V126_V2),
            },
            "v115_price_audit": {
                "path": str(V115_AUDIT.relative_to(ROOT)),
                "sha256": sha256(V115_AUDIT),
                "removed_fraction": audit["summary"]["removed_fraction"],
            },
            "v124_event_autopsy": {
                "path": str(V124.relative_to(ROOT)),
                "sha256": sha256(V124),
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
        "decision": {
            "formal_screen_only_after_nonformal_contract_pass": True,
            "teacher_checkpoint_id": "V121_TRAIN_MATCHED_HALF",
            "teacher_cells_required": 8,
            "hosted_training_now": 0,
        },
        "authority": {
            "nonformal_schedule_contract_runs": 1,
            "formal_screen_cells_after_contract_pass": 16,
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
        "# Winner-v126 sparse-oracle schedule preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Scheduled exact decisions: `{scheduled}` from all `15` frozen V121 "
        "events. Every unscheduled torque exceedance is an automatic failure; "
        "the schedule cannot hide a new event.\n\n"
        "One 32-tick nonformal CPU contract must exercise a real projection "
        "before the 16-cell screen. No training, hosted compute, Gate 5, "
        "RDK-X5, robot, torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "scheduled_decisions": scheduled,
                "matrix_sha256": payload["matrix"]["sha256"],
                "output_sha256": sha256(OUTPUT),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
