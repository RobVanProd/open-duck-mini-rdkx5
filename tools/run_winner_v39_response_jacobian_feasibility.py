#!/usr/bin/env python3
"""Run one frozen CPU-only mirrored response-Jacobian support screen."""

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
import run_winner_v38_mirrored_pitch_shooting_feasibility as v38  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v39_response_jacobian_feasibility_preregistration.json"
V38_RESULT = ANALYSIS / "winner_v38_mirrored_pitch_shooting_feasibility_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = ("COM_X_NEG",)
PITCH_INDICES = (2, 3, 4, 11, 12, 13)
MIRRORED_DIMENSIONS = 3
TICKS = 250
RESPONSE_HORIZON_TICKS = 8


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status")
        != "PREREGISTERED_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_RESPONSE_JACOBIAN_COM_X_NEG_SCREEN"
    ):
        raise ValueError("Winner-v39 is not preregistered")
    expected = {
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "controlled_action_indices": list(PITCH_INDICES),
        "response_dimensions": ["base_pitch_rad", "body_pitch_rate_rad_s"],
        "control_dimensions": ["hip_pitch_magnitude", "knee", "ankle"],
        "duration_ticks": TICKS,
        "response_horizon_ticks": RESPONSE_HORIZON_TICKS,
        "finite_difference_scale": "minimum paired graph action delta per mirrored axis",
        "solver": "numpy.linalg.lstsq(rcond=None), minimum-norm correction",
        "correction_bound": "one finite-difference step per mirrored axis",
        "expected_cells": 2,
    }
    screen = value.get("screen", {})
    if any(screen.get(name) != expected_value for name, expected_value in expected.items()):
        raise ValueError("Winner-v39 screen constants changed")
    if value.get("execution_now") != {
        "response_jacobian_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v39 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v39 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v39 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v39 source manifest changed")


def mirrored_steps(smoke: Any) -> np.ndarray:
    delta = np.asarray(smoke.networks.INTERNAL_ACTION_DELTA, dtype=np.float32)
    if delta.shape != (14,) or np.any(delta <= 0.0) or not np.all(np.isfinite(delta)):
        raise ValueError("Winner-v39 graph action delta changed")
    return np.asarray(
        [min(delta[2], delta[11]), min(delta[3], delta[12]), min(delta[4], delta[13])],
        dtype=np.float32,
    )


def expand_mirrored_target(coordinates: np.ndarray) -> np.ndarray:
    values = np.asarray(coordinates, dtype=np.float32)
    if values.shape != (MIRRORED_DIMENSIONS,) or not np.all(np.isfinite(values)):
        raise ValueError("Winner-v39 mirrored target changed")
    action = np.zeros(14, dtype=np.float32)
    action[np.asarray(PITCH_INDICES, dtype=np.int64)] = values @ v38.MIRROR_MATRIX.T
    return action


def signed_response(smoke: Any, episode: Any, evidence: Mapping[str, Any]) -> np.ndarray:
    gyro = np.asarray(
        smoke.sensor_vector(episode.mujoco, episode.model, episode.data, "gyro"),
        dtype=np.float64,
    )
    if gyro.shape != (3,) or not np.all(np.isfinite(gyro)):
        raise FloatingPointError("Winner-v39 signed gyro changed")
    response = np.asarray([float(evidence["pitch_rad"]), float(gyro[1])], dtype=np.float64)
    if not np.all(np.isfinite(response)):
        raise FloatingPointError("Winner-v39 response is nonfinite")
    return response


def simulate_target_response(
    *, mujoco: Any, smoke: Any, episode: Any, snapshot: Mapping[str, Any],
    mirrored_target: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    v25.restore_episode(mujoco, episode, snapshot)
    raw_target = expand_mirrored_target(mirrored_target)
    prior = episode.previous_action
    valid_ticks = 0
    terminal = None
    evidence: Mapping[str, Any] | None = None
    actions: list[np.ndarray] = []
    for tick in range(RESPONSE_HORIZON_TICKS):
        action = smoke.bounded_action_numpy(raw_target, prior)
        valid, _, evidence = episode.step(action)
        actions.append(action.copy())
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
        valid_ticks += 1
        prior = action
    if evidence is None:
        raise AssertionError("Winner-v39 response rollout is empty")
    response = signed_response(smoke, episode, evidence)
    return response, {
        "valid_ticks": valid_ticks,
        "terminal": terminal,
        "response": response.tolist(),
        "action_sequence_sha256": smoke.array_sha256(
            np.asarray(actions, dtype=np.float32)
        ),
    }


def plan_action(
    *, mujoco: Any, smoke: Any, episode: Any,
) -> tuple[np.ndarray, dict[str, Any]]:
    snapshot = v25.capture_episode(mujoco, episode)
    previous = episode.previous_action
    base = v38.project_previous_to_mirrored(previous)
    steps = mirrored_steps(smoke)
    baseline_response, baseline_receipt = simulate_target_response(
        mujoco=mujoco, smoke=smoke, episode=episode, snapshot=snapshot,
        mirrored_target=base,
    )
    jacobian = np.zeros((2, MIRRORED_DIMENSIONS), dtype=np.float64)
    perturbations: list[dict[str, Any]] = []
    for axis in range(MIRRORED_DIMENSIONS):
        plus = base.copy()
        minus = base.copy()
        plus[axis] = np.clip(plus[axis] + steps[axis], -1.0, 1.0)
        minus[axis] = np.clip(minus[axis] - steps[axis], -1.0, 1.0)
        denominator = float(plus[axis] - minus[axis])
        if denominator <= 0.0:
            raise ValueError("Winner-v39 finite-difference interval collapsed")
        plus_response, plus_receipt = simulate_target_response(
            mujoco=mujoco, smoke=smoke, episode=episode, snapshot=snapshot,
            mirrored_target=plus,
        )
        minus_response, minus_receipt = simulate_target_response(
            mujoco=mujoco, smoke=smoke, episode=episode, snapshot=snapshot,
            mirrored_target=minus,
        )
        jacobian[:, axis] = (plus_response - minus_response) / denominator
        perturbations.append(
            {
                "axis": axis,
                "minus_target_sha256": smoke.array_sha256(minus),
                "plus_target_sha256": smoke.array_sha256(plus),
                "denominator": denominator,
                "minus": minus_receipt,
                "plus": plus_receipt,
            }
        )
    unclipped_correction, residuals, rank, singular_values = np.linalg.lstsq(
        jacobian, -baseline_response, rcond=None
    )
    correction = np.clip(
        unclipped_correction, -steps.astype(np.float64), steps.astype(np.float64)
    )
    target = np.clip(base.astype(np.float64) + correction, -1.0, 1.0).astype(np.float32)
    raw_target = expand_mirrored_target(target)
    action = smoke.bounded_action_numpy(raw_target, previous)
    predicted_response = baseline_response + jacobian @ correction
    v25.restore_episode(mujoco, episode, snapshot)
    return action, {
        "baseline_target_sha256": smoke.array_sha256(base),
        "baseline": baseline_receipt,
        "finite_difference_steps": steps.astype(float).tolist(),
        "perturbations": perturbations,
        "jacobian_sha256": smoke.array_sha256(jacobian),
        "jacobian_rank": int(rank),
        "singular_values": np.asarray(singular_values, dtype=float).tolist(),
        "lstsq_residuals": np.asarray(residuals, dtype=float).tolist(),
        "unclipped_correction_sha256": smoke.array_sha256(unclipped_correction),
        "clipped_correction": correction.tolist(),
        "target_sha256": smoke.array_sha256(target),
        "predicted_response": predicted_response.tolist(),
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
) -> dict[str, Any]:
    episode = smoke.Episode(
        mujoco, scene, configuration, plant, calibrator_design,
        observer_type, canonical_fit,
    )
    if episode.initial_contacts != (1, 1):
        raise ValueError("Winner-v39 cell does not start with both feet loaded")
    trace: list[dict[str, Any]] = []
    actions: list[np.ndarray] = []
    terminal = None
    all_actions_bounded = True
    any_nonzero_action = False
    all_jacobians_full_row_rank = True
    for tick in range(TICKS):
        action, planning = plan_action(
            mujoco=mujoco, smoke=smoke, episode=episode,
        )
        all_jacobians_full_row_rank &= planning["jacobian_rank"] == 2
        bounded = np.array_equal(
            action, smoke.bounded_action_numpy(action, episode.previous_action)
        )
        all_actions_bounded &= bounded
        if not bounded:
            raise ValueError("Winner-v39 selected action violates graph boundary")
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
        "all_jacobians_full_row_rank": bool(all_jacobians_full_row_rank),
        "any_nonzero_action": bool(any_nonzero_action),
        "action_trace_sha256": smoke.array_sha256(np.asarray(actions, dtype=np.float32)),
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
            "Winner-v39 requires --offline-cpu-only --oracle-feasibility-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v39 result")

    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v39 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v38_result = json.loads(V38_RESULT.read_text(encoding="utf-8"))
    if (
        v38_result.get("status")
        != "HOLD_WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY"
        or v38_result.get("decision") != "CLOSE_MIRRORED_PITCH_SHOOTING_MECHANISM"
        or v38_result.get("summary", {}).get("support_passes") != 0
    ):
        raise ValueError("Winner-v38 does not support a new controller family")
    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v39 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v39 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )

    cells: list[dict[str, Any]] = []
    for configuration_id in CONFIGURATION_IDS:
        for plant in smoke.PLANTS:
            cells.append(
                run_cell(
                    mujoco=mujoco, smoke=smoke, reviewed_gate=reviewed_gate,
                    scene=scene, configuration=configurations[configuration_id],
                    plant=plant, calibrator_design=calibrator_design,
                    observer_type=observer_type, canonical_fit=args.canonical_fit,
                )
            )

    validity_checks = {
        "exact_2_anchor_cells": len(cells) == 2,
        "all_response_jacobians_full_row_rank": all(
            row["all_jacobians_full_row_rank"] for row in cells
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
        status = "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        classification = "INVALID_RESPONSE_JACOBIAN_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        classification = "LOCAL_RESPONSE_JACOBIAN_COM_X_NEG_CONTROL_FEASIBLE"
        decision = "AUTHORIZE_RESPONSE_JACOBIAN_TEACHER_CONTRACT_ONLY"
    else:
        status = "HOLD_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        classification = "LOCAL_RESPONSE_JACOBIAN_NOT_FULL_HORIZON_FEASIBLE"
        decision = "CLOSE_LOCAL_RESPONSE_JACOBIAN_CONTROLLER"
    result = {
        "schema_version": "winner_v39.response_jacobian_feasibility_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "controller": {
            "configuration_ids": list(CONFIGURATION_IDS),
            "controlled_action_indices": list(PITCH_INDICES),
            "response_dimensions": ["base_pitch_rad", "body_pitch_rate_rad_s"],
            "control_dimensions": ["hip_pitch_magnitude", "knee", "ankle"],
            "duration_ticks": TICKS,
            "response_horizon_ticks": RESPONSE_HORIZON_TICKS,
            "finite_difference_scale": (
                "minimum paired graph action delta per mirrored axis"
            ),
            "solver": "numpy.linalg.lstsq(rcond=None), minimum-norm correction",
            "correction_bound": "one finite-difference step per mirrored axis",
        },
        "cell_results": cells,
        "summary": {
            "support_passes": sum(row["support_pass"] for row in cells),
            "terminal_ticks": [
                None if row["terminal"] is None else row["terminal"]["tick"]
                for row in cells
            ],
            "v38_terminal_ticks": v38_result["summary"]["terminal_ticks"],
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
            "response_jacobian_cells": len(cells),
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v38_result_lf_sha256": lf_sha256(V38_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "pass_authorizes_only": "one separately frozen response-Jacobian teacher contract",
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
