#!/usr/bin/env python3
"""Run the frozen same-state directional support-control diagnostic."""

from __future__ import annotations

import argparse
import copy
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

PREREGISTRATION = ANALYSIS / "winner_v25_directional_support_control_diagnostic_preregistration.json"
ATTRIBUTION = ANALYSIS / "winner_v24_support_regression_attribution.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
V22_GATE_RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_support_gate.py"
V24_GATE_RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_support_gate.py"
SOURCE_UPDATE = 100
CANDIDATES = (("half", 150), ("final", 200))
CONFIGURATION_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "DISCOVERY_03",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_09",
)
BASE_PREFIX_TICKS = 20
FORK_HORIZON_TICKS = 5
PITCH_DELTA_EPS_RAD = 1.0e-6
ACTION_DELTA_EPS = 1.0e-6
DESTABILIZING_FRACTION_THRESHOLD = 0.75
EXPECTED_BASE_TRAJECTORIES = 20
EXPECTED_FORK_POINTS = 800
EXPECTED_SHORT_HORIZON_ROLLOUTS = 1600


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(b"|")
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(b"|")
    digest.update(array.tobytes())
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v25.directional_support_control_diagnostic_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_SAME_STATE_DIRECTIONAL_DIAGNOSTIC_ONLY"
        or value.get("execution_now")
        != {
            "base_trajectories": 0,
            "fork_points": 0,
            "short_horizon_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v25 preregistration authority changed")
    diagnostic = value.get("diagnostic", {})
    if diagnostic != {
        "source_checkpoint": {"label": "winner_v22_final", "update": SOURCE_UPDATE},
        "candidate_checkpoints": [
            {"label": label, "update": update} for label, update in CANDIDATES
        ],
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "base_prefix_ticks": BASE_PREFIX_TICKS,
        "fork_horizon_ticks": FORK_HORIZON_TICKS,
        "same_policy_input": ["observation", "previous_action", "h_in"],
        "fork_action_hold": "hold the tick-t source or candidate action for all five fork ticks",
        "pitch_score": "abs(candidate_end_pitch)-abs(source_end_pitch)",
        "pitch_delta_epsilon_rad": PITCH_DELTA_EPS_RAD,
        "action_delta_epsilon": ACTION_DELTA_EPS,
        "destabilizing_fraction_threshold": DESTABILIZING_FRACTION_THRESHOLD,
        "expected_base_trajectories": EXPECTED_BASE_TRAJECTORIES,
        "expected_fork_points": EXPECTED_FORK_POINTS,
        "expected_short_horizon_rollouts": EXPECTED_SHORT_HORIZON_ROLLOUTS,
        "branch_rule": (
            "classify local destabilization only if both candidate checkpoints have "
            "destabilizing_fraction>=0.75 and median_abs_pitch_delta_rad>1e-6; otherwise "
            "classify no dominant local destabilization"
        ),
    }:
        raise ValueError("Winner-v25 diagnostic constants changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v25 diagnostic sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v25 diagnostic source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v25 source manifest changed")


def exact_configurations(domain: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    matrix = domain["evaluation_matrix"]
    rows = [
        *matrix["fixed_anchors"],
        *matrix["discovery_samples"],
        *matrix["heldout_samples"],
    ]
    lookup = {str(row["id"]): row for row in rows}
    if not set(CONFIGURATION_IDS).issubset(lookup):
        raise ValueError("Winner-v25 configurations are absent")
    if not all(float(lookup[name]["torso_com_offset_m"][0]) < 0.0 for name in CONFIGURATION_IDS):
        raise ValueError("Winner-v25 population is not strictly negative-X")
    return lookup


def validate_artifact(
    path: Path, receipt: Mapping[str, Any], expected_name: str
) -> None:
    if (
        path.name != expected_name
        or not path.is_file()
        or path.stat().st_size != receipt.get("bytes")
        or sha256(path) != receipt.get("sha256")
    ):
        raise ValueError(f"Winner-v25 artifact changed: {expected_name}")


def graph_session(ort: Any, path: Path) -> Any:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    inputs = [(item.name, item.shape, item.type) for item in session.get_inputs()]
    outputs = [(item.name, item.shape, item.type) for item in session.get_outputs()]
    if inputs != [
        ("obs", [1, 115], "tensor(float)"),
        ("previous_action", [1, 14], "tensor(float)"),
        ("h_in", [1, 64], "tensor(float)"),
    ] or outputs != [
        ("calibration_actions", [1, 14], "tensor(float)"),
        ("previous_action_out", [1, 14], "tensor(float)"),
        ("h_out", [1, 64], "tensor(float)"),
    ]:
        raise ValueError("Winner-v25 ONNX ABI changed")
    return session


def infer(
    session: Any,
    observation: np.ndarray,
    previous_action: np.ndarray,
    h_in: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    action, previous_out, h_out = session.run(
        ["calibration_actions", "previous_action_out", "h_out"],
        {
            "obs": np.asarray(observation, dtype=np.float32)[None, :],
            "previous_action": np.asarray(previous_action, dtype=np.float32)[None, :],
            "h_in": np.asarray(h_in, dtype=np.float32)[None, :],
        },
    )
    action = np.asarray(action[0], dtype=np.float32)
    previous_out = np.asarray(previous_out[0], dtype=np.float32)
    h_out = np.asarray(h_out[0], dtype=np.float32)
    if not np.array_equal(previous_out, action):
        raise ValueError("Winner-v25 previous-action chain changed")
    if not all(np.all(np.isfinite(value)) for value in (action, h_out)):
        raise FloatingPointError("Winner-v25 ONNX output is nonfinite")
    return action, h_out


def capture_episode(mujoco: Any, episode: Any) -> dict[str, Any]:
    specification = mujoco.mjtState.mjSTATE_INTEGRATION
    state = np.empty(
        int(mujoco.mj_stateSize(episode.model, specification)), dtype=np.float64
    )
    mujoco.mj_getState(episode.model, episode.data, state, specification)
    return {
        "state": state,
        "bridge": copy.deepcopy(episode.bridge),
        "observer": copy.deepcopy(episode.observer),
        "history": [value.copy() for value in episode.history],
        "overcurrent_streak": episode.overcurrent_streak.copy(),
        "gyro_xy_norms": list(episode.gyro_xy_norms),
        "valid_ticks": episode.valid_ticks,
        "maximum_abs_tilt": episode.maximum_abs_tilt,
        "minimum_base_z": episode.minimum_base_z,
        "maximum_torque_nm": episode.maximum_torque_nm,
        "maximum_current_a": episode.maximum_current_a,
        "maximum_observer_physical_separation_rad": (
            episode.maximum_observer_physical_separation_rad
        ),
    }


def restore_episode(mujoco: Any, episode: Any, snapshot: Mapping[str, Any]) -> None:
    specification = mujoco.mjtState.mjSTATE_INTEGRATION
    state = np.asarray(snapshot["state"], dtype=np.float64)
    if state.shape != (
        int(mujoco.mj_stateSize(episode.model, specification)),
    ):
        raise ValueError("Winner-v25 clone state size changed")
    mujoco.mj_setState(episode.model, episode.data, state, specification)
    mujoco.mj_forward(episode.model, episode.data)
    episode.bridge = copy.deepcopy(snapshot["bridge"])
    episode.observer = copy.deepcopy(snapshot["observer"])
    episode.history = [value.copy() for value in snapshot["history"]]
    episode.overcurrent_streak = snapshot["overcurrent_streak"].copy()
    episode.gyro_xy_norms = list(snapshot["gyro_xy_norms"])
    episode.valid_ticks = int(snapshot["valid_ticks"])
    episode.maximum_abs_tilt = float(snapshot["maximum_abs_tilt"])
    episode.minimum_base_z = float(snapshot["minimum_base_z"])
    episode.maximum_torque_nm = float(snapshot["maximum_torque_nm"])
    episode.maximum_current_a = float(snapshot["maximum_current_a"])
    episode.maximum_observer_physical_separation_rad = float(
        snapshot["maximum_observer_physical_separation_rad"]
    )


def fork_rollout(
    *,
    mujoco: Any,
    smoke: Any,
    episode: Any,
    snapshot: Mapping[str, Any],
    action: np.ndarray,
) -> dict[str, Any]:
    restore_episode(mujoco, episode, snapshot)
    completed = 0
    terminal = None
    for _ in range(FORK_HORIZON_TICKS):
        valid, _, evidence = episode.step(action)
        if not valid:
            terminal = evidence
            break
        completed += 1
    roll, pitch = smoke.roll_pitch_wxyz(
        np.asarray(episode.data.qpos[3:7], dtype=np.float64)
    )
    specification = mujoco.mjtState.mjSTATE_INTEGRATION
    end_state = np.empty(
        int(mujoco.mj_stateSize(episode.model, specification)), dtype=np.float64
    )
    mujoco.mj_getState(episode.model, episode.data, end_state, specification)
    return {
        "completed_ticks": completed,
        "terminal": terminal,
        "roll_rad": float(roll),
        "pitch_rad": float(pitch),
        "abs_pitch_rad": abs(float(pitch)),
        "end_state": end_state,
        "end_state_sha256": array_sha256(end_state),
        "bridge_value": episode.bridge.value,
        "observer_value": episode.observer.value,
    }


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
            "Winner-v25 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v25 result")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v25 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    if (
        attribution.get("status")
        != "PASS_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v24.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v25 source authority changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v25 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v25 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file() or smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v25 scene changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = exact_configurations(json.loads(DOMAIN.read_text(encoding="utf-8")))

    source_snapshot = v22["snapshot_manifest"][SOURCE_UPDATE - 1]
    source_graph = next(
        row["graph"] for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == SOURCE_UPDATE
    )
    source_snapshot_path = (
        args.v22_training_work_root / "snapshots"
        / f"snapshot_normalized_predictor_update_{SOURCE_UPDATE:03d}.npz"
    )
    source_graph_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    validate_artifact(
        source_snapshot_path,
        source_snapshot,
        f"snapshot_normalized_predictor_update_{SOURCE_UPDATE:03d}.npz",
    )
    validate_artifact(source_graph_path, source_graph, "winner_v22_final.onnx")
    source_session = graph_session(ort, source_graph_path)

    v24_snapshots = {row["completed_updates"]: row for row in v24["snapshot_manifest"]}
    v24_checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    candidate_sessions: dict[str, Any] = {}
    candidate_identities: dict[str, Any] = {}
    for label, update in CANDIDATES:
        snapshot_path = (
            args.v24_training_work_root / "snapshots"
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
        candidate_sessions[label] = graph_session(ort, graph_path)
        candidate_identities[label] = {
            "update": update,
            "snapshot_sha256": v24_snapshots[update]["sha256"],
            "onnx_sha256": v24_checkpoints[label]["graph"]["sha256"],
        }

    fork_rows: list[dict[str, Any]] = []
    base_trajectories = 0
    short_horizon_rollouts = 0
    all_base_prefixes_valid = True
    all_clone_repeats_exact = True
    for configuration_id in CONFIGURATION_IDS:
        configuration = configurations[configuration_id]
        for plant in smoke.PLANTS:
            base = smoke.Episode(
                mujoco, scene, configuration, plant, design, observer_type,
                args.canonical_fit,
            )
            source_probe = smoke.Episode(
                mujoco, scene, configuration, plant, design, observer_type,
                args.canonical_fit,
            )
            repeat_probe = smoke.Episode(
                mujoco, scene, configuration, plant, design, observer_type,
                args.canonical_fit,
            )
            candidate_probes = {
                label: smoke.Episode(
                    mujoco, scene, configuration, plant, design, observer_type,
                    args.canonical_fit,
                )
                for label, _ in CANDIDATES
            }
            observation = base.observation()
            previous_action = np.zeros((14,), dtype=np.float32)
            h_in = np.zeros((64,), dtype=np.float32)
            base_trajectories += 1
            for tick in range(BASE_PREFIX_TICKS):
                source_action, source_h_out = infer(
                    source_session, observation, previous_action, h_in
                )
                if not np.array_equal(
                    source_action,
                    smoke.bounded_action_numpy(source_action, previous_action),
                ):
                    raise ValueError("Winner-v25 source graph boundary changed")
                snapshot = capture_episode(mujoco, base)
                source_branch = fork_rollout(
                    mujoco=mujoco,
                    smoke=smoke,
                    episode=source_probe,
                    snapshot=snapshot,
                    action=source_action,
                )
                repeat_branch = fork_rollout(
                    mujoco=mujoco,
                    smoke=smoke,
                    episode=repeat_probe,
                    snapshot=snapshot,
                    action=source_action,
                )
                short_horizon_rollouts += 2
                clone_exact = (
                    source_branch["end_state_sha256"]
                    == repeat_branch["end_state_sha256"]
                    and np.array_equal(
                        source_branch["bridge_value"], repeat_branch["bridge_value"]
                    )
                    and np.array_equal(
                        source_branch["observer_value"], repeat_branch["observer_value"]
                    )
                )
                all_clone_repeats_exact &= clone_exact
                for label, update in CANDIDATES:
                    candidate_action, _ = infer(
                        candidate_sessions[label], observation, previous_action, h_in
                    )
                    if not np.array_equal(
                        candidate_action,
                        smoke.bounded_action_numpy(candidate_action, previous_action),
                    ):
                        raise ValueError("Winner-v25 candidate graph boundary changed")
                    candidate_branch = fork_rollout(
                        mujoco=mujoco,
                        smoke=smoke,
                        episode=candidate_probes[label],
                        snapshot=snapshot,
                        action=candidate_action,
                    )
                    short_horizon_rollouts += 1
                    pitch_delta = (
                        candidate_branch["abs_pitch_rad"]
                        - source_branch["abs_pitch_rad"]
                    )
                    action_delta = candidate_action - source_action
                    candidate_early_terminal = (
                        candidate_branch["completed_ticks"] < FORK_HORIZON_TICKS
                        and source_branch["completed_ticks"] == FORK_HORIZON_TICKS
                    )
                    fork_rows.append(
                        {
                            "candidate": label,
                            "candidate_update": update,
                            "configuration_id": configuration_id,
                            "plant": plant,
                            "base_tick": tick,
                            "same_input_observation_sha256": array_sha256(observation),
                            "same_input_previous_action_sha256": array_sha256(previous_action),
                            "same_input_h_in_sha256": array_sha256(h_in),
                            "simulator_state_sha256": array_sha256(snapshot["state"]),
                            "source_action": source_action.astype(float).tolist(),
                            "candidate_action": candidate_action.astype(float).tolist(),
                            "action_delta": action_delta.astype(float).tolist(),
                            "action_delta_linf": float(np.max(np.abs(action_delta))),
                            "action_changed": bool(
                                np.max(np.abs(action_delta)) > ACTION_DELTA_EPS
                            ),
                            "source_end_pitch_rad": source_branch["pitch_rad"],
                            "candidate_end_pitch_rad": candidate_branch["pitch_rad"],
                            "abs_pitch_delta_rad": pitch_delta,
                            "candidate_locally_destabilizing": bool(
                                candidate_early_terminal
                                or pitch_delta > PITCH_DELTA_EPS_RAD
                            ),
                            "source_completed_horizon_ticks": source_branch[
                                "completed_ticks"
                            ],
                            "candidate_completed_horizon_ticks": candidate_branch[
                                "completed_ticks"
                            ],
                            "source_end_state_sha256": source_branch[
                                "end_state_sha256"
                            ],
                            "candidate_end_state_sha256": candidate_branch[
                                "end_state_sha256"
                            ],
                            "source_clone_repeat_exact": clone_exact,
                        }
                    )
                valid, next_observation, _ = base.step(source_action)
                if not valid or next_observation is None:
                    all_base_prefixes_valid = False
                    break
                observation = next_observation
                previous_action = source_action
                h_in = source_h_out

    aggregates: dict[str, Any] = {}
    for label, update in CANDIDATES:
        rows = [row for row in fork_rows if row["candidate"] == label]
        pitch_deltas = [row["abs_pitch_delta_rad"] for row in rows]
        destabilizing = sum(row["candidate_locally_destabilizing"] for row in rows)
        changed = sum(row["action_changed"] for row in rows)
        fraction = destabilizing / len(rows) if rows else math.nan
        median_pitch_delta = float(statistics.median(pitch_deltas)) if rows else math.nan
        aggregates[label] = {
            "update": update,
            "fork_points": len(rows),
            "action_changed_points": changed,
            "action_changed_fraction": changed / len(rows) if rows else math.nan,
            "locally_destabilizing_points": destabilizing,
            "locally_destabilizing_fraction": fraction,
            "abs_pitch_delta_rad": {
                "minimum": min(pitch_deltas),
                "median": median_pitch_delta,
                "mean": float(statistics.fmean(pitch_deltas)),
                "maximum": max(pitch_deltas),
            },
            "meets_frozen_local_destabilization_rule": bool(
                fraction >= DESTABILIZING_FRACTION_THRESHOLD
                and median_pitch_delta > PITCH_DELTA_EPS_RAD
            ),
        }
    locally_destabilizing = all(
        row["meets_frozen_local_destabilization_rule"]
        for row in aggregates.values()
    )
    classification = (
        "SAME_STATE_ACTION_CHANGE_LOCALLY_DESTABILIZING"
        if locally_destabilizing
        else "NO_DOMINANT_SAME_STATE_LOCAL_DESTABILIZATION"
    )
    decision = (
        "AUTHORIZE_DIRECTIONAL_COUNTERFACTUAL_OBJECTIVE_CPU_CONTRACT_ONLY"
        if locally_destabilizing
        else "AUTHORIZE_LONGER_HORIZON_RECURRENT_CREDIT_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    checks = {
        "exact_20_base_trajectories": base_trajectories == EXPECTED_BASE_TRAJECTORIES,
        "all_20_tick_base_prefixes_valid": all_base_prefixes_valid,
        "exact_800_candidate_fork_points": len(fork_rows) == EXPECTED_FORK_POINTS,
        "exact_1600_short_horizon_rollouts": (
            short_horizon_rollouts == EXPECTED_SHORT_HORIZON_ROLLOUTS
        ),
        "all_source_clone_repeats_bit_exact": all_clone_repeats_exact,
        "all_source_forks_complete_five_ticks": all(
            row["source_completed_horizon_ticks"] == FORK_HORIZON_TICKS
            for row in fork_rows
        ),
        "all_metrics_finite": all(
            math.isfinite(float(row[key]))
            for row in fork_rows
            for key in (
                "action_delta_linf",
                "source_end_pitch_rad",
                "candidate_end_pitch_rad",
                "abs_pitch_delta_rad",
            )
        ),
        "both_candidates_change_action_on_at_least_95_percent_of_forks": all(
            row["action_changed_fraction"] >= 0.95 for row in aggregates.values()
        ),
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        classification = "INVALID_WINNER_V25_DIRECTIONAL_DIAGNOSTIC"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    result = {
        "schema_version": "winner_v25.directional_support_control_diagnostic_result.v1",
        "status": (
            "PASS_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
            if not failed
            else "HOLD_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
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
            "fork_horizon_ticks": FORK_HORIZON_TICKS,
        },
        "thresholds": {
            "pitch_delta_epsilon_rad": PITCH_DELTA_EPS_RAD,
            "action_delta_epsilon": ACTION_DELTA_EPS,
            "destabilizing_fraction": DESTABILIZING_FRACTION_THRESHOLD,
        },
        "candidate_aggregates": aggregates,
        "fork_results": fork_rows,
        "execution": {
            "base_trajectories": base_trajectories,
            "fork_points": len(fork_rows),
            "short_horizon_rollouts": short_horizon_rollouts,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "base_gate_runner_lf_sha256": lf_sha256(BASE_GATE_RUNNER),
            "v22_gate_runner_lf_sha256": lf_sha256(V22_GATE_RUNNER),
            "v24_gate_runner_lf_sha256": lf_sha256(V24_GATE_RUNNER),
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
