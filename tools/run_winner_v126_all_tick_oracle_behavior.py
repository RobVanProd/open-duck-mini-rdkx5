#!/usr/bin/env python3
"""Run the frozen 16-cell V126 all-tick exact-oracle screen on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v126_exact_oracle_behavior import (  # noqa: E402
    BASE_PREREG,
    canonical_sha256,
    cell_stem,
    execute_cell,
    json_finite,
    missing_trace_audit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v126_all_tick_oracle_preregistration.json"
PREREG_SHA256 = (
    "4c187ad4dfb160d1d811e457a0ddd095f0d30dbfba2ca9697269d2ee3fc45745"
)
CONTRACT = ANALYSIS / "winner_v126_all_tick_oracle_cpu_contract.json"
CONTRACT_SHA256 = "__CONTRACT_SHA256__"
OUTPUT = ANALYSIS / "winner_v126_all_tick_oracle_behavior_result.json"
MARKDOWN = ANALYSIS / "WINNER_V126_ALL_TICK_ORACLE_BEHAVIOR_RESULT_20260724.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite all-tick screen: {run_root}")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite all-tick behavior result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V126_ALL_TICK_EXACT_ORACLE"
        or sha256(CONTRACT) != CONTRACT_SHA256
        or contract.get("status")
        != "PASS_WINNER_V126_ALL_TICK_ORACLE_CPU_CONTRACT"
        or contract.get("authority", {}).get("formal_screen_cells") != 16
    ):
        raise ValueError("all-tick behavior prerequisite changed")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("all-tick behavior execution requires a clean worktree")
    matrix = prereg["matrix"]["rows"]
    if (
        len(matrix) != 16
        or canonical_sha256(matrix) != prereg["matrix"]["sha256"]
        or any(row["oracle_schedule_ticks"] is not None for row in matrix)
    ):
        raise ValueError("all-tick matrix changed")
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    policy_root = Path(prereg["external_inputs"]["policy_root"])
    playground = Path(prereg["external_inputs"]["playground"])
    policies = {item["id"]: item for item in prereg["policies"]}
    for item in policies.values():
        if sha256(policy_root / item["filename"]) != item["sha256"]:
            raise ValueError(f"all-tick policy changed: {item['id']}")
    action_delta = tuple(
        float(value) for value in prereg["oracle"]["action_delta"]
    )
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir(parents=True)
    traces_root.mkdir(parents=True)
    cpu_only = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    started = time.time()
    cells = []
    for index, row in enumerate(matrix, start=1):
        stem = cell_stem(row)
        trace_path = traces_root / f"{stem}.jsonl"
        policy = policy_root / policies[row["checkpoint_id"]]["filename"]
        try:
            cell = execute_cell(
                row=row,
                base_prereg=base_prereg,
                policy=policy,
                playground=playground,
                trace_path=trace_path,
                action_delta=action_delta,
                schedule_ticks=None,
                cpu_only=cpu_only,
            )
        except Exception as exc:
            cell = {
                "schema_version": (
                    "winner_v126.all_tick_oracle_behavior_cell.v1"
                ),
                "status": "HOLD_WINNER_V126_ALL_TICK_ORACLE_BEHAVIOR_CELL",
                "pass": False,
                "failure_reasons": [
                    f"runner_exception_{type(exc).__name__}"
                ],
                "identity": dict(row),
                "policy": {"path": str(policy), "sha256": sha256(policy)},
                "simulator": {
                    "status": f"RUNNER_EXCEPTION_{type(exc).__name__}",
                    "error": str(exc),
                },
                "trace": (
                    missing_trace_audit(trace_path)
                    if not trace_path.is_file()
                    else {"path": str(trace_path)}
                ),
                "robot_clearance": False,
            }
        cell = json_finite(cell)
        cell_path = cells_root / f"{stem}.json"
        cell_path.write_text(
            json.dumps(cell, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        cell["cell_sha256"] = sha256(cell_path)
        cells.append(cell)
        print(
            json.dumps(
                {
                    "completed_cells": index,
                    "total_cells": len(matrix),
                    "passing_cells": sum(item["pass"] for item in cells),
                    "latest": {
                        "checkpoint_id": row["checkpoint_id"],
                        "plant": row["plant"],
                        "command_x_m_s": row["command_x_m_s"],
                        "pass": cell["pass"],
                        "failures": cell["failure_reasons"],
                        "oracle": cell.get("oracle"),
                    },
                }
            ),
            flush=True,
        )
    half_cells = [
        cell
        for cell in cells
        if cell["identity"]["checkpoint_id"]
        == "V121_TRAIN_MATCHED_HALF"
    ]
    validity = (
        len(cells) == 16
        and len(half_cells) == 8
        and all(
            "runner_exception" not in " ".join(cell["failure_reasons"])
            for cell in cells
        )
        and all(
            all(
                (cell.get("oracle") or {}).get("checks", {}).get(name, False)
                for name in (
                    "prediction_exact",
                    "zero_nonempty_residual_violations",
                    "zero_prediction_mismatches",
                    "zero_unscheduled_residual_violations",
                )
            )
            for cell in cells
        )
    )
    teacher_pass = validity and all(cell["pass"] for cell in half_cells)
    summary = {
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "half_cells": len(half_cells),
        "half_passing_cells": sum(cell["pass"] for cell in half_cells),
        "teacher_half_all_eight_pass": teacher_pass,
        "projected_joint_events": sum(
            int((cell.get("oracle") or {}).get("projected_joint_events", 0))
            for cell in cells
        ),
        "empty_intersection_events": sum(
            int((cell.get("oracle") or {}).get("empty_intersection_events", 0))
            for cell in cells
        ),
        "prediction_mismatches": sum(
            int(
                ((cell.get("oracle") or {}).get("summary") or {}).get(
                    "prediction_mismatches", 0
                )
            )
            for cell in cells
        ),
        "nonempty_residual_violations": sum(
            int(
                ((cell.get("oracle") or {}).get("summary") or {}).get(
                    "nonempty_residual_violations", 0
                )
            )
            for cell in cells
        ),
        "unscheduled_residual_violations": sum(
            int(
                ((cell.get("oracle") or {}).get("summary") or {}).get(
                    "unscheduled_residual_violations", 0
                )
            )
            for cell in cells
        ),
    }
    payload = {
        "schema_version": "winner_v126.all_tick_oracle_behavior_result.v1",
        "status": (
            "PASS_WINNER_V126_ALL_TICK_ORACLE_BEHAVIOR_VALID_RESULT"
            if validity
            else "INVALID_WINNER_V126_ALL_TICK_ORACLE_BEHAVIOR_RESULT"
        ),
        "decision": {
            "status": (
                "EARN_ONE_V127_CONSTRAINED_CONTINUATION_CPU_CONTRACT"
                if teacher_pass
                else "CLOSE_V127_CONSTRAINED_CONTINUATION_WITHOUT_TRAINING"
            ),
            "teacher_half_all_eight_pass": teacher_pass,
        },
        "summary": summary,
        "cells": cells,
        "wall_seconds": time.time() - started,
        "run_root": str(run_root),
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "cpu_contract": sha256(CONTRACT),
            "runner": sha256(Path(__file__).resolve()),
            "projector": sha256(ROOT / "tools/exact_torque_oracle.py"),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval_v126.py"),
        },
        "authority": {
            "v127_constrained_continuation_cpu_contract": teacher_pass,
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
        "# V126 all-tick exact-oracle behavior result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']['status']}`\n\n"
        f"Passing cells: `{summary['passing_cells']}/16`.\n\n"
        f"V121-half teacher cells: `{summary['half_passing_cells']}/8`.\n\n"
        f"Projected joint events: `{summary['projected_joint_events']}`.\n\n"
        f"Unscheduled residual violations: "
        f"`{summary['unscheduled_residual_violations']}`.\n\n"
        "This is CPU-only evidence and authorizes no training by itself.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "decision": payload["decision"],
                "summary": summary,
            }
        ),
        flush=True,
    )
    return 0 if validity else 1


if __name__ == "__main__":
    raise SystemExit(main())
