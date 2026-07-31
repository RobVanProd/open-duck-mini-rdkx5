#!/usr/bin/env python3
"""Run the frozen post-prefix recurrent closed-loop credit diagnostic."""

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


PREREGISTRATION = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_preregistration.json"
V25_RESULT = ANALYSIS / "winner_v25_directional_support_control_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
SOURCE_UPDATE = 100
CANDIDATES = (("half", 150), ("final", 200))
CONFIGURATION_IDS = v25.CONFIGURATION_IDS
BASE_PREFIX_TICKS = 20
RECURRENT_HORIZON_TICKS = 32
REGRESSION_FRACTION_THRESHOLD = 0.75
MINIMUM_MEDIAN_LEAD_TICKS = 1.0
ACTION_DELTA_EPS = 1.0e-6
PITCH_DELTA_EPS_RAD = 1.0e-6
EXPECTED_BASE_TRAJECTORIES = 20
EXPECTED_CANDIDATE_BRANCHES = 40
EXPECTED_BRANCH_ROLLOUTS = 80


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def array_sha256(value: np.ndarray) -> str:
    return v25.array_sha256(value)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v26.recurrent_credit_diagnostic_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_POST_PREFIX_RECURRENT_DIAGNOSTIC_ONLY"
        or value.get("execution_now")
        != {
            "base_trajectories": 0,
            "candidate_branches": 0,
            "branch_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v26 preregistration authority changed")
    diagnostic = value.get("diagnostic", {})
    if diagnostic != {
        "source_checkpoint": {"label": "winner_v22_final", "update": SOURCE_UPDATE},
        "candidate_checkpoints": [
            {"label": label, "update": update} for label, update in CANDIDATES
        ],
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "base_prefix_ticks": BASE_PREFIX_TICKS,
        "recurrent_horizon_ticks": RECURRENT_HORIZON_TICKS,
        "shared_fork_inputs": ["physical_state", "observation", "previous_action", "h_in"],
        "branch_semantics": (
            "the captured tick-20 policy observation is supplied identically at the first "
            "branch tick; source and candidate then evolve their own observation, previous-"
            "action, and recurrent hidden-state chains"
        ),
        "regression_definition": (
            "candidate terminates before source; a source surviving 32 branch ticks is "
            "right-censored at absolute tick 52"
        ),
        "regression_fraction_threshold": REGRESSION_FRACTION_THRESHOLD,
        "minimum_median_lead_ticks": MINIMUM_MEDIAN_LEAD_TICKS,
        "action_delta_epsilon": ACTION_DELTA_EPS,
        "pitch_delta_epsilon_rad": PITCH_DELTA_EPS_RAD,
        "expected_base_trajectories": EXPECTED_BASE_TRAJECTORIES,
        "expected_candidate_branches": EXPECTED_CANDIDATE_BRANCHES,
        "expected_branch_rollouts": EXPECTED_BRANCH_ROLLOUTS,
        "branch_rule": (
            "classify post-prefix recurrent closed-loop regression only if both candidate "
            "checkpoints regress on at least 75 percent of branches and have median "
            "candidate failure lead of at least one tick"
        ),
    }:
        raise ValueError("Winner-v26 diagnostic constants changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v26 diagnostic sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v26 diagnostic source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v26 source manifest changed")


def validate_artifact(path: Path, receipt: Mapping[str, Any], expected_name: str) -> None:
    v25.validate_artifact(path, receipt, expected_name)


def recurrent_rollout(
    *,
    mujoco: Any,
    smoke: Any,
    session: Any,
    episode: Any,
    snapshot: Mapping[str, Any],
    initial_observation: np.ndarray,
    initial_previous_action: np.ndarray,
    initial_h_in: np.ndarray,
) -> dict[str, Any]:
    v25.restore_episode(mujoco, episode, snapshot)
    observation = np.asarray(initial_observation, dtype=np.float32).copy()
    previous_action = np.asarray(initial_previous_action, dtype=np.float32).copy()
    h_in = np.asarray(initial_h_in, dtype=np.float32).copy()
    if not np.array_equal(episode.previous_action, previous_action):
        raise ValueError("Winner-v26 restored previous action changed")
    # mjSTATE_INTEGRATION restores the physical integration state and warmstart,
    # but mj_forward recomputes acceleration-derived gyro/accelerometer samples.
    # The frozen fork intentionally supplies the captured policy observation as
    # an independent, identical input to every branch at its first tick.
    observations: list[list[float]] = []
    actions: list[list[float]] = []
    hidden_outputs: list[list[float]] = []
    rolls: list[float] = []
    pitches: list[float] = []
    terminal = None
    valid_ticks = 0
    for relative_tick in range(RECURRENT_HORIZON_TICKS):
        observations.append(observation.astype(float).tolist())
        action, h_out = v25.infer(session, observation, previous_action, h_in)
        if not np.array_equal(
            action, smoke.bounded_action_numpy(action, previous_action)
        ):
            raise ValueError("Winner-v26 graph action boundary changed")
        actions.append(action.astype(float).tolist())
        hidden_outputs.append(h_out.astype(float).tolist())
        valid, next_observation, evidence = episode.step(action)
        roll, pitch = smoke.roll_pitch_wxyz(
            np.asarray(episode.data.qpos[3:7], dtype=np.float64)
        )
        rolls.append(float(roll))
        pitches.append(float(pitch))
        if not valid:
            terminal = {
                **evidence,
                "relative_tick": relative_tick,
                "absolute_tick": BASE_PREFIX_TICKS + valid_ticks,
            }
            break
        valid_ticks += 1
        if next_observation is None:
            raise ValueError("Winner-v26 valid transition omitted observation")
        observation = next_observation
        previous_action = action
        h_in = h_out
    specification = mujoco.mjtState.mjSTATE_INTEGRATION
    end_state = np.empty(
        int(mujoco.mj_stateSize(episode.model, specification)), dtype=np.float64
    )
    mujoco.mj_getState(episode.model, episode.data, end_state, specification)
    trace = {
        "attempted_ticks": len(actions),
        "valid_ticks": valid_ticks,
        "terminal": terminal,
        "terminal_absolute_tick": None if terminal is None else terminal["absolute_tick"],
        "observations": observations,
        "actions": actions,
        "hidden_outputs": hidden_outputs,
        "roll_rad": rolls,
        "pitch_rad": pitches,
        "end_state_sha256": array_sha256(end_state),
    }
    if not all(
        math.isfinite(float(value))
        for sequence in (observations, actions, hidden_outputs, rolls, pitches)
        for row in sequence
        for value in (row if isinstance(row, list) else [row])
    ):
        raise FloatingPointError("Winner-v26 trace is nonfinite")
    return trace


def compare_branches(source: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    common = min(int(source["attempted_ticks"]), int(candidate["attempted_ticks"]))
    action_delta = [
        float(
            np.max(
                np.abs(
                    np.asarray(candidate["actions"][tick], dtype=np.float64)
                    - np.asarray(source["actions"][tick], dtype=np.float64)
                )
            )
        )
        for tick in range(common)
    ]
    hidden_delta = [
        float(
            np.max(
                np.abs(
                    np.asarray(candidate["hidden_outputs"][tick], dtype=np.float64)
                    - np.asarray(source["hidden_outputs"][tick], dtype=np.float64)
                )
            )
        )
        for tick in range(common)
    ]
    pitch_delta = [
        abs(float(candidate["pitch_rad"][tick]))
        - abs(float(source["pitch_rad"][tick]))
        for tick in range(common)
    ]
    source_terminal = source["terminal_absolute_tick"]
    candidate_terminal = candidate["terminal_absolute_tick"]
    regresses = candidate_terminal is not None and (
        source_terminal is None or int(candidate_terminal) < int(source_terminal)
    )
    source_bound = (
        BASE_PREFIX_TICKS + RECURRENT_HORIZON_TICKS
        if source_terminal is None
        else int(source_terminal)
    )
    lead = source_bound - int(candidate_terminal) if regresses else 0
    return {
        "common_attempted_ticks": common,
        "action_delta_linf_by_tick": action_delta,
        "hidden_delta_linf_by_tick": hidden_delta,
        "abs_pitch_delta_rad_by_tick": pitch_delta,
        "initial_action_changed": bool(action_delta and action_delta[0] > ACTION_DELTA_EPS),
        "first_positive_pitch_delta_tick": next(
            (tick for tick, value in enumerate(pitch_delta) if value > PITCH_DELTA_EPS_RAD),
            None,
        ),
        "candidate_terminates_before_source": bool(regresses),
        "candidate_failure_lead_ticks": int(lead),
    }


def aggregate_candidates(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    aggregates: dict[str, Any] = {}
    for label, update in CANDIDATES:
        selected = [row for row in rows if row["candidate"] == label]
        regressed = sum(
            row["comparison"]["candidate_terminates_before_source"] for row in selected
        )
        leads = [row["comparison"]["candidate_failure_lead_ticks"] for row in selected]
        fraction = regressed / len(selected) if selected else math.nan
        median_lead = float(statistics.median(leads)) if leads else math.nan
        aggregates[label] = {
            "update": update,
            "branches": len(selected),
            "initial_action_changed_branches": sum(
                row["comparison"]["initial_action_changed"] for row in selected
            ),
            "regressed_branches": regressed,
            "regression_fraction": fraction,
            "candidate_failure_lead_ticks": {
                "minimum": min(leads),
                "median": median_lead,
                "mean": float(statistics.fmean(leads)),
                "maximum": max(leads),
            },
            "meets_frozen_post_prefix_regression_rule": bool(
                fraction >= REGRESSION_FRACTION_THRESHOLD
                and median_lead >= MINIMUM_MEDIAN_LEAD_TICKS
            ),
        }
    return aggregates


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
            "Winner-v26 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v26 result")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v26 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v25_result = json.loads(V25_RESULT.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    if (
        v25_result.get("status")
        != "PASS_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
        or v25_result.get("decision")
        != "AUTHORIZE_LONGER_HORIZON_RECURRENT_CREDIT_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v24.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v26 source authority changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v26 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v26 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file() or smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v26 scene changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(json.loads(DOMAIN.read_text(encoding="utf-8")))

    source_snapshot = v22["snapshot_manifest"][SOURCE_UPDATE - 1]
    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == SOURCE_UPDATE
    )
    source_snapshot_path = (
        args.v22_training_work_root
        / "snapshots"
        / f"snapshot_normalized_predictor_update_{SOURCE_UPDATE:03d}.npz"
    )
    source_graph_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    validate_artifact(
        source_snapshot_path,
        source_snapshot,
        f"snapshot_normalized_predictor_update_{SOURCE_UPDATE:03d}.npz",
    )
    validate_artifact(source_graph_path, source_graph, "winner_v22_final.onnx")
    source_session = v25.graph_session(ort, source_graph_path)

    v24_snapshots = {row["completed_updates"]: row for row in v24["snapshot_manifest"]}
    v24_checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    candidate_sessions: dict[str, Any] = {}
    candidate_identities: dict[str, Any] = {}
    for label, update in CANDIDATES:
        snapshot_path = (
            args.v24_training_work_root
            / "snapshots"
            / f"snapshot_baseline_anchored_update_{update:03d}.npz"
        )
        graph_path = args.v24_training_work_root / f"graphs/winner_v24_{label}.onnx"
        validate_artifact(
            snapshot_path,
            v24_snapshots[update],
            f"snapshot_baseline_anchored_update_{update:03d}.npz",
        )
        validate_artifact(
            graph_path,
            v24_checkpoints[label]["graph"],
            f"winner_v24_{label}.onnx",
        )
        candidate_sessions[label] = v25.graph_session(ort, graph_path)
        candidate_identities[label] = {
            "update": update,
            "snapshot_sha256": v24_snapshots[update]["sha256"],
            "onnx_sha256": v24_checkpoints[label]["graph"]["sha256"],
        }

    base_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    branch_rollouts = 0
    all_prefixes_valid = True
    all_repeats_exact = True
    for configuration_id in CONFIGURATION_IDS:
        configuration = configurations[configuration_id]
        for plant in smoke.PLANTS:
            base = smoke.Episode(
                mujoco, scene, configuration, plant, design, observer_type, args.canonical_fit
            )
            observation = base.observation()
            previous_action = np.zeros((14,), dtype=np.float32)
            h_in = np.zeros((64,), dtype=np.float32)
            for _ in range(BASE_PREFIX_TICKS):
                action, h_out = v25.infer(
                    source_session, observation, previous_action, h_in
                )
                valid, next_observation, _ = base.step(action)
                if not valid or next_observation is None:
                    all_prefixes_valid = False
                    break
                observation = next_observation
                previous_action = action
                h_in = h_out
            if not all_prefixes_valid:
                break
            snapshot = v25.capture_episode(mujoco, base)
            shared = {
                "configuration_id": configuration_id,
                "plant": plant,
                "simulator_state_sha256": array_sha256(snapshot["state"]),
                "observation": observation.astype(float).tolist(),
                "previous_action": previous_action.astype(float).tolist(),
                "h_in": h_in.astype(float).tolist(),
            }
            source_probe = smoke.Episode(
                mujoco, scene, configuration, plant, design, observer_type, args.canonical_fit
            )
            repeat_probe = smoke.Episode(
                mujoco, scene, configuration, plant, design, observer_type, args.canonical_fit
            )
            source_trace = recurrent_rollout(
                mujoco=mujoco,
                smoke=smoke,
                session=source_session,
                episode=source_probe,
                snapshot=snapshot,
                initial_observation=observation,
                initial_previous_action=previous_action,
                initial_h_in=h_in,
            )
            repeat_trace = recurrent_rollout(
                mujoco=mujoco,
                smoke=smoke,
                session=source_session,
                episode=repeat_probe,
                snapshot=snapshot,
                initial_observation=observation,
                initial_previous_action=previous_action,
                initial_h_in=h_in,
            )
            branch_rollouts += 2
            repeat_exact = source_trace == repeat_trace
            all_repeats_exact &= repeat_exact
            base_rows.append(
                {
                    **shared,
                    "source_trace": source_trace,
                    "source_trace_sha256": canonical_sha256(source_trace),
                    "source_clone_repeat_exact": repeat_exact,
                }
            )
            for label, update in CANDIDATES:
                candidate_probe = smoke.Episode(
                    mujoco,
                    scene,
                    configuration,
                    plant,
                    design,
                    observer_type,
                    args.canonical_fit,
                )
                candidate_trace = recurrent_rollout(
                    mujoco=mujoco,
                    smoke=smoke,
                    session=candidate_sessions[label],
                    episode=candidate_probe,
                    snapshot=snapshot,
                    initial_observation=observation,
                    initial_previous_action=previous_action,
                    initial_h_in=h_in,
                )
                branch_rollouts += 1
                candidate_rows.append(
                    {
                        "candidate": label,
                        "candidate_update": update,
                        "configuration_id": configuration_id,
                        "plant": plant,
                        "shared_simulator_state_sha256": shared[
                            "simulator_state_sha256"
                        ],
                        "candidate_trace": candidate_trace,
                        "candidate_trace_sha256": canonical_sha256(candidate_trace),
                        "comparison": compare_branches(source_trace, candidate_trace),
                    }
                )
        if not all_prefixes_valid:
            break

    aggregates = aggregate_candidates(candidate_rows)
    post_prefix_regression = all(
        row["meets_frozen_post_prefix_regression_rule"]
        for row in aggregates.values()
    )
    classification = (
        "POST_PREFIX_RECURRENT_CLOSED_LOOP_REGRESSION"
        if post_prefix_regression
        else "NO_DOMINANT_POST_PREFIX_RECURRENT_REGRESSION"
    )
    decision = (
        "AUTHORIZE_RECURRENT_PARAMETER_BLOCK_SWAP_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if post_prefix_regression
        else "AUTHORIZE_EARLY_PREFIX_DIVERGENCE_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    checks = {
        "exact_20_base_trajectories": len(base_rows) == EXPECTED_BASE_TRAJECTORIES,
        "all_20_tick_source_prefixes_valid": all_prefixes_valid,
        "exact_40_candidate_branches": len(candidate_rows) == EXPECTED_CANDIDATE_BRANCHES,
        "exact_80_branch_rollouts": branch_rollouts == EXPECTED_BRANCH_ROLLOUTS,
        "all_source_clone_repeats_bit_exact": all_repeats_exact,
        "all_initial_candidate_actions_changed": all(
            row["comparison"]["initial_action_changed"] for row in candidate_rows
        ),
        "all_metrics_finite": all(
            math.isfinite(float(value))
            for row in candidate_rows
            for key in (
                "action_delta_linf_by_tick",
                "hidden_delta_linf_by_tick",
                "abs_pitch_delta_rad_by_tick",
            )
            for value in row["comparison"][key]
        ),
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        classification = "INVALID_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    result = {
        "schema_version": "winner_v26.recurrent_credit_diagnostic_result.v1",
        "status": (
            "PASS_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
            if not failed
            else "HOLD_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
        ),
        "classification": classification,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "population": {
            "source_checkpoint": {
                "label": "winner_v22_final",
                "update": SOURCE_UPDATE,
                "snapshot_sha256": source_snapshot["sha256"],
                "onnx_sha256": source_graph["sha256"],
            },
            "candidate_checkpoints": candidate_identities,
            "configuration_ids": list(CONFIGURATION_IDS),
            "actuator_plants": list(smoke.PLANTS),
            "base_prefix_ticks": BASE_PREFIX_TICKS,
            "recurrent_horizon_ticks": RECURRENT_HORIZON_TICKS,
        },
        "thresholds": {
            "regression_fraction": REGRESSION_FRACTION_THRESHOLD,
            "minimum_median_lead_ticks": MINIMUM_MEDIAN_LEAD_TICKS,
            "action_delta_epsilon": ACTION_DELTA_EPS,
            "pitch_delta_epsilon_rad": PITCH_DELTA_EPS_RAD,
        },
        "base_trajectories": base_rows,
        "candidate_branches": candidate_rows,
        "candidate_aggregates": aggregates,
        "execution": {
            "base_trajectories": len(base_rows),
            "candidate_branches": len(candidate_rows),
            "branch_rollouts": branch_rollouts,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v25_result_lf_sha256": lf_sha256(V25_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
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
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
