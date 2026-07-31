#!/usr/bin/env python3
"""Run V158's shadow-only x=.077 causal census."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
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


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v158_x077_shadow_census_preregistration.json"
COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = v126_behavior.BASE_PREREG
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V155_RESULT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
V157_RESULT = ANALYSIS / "winner_v157_dual_checkpoint_nominal_result.json"
OUTPUT = ANALYSIS / "winner_v158_x077_shadow_census_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V158_X077_SHADOW_CENSUS_RESULT_20260725.md"
)
TORQUE_LIMIT = 1.91229675


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v158_x077_shadow", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V158 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_trace(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


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
            raise FileExistsError(f"refusing to overwrite V158: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    paths = {
        "runner": Path(__file__).resolve(),
        "composer": COMPOSER,
        "projector": PROJECTOR,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v140_result": V140_RESULT,
        "v155_result": V155_RESULT,
        "v157_result": V157_RESULT,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_policy": policy,
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V158_X077_SHADOW_CENSUS"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V158 preregistration changed")
    row = prereg["matrix"]["row"]
    evaluator = load_evaluator(evaluator_path)
    v126_behavior.ClosedLoopConfig = evaluator.ClosedLoopConfig
    shadow = "P31_34_PITCH_WITH_P30_NONPITCH"

    def run_shadow(config):
        return evaluator.run_closed_loop_sim(
            dataclasses.replace(
                config,
                exact_torque_oracle_shadow_fit=v126_behavior.actuator_fit(
                    base_prereg, shadow
                ),
                exact_torque_oracle_maximum_fit_passes=14,
                exact_torque_oracle_apply=False,
            )
        )

    v126_behavior.run_closed_loop_sim = run_shadow
    run_root.mkdir(parents=True)
    trace_root = run_root / "traces"
    cell_root = run_root / "cells"
    trace_root.mkdir()
    cell_root.mkdir()
    trace_path = trace_root / "v158_v140_p30_x0.077_seed167931544.jsonl"
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cell = v126_behavior.execute_cell(
        row=row,
        base_prereg=base_prereg,
        policy=policy,
        playground=Path(v126["external_inputs"]["playground"]),
        trace_path=trace_path,
        action_delta=tuple(
            float(value) for value in v126["oracle"]["action_delta"]
        ),
        schedule_ticks=None,
        cpu_only=cpu_only,
    )
    cell_path = cell_root / "v158_v140_p30_x0.077_seed167931544.json"
    cell_path.write_text(
        json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rows = load_trace(trace_path)
    forces = np.abs(
        np.asarray(
            [row_["actuator_force_nm"] for row_ in rows],
            dtype=np.float64,
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
    oracle_rows = [
        row_["exact_torque_oracle"]
        for row_ in rows
        if isinstance(row_.get("exact_torque_oracle"), dict)
    ]
    action = np.asarray([row_["action"] for row_ in rows], dtype=np.float32)
    base_action = np.asarray(
        [row_["policy_base_action"] for row_ in rows], dtype=np.float32
    )
    all_labeled = all(
        event["source_tick"] is not None
        and event["joint"] in event["source_projected_joint_indices"]
        and event["joint"] not in event["source_empty_joint_indices"]
        and event["source_action_delta"] != 0.0
        and abs(event["projected_force_nm"]) <= TORQUE_LIMIT + 5.0e-6
        for event in events
    )
    peak_flat = int(np.argmax(forces))
    peak_tick, peak_joint = np.unravel_index(peak_flat, forces.shape)
    projected_by_joint = {
        str(joint): sum(
            joint in oracle["projected_joint_indices"]
            for oracle in oracle_rows
        )
        for joint in range(14)
    }
    checks = {
        "cpu_only": cpu_only,
        "complete_600_tick_trace": (
            len(rows) == len(oracle_rows) == 600
        ),
        "shadow_action_never_applied": bool(
            np.array_equal(action, base_action)
        ),
        "torque_failure_reproduced": (
            bool(events)
            and cell["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
        ),
        "zero_empty_intersections": all(
            not oracle["empty_intersection_joint_indices"]
            for oracle in oracle_rows
        ),
        "every_violation_has_safe_nonempty_precursor_label": (
            bool(events) and all_labeled
        ),
        "no_training_hosted_compute_behavior_selection_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v158.x077_shadow_census_result.v1",
        "status": (
            "PASS_WINNER_V158_X077_SHADOW_CENSUS"
            if not failed
            else "HOLD_WINNER_V158_X077_SHADOW_CENSUS"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "identity": row,
        "policy": {"path": str(policy), "sha256": sha256(policy)},
        "cell": cell,
        "trace": {"path": str(trace_path), "sha256": sha256(trace_path)},
        "torque": {
            "limit_nm": TORQUE_LIMIT,
            "events": len(events),
            "event_rows": events,
            "violating_joints": sorted({event["joint"] for event in events}),
            "peak_tick": int(peak_tick),
            "peak_joint": int(peak_joint),
            "peak_nm": float(forces[peak_tick, peak_joint]),
        },
        "oracle": {
            "rows": len(oracle_rows),
            "projected_ticks": sum(
                float(oracle["clip_linf"]) > 0.0 for oracle in oracle_rows
            ),
            "projected_joint_events": sum(
                len(oracle["projected_joint_indices"])
                for oracle in oracle_rows
            ),
            "projected_by_joint": projected_by_joint,
            "maximum_clip_linf": max(
                float(oracle["clip_linf"]) for oracle in oracle_rows
            ),
        },
        "decision": (
            "EARN_V159_POLICY_SPACE_REDESIGN_AUDIT"
            if not failed
            else "ESCALATE_DIRECTLY_TO_GAIT_LEVEL_REDESIGN"
        ),
        "authority": {
            "mechanism_classification": not failed,
            "training": False,
            "hosted_training": False,
            "candidate_behavior": False,
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
        "# Winner V158 x=.077 shadow census\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Actual torque events: `{len(events)}` across "
        f"`{payload['torque']['violating_joints']}`.\n"
        f"- Oracle projected joint events: "
        f"`{payload['oracle']['projected_joint_events']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Shadow only; no action application, training, Colab, "
        "deployment, Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
