#!/usr/bin/env python3
"""Run the preregistered read-only T228 nominal failure autopsy."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    canonical_sha256,
)


PREREG = (
    ANALYSIS / "t232_t228_nominal_failure_autopsy_preregistration.json"
)
OUTPUT = ANALYSIS / "t232_t228_nominal_failure_autopsy_result.json"
MARKDOWN = ANALYSIS / "T232_T228_NOMINAL_FAILURE_AUTOPSY_RESULT_20260730.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def arrays(path: Path) -> dict[str, np.ndarray]:
    model = onnx.load(path, load_external_data=True)
    return {
        value.name: numpy_helper.to_array(value).astype(np.float64)
        for value in model.graph.initializer
    }


def stats(values: np.ndarray) -> dict[str, float]:
    flat = np.asarray(values, dtype=np.float64).reshape(-1)
    if flat.size == 0:
        return {"rms": 0.0, "p95_abs": 0.0, "max_abs": 0.0}
    return {
        "rms": float(np.sqrt(np.mean(np.square(flat)))),
        "p95_abs": float(np.quantile(np.abs(flat), 0.95)),
        "max_abs": float(np.max(np.abs(flat))),
    }


def longest_run(mask: np.ndarray) -> int:
    best = current = 0
    for value in np.asarray(mask, dtype=bool):
        if value:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def trace_key(row: dict[str, Any]) -> tuple[str, float]:
    return row["fit_id"], float(row["command_x_m_s"])


def head_params(
    initializers: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    return (
        initializers["nominal_condition_negative_adapter_weight"],
        initializers["nominal_condition_negative_adapter_bias"],
    )


def gate_params(initializers: dict[str, np.ndarray]) -> tuple[np.ndarray, ...]:
    return (
        initializers["hidden_gate_mean"],
        initializers["hidden_gate_scale"],
        initializers["hidden_gate_coefficient"].reshape(-1),
        initializers["hidden_gate_intercept"].reshape(-1),
    )


def hidden(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray(
        [row["policy_state_output"]["h_out"][0] for row in rows],
        dtype=np.float64,
    )


def field(rows: list[dict[str, Any]], name: str) -> np.ndarray:
    return np.asarray([row[name] for row in rows], dtype=np.float64)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T232: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg["status"] != (
        "PREREGISTERED_T232_T228_NOMINAL_FAILURE_AUTOPSY"
    ):
        raise RuntimeError("T232 preregistration status is not exact")

    graph_paths = {
        int(step): Path(row["path"])
        for step, row in prereg["graphs"].items()
    }
    graph_arrays = {step: arrays(path) for step, path in graph_paths.items()}
    source_names = set(graph_arrays[0])
    changed_by_step: dict[str, list[str]] = {}
    delta_by_step: dict[str, dict[str, float]] = {}
    for step in (1_003_520, 2_007_040):
        if set(graph_arrays[step]) != source_names:
            raise RuntimeError(f"initializer topology differs at {step}")
        changed = sorted(
            name
            for name in source_names
            if not np.array_equal(graph_arrays[0][name], graph_arrays[step][name])
        )
        changed_by_step[str(step)] = changed
        delta_by_step[str(step)] = {
            name: float(
                np.sqrt(
                    np.mean(
                        np.square(
                            graph_arrays[step][name]
                            - graph_arrays[0][name]
                        )
                    )
                )
            )
            for name in changed
        }

    traces: dict[str, dict[tuple[str, float], list[dict[str, Any]]]] = {}
    trace_meta: dict[str, dict[tuple[str, float], dict[str, Any]]] = {}
    for family, rows in prereg["traces"].items():
        traces[family] = {}
        trace_meta[family] = {}
        for row in rows:
            path = Path(row["trace"]["path"])
            if sha256(path) != row["trace"]["sha256"]:
                raise RuntimeError(f"trace hash mismatch: {path}")
            key = trace_key(row)
            traces[family][key] = load_jsonl(path)
            trace_meta[family][key] = row

    mean, scale, coefficient, intercept = gate_params(graph_arrays[0])
    source_w, source_b = head_params(graph_arrays[0])
    head_replay: list[dict[str, Any]] = []
    trained_nonzero_by_source_trace: list[bool] = []
    for key, rows in sorted(traces["source_t216_final"].items()):
        h_out = hidden(rows)
        score = (
            ((h_out - mean) / scale) @ coefficient
            + float(intercept[0])
        )
        active = score >= 0.0
        source_location = h_out @ source_w + source_b
        replay: dict[str, Any] = {
            "fit_id": key[0],
            "command_x_m_s": key[1],
            "rows": len(rows),
            "gate_active_rows": int(np.sum(active)),
            "gate_active_fraction": float(np.mean(active)),
            "gate_longest_active_run_ticks": longest_run(active),
            "gate_score": stats(score),
            "checkpoint_deltas": {},
        }
        for step in (1_003_520, 2_007_040):
            weight, bias = head_params(graph_arrays[step])
            delta = (h_out @ weight + bias) - source_location
            conditional = delta * active[:, None]
            per_joint = {
                name: stats(conditional[:, index])
                for index, name in enumerate(prereg["analysis"]["joint_order"])
            }
            top_joint = max(
                per_joint,
                key=lambda name: per_joint[name]["rms"],
            )
            replay["checkpoint_deltas"][str(step)] = {
                "all_rows": stats(delta),
                "gate_applied": stats(conditional),
                "top_joint": top_joint,
                "top_joint_stats": per_joint[top_joint],
                "per_joint": per_joint,
            }
            trained_nonzero_by_source_trace.append(
                stats(conditional)["max_abs"]
                > prereg["analysis"]["thresholds"]["nonzero_float32_effect"]
            )
        head_replay.append(replay)

    family_to_step = {
        "t228_half": 1_003_520,
        "t228_final": 2_007_040,
    }
    drift_rows: list[dict[str, Any]] = []
    for family, step in family_to_step.items():
        for key, candidate in sorted(traces[family].items()):
            source = traces["source_t216_final"][key]
            count = min(len(source), len(candidate))
            source_action = field(source[:count], "action")
            candidate_action = field(candidate[:count], "action")
            action_delta = candidate_action - source_action
            source_pitch = field(source[:count], "body_pitch_rad")
            candidate_pitch = field(candidate[:count], "body_pitch_rad")
            source_force = field(source[:count], "actuator_force_nm")
            candidate_force = field(candidate[:count], "actuator_force_nm")
            source_contacts = field(source[:count], "foot_contacts")
            candidate_contacts = field(candidate[:count], "foot_contacts")
            tick_rms = np.sqrt(np.mean(np.square(action_delta), axis=1))
            nonzero = np.flatnonzero(
                tick_rms
                > prereg["analysis"]["thresholds"]["nonzero_float32_effect"]
            )
            prefix = min(
                prereg["analysis"]["thresholds"]["prefix_ticks"], count
            )
            precursor = min(
                prereg["analysis"]["thresholds"][
                    "termination_precursor_ticks"
                ],
                count,
            )
            precursor_force_delta = (
                candidate_force[-precursor:] - source_force[-precursor:]
            )
            joint_rms = np.sqrt(
                np.mean(np.square(precursor_force_delta), axis=0)
            )
            top_force_joint_index = int(np.argmax(joint_rms))
            meta = trace_meta[family][key]
            drift_rows.append(
                {
                    "family": family,
                    "step": step,
                    "fit_id": key[0],
                    "command_x_m_s": key[1],
                    "source_rows": len(source),
                    "candidate_rows": len(candidate),
                    "candidate_green": meta["cell_green"],
                    "termination_reason": meta["termination_reason"],
                    "aligned_rows": count,
                    "first_action_divergence_tick": (
                        int(nonzero[0]) if nonzero.size else None
                    ),
                    "action_delta_all": stats(action_delta),
                    "action_delta_first_64": stats(action_delta[:prefix]),
                    "pitch_delta_all": stats(
                        candidate_pitch - source_pitch
                    ),
                    "candidate_peak_abs_pitch_rad": float(
                        np.max(np.abs(candidate_pitch))
                    ),
                    "source_peak_abs_pitch_same_prefix_rad": float(
                        np.max(np.abs(source_pitch))
                    ),
                    "termination_precursor_force_delta": stats(
                        precursor_force_delta
                    ),
                    "termination_precursor_top_force_joint": prereg[
                        "analysis"
                    ]["joint_order"][top_force_joint_index],
                    "termination_precursor_top_force_joint_rms_nm": float(
                        joint_rms[top_force_joint_index]
                    ),
                    "contact_disagreement_rows": int(
                        np.sum(np.any(source_contacts != candidate_contacts, axis=1))
                    ),
                }
            )

    hosted_cost = [
        float(row["value"])
        for row in prereg["hosted_metrics"]["eval_dense_torque_cost"]
    ]
    hosted_reward = [
        float(row["value"])
        for row in prereg["hosted_metrics"]["eval_reward"]
    ]
    expected_changes = [
        "nominal_condition_negative_adapter_bias",
        "nominal_condition_negative_adapter_weight",
    ]
    source_green = all(
        row["cell_green"]
        for row in prereg["traces"]["source_t216_final"]
    )
    final_green = any(
        row["cell_green"] for row in prereg["traces"]["t228_final"]
    )
    all_failures_clean = all(
        row["termination_reason"] == "fall_or_nan"
        and row["replacement_quality_pass"]
        and row["duration_protection_pass"]
        and row["strict_overcurrent_run_ticks"]
        < prereg["analysis"]["thresholds"]["trip_ticks"]
        and row["strict_overload_run_ticks"]
        < prereg["analysis"]["thresholds"]["trip_ticks"]
        for family in ("t228_half", "t228_final")
        for row in prereg["traces"][family]
        if not row["cell_green"]
    )
    classification_checks = {
        "hosted_eval_cost_half_and_final_below_step_zero": (
            hosted_cost[1] < hosted_cost[0]
            and hosted_cost[2] < hosted_cost[0]
        ),
        "source_four_of_four_green": source_green,
        "t228_final_zero_of_four_green": not final_green,
        "all_failures_are_falls_not_quality_or_duration_trips": (
            all_failures_clean
        ),
        "only_trainable_head_changed": (
            changed_by_step["1003520"] == expected_changes
            and changed_by_step["2007040"] == expected_changes
        ),
        "trained_head_nonzero_on_every_source_moving_trace": all(
            trained_nonzero_by_source_trace
        ),
    }
    classification_checks = {
        name: bool(value) for name, value in classification_checks.items()
    }
    classification_pass = all(classification_checks.values())
    status = (
        "PASS_T232_TRAINING_DISTRIBUTION_IMPROVEMENT_WITH_"
        "NOMINAL_ATTRACTOR_LOSS"
        if classification_pass
        else "HOLD_T232_T228_CAUSAL_CLASSIFICATION"
    )
    decision = (
        prereg["classification_rule"]["pass_decision"]
        if classification_pass
        else prereg["classification_rule"]["otherwise"]
    )
    result_basis: dict[str, Any] = {
        "schema_version": "open_duck.t232_t228_nominal_failure_autopsy.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "graph_drift": {
            "changed_initializers_by_step": changed_by_step,
            "initializer_rms_delta_by_step": delta_by_step,
        },
        "hosted_distribution": {
            "eval_dense_torque_cost": hosted_cost,
            "eval_reward": hosted_reward,
            "cost_half_minus_step_zero": hosted_cost[1] - hosted_cost[0],
            "cost_final_minus_step_zero": hosted_cost[2] - hosted_cost[0],
            "reward_half_minus_step_zero": hosted_reward[1] - hosted_reward[0],
            "reward_final_minus_step_zero": hosted_reward[2] - hosted_reward[0],
        },
        "head_replay_on_source_pass_traces": head_replay,
        "closed_loop_drift": drift_rows,
        "classification_checks": classification_checks,
        "classification_pass": classification_pass,
        "interpretation": {
            "formal_failure": (
                "fall_or_early_termination; tracking, rate, saturation, and "
                "100-tick current/torque duration protection remained green"
            ),
            "causal_scope": (
                "only the nominal-condition negative-adapter output weight "
                "and bias changed; mature actor, recurrence, normalizer, "
                "reward, cost, ABI, and deployment structure were frozen"
            ),
            "hosted_vs_nominal": (
                "the randomized hosted cost improved at both exports while "
                "the frozen nominal source attractor was progressively lost"
            ),
            "next_work": (
                "CPU-falsify a source-attractor preservation mechanism; "
                "no hosted continuation is earned by this result alone"
            ),
        },
        "execution": {
            "trace_rows": sum(
                len(rows)
                for family in traces.values()
                for rows in family.values()
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "cpu_falsifier_preregistration": classification_pass,
            "behavior": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    result = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T232 T228 nominal failure autopsy result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Hosted dense cost (0/half/final): "
        f"`{hosted_cost[0]:.6f} / {hosted_cost[1]:.6f} / "
        f"{hosted_cost[2]:.6f}`\n"
        "- Formal T231 failures: falls/early termination, not tracking, "
        "rate, saturation, or 100-tick protection trips\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if classification_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
