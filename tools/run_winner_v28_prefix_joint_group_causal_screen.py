#!/usr/bin/env python3
"""Run the frozen Winner-v28 prefix joint-group causal screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v25_directional_support_control_diagnostic as v25  # noqa: E402
import run_winner_v27_early_prefix_recovery_scan as v27  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_preregistration.json"
V27_RESULT = ANALYSIS / "winner_v27_early_prefix_recovery_scan_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V24_SUPPORT = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
SOURCE_UPDATE = 100
CANDIDATES = (("half", 150), ("final", 200))
CONFIGURATION_IDS = v25.CONFIGURATION_IDS
REPAIR_TICKS = 8
ABSOLUTE_END_TICK = 52
MINIMUM_RECOVERY_GAIN = 0.25
ACTION_DELTA_EPS = 1.0e-6
GROUPS = {
    "LEFT_LATERAL": (0, 1),
    "LEFT_PITCH_CHAIN": (2, 3, 4),
    "HEAD": (5, 6, 7, 8),
    "RIGHT_LATERAL": (9, 10),
    "RIGHT_PITCH_CHAIN": (11, 12, 13),
}
ARMS = ("CONTROL", *GROUPS)
EXPECTED_PREFIX_ARMS = 240
EXPECTED_RECOVERY_ROLLOUTS = 480
CONTROL_REPLAY_POSE_ATOL_RAD = 1.0e-12


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v28.prefix_joint_group_causal_screen_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_PREFIX_JOINT_GROUP_SCREEN_ONLY"
        or value.get("execution_now")
        != {
            "prefix_arms": 0,
            "source_recovery_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v28 preregistration authority changed")
    diagnostic = value.get("diagnostic", {})
    if diagnostic != {
        "source_checkpoint": {"label": "winner_v22_final", "update": SOURCE_UPDATE},
        "candidate_checkpoints": [
            {"label": label, "update": update} for label, update in CANDIDATES
        ],
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "repair_ticks": REPAIR_TICKS,
        "absolute_end_tick": ABSOLUTE_END_TICK,
        "arms": {"CONTROL": [], **{name: list(indices) for name, indices in GROUPS.items()}},
        "repair_semantics": (
            "for ticks 0-7 only, replace the named candidate action indices with the "
            "Winner-v22 source action computed on the same branch observation and realized "
            "previous action; preserve all other candidate indices"
        ),
        "recovery_semantics": (
            "after tick 8, run Winner-v22 with its shadow hidden state from the repaired "
            "history and score survival against the unchanged candidate support terminal"
        ),
        "minimum_recovery_gain": MINIMUM_RECOVERY_GAIN,
        "action_delta_epsilon": ACTION_DELTA_EPS,
        "control_replay_pose_atol_rad": CONTROL_REPLAY_POSE_ATOL_RAD,
        "expected_prefix_arms": EXPECTED_PREFIX_ARMS,
        "expected_source_recovery_rollouts": EXPECTED_RECOVERY_ROLLOUTS,
        "selection_rule": (
            "select exactly one group only if its recovery-fraction gain is at least 0.25 "
            "for both checkpoints and its minimum checkpoint gain is strictly greater "
            "than every other group"
        ),
    }:
        raise ValueError("Winner-v28 diagnostic constants changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v28 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v28 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v28 source manifest changed")


def recovery_against_terminal(
    candidate_terminal: int, source_trace: Mapping[str, Any]
) -> dict[str, Any]:
    source_terminal = source_trace["terminal_absolute_tick"]
    recovered = source_terminal is None or int(source_terminal) > candidate_terminal
    lead = (
        (ABSOLUTE_END_TICK if source_terminal is None else int(source_terminal))
        - candidate_terminal
        if recovered
        else 0
    )
    return {
        "source_recovers": bool(recovered),
        "source_survival_lead_ticks": int(lead),
    }


def control_replays_v27(
    observed: Mapping[str, Any], recorded: Mapping[str, Any]
) -> bool:
    exact_fields = (
        "actions_sha256",
        "attempted_ticks",
        "hidden_outputs_sha256",
        "initial_action",
        "terminal_absolute_tick",
        "valid_ticks",
    )
    if any(observed[field] != recorded[field] for field in exact_fields):
        return False
    for field in ("roll_rad", "pitch_rad"):
        left = np.asarray(observed[field], dtype=np.float64)
        right = np.asarray(recorded[field], dtype=np.float64)
        if left.shape != right.shape or not np.allclose(
            left, right, rtol=0.0, atol=CONTROL_REPLAY_POSE_ATOL_RAD
        ):
            return False
    left_terminal = observed["terminal"]
    right_terminal = recorded["terminal"]
    if (left_terminal is None) != (right_terminal is None):
        return False
    if left_terminal is not None:
        for field in (
            "checks",
            "contacts",
            "fixed_p30_observer_target_sha256",
            "physical_applied_target_sha256",
            "sent_target_sha256",
        ):
            if left_terminal[field] != right_terminal[field]:
                return False
    return True


def aggregate_screen(rows: list[Mapping[str, Any]]) -> tuple[dict[str, Any], str | None]:
    aggregates: dict[str, Any] = {}
    for label, update in CANDIDATES:
        selected = [row for row in rows if row["candidate"] == label]
        by_arm: dict[str, Any] = {}
        for arm in ARMS:
            arm_rows = [row for row in selected if row["arm"] == arm]
            recovered = sum(row["comparison"]["source_recovers"] for row in arm_rows)
            leads = [row["comparison"]["source_survival_lead_ticks"] for row in arm_rows]
            by_arm[arm] = {
                "cells": len(arm_rows),
                "recovered": recovered,
                "recovery_fraction": recovered / len(arm_rows),
                "source_survival_lead_ticks": {
                    "minimum": min(leads),
                    "median": float(statistics.median(leads)),
                    "mean": float(statistics.fmean(leads)),
                    "maximum": max(leads),
                },
            }
        baseline = by_arm["CONTROL"]["recovery_fraction"]
        for arm in GROUPS:
            by_arm[arm]["recovery_fraction_gain"] = (
                by_arm[arm]["recovery_fraction"] - baseline
            )
        aggregates[label] = {"update": update, "arms": by_arm}
    minimum_gain = {
        arm: min(
            aggregates[label]["arms"][arm]["recovery_fraction_gain"]
            for label, _ in CANDIDATES
        )
        for arm in GROUPS
    }
    best = max(minimum_gain.values())
    winners = [arm for arm, gain in minimum_gain.items() if gain == best]
    selected_group = (
        winners[0]
        if len(winners) == 1 and best >= MINIMUM_RECOVERY_GAIN
        else None
    )
    for label, _ in CANDIDATES:
        aggregates[label]["minimum_checkpoint_gain_by_group"] = minimum_gain
    return aggregates, selected_group


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--v24-training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--read-only-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.read_only_diagnostic_authorized:
        raise PermissionError(
            "Winner-v28 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v28 result")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v28 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v27_result = json.loads(V27_RESULT.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    if (
        v27_result.get("status") != "PASS_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
        or v27_result.get("decision")
        != "AUTHORIZE_PREFIX_JOINT_GROUP_ACTION_CAUSAL_SCREEN_PREREGISTRATION_ONLY"
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v24.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v28 source authority changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v28 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v28 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(json.loads(DOMAIN.read_text(encoding="utf-8")))

    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == SOURCE_UPDATE
    )
    source_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    v25.validate_artifact(source_path, source_graph, "winner_v22_final.onnx")
    source_session = v25.graph_session(ort, source_path)
    checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    candidate_sessions = {}
    candidate_identities = {}
    for label, update in CANDIDATES:
        graph = checkpoints[label]["graph"]
        path = args.v24_training_work_root / f"graphs/winner_v24_{label}.onnx"
        v25.validate_artifact(path, graph, f"winner_v24_{label}.onnx")
        candidate_sessions[label] = v25.graph_session(ort, path)
        candidate_identities[label] = {"update": update, "onnx_sha256": graph["sha256"]}
    support = json.loads(V24_SUPPORT.read_text(encoding="utf-8"))
    candidate_terminals = {
        label: v27.support_terminal_lookup(support, label, update)
        for label, update in CANDIDATES
    }
    v27_tick8 = {
        (row["candidate"], row["configuration_id"], row["plant"]): row
        for row in v27_result["fork_results"]
        if row["fork_tick"] == 8
    }

    rows: list[dict[str, Any]] = []
    prefix_arms = 0
    recovery_rollouts = 0
    all_prefixes_valid = True
    all_repeats_exact = True
    all_controls_replay_v27 = True
    all_interventions_change_named_action = True
    for label, update in CANDIDATES:
        candidate_session = candidate_sessions[label]
        for configuration_id in CONFIGURATION_IDS:
            configuration = configurations[configuration_id]
            for plant in smoke.PLANTS:
                expected_terminal = candidate_terminals[label][(configuration_id, plant)]
                if expected_terminal is None:
                    raise ValueError("Winner-v28 selected candidate cell does not fail")
                for arm in ARMS:
                    episode = smoke.Episode(
                        mujoco, scene, configuration, plant, design, observer_type,
                        args.canonical_fit,
                    )
                    observation = episode.observation()
                    previous_action = np.zeros((14,), dtype=np.float32)
                    candidate_h = np.zeros((64,), dtype=np.float32)
                    source_h = np.zeros((64,), dtype=np.float32)
                    intervention_deltas: list[float] = []
                    prefix_arms += 1
                    for _ in range(REPAIR_TICKS):
                        candidate_action, candidate_h_out = v25.infer(
                            candidate_session, observation, previous_action, candidate_h
                        )
                        source_action, source_h_out = v25.infer(
                            source_session, observation, previous_action, source_h
                        )
                        realized = candidate_action.copy()
                        if arm != "CONTROL":
                            indices = np.asarray(GROUPS[arm], dtype=np.int64)
                            realized[indices] = source_action[indices]
                            intervention_deltas.append(
                                float(
                                    np.max(
                                        np.abs(
                                            source_action[indices]
                                            - candidate_action[indices]
                                        )
                                    )
                                )
                            )
                        if not np.array_equal(
                            realized, smoke.bounded_action_numpy(realized, previous_action)
                        ):
                            raise ValueError("Winner-v28 composed action violates boundary")
                        valid, next_observation, _ = episode.step(realized)
                        if not valid or next_observation is None:
                            all_prefixes_valid = False
                            break
                        observation = next_observation
                        previous_action = realized
                        candidate_h = candidate_h_out
                        source_h = source_h_out
                    if not all_prefixes_valid:
                        break
                    if arm != "CONTROL" and not any(
                        delta > ACTION_DELTA_EPS for delta in intervention_deltas
                    ):
                        all_interventions_change_named_action = False
                    snapshot = v25.capture_episode(mujoco, episode)
                    source_probe = smoke.Episode(
                        mujoco, scene, configuration, plant, design, observer_type,
                        args.canonical_fit,
                    )
                    repeat_probe = smoke.Episode(
                        mujoco, scene, configuration, plant, design, observer_type,
                        args.canonical_fit,
                    )
                    source_trace = v27.compact_rollout(
                        mujoco=mujoco,
                        smoke=smoke,
                        session=source_session,
                        episode=source_probe,
                        snapshot=snapshot,
                        initial_observation=observation,
                        initial_previous_action=previous_action,
                        initial_h_in=source_h,
                        fork_tick=REPAIR_TICKS,
                    )
                    repeat_trace = v27.compact_rollout(
                        mujoco=mujoco,
                        smoke=smoke,
                        session=source_session,
                        episode=repeat_probe,
                        snapshot=snapshot,
                        initial_observation=observation,
                        initial_previous_action=previous_action,
                        initial_h_in=source_h,
                        fork_tick=REPAIR_TICKS,
                    )
                    recovery_rollouts += 2
                    repeat_exact = source_trace == repeat_trace
                    all_repeats_exact &= repeat_exact
                    if arm == "CONTROL" and not control_replays_v27(
                        source_trace,
                        v27_tick8[(label, configuration_id, plant)][
                            "source_recovery_trace"
                        ],
                    ):
                        all_controls_replay_v27 = False
                    rows.append(
                        {
                            "candidate": label,
                            "candidate_update": update,
                            "configuration_id": configuration_id,
                            "plant": plant,
                            "arm": arm,
                            "replaced_action_indices": (
                                [] if arm == "CONTROL" else list(GROUPS[arm])
                            ),
                            "maximum_replaced_action_delta": (
                                0.0 if arm == "CONTROL" else max(intervention_deltas)
                            ),
                            "tick8_snapshot_state_sha256": v25.array_sha256(
                                snapshot["state"]
                            ),
                            "source_recovery_trace": source_trace,
                            "source_repeat_exact": repeat_exact,
                            "candidate_support_terminal_tick": expected_terminal,
                            "comparison": recovery_against_terminal(
                                expected_terminal, source_trace
                            ),
                        }
                    )
                if not all_prefixes_valid:
                    break
            if not all_prefixes_valid:
                break
        if not all_prefixes_valid:
            break

    aggregates, selected_group = aggregate_screen(rows)
    classification = (
        "SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
        if selected_group is not None
        else "NO_SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
    )
    decision = (
        "AUTHORIZE_SELECTED_PREFIX_GROUP_OBJECTIVE_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if selected_group is not None
        else "AUTHORIZE_PREFIX_GROUP_INTERACTION_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    checks = {
        "exact_240_prefix_arms": prefix_arms == EXPECTED_PREFIX_ARMS,
        "all_prefix_arms_valid_through_tick_8": all_prefixes_valid,
        "exact_480_source_recovery_rollouts": (
            recovery_rollouts == EXPECTED_RECOVERY_ROLLOUTS
        ),
        "all_source_recovery_repeats_bit_exact": all_repeats_exact,
        "all_control_arms_reproduce_winner_v27_tick8": all_controls_replay_v27,
        "all_group_interventions_change_named_action": (
            all_interventions_change_named_action
        ),
        "all_metrics_finite": all(
            math.isfinite(float(row["maximum_replaced_action_delta"])) for row in rows
        ),
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        classification = "INVALID_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        selected_group = None
    result = {
        "schema_version": "winner_v28.prefix_joint_group_causal_screen_result.v1",
        "status": (
            "PASS_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
            if not failed
            else "HOLD_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        ),
        "classification": classification,
        "decision": decision,
        "selected_group": selected_group,
        "checks": checks,
        "failed_checks": failed,
        "population": {
            "source_checkpoint": {
                "label": "winner_v22_final",
                "update": SOURCE_UPDATE,
                "onnx_sha256": source_graph["sha256"],
            },
            "candidate_checkpoints": candidate_identities,
            "configuration_ids": list(CONFIGURATION_IDS),
            "actuator_plants": list(smoke.PLANTS),
            "repair_ticks": REPAIR_TICKS,
            "absolute_end_tick": ABSOLUTE_END_TICK,
            "arms": {"CONTROL": [], **{name: list(indices) for name, indices in GROUPS.items()}},
        },
        "thresholds": {
            "minimum_recovery_gain": MINIMUM_RECOVERY_GAIN,
            "action_delta_epsilon": ACTION_DELTA_EPS,
            "control_replay_pose_atol_rad": CONTROL_REPLAY_POSE_ATOL_RAD,
        },
        "arm_results": rows,
        "candidate_aggregates": aggregates,
        "execution": {
            "prefix_arms": prefix_arms,
            "source_recovery_rollouts": recovery_rollouts,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v27_result_lf_sha256": lf_sha256(V27_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "v24_support_lf_sha256": lf_sha256(V24_SUPPORT),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the single CPU contract named by the frozen decision tree",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(result["classification"])
    print(f"SELECTED_GROUP={selected_group}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
