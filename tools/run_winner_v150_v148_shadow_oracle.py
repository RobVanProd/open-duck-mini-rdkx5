#!/usr/bin/env python3
"""Run one shadow-oracle diagnostic on V148's displaced trajectory."""

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
PREREG = ANALYSIS / "winner_v150_v148_shadow_oracle_preregistration.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V148_RESULT = ANALYSIS / "winner_v148_single_center_residual_result.json"
V149_RESULT = (
    ANALYSIS / "winner_v149_single_center_causal_behavior_result.json"
)
V144_COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
OUTPUT = ANALYSIS / "winner_v150_v148_shadow_oracle_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V150_V148_SHADOW_ORACLE_RESULT_20260725.md"
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
        "closed_loop_sim_eval_v150_v148_shadow", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V150 evaluator: {path}")
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


def numeric_linf(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    field: str,
) -> float:
    a = np.asarray([row[field] for row in left], dtype=np.float64)
    b = np.asarray([row[field] for row in right], dtype=np.float64)
    return float(np.max(np.abs(a - b)))


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
            raise FileExistsError(f"refusing to overwrite V150: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v148 = json.loads(V148_RESULT.read_text(encoding="utf-8"))
    v149 = json.loads(V149_RESULT.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v148["artifact"]["deployed"]["path"])
    source_trace = Path(v149["cell"]["trace"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v148_result": sha256(V148_RESULT),
        "v149_result": sha256(V149_RESULT),
        "v144_composer": sha256(V144_COMPOSER),
        "two_fit_projector": sha256(PROJECTOR),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "source_trace": sha256(source_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V150_V148_SHADOW_ORACLE"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V150 preregistration changed")
    row = prereg["matrix"]["row"]
    evaluator = load_evaluator(evaluator_path)
    v126_behavior.ClosedLoopConfig = evaluator.ClosedLoopConfig
    shadow_fit = "P31_34_PITCH_WITH_P30_NONPITCH"

    def run_shadow(config):
        return evaluator.run_closed_loop_sim(
            dataclasses.replace(
                config,
                exact_torque_oracle_shadow_fit=v126_behavior.actuator_fit(
                    base_prereg, shadow_fit
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
    trace_path = trace_root / "v150_v148_p30_x0.074_seed167931544.jsonl"
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
    cell_path = cell_root / "v150_v148_p30_x0.074_seed167931544.json"
    cell_path.write_text(
        json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    source_rows = load_trace(source_trace)
    shadow_rows = load_trace(trace_path)
    forces = np.abs(
        np.asarray(
            [row_["actuator_force_nm"] for row_ in shadow_rows],
            dtype=np.float64,
        )
    )
    violations = np.argwhere(forces > TORQUE_LIMIT)
    event_rows = []
    for tick_value, joint_value in violations:
        tick = int(tick_value)
        joint = int(joint_value)
        matured = next(
            (
                item
                for item in shadow_rows[tick][
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
            else shadow_rows[source_tick]["exact_torque_oracle"]
        )
        event_rows.append(
            {
                "tick": tick,
                "joint": joint,
                "actual_force_nm": float(forces[tick, joint]),
                "source_tick": source_tick,
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
                "source_action_delta": (
                    None
                    if oracle is None
                    else float(
                        np.asarray(oracle["final_action"])[joint]
                        - np.asarray(oracle["base_action"])[joint]
                    )
                ),
                "base_action": (
                    None if oracle is None else oracle["base_action"]
                ),
                "final_action": (
                    None if oracle is None else oracle["final_action"]
                ),
                "projected_force_nm": (
                    None
                    if matured is None
                    else float(matured["predicted_force_nm"])
                ),
            }
        )
    reproduced = {
        field: numeric_linf(source_rows, shadow_rows, field)
        for field in (
            "action",
            "actuator_force_nm",
            "qpos",
            "qvel",
            "obs_state",
        )
    }
    oracle_rows = [
        row_["exact_torque_oracle"]
        for row_ in shadow_rows
        if isinstance(row_.get("exact_torque_oracle"), dict)
    ]
    all_events_labeled = all(
        event["source_tick"] is not None
        and event["joint"] in event["source_projected_joint_indices"]
        and event["joint"] not in event["source_empty_joint_indices"]
        and event["source_action_delta"] != 0.0
        and abs(event["projected_force_nm"]) <= TORQUE_LIMIT + 5.0e-6
        for event in event_rows
    )
    checks = {
        "cpu_only": cpu_only,
        "complete_600_tick_trace": (
            len(source_rows) == len(shadow_rows) == len(oracle_rows) == 600
        ),
        "shadow_does_not_change_v148_trajectory": all(
            value == 0.0 for value in reproduced.values()
        ),
        "exact_single_displaced_event_right_ankle_tick586": (
            len(event_rows) == 1
            and event_rows[0]["tick"] == 586
            and event_rows[0]["joint"] == 13
            and 1.9200 < event_rows[0]["actual_force_nm"] < 1.9201
        ),
        "behavior_failure_remains_torque_only": (
            cell["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
        ),
        "zero_empty_intersections": all(
            not row_["empty_intersection_joint_indices"]
            for row_ in oracle_rows
        ),
        "every_actual_violation_has_safe_nonempty_precursor_label": (
            bool(event_rows) and all_events_labeled
        ),
        "no_training_or_hosted_compute": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v150.v148_shadow_oracle_result.v1",
        "status": (
            "PASS_WINNER_V150_V148_SHADOW_ORACLE"
            if not failed
            else "HOLD_WINNER_V150_V148_SHADOW_ORACLE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "identity": row,
        "policy": {"path": str(policy), "sha256": sha256(policy)},
        "trajectory_reproduction_linf": reproduced,
        "cell": cell,
        "trace": {"path": str(trace_path), "sha256": sha256(trace_path)},
        "torque": {
            "limit_nm": TORQUE_LIMIT,
            "events": len(event_rows),
            "event_rows": event_rows,
        },
        "oracle": {
            "rows": len(oracle_rows),
            "projected_ticks": sum(
                float(row_["clip_linf"]) > 0.0 for row_ in oracle_rows
            ),
            "projected_joint_events": sum(
                len(row_["projected_joint_indices"])
                for row_ in oracle_rows
            ),
        },
        "diagnosis": (
            "V148 exactly fixes the original tick-397 event, and the "
            "closed-loop displacement creates one new, preventable "
            "right-ankle event at tick 586"
            if not failed
            else "the displaced V148 event lacks an exact causal label"
        ),
        "decision": (
            "EARN_V151_BOUNDED_TWO_CENTER_CONTRACT_PREREGISTRATION"
            if not failed
            else "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
        ),
        "authority": {
            "v151_preregistration": not failed,
            "policy_change": False,
            "behavior": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V150 V148 shadow-oracle diagnostic\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Torque events: `{len(event_rows)}`.\n"
        f"- Event rows: `{event_rows}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- One CPU shadow replay only; no policy change, training, Colab, "
        "deployment, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
