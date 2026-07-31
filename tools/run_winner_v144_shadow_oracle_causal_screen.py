#!/usr/bin/env python3
"""Run one preregistered shadow-oracle causal trace on V140."""

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
PREREG = ANALYSIS / "winner_v144_shadow_oracle_preregistration_v2.json"
COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = v126_behavior.BASE_PREREG
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V141_PREREG = (
    ANALYSIS / "winner_v141_projected_final_behavior_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V142_ATTRIBUTION = (
    ANALYSIS / "winner_v142_transferred_load_attribution.json"
)
OUTPUT = ANALYSIS / "winner_v144_shadow_oracle_result.json"
MARKDOWN = ANALYSIS / "WINNER_V144_SHADOW_ORACLE_RESULT_20260725.md"
TORQUE_LIMIT = 1.91229675


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v144_shadow_oracle", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V144 evaluator: {path}")
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
            raise FileExistsError(f"refusing to overwrite V144: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v141_prereg = json.loads(V141_PREREG.read_text(encoding="utf-8"))
    v141_result = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    source_trace = Path(
        v141_result["new_final_cells"][1]["trace"]["path"]
    )
    observed_hashes = {
        "composer": sha256(COMPOSER),
        "runner": sha256(Path(__file__).resolve()),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v140_result": sha256(V140_RESULT),
        "v141_preregistration": sha256(V141_PREREG),
        "v141_result": sha256(V141_RESULT),
        "v142_attribution": sha256(V142_ATTRIBUTION),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "source_trace": sha256(source_trace),
        "two_fit_projector": sha256(
            ROOT / "tools/exact_torque_oracle_two_fit.py"
        ),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V144_SHADOW_ORACLE_CAUSAL_SCREEN"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V144 preregistration changed")
    matrix = v141_prereg["matrix"]["new_final_rows"]
    row = matrix[1]
    if (
        row["plant"] != "P30_ALL_JOINT"
        or float(row["command_x_m_s"]) != 0.074
        or int(row["seed"]) != 167931544
    ):
        raise ValueError("V144 selected cell changed")
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
    trace_path = trace_root / "v144_shadow_p30_x0.074_seed167931544.jsonl"
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    policy_spec = next(
        value
        for value in v126["policies"]
        if value["id"] == "V121_TRAIN_MATCHED_FINAL"
    )
    policy_spec = {
        **policy_spec,
        "filename": policy.name,
    }
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
    cell_path = cell_root / "v144_shadow_p30_x0.074_seed167931544.json"
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
    peak_tick, peak_joint = np.unravel_index(np.argmax(forces), forces.shape)
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
                "projected_force_nm": (
                    None
                    if matured is None
                    else float(matured["predicted_force_nm"])
                ),
            }
        )
    oracle_rows = [
        row_["exact_torque_oracle"]
        for row_ in shadow_rows
        if isinstance(row_.get("exact_torque_oracle"), dict)
    ]
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
    all_events_labeled = all(
        event["source_tick"] is not None
        and event["joint"] in event["source_projected_joint_indices"]
        and event["joint"] not in event["source_empty_joint_indices"]
        and event["source_action_delta"] != 0.0
        and abs(event["projected_force_nm"]) <= TORQUE_LIMIT + 5.0e-6
        for event in event_rows
    )
    peak_event = next(
        event
        for event in event_rows
        if event["tick"] == int(peak_tick)
        and event["joint"] == int(peak_joint)
    )
    checks = {
        "cpu_only": cpu_only,
        "complete_600_tick_trace": (
            len(source_rows) == len(shadow_rows) == len(oracle_rows) == 600
        ),
        "shadow_does_not_change_source_trajectory": all(
            value == 0.0 for value in reproduced.values()
        ),
        "source_failure_reproduced_at_right_ankle_tick397": (
            int(peak_tick) == 397
            and int(peak_joint) == 13
            and 1.920 < float(forces[peak_tick, peak_joint]) < 1.921
        ),
        "source_behavior_failure_is_torque_only": (
            cell["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
        ),
        "oracle_computed_without_application": (
            cell["simulator"]["status"] is not None
            and all(
                row_["exact_torque_oracle"] is not None
                for row_ in shadow_rows
            )
        ),
        "zero_empty_intersections": all(
            not row_["empty_intersection_joint_indices"]
            for row_ in oracle_rows
        ),
        "all_actual_violations_have_safe_nonempty_precursor_labels": (
            bool(event_rows) and all_events_labeled
        ),
        "peak_right_ankle_has_safe_nonempty_precursor_label": (
            peak_event["joint"]
            in peak_event["source_projected_joint_indices"]
            and peak_event["joint"]
            not in peak_event["source_empty_joint_indices"]
            and peak_event["source_action_delta"] != 0.0
            and abs(peak_event["projected_force_nm"])
            <= TORQUE_LIMIT + 5.0e-6
        ),
        "no_training_or_hosted_compute": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v144.shadow_oracle_causal_result.v1",
        "status": (
            "PASS_WINNER_V144_SHADOW_ORACLE_CAUSAL_SCREEN"
            if not failed
            else "HOLD_WINNER_V144_SHADOW_ORACLE_CAUSAL_SCREEN"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "identity": row,
        "policy": {"path": str(policy), "sha256": sha256(policy)},
        "trajectory_reproduction_linf": reproduced,
        "source_cell": cell,
        "trace": {"path": str(trace_path), "sha256": sha256(trace_path)},
        "torque": {
            "limit_nm": TORQUE_LIMIT,
            "events": len(event_rows),
            "peak_tick": int(peak_tick),
            "peak_joint": int(peak_joint),
            "peak_nm": float(forces[peak_tick, peak_joint]),
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
            "peak_event": peak_event,
        },
        "diagnosis": (
            "the exact two-fit oracle directly labels every transferred "
            "torque event on the unmodified V140 closed-loop trajectory"
            if not failed
            else (
                "the shadow oracle does not provide complete causal labels "
                "for the transferred V140 torque events"
            )
        ),
        "decision": (
            "EARN_ONE_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION"
            if not failed
            else "CLOSE_ON_POLICY_DAGGER_FROM_V140"
        ),
        "authority": {
            "v145_cpu_preregistration": not failed,
            "training": False,
            "behavior": False,
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
        "# Winner V144 shadow-oracle causal screen\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Source trajectory reproduction L-inf: `{reproduced}`.\n"
        f"- Torque events: `{len(event_rows)}`; peak: "
        f"`joint {peak_joint}, tick {peak_tick}, "
        f"{forces[peak_tick, peak_joint]:.6f} N.m`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- One CPU shadow trace only; no action modification, training, "
        "Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
