#!/usr/bin/env python3
"""Run V160's four-cell V140 shadow-oracle census."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v126_exact_oracle_behavior as v126_behavior  # noqa: E402
from run_winner_v158_x077_shadow_census import (  # noqa: E402
    load_evaluator,
    load_trace,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v160_remaining_shadow_census_preregistration.json"
)
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = v126_behavior.BASE_PREREG
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
OUTPUT = ANALYSIS / "winner_v160_remaining_shadow_census_result.json"
MARKDOWN = ANALYSIS / "WINNER_V160_REMAINING_SHADOW_CENSUS_RESULT_20260725.md"
COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
TORQUE_LIMIT = 1.91229675


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_trace(path: Path) -> dict[str, Any]:
    rows = load_trace(path)
    forces = np.abs(
        np.asarray(
            [row["actuator_force_nm"] for row in rows], dtype=np.float64
        )
    )
    violations = np.argwhere(forces > TORQUE_LIMIT)
    events = []
    for tick_value, joint_value in violations:
        tick = int(tick_value)
        joint = int(joint_value)
        matured = next(
            (
                item
                for item in rows[tick][
                    "exact_torque_oracle_matured_predictions"
                ]
                if int(item["joint_index"]) == joint
            ),
            None,
        )
        source_tick = None if matured is None else int(matured["source_tick"])
        oracle = (
            None
            if source_tick is None
            else rows[source_tick]["exact_torque_oracle"]
        )
        events.append(
            {
                "tick": tick,
                "joint": joint,
                "actual_force_nm": float(forces[tick, joint]),
                "source_tick": source_tick,
                "source_action_delta": (
                    None
                    if oracle is None
                    else float(
                        np.asarray(oracle["final_action"])[joint]
                        - np.asarray(oracle["base_action"])[joint]
                    )
                ),
                "source_projected_joint_indices": (
                    None
                    if oracle is None
                    else oracle["projected_joint_indices"]
                ),
                "source_empty_joint_indices": (
                    None
                    if oracle is None
                    else oracle["empty_intersection_joint_indices"]
                ),
                "projected_force_nm": (
                    None
                    if matured is None
                    else float(matured["predicted_force_nm"])
                ),
            }
        )
    oracles = [
        row["exact_torque_oracle"]
        for row in rows
        if isinstance(row.get("exact_torque_oracle"), dict)
    ]
    actions = np.asarray([row["action"] for row in rows], dtype=np.float32)
    bases = np.asarray(
        [row["policy_base_action"] for row in rows], dtype=np.float32
    )
    projected_by_joint = {
        str(joint): sum(
            joint in oracle["projected_joint_indices"]
            for oracle in oracles
        )
        for joint in range(14)
    }
    all_labeled = all(
        event["source_tick"] is not None
        and event["joint"] in event["source_projected_joint_indices"]
        and event["joint"] not in event["source_empty_joint_indices"]
        and event["source_action_delta"] != 0.0
        and abs(event["projected_force_nm"]) <= TORQUE_LIMIT + 5.0e-6
        for event in events
    )
    return {
        "rows": len(rows),
        "oracle_rows": len(oracles),
        "sha256": sha256(path),
        "peak_nm": float(np.max(forces)),
        "actual_violation_events": events,
        "actual_violating_joints": sorted(
            {int(event["joint"]) for event in events}
        ),
        "projected_joint_events": int(
            sum(len(oracle["projected_joint_indices"]) for oracle in oracles)
        ),
        "projected_by_joint": projected_by_joint,
        "empty_intersection_events": int(
            sum(
                len(oracle["empty_intersection_joint_indices"])
                for oracle in oracles
            )
        ),
        "maximum_clip_linf": float(
            max(float(oracle["clip_linf"]) for oracle in oracles)
        ),
        "checks": {
            "trace_rows_exact_600": len(rows) == 600,
            "oracle_rows_exact_600": len(oracles) == 600,
            "shadow_action_never_applied": bool(
                np.array_equal(actions, bases)
            ),
            "all_actual_violations_have_safe_nonempty_precursor": all_labeled,
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
            raise FileExistsError(f"refusing to overwrite V160: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    paths = {
        "builder": TOOLS
        / "build_winner_v160_remaining_shadow_census_preregistration.py",
        "v140_result": V140_RESULT,
        "v141_result": ANALYSIS
        / "winner_v141_projected_final_behavior_result.json",
        "v144_reporting_correction": ANALYSIS
        / "winner_v144_shadow_oracle_reporting_correction.json",
        "v158_reporting_correction": ANALYSIS
        / "winner_v158_x077_shadow_census_reporting_correction.json",
        "v159_invalidity": ANALYSIS
        / "winner_v159_cadence_screen_invalidity.json",
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "composer": COMPOSER,
        "projector": PROJECTOR,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_policy": policy,
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V160_REMAINING_SHADOW_CENSUS"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V160 preregistration changed")
    evaluator = load_evaluator(evaluator_path)
    v126_behavior.ClosedLoopConfig = evaluator.ClosedLoopConfig
    shadow_fit = "P31_34_PITCH_WITH_P30_NONPITCH"

    def run_shadow(config):
        return evaluator.run_closed_loop_sim(
            dataclasses.replace(
                config,
                exact_torque_oracle_shadow_fit=v126_behavior.actuator_fit(
                    base, shadow_fit
                ),
                exact_torque_oracle_maximum_fit_passes=14,
                exact_torque_oracle_apply=False,
            )
        )

    v126_behavior.run_closed_loop_sim = run_shadow
    run_root.mkdir(parents=True)
    traces_root = run_root / "traces"
    cells_root = run_root / "cells"
    traces_root.mkdir()
    cells_root.mkdir()
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cells = []
    started = time.time()
    for index, row in enumerate(prereg["matrix"]["rows"], start=1):
        plant_slug = str(row["plant"]).lower()
        stem = (
            f"v160_v140_{plant_slug}_x"
            f"{float(row['command_x_m_s']):.3f}_seed{int(row['seed'])}"
        )
        trace_path = traces_root / f"{stem}.jsonl"
        cell = v126_behavior.execute_cell(
            row=row,
            base_prereg=base,
            policy=policy,
            playground=Path(v126["external_inputs"]["playground"]),
            trace_path=trace_path,
            action_delta=tuple(
                float(value) for value in v126["oracle"]["action_delta"]
            ),
            schedule_ticks=None,
            cpu_only=cpu_only,
        )
        cell_path = cells_root / f"{stem}.json"
        cell_path.write_text(
            json.dumps(cell, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        audit = audit_trace(trace_path)
        cells.append(
            {
                "identity": row,
                "source_cell_status": cell["status"],
                "source_cell_failure_reasons": cell["failure_reasons"],
                "source_cell_sha256": sha256(cell_path),
                "trace": audit,
            }
        )
        print(
            json.dumps(
                {
                    "completed": index,
                    "total": 4,
                    "plant": row["plant"],
                    "command_x": row["command_x_m_s"],
                    "peak_nm": audit["peak_nm"],
                    "violations": len(audit["actual_violation_events"]),
                    "projected_joint_events": audit[
                        "projected_joint_events"
                    ],
                }
            ),
            flush=True,
        )
    checks = {
        "cpu_only": cpu_only,
        "four_cells_completed": len(cells) == 4,
        "all_trace_validity_checks_green": all(
            all(cell["trace"]["checks"].values()) for cell in cells
        ),
        "all_shadow_actions_unmodified": all(
            cell["trace"]["checks"]["shadow_action_never_applied"]
            for cell in cells
        ),
        "no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v160.remaining_shadow_census_result.v1",
        "status": (
            "PASS_WINNER_V160_REMAINING_SHADOW_CENSUS"
            if not failed
            else "HOLD_WINNER_V160_REMAINING_SHADOW_CENSUS"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
            "runner": sha256(Path(__file__).resolve()),
        },
        "cells": cells,
        "aggregate": {
            "cells": len(cells),
            "cells_with_actual_violations": sum(
                bool(cell["trace"]["actual_violation_events"])
                for cell in cells
            ),
            "actual_violation_events": sum(
                len(cell["trace"]["actual_violation_events"])
                for cell in cells
            ),
            "projected_joint_events": sum(
                cell["trace"]["projected_joint_events"] for cell in cells
            ),
            "empty_intersection_events": sum(
                cell["trace"]["empty_intersection_events"] for cell in cells
            ),
            "violating_joints": sorted(
                {
                    joint
                    for cell in cells
                    for joint in cell["trace"]["actual_violating_joints"]
                }
            ),
            "worst_peak_nm": max(
                cell["trace"]["peak_nm"] for cell in cells
            ),
        },
        "artifacts": {
            "run_root": str(run_root),
            "wall_seconds": time.time() - started,
        },
        "decision": (
            "EARN_V161_V140_ON_POLICY_ORACLE_DATASET_AUDIT"
            if not failed
            else "HOLD_FOR_SHADOW_CENSUS_VALIDITY_REPAIR"
        ),
        "selection_weight": 0,
        "authority": {
            "cpu_shadow_diagnostic": True,
            "training": False,
            "hosted_training": False,
            "candidate_behavior": False,
            "policy_or_runtime_change": False,
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
        "# Winner V160 remaining shadow census result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Completed cells: `{len(cells)}/4`.\n"
        "- Cells with actual torque violations: "
        f"`{payload['aggregate']['cells_with_actual_violations']}/4`; "
        "actual events: "
        f"`{payload['aggregate']['actual_violation_events']}`.\n"
        "- Projected joint events: "
        f"`{payload['aggregate']['projected_joint_events']}`; empty "
        "intersections: "
        f"`{payload['aggregate']['empty_intersection_events']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Selection weight zero; no training, Colab, policy/runtime "
        "change, deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
