#!/usr/bin/env python3
"""Run the frozen Winner-v27 early-prefix source-recovery scan."""

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


PREREGISTRATION = ANALYSIS / "winner_v27_early_prefix_recovery_scan_preregistration.json"
V26_RESULT = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V22_SUPPORT = ANALYSIS / "winner_v22_normalized_predictor_support_gate_result.json"
V24_SUPPORT = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
SOURCE_UPDATE = 100
CANDIDATES = (("half", 150), ("final", 200))
CONFIGURATION_IDS = v25.CONFIGURATION_IDS
FORK_TICKS = (0, 4, 8, 12, 16, 20)
ABSOLUTE_END_TICK = 52
TICK0_RECOVERY_FRACTION = 1.0
TICK20_MAX_RECOVERY_FRACTION = 0.25
ACTION_DELTA_EPS = 1.0e-6
EXPECTED_CANDIDATE_PREFIXES = 40
EXPECTED_FORKS = 240
EXPECTED_BRANCH_ROLLOUTS = 720


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v27.early_prefix_recovery_scan_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_EARLY_PREFIX_RECOVERY_SCAN_ONLY"
        or value.get("execution_now")
        != {
            "candidate_prefixes": 0,
            "forks": 0,
            "branch_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v27 preregistration authority changed")
    diagnostic = value.get("diagnostic", {})
    if diagnostic != {
        "source_checkpoint": {"label": "winner_v22_final", "update": SOURCE_UPDATE},
        "candidate_checkpoints": [
            {"label": label, "update": update} for label, update in CANDIDATES
        ],
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "candidate_prefix_ticks": 20,
        "fork_ticks": list(FORK_TICKS),
        "absolute_end_tick": ABSOLUTE_END_TICK,
        "source_shadow_state": (
            "source hidden state is advanced on the candidate observation and previous-"
            "action history while its action output is ignored"
        ),
        "fork_semantics": (
            "candidate continuation and source recovery start from the same candidate "
            "physical/bridge/observer/history snapshot and captured policy observation; "
            "each uses its own history-consistent recurrent hidden state"
        ),
        "recovery_definition": (
            "source recovery survives to absolute tick 52 or terminates strictly later "
            "than the exact candidate continuation"
        ),
        "tick0_required_recovery_fraction": TICK0_RECOVERY_FRACTION,
        "tick20_max_recovery_fraction_for_lock_in": TICK20_MAX_RECOVERY_FRACTION,
        "action_delta_epsilon": ACTION_DELTA_EPS,
        "expected_candidate_prefixes": EXPECTED_CANDIDATE_PREFIXES,
        "expected_forks": EXPECTED_FORKS,
        "expected_branch_rollouts": EXPECTED_BRANCH_ROLLOUTS,
        "branch_rule": (
            "classify early physical-state lock-in only if both checkpoints have exact "
            "1.0 source-recovery fraction at tick 0 and at most 0.25 at tick 20"
        ),
    }:
        raise ValueError("Winner-v27 diagnostic constants changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v27 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v27 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v27 source manifest changed")


def support_terminal_lookup(
    result: Mapping[str, Any], label: str, update: int
) -> dict[tuple[str, str], int | None]:
    checkpoint = next(
        row
        for row in result["checkpoint_results"]
        if row["label"] == label and row["update"] == update
    )
    rows = {
        (row["configuration_id"], row["plant"]): (
            None if row["terminal"] is None else int(row["terminal"]["tick"])
        )
        for row in checkpoint["core_model_plant_cells"]
        if row["configuration_id"] in CONFIGURATION_IDS
    }
    expected = {
        (configuration, plant)
        for configuration in CONFIGURATION_IDS
        for plant in ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
    }
    if set(rows) != expected:
        raise ValueError("Winner-v27 support-terminal population changed")
    return rows


def right_censor_terminal(value: int | None) -> int | None:
    return None if value is None or value >= ABSOLUTE_END_TICK else value


def compact_rollout(
    *,
    mujoco: Any,
    smoke: Any,
    session: Any,
    episode: Any,
    snapshot: Mapping[str, Any],
    initial_observation: np.ndarray,
    initial_previous_action: np.ndarray,
    initial_h_in: np.ndarray,
    fork_tick: int,
) -> dict[str, Any]:
    v25.restore_episode(mujoco, episode, snapshot)
    observation = np.asarray(initial_observation, dtype=np.float32).copy()
    previous_action = np.asarray(initial_previous_action, dtype=np.float32).copy()
    h_in = np.asarray(initial_h_in, dtype=np.float32).copy()
    if not np.array_equal(episode.previous_action, previous_action):
        raise ValueError("Winner-v27 restored previous action changed")
    observations: list[np.ndarray] = []
    actions: list[np.ndarray] = []
    hidden: list[np.ndarray] = []
    pitch: list[float] = []
    roll: list[float] = []
    terminal = None
    valid_ticks = 0
    for relative_tick in range(ABSOLUTE_END_TICK - fork_tick):
        observations.append(observation.copy())
        action, h_out = v25.infer(session, observation, previous_action, h_in)
        if not np.array_equal(action, smoke.bounded_action_numpy(action, previous_action)):
            raise ValueError("Winner-v27 graph action boundary changed")
        actions.append(action.copy())
        hidden.append(h_out.copy())
        valid, next_observation, evidence = episode.step(action)
        current_roll, current_pitch = smoke.roll_pitch_wxyz(
            np.asarray(episode.data.qpos[3:7], dtype=np.float64)
        )
        roll.append(float(current_roll))
        pitch.append(float(current_pitch))
        if not valid:
            terminal = {
                **evidence,
                "relative_tick": relative_tick,
                "absolute_tick": fork_tick + valid_ticks,
            }
            break
        valid_ticks += 1
        if next_observation is None:
            raise ValueError("Winner-v27 valid transition omitted observation")
        observation = next_observation
        previous_action = action
        h_in = h_out
    for sequence in (observations, actions, hidden):
        if not all(np.all(np.isfinite(value)) for value in sequence):
            raise FloatingPointError("Winner-v27 branch array is nonfinite")
    if not all(math.isfinite(value) for value in [*roll, *pitch]):
        raise FloatingPointError("Winner-v27 branch pose is nonfinite")
    specification = mujoco.mjtState.mjSTATE_INTEGRATION
    end_state = np.empty(
        int(mujoco.mj_stateSize(episode.model, specification)), dtype=np.float64
    )
    mujoco.mj_getState(episode.model, episode.data, end_state, specification)
    return {
        "attempted_ticks": len(actions),
        "valid_ticks": valid_ticks,
        "terminal": terminal,
        "terminal_absolute_tick": None if terminal is None else terminal["absolute_tick"],
        "initial_action": actions[0].astype(float).tolist(),
        "observations_sha256": v25.array_sha256(np.stack(observations)),
        "actions_sha256": v25.array_sha256(np.stack(actions)),
        "hidden_outputs_sha256": v25.array_sha256(np.stack(hidden)),
        "roll_rad": roll,
        "pitch_rad": pitch,
        "end_state_sha256": v25.array_sha256(end_state),
    }


def compare_recovery(
    candidate: Mapping[str, Any], source: Mapping[str, Any]
) -> dict[str, Any]:
    candidate_terminal = candidate["terminal_absolute_tick"]
    source_terminal = source["terminal_absolute_tick"]
    recovered = source_terminal is None or (
        candidate_terminal is not None and int(source_terminal) > int(candidate_terminal)
    )
    lead = (
        0
        if not recovered or candidate_terminal is None
        else (
            ABSOLUTE_END_TICK if source_terminal is None else int(source_terminal)
        )
        - int(candidate_terminal)
    )
    action_delta = float(
        np.max(
            np.abs(
                np.asarray(source["initial_action"], dtype=np.float64)
                - np.asarray(candidate["initial_action"], dtype=np.float64)
            )
        )
    )
    return {
        "source_recovers": bool(recovered),
        "source_survival_lead_ticks": int(lead),
        "initial_action_delta_linf": action_delta,
        "initial_action_changed": bool(action_delta > ACTION_DELTA_EPS),
    }


def aggregate_scan(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    aggregates: dict[str, Any] = {}
    for label, update in CANDIDATES:
        selected = [row for row in rows if row["candidate"] == label]
        by_tick: dict[str, Any] = {}
        for tick in FORK_TICKS:
            at_tick = [row for row in selected if row["fork_tick"] == tick]
            recovered = sum(row["comparison"]["source_recovers"] for row in at_tick)
            leads = [row["comparison"]["source_survival_lead_ticks"] for row in at_tick]
            by_tick[str(tick)] = {
                "forks": len(at_tick),
                "recovered": recovered,
                "recovery_fraction": recovered / len(at_tick),
                "source_survival_lead_ticks": {
                    "minimum": min(leads),
                    "median": float(statistics.median(leads)),
                    "mean": float(statistics.fmean(leads)),
                    "maximum": max(leads),
                },
            }
        latest: list[int | None] = []
        for configuration in CONFIGURATION_IDS:
            for plant in ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"):
                recovered_ticks = [
                    row["fork_tick"]
                    for row in selected
                    if row["configuration_id"] == configuration
                    and row["plant"] == plant
                    and row["comparison"]["source_recovers"]
                ]
                latest.append(max(recovered_ticks) if recovered_ticks else None)
        tick0 = by_tick["0"]["recovery_fraction"]
        tick20 = by_tick["20"]["recovery_fraction"]
        aggregates[label] = {
            "update": update,
            "forks": len(selected),
            "by_fork_tick": by_tick,
            "latest_recoverable_tick_by_cell": latest,
            "meets_frozen_early_state_lock_in_rule": bool(
                tick0 == TICK0_RECOVERY_FRACTION
                and tick20 <= TICK20_MAX_RECOVERY_FRACTION
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
            "Winner-v27 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v27 result")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v27 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v26 = json.loads(V26_RESULT.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    if (
        v26.get("status") != "PASS_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
        or v26.get("decision")
        != "AUTHORIZE_EARLY_PREFIX_DIVERGENCE_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v24.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v27 source authority changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v27 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v27 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file() or smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v27 scene changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(json.loads(DOMAIN.read_text(encoding="utf-8")))

    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == SOURCE_UPDATE
    )
    source_graph_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    v25.validate_artifact(source_graph_path, source_graph, "winner_v22_final.onnx")
    source_session = v25.graph_session(ort, source_graph_path)
    v24_checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    candidate_sessions = {}
    candidate_identities = {}
    for label, update in CANDIDATES:
        graph_path = args.v24_training_work_root / f"graphs/winner_v24_{label}.onnx"
        graph = v24_checkpoints[label]["graph"]
        v25.validate_artifact(graph_path, graph, f"winner_v24_{label}.onnx")
        candidate_sessions[label] = v25.graph_session(ort, graph_path)
        candidate_identities[label] = {"update": update, "onnx_sha256": graph["sha256"]}
    v22_support = json.loads(V22_SUPPORT.read_text(encoding="utf-8"))
    v24_support = json.loads(V24_SUPPORT.read_text(encoding="utf-8"))
    expected_source_terminal = support_terminal_lookup(v22_support, "final", 100)
    expected_candidate_terminal = {
        label: support_terminal_lookup(v24_support, label, update)
        for label, update in CANDIDATES
    }

    rows: list[dict[str, Any]] = []
    candidate_prefixes = 0
    branch_rollouts = 0
    all_prefixes_valid = True
    all_source_repeats_exact = True
    all_candidate_continuations_exact = True
    all_fork0_support_replays_exact = True
    for label, update in CANDIDATES:
        candidate_session = candidate_sessions[label]
        for configuration_id in CONFIGURATION_IDS:
            configuration = configurations[configuration_id]
            for plant in smoke.PLANTS:
                base = smoke.Episode(
                    mujoco,
                    scene,
                    configuration,
                    plant,
                    design,
                    observer_type,
                    args.canonical_fit,
                )
                observation = base.observation()
                previous_action = np.zeros((14,), dtype=np.float32)
                candidate_h = np.zeros((64,), dtype=np.float32)
                source_shadow_h = np.zeros((64,), dtype=np.float32)
                snapshots: dict[int, dict[str, Any]] = {}
                candidate_prefixes += 1
                for tick in range(21):
                    if tick in FORK_TICKS:
                        snapshots[tick] = {
                            "episode": v25.capture_episode(mujoco, base),
                            "observation": observation.copy(),
                            "previous_action": previous_action.copy(),
                            "candidate_h": candidate_h.copy(),
                            "source_shadow_h": source_shadow_h.copy(),
                        }
                    if tick == 20:
                        break
                    candidate_action, candidate_h_out = v25.infer(
                        candidate_session,
                        observation,
                        previous_action,
                        candidate_h,
                    )
                    _, source_shadow_h_out = v25.infer(
                        source_session,
                        observation,
                        previous_action,
                        source_shadow_h,
                    )
                    valid, next_observation, _ = base.step(candidate_action)
                    if not valid or next_observation is None:
                        all_prefixes_valid = False
                        break
                    observation = next_observation
                    previous_action = candidate_action
                    candidate_h = candidate_h_out
                    source_shadow_h = source_shadow_h_out
                if not all_prefixes_valid:
                    break
                candidate_terminal_across_forks: list[int | None] = []
                for fork_tick in FORK_TICKS:
                    item = snapshots[fork_tick]
                    candidate_probe = smoke.Episode(
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
                    candidate_trace = compact_rollout(
                        mujoco=mujoco,
                        smoke=smoke,
                        session=candidate_session,
                        episode=candidate_probe,
                        snapshot=item["episode"],
                        initial_observation=item["observation"],
                        initial_previous_action=item["previous_action"],
                        initial_h_in=item["candidate_h"],
                        fork_tick=fork_tick,
                    )
                    source_trace = compact_rollout(
                        mujoco=mujoco,
                        smoke=smoke,
                        session=source_session,
                        episode=source_probe,
                        snapshot=item["episode"],
                        initial_observation=item["observation"],
                        initial_previous_action=item["previous_action"],
                        initial_h_in=item["source_shadow_h"],
                        fork_tick=fork_tick,
                    )
                    repeat_trace = compact_rollout(
                        mujoco=mujoco,
                        smoke=smoke,
                        session=source_session,
                        episode=repeat_probe,
                        snapshot=item["episode"],
                        initial_observation=item["observation"],
                        initial_previous_action=item["previous_action"],
                        initial_h_in=item["source_shadow_h"],
                        fork_tick=fork_tick,
                    )
                    branch_rollouts += 3
                    repeat_exact = source_trace == repeat_trace
                    all_source_repeats_exact &= repeat_exact
                    candidate_terminal_across_forks.append(
                        candidate_trace["terminal_absolute_tick"]
                    )
                    if candidate_trace["terminal_absolute_tick"] != expected_candidate_terminal[
                        label
                    ][(configuration_id, plant)]:
                        all_candidate_continuations_exact = False
                    if fork_tick == 0 and source_trace["terminal_absolute_tick"] != (
                        right_censor_terminal(
                            expected_source_terminal[(configuration_id, plant)]
                        )
                    ):
                        all_fork0_support_replays_exact = False
                    rows.append(
                        {
                            "candidate": label,
                            "candidate_update": update,
                            "configuration_id": configuration_id,
                            "plant": plant,
                            "fork_tick": fork_tick,
                            "snapshot_state_sha256": v25.array_sha256(
                                item["episode"]["state"]
                            ),
                            "observation_sha256": v25.array_sha256(item["observation"]),
                            "previous_action_sha256": v25.array_sha256(
                                item["previous_action"]
                            ),
                            "candidate_h_sha256": v25.array_sha256(item["candidate_h"]),
                            "source_shadow_h_sha256": v25.array_sha256(
                                item["source_shadow_h"]
                            ),
                            "candidate_trace": candidate_trace,
                            "source_recovery_trace": source_trace,
                            "source_repeat_exact": repeat_exact,
                            "comparison": compare_recovery(candidate_trace, source_trace),
                        }
                    )
                if len(set(candidate_terminal_across_forks)) != 1:
                    all_candidate_continuations_exact = False
            if not all_prefixes_valid:
                break
        if not all_prefixes_valid:
            break

    aggregates = aggregate_scan(rows)
    lock_in = all(
        row["meets_frozen_early_state_lock_in_rule"] for row in aggregates.values()
    )
    classification = (
        "EARLY_PREFIX_PHYSICAL_STATE_LOCK_IN"
        if lock_in
        else "EARLY_PREFIX_STATE_REMAINS_SOURCE_RECOVERABLE"
    )
    decision = (
        "AUTHORIZE_PREFIX_JOINT_GROUP_ACTION_CAUSAL_SCREEN_PREREGISTRATION_ONLY"
        if lock_in
        else "AUTHORIZE_STATE_CONTROLLER_CROSS_SWAP_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    checks = {
        "exact_40_candidate_prefixes": candidate_prefixes == EXPECTED_CANDIDATE_PREFIXES,
        "all_candidate_prefixes_valid_through_tick_20": all_prefixes_valid,
        "exact_240_forks": len(rows) == EXPECTED_FORKS,
        "exact_720_branch_rollouts": branch_rollouts == EXPECTED_BRANCH_ROLLOUTS,
        "all_source_recovery_repeats_bit_exact": all_source_repeats_exact,
        "all_candidate_continuations_reproduce_support_terminal": (
            all_candidate_continuations_exact
        ),
        "all_fork0_source_replays_reproduce_v22_support_terminal": (
            all_fork0_support_replays_exact
        ),
        "all_initial_source_candidate_actions_changed": all(
            row["comparison"]["initial_action_changed"] for row in rows
        ),
        "all_metrics_finite": all(
            math.isfinite(float(row["comparison"]["initial_action_delta_linf"]))
            for row in rows
        ),
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        classification = "INVALID_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    result = {
        "schema_version": "winner_v27.early_prefix_recovery_scan_result.v1",
        "status": (
            "PASS_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
            if not failed
            else "HOLD_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
        ),
        "classification": classification,
        "decision": decision,
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
            "fork_ticks": list(FORK_TICKS),
            "absolute_end_tick": ABSOLUTE_END_TICK,
        },
        "thresholds": {
            "tick0_required_recovery_fraction": TICK0_RECOVERY_FRACTION,
            "tick20_max_recovery_fraction_for_lock_in": (
                TICK20_MAX_RECOVERY_FRACTION
            ),
            "action_delta_epsilon": ACTION_DELTA_EPS,
        },
        "fork_results": rows,
        "candidate_aggregates": aggregates,
        "execution": {
            "candidate_prefixes": candidate_prefixes,
            "forks": len(rows),
            "branch_rollouts": branch_rollouts,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v26_result_lf_sha256": lf_sha256(V26_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "v22_support_lf_sha256": lf_sha256(V22_SUPPORT),
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
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
