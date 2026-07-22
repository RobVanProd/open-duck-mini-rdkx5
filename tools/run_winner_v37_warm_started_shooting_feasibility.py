#!/usr/bin/env python3
"""Run one frozen CPU-only warm-started support-oracle screen."""

from __future__ import annotations

import argparse
import hashlib
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
import run_winner_v36_support_oracle_shooting_feasibility as v36  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v37_warm_started_shooting_feasibility_preregistration.json"
V36_RESULT = ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = v36.CONFIGURATION_IDS
PITCH_INDICES = v36.PITCH_INDICES
TICKS = v36.TICKS
HORIZON_TICKS = v36.HORIZON_TICKS
ACTION_BLOCK_TICKS = v36.ACTION_BLOCK_TICKS
BLOCKS = v36.BLOCKS
POPULATION = v36.POPULATION
ELITES = v36.ELITES
ITERATIONS = v36.ITERATIONS
INITIAL_STD = v36.INITIAL_STD
MINIMUM_STD = v36.MINIMUM_STD
ROOT_SEED = v36.ROOT_SEED


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status")
        != "PREREGISTERED_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_WARM_STARTED_COM_X_NEG_SCREEN"
    ):
        raise ValueError("Winner-v37 is not preregistered")
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
        raise ValueError("Winner-v37 screen constants changed")
    if screen.get("proposal_memory") != {
        "first_tick": "exact Winner-v36 cold mean",
        "later_ticks": (
            "shift prior winning raw eight-tick plan left by one tick, repeat its "
            "terminal action, then average adjacent pairs into four two-tick blocks"
        ),
        "covariance": "reset every tick to the unchanged 0.20 initial standard deviation",
    }:
        raise ValueError("Winner-v37 proposal memory changed")
    if value.get("execution_now") != {
        "oracle_support_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v37 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v37 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v37 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v37 source manifest changed")


def shift_winning_blocks(raw_blocks: np.ndarray) -> np.ndarray:
    blocks = np.asarray(raw_blocks, dtype=np.float32)
    if blocks.shape != (BLOCKS, len(PITCH_INDICES)) or not np.all(np.isfinite(blocks)):
        raise ValueError("Winner-v37 winning block shape changed")
    expanded = np.repeat(blocks, ACTION_BLOCK_TICKS, axis=0)
    shifted = np.concatenate([expanded[1:], expanded[-1:]], axis=0)
    return np.mean(
        shifted.reshape(BLOCKS, ACTION_BLOCK_TICKS, len(PITCH_INDICES)),
        axis=1,
        dtype=np.float64,
    ).astype(np.float32)


def plan_action(
    *,
    mujoco: Any,
    smoke: Any,
    episode: Any,
    rng: np.random.Generator,
    warm_mean: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    snapshot = v25.capture_episode(mujoco, episode)
    previous = episode.previous_action
    cold_mean = np.repeat(
        previous[np.asarray(PITCH_INDICES, dtype=np.int64)][None, :],
        BLOCKS,
        axis=0,
    ).astype(np.float32)
    if warm_mean is None:
        mean = cold_mean
        warm_start_active = False
    else:
        mean = np.asarray(warm_mean, dtype=np.float32)
        if mean.shape != cold_mean.shape or not np.all(np.isfinite(mean)):
            raise ValueError("Winner-v37 warm mean changed")
        mean = np.clip(mean, -1.0, 1.0).astype(np.float32)
        warm_start_active = True
    input_mean = mean.copy()
    std = np.full_like(mean, np.float32(INITIAL_STD))
    best_rank: tuple[Any, ...] | None = None
    best_sequence: np.ndarray | None = None
    best_blocks: np.ndarray | None = None
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
            sequence = v36.expand_blocks(samples[candidate])
            rank, item, bounded = v36.simulate_sequence(
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
            best_blocks = samples[winner].copy()
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
    if (
        best_sequence is None
        or best_blocks is None
        or best_metrics is None
        or best_rank is None
    ):
        raise AssertionError("Winner-v37 search produced no action")
    next_warm_mean = shift_winning_blocks(best_blocks)
    return best_sequence[0].copy(), next_warm_mean, {
        "warm_start_active": warm_start_active,
        "input_mean_sha256": smoke.array_sha256(input_mean),
        "cold_mean_sha256": smoke.array_sha256(cold_mean),
        "input_mean_differs_from_cold": not np.array_equal(input_mean, cold_mean),
        "next_warm_mean_sha256": smoke.array_sha256(next_warm_mean),
        "winning_raw_blocks_sha256": smoke.array_sha256(best_blocks),
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
    expected_v36_first_action_sha256: str,
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
        raise ValueError("Winner-v37 cell does not start with both feet loaded")
    trace: list[dict[str, Any]] = []
    actions: list[np.ndarray] = []
    warm_means: list[np.ndarray] = []
    warm_mean: np.ndarray | None = None
    terminal = None
    all_actions_bounded = True
    any_nonzero_action = False
    warm_active_after_tick0 = True
    any_warm_mean_differs_from_cold = False
    first_action_matches_v36 = False
    for tick in range(TICKS):
        action, next_warm_mean, planning = plan_action(
            mujoco=mujoco,
            smoke=smoke,
            episode=episode,
            rng=rng,
            warm_mean=warm_mean,
        )
        action_sha256 = smoke.array_sha256(action)
        if tick == 0:
            first_action_matches_v36 = action_sha256 == expected_v36_first_action_sha256
            if not first_action_matches_v36:
                raise ValueError("Winner-v37 first action does not reproduce Winner-v36")
        else:
            warm_active_after_tick0 &= planning["warm_start_active"]
        any_warm_mean_differs_from_cold |= planning["input_mean_differs_from_cold"]
        bounded = np.array_equal(
            action, smoke.bounded_action_numpy(action, episode.previous_action)
        )
        all_actions_bounded &= bounded
        if not bounded:
            raise ValueError("Winner-v37 selected action violates graph boundary")
        any_nonzero_action |= bool(np.any(np.abs(action) > np.float32(1.0e-6)))
        valid, _, evidence = episode.step(action)
        actions.append(action.copy())
        warm_means.append(next_warm_mean.copy())
        trace.append(
            {
                "tick": tick,
                "action_sha256": action_sha256,
                "planning": planning,
                "transition": evidence,
            }
        )
        warm_mean = next_warm_mean
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
        "first_action_matches_v36": bool(first_action_matches_v36),
        "warm_active_after_tick0": bool(warm_active_after_tick0),
        "any_warm_mean_differs_from_cold": bool(any_warm_mean_differs_from_cold),
        "action_trace_sha256": smoke.array_sha256(np.asarray(actions, dtype=np.float32)),
        "warm_mean_trace_sha256": smoke.array_sha256(
            np.asarray(warm_means, dtype=np.float32)
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
            "Winner-v37 requires --offline-cpu-only --oracle-feasibility-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v37 result")

    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v37 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v36_result = json.loads(V36_RESULT.read_text(encoding="utf-8"))
    if (
        v36_result.get("status")
        != "HOLD_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        or v36_result.get("decision")
        != "DO_NOT_USE_V36_SHOOTING_CONTROLLER_AS_TEACHER"
        or v36_result.get("summary", {}).get("support_passes") != 0
    ):
        raise ValueError("Winner-v36 does not support the warm-start falsification")
    expected_first_actions = {
        row["plant"]: row["trace"][0]["action_sha256"]
        for row in v36_result["cell_results"]
    }
    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v37 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v37 Playground commit changed")
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
                expected_v36_first_action_sha256=expected_first_actions[plant],
            )
            cell["prng"] = {
                "algorithm": "NumPy PCG64",
                "seed_sequence_entropy": [ROOT_SEED, 36, configuration_index, plant_index],
                "seed_sequence_state_u32": sequence.generate_state(4).astype(int).tolist(),
            }
            cells.append(cell)

    validity_checks = {
        "exact_2_anchor_cells": len(cells) == 2,
        "all_first_actions_match_v36": all(
            row["first_action_matches_v36"] for row in cells
        ),
        "all_later_ticks_use_warm_start": all(
            row["warm_active_after_tick0"] for row in cells
        ),
        "all_cells_exercise_nontrivial_warm_mean": all(
            row["any_warm_mean_differs_from_cold"] for row in cells
        ),
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
        status = "INVALID_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        classification = "INVALID_WARM_STARTED_SHOOTING_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        classification = "STATEFUL_PROPOSAL_COM_X_NEG_CONTROL_FEASIBLE"
        decision = "AUTHORIZE_FULL_CONFIGURATION_WARM_STARTED_ORACLE_PREREGISTRATION_ONLY"
    else:
        status = "HOLD_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        classification = "STATEFUL_PROPOSAL_NOT_FULL_HORIZON_FEASIBLE"
        decision = "CLOSE_WARM_STARTED_SHOOTING_PROPOSAL_MECHANISM"
    result = {
        "schema_version": "winner_v37.warm_started_shooting_feasibility_result.v1",
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
            "proposal_memory": preregistration["screen"]["proposal_memory"],
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
            "v36_terminal_ticks": v36_result["summary"]["terminal_ticks"],
            "terminal_tick_deltas_vs_v36": [
                (
                    TICKS if row["terminal"] is None else row["terminal"]["tick"]
                ) - v36_tick
                for row, v36_tick in zip(
                    cells, v36_result["summary"]["terminal_ticks"], strict=True
                )
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
            "winner_v36_result_lf_sha256": lf_sha256(V36_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "pass_authorizes_only": (
                "one separately frozen full-configuration CPU warm-started oracle screen"
            ),
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
    print(f"DELTAS_VS_V36={result['summary']['terminal_tick_deltas_vs_v36']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
