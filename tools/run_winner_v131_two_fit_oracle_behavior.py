#!/usr/bin/env python3
"""Run the frozen eight-cell V131 two-fit oracle teacher screen."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v126_exact_oracle_behavior as v126_behavior  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v131_two_fit_oracle_behavior_preregistration.json"
CPU_CONTRACT = ANALYSIS / "winner_v131_two_fit_oracle_cpu_contract.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = v126_behavior.BASE_PREREG
OUTPUT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_RESULT_20260724.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v131_two_fit", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V131 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def robust_trace_audit(path: Path, moving: bool) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    oracle_rows = [
        row["exact_torque_oracle"]
        for row in rows
        if isinstance(row.get("exact_torque_oracle"), dict)
    ]
    robust = [row for row in oracle_rows if "robust_safe" in row]
    bypass = [
        row
        for row in oracle_rows
        if row.get("status") == "BYPASS_EXACT_X0_DEADBAND"
    ]
    return {
        "rows": len(rows),
        "oracle_rows": len(oracle_rows),
        "robust_rows": len(robust),
        "robust_safe_rows": sum(bool(row["robust_safe"]) for row in robust),
        "x0_bypass_rows": len(bypass),
        "empty_intersection_events": sum(
            len(row["empty_intersection_joint_indices"]) for row in robust
        ),
        "projected_ticks": sum(
            float(row["clip_linf"]) > 0.0 for row in robust
        ),
        "projected_joint_events": sum(
            len(row["projected_joint_indices"]) for row in robust
        ),
        "clip_linf_max": max(
            (float(row["clip_linf"]) for row in robust), default=0.0
        ),
        "checks": {
            "complete_600": len(rows) == len(oracle_rows) == 600,
            "moving_all_robust": (
                not moving
                or (len(robust) == 600 and all(row["robust_safe"] for row in robust))
            ),
            "x0_all_exact_bypass": (
                moving or (len(bypass) == 600 and len(robust) == 0)
            ),
            "zero_empty_intersections": all(
                not row["empty_intersection_joint_indices"] for row in robust
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V131 behavior: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("V131 behavior requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    contract = json.loads(CPU_CONTRACT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "cpu_contract": sha256(CPU_CONTRACT),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "two_fit_projector": sha256(
            ROOT / "tools/exact_torque_oracle_two_fit.py"
        ),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or contract.get("decision")
        != "EARN_ONE_V131_FINAL_TEACHER_8_CELL_PREREGISTRATION"
    ):
        raise ValueError("V131 behavior preregistration changed")
    evaluator = load_evaluator(evaluator_path)
    v126_behavior.ClosedLoopConfig = evaluator.ClosedLoopConfig
    matrix = prereg["matrix"]["rows"]
    if len(matrix) != 8:
        raise ValueError("V131 behavior matrix must contain eight cells")
    policies = {row["id"]: row for row in v126["policies"]}
    policy_root = Path(v126["external_inputs"]["policy_root"])
    playground = Path(v126["external_inputs"]["playground"])
    action_delta = tuple(
        float(value) for value in v126["oracle"]["action_delta"]
    )
    run_root.mkdir(parents=True)
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir()
    traces_root.mkdir()
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    started = time.time()
    cells = []
    for index, row in enumerate(matrix, start=1):
        active = str(row["plant"])
        shadow = (
            "P31_34_PITCH_WITH_P30_NONPITCH"
            if active == "P30_ALL_JOINT"
            else "P30_ALL_JOINT"
        )

        def run_with_shadow(config, *, shadow_plant=shadow):
            return evaluator.run_closed_loop_sim(
                dataclasses.replace(
                    config,
                    exact_torque_oracle_shadow_fit=(
                        v126_behavior.actuator_fit(
                            base_prereg, shadow_plant
                        )
                    ),
                    exact_torque_oracle_maximum_fit_passes=14,
                )
            )

        v126_behavior.run_closed_loop_sim = run_with_shadow
        stem = v126_behavior.cell_stem(row)
        trace_path = traces_root / f"{stem}.jsonl"
        policy_spec = policies[row["checkpoint_id"]]
        policy = policy_root / policy_spec["filename"]
        cell = v126_behavior.execute_cell(
            row=row,
            base_prereg=base_prereg,
            policy=policy,
            playground=playground,
            trace_path=trace_path,
            action_delta=action_delta,
            schedule_ticks=None,
            cpu_only=cpu_only,
        )
        robust = robust_trace_audit(
            trace_path, moving=float(row["command_x_m_s"]) >= 0.01
        )
        cell["two_fit_oracle"] = robust
        for name, passed in robust["checks"].items():
            cell["metrics"]["checks"][f"two_fit_{name}"] = passed
            if not passed:
                cell["failure_reasons"].append(f"two_fit_{name}")
        cell["failure_reasons"] = sorted(set(cell["failure_reasons"]))
        cell["pass"] = not cell["failure_reasons"]
        cell["status"] = (
            "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_CELL"
            if cell["pass"]
            else "HOLD_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_CELL"
        )
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
                    "total_cells": 8,
                    "passing_cells": sum(item["pass"] for item in cells),
                    "latest": {
                        "plant": active,
                        "command_x_m_s": row["command_x_m_s"],
                        "pass": cell["pass"],
                        "failures": cell["failure_reasons"],
                        "two_fit_oracle": robust,
                    },
                }
            ),
            flush=True,
        )
    validity = (
        len(cells) == 8
        and all(cell["two_fit_oracle"]["rows"] == 600 for cell in cells)
        and all(
            "runner_exception" not in " ".join(cell["failure_reasons"])
            for cell in cells
        )
    )
    teacher_pass = validity and all(cell["pass"] for cell in cells)
    summary = {
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "robust_rows": sum(
            cell["two_fit_oracle"]["robust_rows"] for cell in cells
        ),
        "robust_safe_rows": sum(
            cell["two_fit_oracle"]["robust_safe_rows"] for cell in cells
        ),
        "x0_bypass_rows": sum(
            cell["two_fit_oracle"]["x0_bypass_rows"] for cell in cells
        ),
        "empty_intersection_events": sum(
            cell["two_fit_oracle"]["empty_intersection_events"]
            for cell in cells
        ),
        "projected_ticks": sum(
            cell["two_fit_oracle"]["projected_ticks"] for cell in cells
        ),
        "projected_joint_events": sum(
            cell["two_fit_oracle"]["projected_joint_events"]
            for cell in cells
        ),
        "clip_linf_max": max(
            cell["two_fit_oracle"]["clip_linf_max"] for cell in cells
        ),
    }
    payload = {
        "schema_version": "winner_v131.two_fit_oracle_behavior_result.v1",
        "status": (
            "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            if validity
            else "INVALID_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_RESULT"
        ),
        "failed_validity_checks": (
            [] if validity else ["eight_complete_nonexception_cells"]
        ),
        "decision": (
            "EARN_ONE_V132_ROBUST_TEACHER_DATASET_AUDIT"
            if teacher_pass
            else "CLOSE_TWO_FIT_TEACHER_WITHOUT_TRAINING"
        ),
        "summary": summary,
        "cells": cells,
        "wall_seconds": time.time() - started,
        "run_root": str(run_root),
        "input_hashes": observed_hashes,
        "authority": {
            "robust_teacher_dataset_audit": teacher_pass,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V131 two-fit oracle behavior\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Decision: `{payload['decision']}`\n"
        f"- Passing cells: `{summary['passing_cells']}/8`.\n"
        f"- Robust-safe moving rows: `{summary['robust_safe_rows']}` / "
        f"`{summary['robust_rows']}`.\n"
        "- CPU simulation only; no training or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if validity else 1


if __name__ == "__main__":
    raise SystemExit(main())
