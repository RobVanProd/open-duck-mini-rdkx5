#!/usr/bin/env python3
"""Run the preregistered read-only Winner-v23 negative-X response-use audit."""

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

PREREGISTRATION = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_preregistration.json"
TRAINING_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
HOLD_ATTRIBUTION = ANALYSIS / "winner_v22_support_hold_attribution.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
V22_GATE_RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_support_gate.py"
CHECKPOINTS = (("half", 50), ("final", 100))
PAIR_IDS = (
    ("COM_X_NEG", "COM_X_POS"),
    ("COM_CORNER_00", "COM_CORNER_04"),
    ("COM_CORNER_01", "COM_CORNER_05"),
    ("COM_CORNER_02", "COM_CORNER_06"),
    ("COM_CORNER_03", "COM_CORNER_07"),
)
EARLY_TICKS = 25
MIN_PERSISTENT_TICKS = 5
HIDDEN_LINF_THRESHOLD = 1.0e-7
FORK_ACTION_LINF_THRESHOLD = 1.0e-5
MIN_DECISION_CELLS = 16


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
        != "winner_v23.negative_x_response_use_diagnostic_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_20_PAIR_CELL_DIAGNOSTIC_ONLY"
        or value.get("execution_now")
        != {
            "paired_cells": 0,
            "physics_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v23 diagnostic preregistration changed")
    diagnostic = value.get("diagnostic", {})
    if (
        diagnostic.get("configuration_pairs") != [list(pair) for pair in PAIR_IDS]
        or diagnostic.get("checkpoint_labels") != ["half", "final"]
        or diagnostic.get("actuator_plants")
        != ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"]
        or diagnostic.get("paired_cells") != 20
        or diagnostic.get("physics_rollouts") != 40
        or diagnostic.get("full_rollout_ticks") != 250
        or diagnostic.get("early_analysis_ticks") != EARLY_TICKS
        or diagnostic.get("minimum_persistent_ticks") != MIN_PERSISTENT_TICKS
        or diagnostic.get("hidden_linf_threshold") != HIDDEN_LINF_THRESHOLD
        or diagnostic.get("same_input_hidden_fork_action_linf_threshold")
        != FORK_ACTION_LINF_THRESHOLD
        or diagnostic.get("minimum_cells_for_branch") != MIN_DECISION_CELLS
    ):
        raise ValueError("Winner-v23 diagnostic constants changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v23 diagnostic sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v23 diagnostic source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v23 diagnostic source manifest changed")


def exact_configurations(domain: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    matrix = domain["evaluation_matrix"]
    rows = [
        *matrix["fixed_anchors"],
        *matrix["discovery_samples"],
        *matrix["heldout_samples"],
    ]
    lookup = {str(row["id"]): row for row in rows}
    expected = {identifier for pair in PAIR_IDS for identifier in pair}
    if not expected.issubset(lookup):
        raise ValueError("Winner-v23 paired configurations are absent")
    for negative_id, positive_id in PAIR_IDS:
        negative = lookup[negative_id]
        positive = lookup[positive_id]
        neg_com = list(negative["torso_com_offset_m"])
        pos_com = list(positive["torso_com_offset_m"])
        left = {key: value for key, value in negative.items() if key not in {"id", "torso_com_offset_m"}}
        right = {key: value for key, value in positive.items() if key not in {"id", "torso_com_offset_m"}}
        if (
            neg_com[0] >= 0.0
            or pos_com[0] <= 0.0
            or neg_com[1:] != pos_com[1:]
            or abs(float(neg_com[0]) + float(pos_com[0])) > 1.0e-12
            or left != right
        ):
            raise ValueError(f"Winner-v23 pair is not an exact X-sign flip: {negative_id}")
    return lookup


def first_persistent_crossing(values: np.ndarray, threshold: float) -> int | None:
    mask = np.asarray(values, dtype=np.float64) > float(threshold)
    for start in range(0, len(mask) - MIN_PERSISTENT_TICKS + 1):
        if bool(np.all(mask[start : start + MIN_PERSISTENT_TICKS])):
            return start
    return None


def inference_actions(
    session: Any,
    observation: np.ndarray,
    previous_action: np.ndarray,
    h_in: np.ndarray,
) -> np.ndarray:
    value = session.run(
        ["calibration_actions"],
        {
            "obs": np.asarray(observation, dtype=np.float32)[None, :],
            "previous_action": np.asarray(previous_action, dtype=np.float32)[None, :],
            "h_in": np.asarray(h_in, dtype=np.float32)[None, :],
        },
    )[0][0]
    return np.asarray(value, dtype=np.float32)


def pair_metrics(
    *,
    session: Any,
    negative: Mapping[str, Any],
    positive: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
    auxiliary_indices: np.ndarray,
) -> dict[str, Any]:
    neg = negative["_arrays"]
    pos = positive["_arrays"]
    common = min(len(neg["observations"]) - 1, len(pos["observations"]) - 1)
    if common < EARLY_TICKS:
        raise ValueError("Winner-v23 pair lacks the frozen 25-tick pre-failure window")
    count = EARLY_TICKS
    hidden_linf = np.max(
        np.abs(neg["hidden"][:count] - pos["hidden"][:count]), axis=1
    )
    action_linf = np.max(
        np.abs(neg["actions"][:count] - pos["actions"][:count]), axis=1
    )
    fork_linf = np.zeros((count,), dtype=np.float64)
    zeros_h = np.zeros((64,), dtype=np.float32)
    zeros_action = np.zeros((14,), dtype=np.float32)
    for tick in range(count):
        h_negative = zeros_h if tick == 0 else neg["hidden"][tick - 1]
        h_positive = zeros_h if tick == 0 else pos["hidden"][tick - 1]
        previous = zeros_action if tick == 0 else neg["actions"][tick - 1]
        action_negative_h = inference_actions(
            session, neg["observations"][tick], previous, h_negative
        )
        action_positive_h = inference_actions(
            session, neg["observations"][tick], previous, h_positive
        )
        fork_linf[tick] = float(
            np.max(np.abs(action_negative_h - action_positive_h))
        )
    neg_target = (
        neg["observations"][1 : count + 1, auxiliary_indices] - target_mean
    ) / target_std
    pos_target = (
        pos["observations"][1 : count + 1, auxiliary_indices] - target_mean
    ) / target_std
    neg_prediction = neg["predictions"][:count]
    pos_prediction = pos["predictions"][:count]
    neg_learned = float(np.mean(np.square(neg_prediction - neg_target), dtype=np.float64))
    neg_constant = float(np.mean(np.square(neg_target), dtype=np.float64))
    pos_learned = float(np.mean(np.square(pos_prediction - pos_target), dtype=np.float64))
    pos_constant = float(np.mean(np.square(pos_target), dtype=np.float64))
    hidden_tick = first_persistent_crossing(hidden_linf, HIDDEN_LINF_THRESHOLD)
    fork_tick = first_persistent_crossing(fork_linf, FORK_ACTION_LINF_THRESHOLD)
    return {
        "common_valid_transition_prefix_ticks": common,
        "early_analysis_ticks": count,
        "hidden_linf_by_tick": hidden_linf.astype(float).tolist(),
        "actual_action_linf_by_tick": action_linf.astype(float).tolist(),
        "same_input_hidden_fork_action_linf_by_tick": fork_linf.astype(float).tolist(),
        "hidden_first_persistent_crossing_tick": hidden_tick,
        "fork_action_first_persistent_crossing_tick": fork_tick,
        "response_encoded_early": hidden_tick is not None,
        "response_used_by_action_early": fork_tick is not None,
        "negative_early_learned_normalized_prediction_mse": neg_learned,
        "negative_early_constant_normalized_prediction_mse": neg_constant,
        "positive_early_learned_normalized_prediction_mse": pos_learned,
        "positive_early_constant_normalized_prediction_mse": pos_constant,
        "predictor_beats_constant_both_signs_early": (
            neg_learned < neg_constant and pos_learned < pos_constant
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--read-only-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.read_only_diagnostic_authorized:
        raise PermissionError(
            "Winner-v23 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v23 diagnostic evidence")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as base_gate
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import run_winner_v22_normalized_predictor_support_gate as v22_gate

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v23 diagnostic requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    training_result = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    attribution = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        training_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training_result.get("decision")
        != "AUTHORIZE_SEPARATE_CORRECTED_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or training_result.get("failed_checks") != []
        or attribution.get("status") != "PASS_WINNER_V22_SUPPORT_HOLD_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or attribution.get("failed_checks") != []
    ):
        raise ValueError("Winner-v23 source evidence changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v23 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v23 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file() or smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v23 scene changed")
    design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = exact_configurations(json.loads(DOMAIN.read_text(encoding="utf-8")))
    observer_type = smoke.load_runtime_observer(args.canonical_fit)

    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    v22_gate.v22v2 = v22v2
    v22_gate._TRAINING = training_result
    session_options = ort.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    paired_results: list[dict[str, Any]] = []
    for label, update in CHECKPOINTS:
        snapshot_path, graph_path = v22_gate.checkpoint_paths(
            args.training_work_root, label
        )
        snapshot = v22v2.load_snapshot(snapshot_path)
        v22_gate._validate_snapshot(
            snapshot, expected_stage="normalized_predictor_joint_stage2"
        )
        if snapshot["metadata"]["completed_updates"] != update:
            raise ValueError("Winner-v23 checkpoint boundary changed")
        parameters = snapshot["parameters"]
        target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
        target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
        session = ort.InferenceSession(
            str(graph_path),
            sess_options=session_options,
            providers=["CPUExecutionProvider"],
        )
        for negative_id, positive_id in PAIR_IDS:
            for plant in smoke.PLANTS:
                negative = base_gate.run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=configurations[negative_id],
                    plant=plant,
                    calibrator_design=design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=session,
                    parameters=parameters,
                    target_mean=target_mean,
                    target_std=target_std,
                )
                positive = base_gate.run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=configurations[positive_id],
                    plant=plant,
                    calibrator_design=design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=session,
                    parameters=parameters,
                    target_mean=target_mean,
                    target_std=target_std,
                )
                metrics = pair_metrics(
                    session=session,
                    negative=negative,
                    positive=positive,
                    target_mean=target_mean,
                    target_std=target_std,
                    auxiliary_indices=training.AUXILIARY_INDICES,
                )
                paired_results.append(
                    {
                        "checkpoint": label,
                        "update": update,
                        "plant": plant,
                        "negative_configuration_id": negative_id,
                        "positive_configuration_id": positive_id,
                        "negative_support_pass": negative["support_pass"],
                        "positive_support_pass": positive["support_pass"],
                        "negative_terminal": negative["terminal"],
                        "positive_terminal": positive["terminal"],
                        "negative_trace_hashes": negative["trace_hashes"],
                        "positive_trace_hashes": positive["trace_hashes"],
                        **metrics,
                    }
                )
    encoded = sum(row["response_encoded_early"] for row in paired_results)
    used = sum(row["response_used_by_action_early"] for row in paired_results)
    predicted = sum(
        row["predictor_beats_constant_both_signs_early"] for row in paired_results
    )
    if encoded >= MIN_DECISION_CELLS and predicted >= MIN_DECISION_CELLS:
        if used >= MIN_DECISION_CELLS:
            classification = "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE"
            decision = "AUTHORIZE_NEGATIVE_X_SUPPORT_CONTROL_OBJECTIVE_CPU_CONTRACT_ONLY"
        else:
            classification = "RESPONSE_STATE_PRESENT_ACTION_COUPLING_DEFICIT"
            decision = "AUTHORIZE_RESPONSE_ACTION_COUPLING_CPU_CONTRACT_ONLY"
    else:
        classification = "EARLY_RESPONSE_INFERENCE_DEFICIT"
        decision = "AUTHORIZE_EARLY_RESPONSE_INFERENCE_CPU_CONTRACT_ONLY"
    checks = {
        "exact_20_paired_cells": len(paired_results) == 20,
        "exact_40_unchanged_physics_rollouts": len(paired_results) * 2 == 40,
        "all_25_tick_windows_present": all(
            row["early_analysis_ticks"] == EARLY_TICKS
            and row["common_valid_transition_prefix_ticks"] >= EARLY_TICKS
            for row in paired_results
        ),
        "all_metrics_finite": all(
            all(
                math.isfinite(float(value))
                for key, value in row.items()
                if key.endswith("_mse")
            )
            and all(math.isfinite(value) for value in row["hidden_linf_by_tick"])
            and all(math.isfinite(value) for value in row["actual_action_linf_by_tick"])
            and all(
                math.isfinite(value)
                for value in row["same_input_hidden_fork_action_linf_by_tick"]
            )
            for row in paired_results
        ),
        "all_positive_sign_controls_pass_support": all(
            row["positive_support_pass"] for row in paired_results
        ),
        "at_least_16_negative_sign_cells_reproduce_support_failure": sum(
            row["negative_support_pass"] is False for row in paired_results
        )
        >= MIN_DECISION_CELLS,
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        decision = "DO_NOT_ADVANCE_WINNER_V23_DIAGNOSTIC"
    result = {
        "schema_version": "winner_v23.negative_x_response_use_diagnostic_result.v1",
        "status": (
            "PASS_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
            if not failed_checks
            else "HOLD_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
        ),
        "decision": decision,
        "classification": classification,
        "checks": checks,
        "failed_checks": failed_checks,
        "population": {
            "configuration_pairs": [list(pair) for pair in PAIR_IDS],
            "checkpoint_labels": ["half", "final"],
            "actuator_plants": list(smoke.PLANTS),
            "paired_cells": len(paired_results),
            "physics_rollouts": len(paired_results) * 2,
            "early_analysis_ticks": EARLY_TICKS,
        },
        "thresholds": {
            "minimum_persistent_ticks": MIN_PERSISTENT_TICKS,
            "hidden_linf": HIDDEN_LINF_THRESHOLD,
            "same_input_hidden_fork_action_linf": FORK_ACTION_LINF_THRESHOLD,
            "minimum_cells_for_branch": MIN_DECISION_CELLS,
        },
        "aggregate": {
            "response_encoded_early_cells": encoded,
            "response_used_by_action_early_cells": used,
            "predictor_beats_constant_both_signs_early_cells": predicted,
            "negative_support_failure_cells": sum(
                row["negative_support_pass"] is False for row in paired_results
            ),
            "positive_support_failure_cells": sum(
                row["positive_support_pass"] is False for row in paired_results
            ),
        },
        "paired_results": paired_results,
        "execution": {
            "paired_cells": len(paired_results),
            "physics_rollouts": len(paired_results) * 2,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
            "hold_attribution_lf_sha256": lf_sha256(HOLD_ATTRIBUTION),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "base_gate_runner_lf_sha256": lf_sha256(BASE_GATE_RUNNER),
            "v22_gate_runner_lf_sha256": lf_sha256(V22_GATE_RUNNER),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
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
    for name in failed_checks:
        print(f"FAILED={name}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
