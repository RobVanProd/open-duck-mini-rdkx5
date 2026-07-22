#!/usr/bin/env python3
"""Run one frozen CPU-only support-oracle shooting feasibility screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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


PREREGISTRATION = ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_preregistration.json"
V35_RESULT = ANALYSIS / "winner_v35_full_horizon_source_continuation_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = ("COM_X_NEG",)
PITCH_INDICES = (2, 3, 4, 11, 12, 13)
TICKS = 250
HORIZON_TICKS = 8
ACTION_BLOCK_TICKS = 2
BLOCKS = HORIZON_TICKS // ACTION_BLOCK_TICKS
POPULATION = 64
ELITES = 8
ITERATIONS = 4
INITIAL_STD = 0.20
MINIMUM_STD = 0.03
ROOT_SEED = 120120


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status")
        != "PREREGISTERED_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_COM_X_NEG_SHOOTING_SCREEN"
    ):
        raise ValueError("Winner-v36 is not preregistered")
    expected = {
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "controlled_action_indices": list(PITCH_INDICES),
        "duration_ticks": TICKS,
        "horizon_ticks": HORIZON_TICKS,
        "action_block_ticks": ACTION_BLOCK_TICKS,
        "population": POPULATION,
        "elites": ELITES,
        "iterations": ITERATIONS,
        "initial_std": INITIAL_STD,
        "minimum_std": MINIMUM_STD,
        "root_seed": ROOT_SEED,
        "expected_cells": 2,
    }
    screen = value.get("screen", {})
    if any(screen.get(name) != expected_value for name, expected_value in expected.items()):
        raise ValueError("Winner-v36 screen constants changed")
    if value.get("execution_now") != {
        "oracle_support_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v36 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v36 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v36 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v36 source manifest changed")


def expand_blocks(block_values: np.ndarray) -> np.ndarray:
    values = np.asarray(block_values, dtype=np.float32)
    if values.shape != (BLOCKS, len(PITCH_INDICES)):
        raise ValueError("Winner-v36 block sequence shape changed")
    full_blocks = np.zeros((BLOCKS, 14), dtype=np.float32)
    full_blocks[:, np.asarray(PITCH_INDICES, dtype=np.int64)] = values
    return np.repeat(full_blocks, ACTION_BLOCK_TICKS, axis=0)


def simulate_sequence(
    *,
    mujoco: Any,
    smoke: Any,
    episode: Any,
    snapshot: Mapping[str, Any],
    sequence: np.ndarray,
) -> tuple[tuple[Any, ...], dict[str, Any], np.ndarray]:
    v25.restore_episode(mujoco, episode, snapshot)
    prior = episode.previous_action
    bounded_actions: list[np.ndarray] = []
    terminal = None
    final_evidence: Mapping[str, Any] | None = None
    action_delta_energy = 0.0
    action_energy = 0.0
    survival_ticks = 0
    for raw in np.asarray(sequence, dtype=np.float32):
        action = smoke.bounded_action_numpy(raw, prior)
        action_delta_energy += float(np.mean(np.square(action - prior), dtype=np.float64))
        action_energy += float(np.mean(np.square(action), dtype=np.float64))
        valid, _, evidence = episode.step(action)
        bounded_actions.append(action.copy())
        final_evidence = evidence
        if not valid:
            terminal = evidence
            break
        survival_ticks += 1
        prior = action
    summary = episode.summary()
    evidence = dict(final_evidence or {})
    final_tilt = max(abs(float(evidence.get("roll_rad", 0.0))), abs(float(evidence.get("pitch_rad", 0.0))))
    final_gyro = float(evidence.get("gyro_xy_norm_rad_s", math.inf))
    rank = (
        survival_ticks,
        -float(summary["maximum_abs_tilt_rad"]),
        float(summary["minimum_base_z_m"]),
        -final_tilt,
        -final_gyro,
        -action_delta_energy,
        -action_energy,
    )
    return rank, {
        "survival_ticks": survival_ticks,
        "terminal": terminal,
        "maximum_abs_tilt_rad": float(summary["maximum_abs_tilt_rad"]),
        "minimum_base_z_m": float(summary["minimum_base_z_m"]),
        "final_abs_tilt_rad": final_tilt,
        "final_gyro_xy_norm_rad_s": final_gyro,
        "action_delta_energy": action_delta_energy,
        "action_energy": action_energy,
    }, np.asarray(bounded_actions, dtype=np.float32)


def plan_action(
    *,
    mujoco: Any,
    smoke: Any,
    episode: Any,
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[str, Any]]:
    snapshot = v25.capture_episode(mujoco, episode)
    previous = episode.previous_action
    mean = np.repeat(
        previous[np.asarray(PITCH_INDICES, dtype=np.int64)][None, :],
        BLOCKS,
        axis=0,
    ).astype(np.float32)
    std = np.full_like(mean, np.float32(INITIAL_STD))
    best_rank: tuple[Any, ...] | None = None
    best_sequence: np.ndarray | None = None
    best_metrics: dict[str, Any] | None = None
    iteration_receipts: list[dict[str, Any]] = []
    for iteration in range(ITERATIONS):
        samples = rng.normal(
            mean,
            std,
            size=(POPULATION, BLOCKS, len(PITCH_INDICES)),
        ).astype(np.float32)
        samples = np.clip(samples, -1.0, 1.0).astype(np.float32)
        samples[0] = mean
        ranks: list[tuple[Any, ...]] = []
        sequences: list[np.ndarray] = []
        metrics: list[dict[str, Any]] = []
        for candidate in range(POPULATION):
            sequence = expand_blocks(samples[candidate])
            rank, item, bounded = simulate_sequence(
                mujoco=mujoco,
                smoke=smoke,
                episode=episode,
                snapshot=snapshot,
                sequence=sequence,
            )
            ranks.append(rank)
            sequences.append(bounded)
            metrics.append(item)
        order = sorted(range(POPULATION), key=lambda index: ranks[index])[-ELITES:]
        elite = samples[np.asarray(order, dtype=np.int64)]
        mean = np.mean(elite, axis=0, dtype=np.float64).astype(np.float32)
        std = np.maximum(
            np.std(elite, axis=0, dtype=np.float64).astype(np.float32),
            np.float32(MINIMUM_STD),
        )
        winner = max(range(POPULATION), key=lambda index: ranks[index])
        if best_rank is None or ranks[winner] > best_rank:
            best_rank = ranks[winner]
            best_sequence = sequences[winner]
            best_metrics = metrics[winner]
        iteration_receipts.append(
            {
                "iteration": iteration,
                "winning_candidate": winner,
                "winning_rank": list(ranks[winner]),
                "elite_indices": order,
                "mean_sha256": smoke.array_sha256(mean),
                "std_sha256": smoke.array_sha256(std),
            }
        )
    v25.restore_episode(mujoco, episode, snapshot)
    if best_sequence is None or best_metrics is None or best_rank is None:
        raise AssertionError("Winner-v36 search produced no action")
    return best_sequence[0].copy(), {
        "winning_rank": list(best_rank),
        "winning_horizon": best_metrics,
        "winning_sequence_sha256": smoke.array_sha256(best_sequence),
        "iteration_receipts": iteration_receipts,
    }


def run_cell(
    *,
    mujoco: Any,
    smoke: Any,
    reviewed_gate: Any,
    scene: Path,
    configuration: Mapping[str, Any],
    plant: str,
    calibrator_design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    rng: np.random.Generator,
) -> dict[str, Any]:
    episode = smoke.Episode(
        mujoco,
        scene,
        configuration,
        plant,
        calibrator_design,
        observer_type,
        canonical_fit,
    )
    if episode.initial_contacts != (1, 1):
        raise ValueError("Winner-v36 cell does not start with both feet loaded")
    trace: list[dict[str, Any]] = []
    actions: list[np.ndarray] = []
    terminal = None
    all_actions_bounded = True
    any_nonzero_action = False
    for tick in range(TICKS):
        action, planning = plan_action(
            mujoco=mujoco,
            smoke=smoke,
            episode=episode,
            rng=rng,
        )
        bounded = np.array_equal(
            action, smoke.bounded_action_numpy(action, episode.previous_action)
        )
        all_actions_bounded &= bounded
        if not bounded:
            raise ValueError("Winner-v36 selected action violates graph boundary")
        any_nonzero_action |= bool(np.any(np.abs(action) > np.float32(1.0e-6)))
        valid, _, evidence = episode.step(action)
        actions.append(action.copy())
        trace.append(
            {
                "tick": tick,
                "action_sha256": smoke.array_sha256(action),
                "planning": planning,
                "transition": evidence,
            }
        )
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
    summary = episode.summary()
    return {
        "configuration_id": configuration["id"],
        "configuration_sha256": smoke.canonical_sha256(configuration),
        "plant": plant,
        "controlled_action_indices": list(PITCH_INDICES),
        "terminal": terminal,
        "episode": summary,
        "support_pass": reviewed_gate.support_pass(summary) and terminal is None,
        "all_actions_bounded": bool(all_actions_bounded),
        "any_nonzero_action": bool(any_nonzero_action),
        "action_trace_sha256": smoke.array_sha256(
            np.asarray(actions, dtype=np.float32)
        ),
        "trace": trace,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--oracle-feasibility-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.oracle_feasibility_authorized:
        raise PermissionError(
            "Winner-v36 requires --offline-cpu-only --oracle-feasibility-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v36 result")

    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v36 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v35 = json.loads(V35_RESULT.read_text(encoding="utf-8"))
    if (
        v35.get("status") != "HOLD_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        or v35.get("decision") != "CLOSE_V28_HYBRID_TEACHER_ROUTE"
    ):
        raise ValueError("Winner-v35 does not authorize a new feasibility mechanism")
    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v36 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v36 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )

    cells: list[dict[str, Any]] = []
    for configuration_index, configuration_id in enumerate(CONFIGURATION_IDS):
        for plant_index, plant in enumerate(smoke.PLANTS):
            sequence = np.random.SeedSequence(
                [ROOT_SEED, 36, configuration_index, plant_index]
            )
            rng = np.random.Generator(np.random.PCG64(sequence))
            cell = run_cell(
                mujoco=mujoco,
                smoke=smoke,
                reviewed_gate=reviewed_gate,
                scene=scene,
                configuration=configurations[configuration_id],
                plant=plant,
                calibrator_design=calibrator_design,
                observer_type=observer_type,
                canonical_fit=args.canonical_fit,
                rng=rng,
            )
            cell["prng"] = {
                "algorithm": "NumPy PCG64",
                "seed_sequence_entropy": [ROOT_SEED, 36, configuration_index, plant_index],
                "seed_sequence_state_u32": sequence.generate_state(4).astype(int).tolist(),
            }
            cells.append(cell)

    validity_checks = {
        "exact_2_anchor_cells": len(cells) == 2,
        "all_selected_actions_graph_bounded": all(
            row["all_actions_bounded"] for row in cells
        ),
        "all_cells_use_nonzero_control": all(row["any_nonzero_action"] for row in cells),
    }
    efficacy_checks = {
        "both_plants_pass_full_250_tick_support_gate": all(
            row["support_pass"] for row in cells
        ),
    }
    checks = {**validity_checks, **efficacy_checks}
    valid = all(validity_checks.values())
    passed = valid and all(efficacy_checks.values())
    if not valid:
        status = "INVALID_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        classification = "INVALID_SUPPORT_ORACLE_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        classification = "COM_X_NEG_FULL_HORIZON_SHOOTING_CONTROL_FEASIBLE"
        decision = "AUTHORIZE_FULL_CONFIGURATION_ORACLE_FEASIBILITY_PREREGISTRATION_ONLY"
    else:
        status = "HOLD_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        classification = "THIS_SHOOTING_CONTROLLER_NOT_FULL_HORIZON_FEASIBLE"
        decision = "DO_NOT_USE_V36_SHOOTING_CONTROLLER_AS_TEACHER"
    result = {
        "schema_version": "winner_v36.support_oracle_shooting_feasibility_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "controller": {
            "configuration_ids": list(CONFIGURATION_IDS),
            "controlled_action_indices": list(PITCH_INDICES),
            "duration_ticks": TICKS,
            "horizon_ticks": HORIZON_TICKS,
            "action_block_ticks": ACTION_BLOCK_TICKS,
            "population": POPULATION,
            "elites": ELITES,
            "iterations": ITERATIONS,
            "initial_std": INITIAL_STD,
            "minimum_std": MINIMUM_STD,
            "root_seed": ROOT_SEED,
            "objective": (
                "lexicographic(survival_ticks,-maximum_abs_tilt,+minimum_base_z,"
                "-final_abs_tilt,-final_gyro,-action_delta_energy,-action_energy)"
            ),
        },
        "cell_results": cells,
        "summary": {
            "support_passes": sum(row["support_pass"] for row in cells),
            "terminal_ticks": [
                None if row["terminal"] is None else row["terminal"]["tick"]
                for row in cells
            ],
            "maximum_abs_tilt_rad": max(
                row["episode"]["maximum_abs_tilt_rad"] for row in cells
            ),
            "maximum_current_a": max(
                row["episode"]["maximum_current_a"] for row in cells
            ),
            "maximum_torque_nm": max(
                row["episode"]["maximum_torque_nm"] for row in cells
            ),
        },
        "execution": {
            "oracle_support_cells": len(cells),
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v35_result_lf_sha256": lf_sha256(V35_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "pass_authorizes_only": "one separately frozen full-configuration CPU oracle feasibility screen",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(status)
    print(f"SUPPORT_PASSES={result['summary']['support_passes']}/2")
    print(f"TERMINAL_TICKS={result['summary']['terminal_ticks']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
