#!/usr/bin/env python3
"""Run one frozen CPU-only full-horizon static-equilibrium target screen."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
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
import run_winner_v34_prefix_right_pitch_hard_intervention as v34  # noqa: E402
import run_winner_v38_mirrored_pitch_shooting_feasibility as v38  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v41_static_equilibrium_target_feasibility_preregistration.json"
V40_RESULT = ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = ("COM_X_NEG",)
PITCH_INDICES = (2, 3, 4, 11, 12, 13)
GRID_VALUES = tuple(float(value) for value in np.linspace(-1.0, 1.0, 9))
GRID_DIMENSIONS = 3
EXPECTED_CANDIDATES = 9 ** GRID_DIMENSIONS
TICKS = 250


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status")
        != "PREREGISTERED_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_FULL_HORIZON_STATIC_TARGET_SCREEN"
    ):
        raise ValueError("Winner-v41 is not preregistered")
    expected = {
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "controlled_action_indices": list(PITCH_INDICES),
        "coordinate_order": ["hip_pitch_magnitude", "knee", "ankle"],
        "grid_values": list(GRID_VALUES),
        "grid_dimensions": GRID_DIMENSIONS,
        "candidate_count": EXPECTED_CANDIDATES,
        "duration_ticks": TICKS,
        "target_semantics": "one time-invariant raw action target for all 250 ticks",
        "plant_semantics": "one shared target must pass both measured actuator plants",
    }
    screen = value.get("screen", {})
    if any(screen.get(name) != expected_value for name, expected_value in expected.items()):
        raise ValueError("Winner-v41 screen constants changed")
    if value.get("execution_now") != {
        "static_target_candidates": 0,
        "candidate_plant_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v41 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v41 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v41 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v41 source manifest changed")


def candidate_coordinates() -> list[np.ndarray]:
    rows = [
        np.asarray(values, dtype=np.float32)
        for values in itertools.product(GRID_VALUES, repeat=GRID_DIMENSIONS)
    ]
    if len(rows) != EXPECTED_CANDIDATES:
        raise AssertionError("Winner-v41 grid size changed")
    if not np.array_equal(rows[EXPECTED_CANDIDATES // 2], np.zeros(3, dtype=np.float32)):
        raise AssertionError("Winner-v41 grid center changed")
    return rows


def evaluate_target(
    *, mujoco: Any, smoke: Any, reviewed_gate: Any, episode: Any,
    initial_snapshot: Mapping[str, Any], coordinates: np.ndarray,
    include_trace: bool,
) -> dict[str, Any]:
    v25.restore_episode(mujoco, episode, initial_snapshot)
    raw_target = v38.expand_mirrored_blocks(
        np.asarray(coordinates, dtype=np.float32)[None, :]
    )[0]
    if raw_target.shape != (14,) or np.any(raw_target[5:9] != 0.0):
        raise ValueError("Winner-v41 target expansion changed")
    action_hashes: list[str] = []
    actions: list[np.ndarray] = []
    trace: list[dict[str, Any]] = []
    terminal = None
    all_actions_bounded = True
    for tick in range(TICKS):
        previous = episode.previous_action
        action = smoke.bounded_action_numpy(raw_target, previous)
        bounded = np.array_equal(action, smoke.bounded_action_numpy(action, previous))
        all_actions_bounded &= bounded
        if not bounded:
            raise ValueError("Winner-v41 selected action violates graph boundary")
        valid, _, evidence = episode.step(action)
        action_hash = smoke.array_sha256(action)
        action_hashes.append(action_hash)
        actions.append(action.copy())
        if include_trace:
            trace.append(
                {"tick": tick, "action_sha256": action_hash, "transition": evidence}
            )
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
    summary = episode.summary()
    result = {
        "plant": episode.plant,
        "terminal": terminal,
        "episode": summary,
        "support_pass": reviewed_gate.support_pass(summary) and terminal is None,
        "all_actions_bounded": bool(all_actions_bounded),
        "raw_target_sha256": smoke.array_sha256(raw_target),
        "action_trace_sha256": smoke.array_sha256(np.asarray(actions, dtype=np.float32)),
        "action_hash_chain_sha256": canonical_sha256(action_hashes),
    }
    if include_trace:
        result["trace"] = trace
    return result


def candidate_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    plants = row["plant_results"]
    valid_ticks = [item["episode"]["valid_ticks"] for item in plants]
    support_count = sum(item["support_pass"] for item in plants)
    minimum_base_z = min(item["episode"]["minimum_base_z_m"] for item in plants)
    maximum_tilt = max(item["episode"]["maximum_abs_tilt_rad"] for item in plants)
    maximum_final_gyro = max(
        item["episode"]["maximum_final_window_gyro_xy_norm_rad_s"] for item in plants
    )
    coordinates = np.asarray(row["coordinates"], dtype=np.float64)
    return (
        support_count,
        min(valid_ticks),
        sum(valid_ticks),
        minimum_base_z,
        -maximum_tilt,
        -maximum_final_gyro,
        -float(np.dot(coordinates, coordinates)),
        -int(row["candidate_index"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--static-equilibrium-feasibility-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.static_equilibrium_feasibility_authorized:
        raise PermissionError(
            "Winner-v41 requires --offline-cpu-only "
            "--static-equilibrium-feasibility-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v41 result")

    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v41 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v40 = json.loads(V40_RESULT.read_text(encoding="utf-8"))
    if (
        v40.get("status")
        != "PASS_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
        or v40.get("decision") != "CLOSE_EXACT_V39_CONTROLLER_WITHOUT_RERUN"
        or v40.get("execution", {}).get("simulation_cells") != 0
        or v40.get("authority", {}).get("pass_authorizes_only")
        != "a separately frozen nonlocal support-controller feasibility design"
    ):
        raise ValueError("Winner-v40 does not authorize the V41 design")
    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v41 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v41 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configuration = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )["COM_X_NEG"]

    episodes: dict[str, Any] = {}
    initial_snapshots: dict[str, Mapping[str, Any]] = {}
    for plant in smoke.PLANTS:
        episode = smoke.Episode(
            mujoco, scene, configuration, plant, calibrator_design,
            observer_type, args.canonical_fit,
        )
        if episode.initial_contacts != (1, 1):
            raise ValueError("Winner-v41 cell does not start with both feet loaded")
        episodes[plant] = episode
        initial_snapshots[plant] = v25.capture_episode(mujoco, episode)

    candidates: list[dict[str, Any]] = []
    for candidate_index, coordinates in enumerate(candidate_coordinates()):
        plant_results = [
            evaluate_target(
                mujoco=mujoco, smoke=smoke, reviewed_gate=reviewed_gate,
                episode=episodes[plant], initial_snapshot=initial_snapshots[plant],
                coordinates=coordinates, include_trace=False,
            )
            for plant in smoke.PLANTS
        ]
        candidates.append(
            {
                "candidate_index": candidate_index,
                "coordinates": coordinates.astype(float).tolist(),
                "coordinates_sha256": smoke.array_sha256(coordinates),
                "plant_results": plant_results,
                "shared_support_pass": all(item["support_pass"] for item in plant_results),
            }
        )

    passing = [row for row in candidates if row["shared_support_pass"]]
    selected = max(passing if passing else candidates, key=candidate_key)
    selected_kind = "shared_support_pass" if passing else "diagnostic_best_not_promoted"
    selected_coordinates = np.asarray(selected["coordinates"], dtype=np.float32)
    replay_results = [
        evaluate_target(
            mujoco=mujoco, smoke=smoke, reviewed_gate=reviewed_gate,
            episode=episodes[plant], initial_snapshot=initial_snapshots[plant],
            coordinates=selected_coordinates, include_trace=True,
        )
        for plant in smoke.PLANTS
    ]
    replay_exact = all(
        {name: replay[name] for name in original}
        == original
        for original, replay in zip(selected["plant_results"], replay_results)
    )
    validity_checks = {
        "exact_729_static_targets": len(candidates) == EXPECTED_CANDIDATES,
        "exact_1458_candidate_plant_cells": sum(
            len(row["plant_results"]) for row in candidates
        ) == EXPECTED_CANDIDATES * 2,
        "all_candidate_actions_graph_bounded": all(
            plant["all_actions_bounded"]
            for row in candidates for plant in row["plant_results"]
        ),
        "selected_target_replay_exact": replay_exact,
    }
    efficacy_checks = {
        "at_least_one_shared_target_passes_both_plants": bool(passing),
    }
    checks = {**validity_checks, **efficacy_checks}
    valid = all(validity_checks.values())
    passed = valid and all(efficacy_checks.values())
    if not valid:
        status = "INVALID_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
        classification = "INVALID_STATIC_EQUILIBRIUM_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
        classification = "SHARED_FULL_HORIZON_STATIC_SUPPORT_TARGET_EXISTS"
        decision = "AUTHORIZE_STATIC_TARGET_TEACHER_CONTRACT_ONLY"
    else:
        status = "HOLD_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
        classification = "NO_SHARED_COARSE_GRID_STATIC_SUPPORT_TARGET"
        decision = "CLOSE_STATIC_EQUILIBRIUM_TARGET_ROUTE"
    result = {
        "schema_version": "winner_v41.static_equilibrium_target_feasibility_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": checks,
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "screen": {
            "configuration_ids": list(CONFIGURATION_IDS),
            "controlled_action_indices": list(PITCH_INDICES),
            "coordinate_order": ["hip_pitch_magnitude", "knee", "ankle"],
            "grid_values": list(GRID_VALUES),
            "grid_dimensions": GRID_DIMENSIONS,
            "candidate_count": EXPECTED_CANDIDATES,
            "duration_ticks": TICKS,
            "target_semantics": "one time-invariant raw action target for all 250 ticks",
            "plant_semantics": "one shared target must pass both measured actuator plants",
        },
        "candidate_results": candidates,
        "selection": {
            "kind": selected_kind,
            "candidate_index": selected["candidate_index"],
            "coordinates": selected["coordinates"],
            "coordinates_sha256": selected["coordinates_sha256"],
            "shared_support_pass_count": len(passing),
            "replay_exact": replay_exact,
            "replay_results": replay_results,
        },
        "summary": {
            "shared_support_pass_count": len(passing),
            "per_plant_support_pass_counts": {
                plant: sum(
                    row["plant_results"][plant_index]["support_pass"]
                    for row in candidates
                )
                for plant_index, plant in enumerate(smoke.PLANTS)
            },
            "selected_candidate_index": selected["candidate_index"],
            "selected_coordinates": selected["coordinates"],
            "selected_terminal_ticks": [
                None if row["terminal"] is None else row["terminal"]["tick"]
                for row in replay_results
            ],
        },
        "execution": {
            "static_target_candidates": len(candidates),
            "candidate_plant_cells": sum(len(row["plant_results"]) for row in candidates),
            "selected_target_replay_cells": 2,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v40_result_lf_sha256": lf_sha256(V40_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen static-target teacher contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(status)
    print(f"SHARED_SUPPORT_PASSES={len(passing)}/{EXPECTED_CANDIDATES}")
    print(f"SELECTED_COORDINATES={selected['coordinates']}")
    print(f"SELECTED_TERMINAL_TICKS={result['summary']['selected_terminal_ticks']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
