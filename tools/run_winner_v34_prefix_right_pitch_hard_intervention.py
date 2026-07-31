#!/usr/bin/env python3
"""Run the frozen zero-update Winner-v34 direct prefix intervention diagnostic."""

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
PREREGISTRATION = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_preregistration.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_TRAINING = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V32_PREREGISTRATION = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_07",
    "HELDOUT_09",
    "HELDOUT_15",
)
CHECKPOINTS = (("half", 251), ("final", 301))
ARMS = ("CONTROL", "RIGHT_PITCH_REPLACED")
RIGHT_PITCH_INDICES = (11, 12, 13)
REPLACEMENT_TICKS = 8
TICKS = 250
ACTION_DELTA_EPS = 1.0e-6
CONTROL_SCALAR_FLOAT_ATOL = 1.0e-12


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status")
        != "PREREGISTERED_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_DIRECT_PREFIX_INTERVENTION_ONLY"
    ):
        raise ValueError("Winner-v34 is not preregistered")
    diagnostic = value.get("diagnostic", {})
    if diagnostic != {
        **diagnostic,
        "candidate_checkpoints": [
            {"label": "half", "update": 251},
            {"label": "final", "update": 301},
        ],
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "arms": {"CONTROL": [], "RIGHT_PITCH_REPLACED": list(RIGHT_PITCH_INDICES)},
        "replacement_ticks": list(range(REPLACEMENT_TICKS)),
        "duration_ticks": TICKS,
        "expected_cells": 120,
        "expected_cells_per_arm": 60,
        "action_delta_epsilon": ACTION_DELTA_EPS,
        "control_scalar_float_atol": CONTROL_SCALAR_FLOAT_ATOL,
    }:
        raise ValueError("Winner-v34 diagnostic dimensions changed")
    if value.get("execution_now") != {
        "control_cells": 0,
        "replacement_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v34 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v34 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if item.get("hash_mode") != "lf" or lf_sha256(path) != item.get("sha256"):
            raise ValueError(f"Winner-v34 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v34 source manifest changed")


def configure_reviewed_modules() -> tuple[Any, Any, Any, Any, Any, Any]:
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as reviewed_gate
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v22_normalized_support_gate as normalized_support
    import run_winner_v33_prefix_right_pitch_anchor_support_gate as v33

    v33.reviewed_gate = reviewed_gate
    v33.smoke = smoke
    v33.training = training
    v33.v21 = v21
    v33.v22v2 = v22v2
    v33.normalized_support = normalized_support
    v33._TRAINING = json.loads(V32_TRAINING.read_text(encoding="utf-8"))
    v33._TRAINING_PREREG = json.loads(
        V32_PREREGISTRATION.read_text(encoding="utf-8")
    )
    return smoke, reviewed_gate, training, v22v2, normalized_support, v33


def candidate_paths(
    work_root: Path, training_result: Mapping[str, Any], label: str, update: int
) -> tuple[Path, Path]:
    snapshot = work_root / "snapshots" / f"snapshot_prefix_anchor_update_{update:03d}.npz"
    graph = work_root / "graphs" / f"winner_v32_{label}.onnx"
    snapshot_receipt = next(
        row for row in training_result["snapshot_manifest"] if row["completed_updates"] == update
    )
    graph_receipt = next(
        row["graph"]
        for row in training_result["persistent_checkpoints"]
        if row["label"] == label and row["completed_updates"] == update
    )
    v25.validate_artifact(snapshot, snapshot_receipt, snapshot.name)
    v25.validate_artifact(graph, graph_receipt, graph.name)
    return snapshot, graph


def control_signature(cell: Mapping[str, Any]) -> dict[str, Any]:
    hashes = cell["trace_hashes"]
    return {
        "terminal": cell["terminal"],
        "episode": cell["episode"],
        "support_pass": cell["support_pass"],
        "previous_action_chain_exact": cell["previous_action_chain_exact"],
        "final_h_out": cell["final_h_out"],
        "trace_hashes": {
            name: hashes[name] for name in ("actions", "hidden")
        },
    }


def compare_control_replay(
    observed: Mapping[str, Any], expected: Mapping[str, Any]
) -> tuple[bool, float]:
    """Require exact traces/discrete outcomes and only tolerate redundant floats."""

    left = control_signature(observed)
    right = control_signature(expected)
    maximum_float_delta = 0.0

    def compare(a: Any, b: Any) -> bool:
        nonlocal maximum_float_delta
        if isinstance(a, Mapping) or isinstance(b, Mapping):
            if not isinstance(a, Mapping) or not isinstance(b, Mapping) or set(a) != set(b):
                return False
            return all(compare(a[key], b[key]) for key in a)
        if isinstance(a, list) or isinstance(b, list):
            if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
                return False
            return all(compare(x, y) for x, y in zip(a, b, strict=True))
        if type(a) is float or type(b) is float:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                return False
            delta = abs(float(a) - float(b))
            maximum_float_delta = max(maximum_float_delta, delta)
            return delta <= CONTROL_SCALAR_FLOAT_ATOL
        return type(a) is type(b) and a == b

    return compare(left, right), maximum_float_delta


def run_cell(
    *,
    mujoco: Any,
    jnp: Any,
    smoke: Any,
    reviewed_gate: Any,
    training: Any,
    scene: Path,
    configuration: Mapping[str, Any],
    plant: str,
    calibrator_design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    candidate_session: Any,
    source_session: Any,
    parameters: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
    arm: str,
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
        raise ValueError("Winner-v34 cell does not start with both feet loaded")
    observation = reviewed_gate.ObservationTransport(None, None).observe(episode.observation())
    action_delay = reviewed_gate.DelayedActionQueue(0)
    previous_action = np.zeros((14,), dtype=np.float32)
    candidate_h = np.zeros((64,), dtype=np.float32)
    source_h = np.zeros((64,), dtype=np.float32)
    observations: list[np.ndarray] = []
    actions: list[np.ndarray] = []
    candidate_actions: list[np.ndarray] = []
    predictions: list[np.ndarray] = []
    hidden: list[np.ndarray] = []
    normalized_squared_errors: list[np.ndarray] = []
    baseline_normalized_squared_errors: list[np.ndarray] = []
    maximum_jax_onnx_hidden_error = 0.0
    previous_action_chain_exact = True
    all_realized_actions_bounded = True
    replacement_deltas: list[float] = []
    terminal = None
    indices = np.asarray(RIGHT_PITCH_INDICES, dtype=np.int64)
    for tick in range(TICKS):
        outputs = candidate_session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {
                "obs": observation[None, :],
                "previous_action": previous_action[None, :],
                "h_in": candidate_h[None, :],
            },
        )
        candidate_action = np.asarray(outputs[0][0], dtype=np.float32)
        previous_out = np.asarray(outputs[1][0], dtype=np.float32)
        candidate_h_out = np.asarray(outputs[2][0], dtype=np.float32)
        source_action, source_h_out = v25.infer(
            source_session, observation, previous_action, source_h
        )
        previous_action_chain_exact &= np.array_equal(previous_out, candidate_action)
        jax_h, prediction = training.response_step(
            parameters,
            jnp.asarray(observation),
            jnp.asarray(previous_action),
            jnp.asarray(candidate_h),
            jnp.asarray(candidate_action),
        )
        prediction_np = np.asarray(prediction, dtype=np.float32)
        maximum_jax_onnx_hidden_error = max(
            maximum_jax_onnx_hidden_error,
            float(
                np.max(
                    np.abs(np.asarray(jax_h, dtype=np.float32) - candidate_h_out)
                )
            ),
        )
        realized = candidate_action.copy()
        if arm == "RIGHT_PITCH_REPLACED" and tick < REPLACEMENT_TICKS:
            realized[indices] = source_action[indices]
            replacement_deltas.append(
                float(np.max(np.abs(source_action[indices] - candidate_action[indices])))
            )
        bounded = np.array_equal(
            realized, smoke.bounded_action_numpy(realized, previous_action)
        )
        all_realized_actions_bounded &= bounded
        if not bounded:
            raise ValueError("Winner-v34 composed action violates graph boundary")
        delayed = action_delay.push(realized)
        valid, next_raw, evidence = reviewed_gate.step_episode(episode, realized, delayed)
        observations.append(observation.copy())
        actions.append(realized.copy())
        candidate_actions.append(candidate_action.copy())
        predictions.append(prediction_np.copy())
        hidden.append(candidate_h_out.copy())
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
        if next_raw is None:
            raise AssertionError("valid Winner-v34 transition lacks next observation")
        next_observation = next_raw
        target = next_observation[training.AUXILIARY_INDICES]
        normalized_squared_errors.append(np.square((prediction_np - target) / target_std))
        baseline_normalized_squared_errors.append(
            np.square((target_mean - target) / target_std)
        )
        observation = next_observation
        previous_action = realized
        candidate_h = candidate_h_out
        source_h = source_h_out
    summary = episode.summary()
    learned_mse = (
        float(np.mean(np.asarray(normalized_squared_errors, dtype=np.float64)))
        if normalized_squared_errors
        else math.inf
    )
    baseline_mse = (
        float(np.mean(np.asarray(baseline_normalized_squared_errors, dtype=np.float64)))
        if baseline_normalized_squared_errors
        else math.inf
    )
    arrays = {
        "observations": np.asarray(observations, dtype=np.float32),
        "actions": np.asarray(actions, dtype=np.float32),
        "candidate_actions": np.asarray(candidate_actions, dtype=np.float32),
        "predictions": np.asarray(predictions, dtype=np.float32),
        "hidden": np.asarray(hidden, dtype=np.float32),
    }
    return {
        "configuration_id": configuration["id"],
        "configuration_sha256": reviewed_gate.canonical_sha256(configuration),
        "plant": plant,
        "condition": None,
        "arm": arm,
        "replaced_action_indices": (
            [] if arm == "CONTROL" else list(RIGHT_PITCH_INDICES)
        ),
        "replacement_ticks": 0 if arm == "CONTROL" else REPLACEMENT_TICKS,
        "maximum_replaced_action_delta": (
            0.0 if not replacement_deltas else max(replacement_deltas)
        ),
        "named_action_changed": (
            arm == "CONTROL" or any(delta > ACTION_DELTA_EPS for delta in replacement_deltas)
        ),
        "all_realized_actions_bounded": bool(all_realized_actions_bounded),
        "terminal": terminal,
        "episode": summary,
        "support_pass": reviewed_gate.support_pass(summary) and terminal is None,
        "previous_action_chain_exact": bool(previous_action_chain_exact),
        "maximum_jax_onnx_hidden_error": maximum_jax_onnx_hidden_error,
        "learned_normalized_prediction_mse": learned_mse,
        "constant_normalized_prediction_mse": baseline_mse,
        "final_h_out": candidate_h.astype(float).tolist(),
        "trace_hashes": {
            name: reviewed_gate.array_sha256(value) for name, value in arrays.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--v32-training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--read-only-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.read_only_diagnostic_authorized:
        raise PermissionError(
            "Winner-v34 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v34 result")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnxruntime as ort

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v34 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v32 = json.loads(V32_TRAINING.read_text(encoding="utf-8"))
    v33_result = json.loads(V33_RESULT.read_text(encoding="utf-8"))
    v28_result = json.loads(V28_RESULT.read_text(encoding="utf-8"))
    if (
        v22.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v32.get("status") != "PASS_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_ARTIFACT"
        or v33_result.get("status")
        != "HOLD_WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE"
        or v28_result.get("selected_group") != "RIGHT_PITCH_CHAIN"
    ):
        raise ValueError("Winner-v34 source authority changed")
    smoke, reviewed_gate, training, _, _, v33 = configure_reviewed_modules()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v34 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v34 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )
    if not set(CONFIGURATION_IDS).issubset(configurations):
        raise ValueError("Winner-v34 configuration union changed")

    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    source_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    v25.validate_artifact(source_path, source_graph, source_path.name)
    source_session = v25.graph_session(ort, source_path)
    v33_reference = {
        (checkpoint["label"], cell["configuration_id"], cell["plant"]): cell
        for checkpoint in v33_result["checkpoint_results"]
        for cell in checkpoint["core_model_plant_cells"]
    }

    rows: list[dict[str, Any]] = []
    for label, update in CHECKPOINTS:
        snapshot_path, graph_path = candidate_paths(
            args.v32_training_work_root, v32, label, update
        )
        snapshot = v33.load_snapshot_for_reviewed_gate(snapshot_path)
        parameters = snapshot["parameters"]
        target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
        target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
        candidate_session = v25.graph_session(ort, graph_path)
        for configuration_id in CONFIGURATION_IDS:
            for plant in smoke.PLANTS:
                reference = v33_reference[(label, configuration_id, plant)]
                for arm in ARMS:
                    cell = run_cell(
                        mujoco=mujoco,
                        jnp=jnp,
                        smoke=smoke,
                        reviewed_gate=reviewed_gate,
                        training=training,
                        scene=scene,
                        configuration=configurations[configuration_id],
                        plant=plant,
                        calibrator_design=calibrator_design,
                        observer_type=observer_type,
                        canonical_fit=args.canonical_fit,
                        candidate_session=candidate_session,
                        source_session=source_session,
                        parameters=parameters,
                        target_mean=target_mean,
                        target_std=target_std,
                        arm=arm,
                    )
                    cell["checkpoint"] = label
                    cell["checkpoint_update"] = update
                    cell["original_v33_support_pass"] = bool(reference["support_pass"])
                    cell["original_v33_terminal_tick"] = (
                        None if reference["terminal"] is None else reference["terminal"]["tick"]
                    )
                    if arm == "CONTROL":
                        replay_exact, maximum_scalar_delta = compare_control_replay(
                            cell, reference
                        )
                    else:
                        replay_exact, maximum_scalar_delta = True, 0.0
                    cell["control_replays_v33_exactly"] = replay_exact
                    cell["control_maximum_scalar_abs_difference"] = maximum_scalar_delta
                    rows.append(cell)

    controls = [row for row in rows if row["arm"] == "CONTROL"]
    replacements = [row for row in rows if row["arm"] == "RIGHT_PITCH_REPLACED"]
    originally_failing = [row for row in replacements if not row["original_v33_support_pass"]]
    originally_passing = [row for row in replacements if row["original_v33_support_pass"]]
    validity_checks = {
        "exact_120_cells": len(rows) == 120,
        "exact_60_control_cells": len(controls) == 60,
        "exact_60_replacement_cells": len(replacements) == 60,
        "all_60_control_cells_replay_v33_exactly": all(
            row["control_replays_v33_exactly"] for row in controls
        ),
        "every_replacement_cell_changes_a_named_action": all(
            row["named_action_changed"] for row in replacements
        ),
        "all_realized_actions_obey_graph_boundary": all(
            row["all_realized_actions_bounded"] for row in rows
        ),
        "all_candidate_previous_action_outputs_exact": all(
            row["previous_action_chain_exact"] for row in rows
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            row["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for row in rows
        ),
    }
    efficacy_checks = {
        "all_60_replacement_cells_pass_support": all(
            row["support_pass"] for row in replacements
        ),
        "all_originally_failing_cells_recovered": bool(originally_failing)
        and all(row["support_pass"] for row in originally_failing),
        "all_originally_passing_cells_remain_passing": bool(originally_passing)
        and all(row["support_pass"] for row in originally_passing),
    }
    checks = {**validity_checks, **efficacy_checks}
    valid = all(validity_checks.values())
    passed = valid and all(efficacy_checks.values())
    if not valid:
        status = "INVALID_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        classification = "INVALID_DIRECT_PREFIX_INTERVENTION"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        classification = "DIRECT_PREFIX_RIGHT_PITCH_REPLACEMENT_FULL_SUPPORT_RECOVERY"
        decision = "AUTHORIZE_HARD_PREFIX_MECHANISM_OBJECTIVE_PREREGISTRATION_ONLY"
    else:
        status = "HOLD_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        classification = "NO_FULL_DIRECT_PREFIX_SUPPORT_RECOVERY"
        decision = "CLOSE_RIGHT_PITCH_PREFIX_REPLACEMENT_MECHANISM"
    failed = sorted(name for name, value in checks.items() if not value)
    result = {
        "schema_version": "winner_v34.prefix_right_pitch_hard_intervention_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "configuration_ids": list(CONFIGURATION_IDS),
        "candidate_checkpoints": [
            {"label": label, "update": update} for label, update in CHECKPOINTS
        ],
        "source_checkpoint": {
            "label": "winner_v22_final",
            "update": 100,
            "onnx_sha256": source_graph["sha256"],
        },
        "arms": {"CONTROL": [], "RIGHT_PITCH_REPLACED": list(RIGHT_PITCH_INDICES)},
        "replacement_ticks": list(range(REPLACEMENT_TICKS)),
        "cell_results": rows,
        "summary": {
            "control_passes": sum(row["support_pass"] for row in controls),
            "replacement_passes": sum(row["support_pass"] for row in replacements),
            "originally_failing_cells": len(originally_failing),
            "originally_failing_recovered": sum(
                row["support_pass"] for row in originally_failing
            ),
            "originally_passing_cells": len(originally_passing),
            "originally_passing_preserved": sum(
                row["support_pass"] for row in originally_passing
            ),
            "maximum_replaced_action_delta": max(
                row["maximum_replaced_action_delta"] for row in replacements
            ),
        },
        "execution": {
            "control_cells": len(controls),
            "replacement_cells": len(replacements),
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v28_result_lf_sha256": lf_sha256(V28_RESULT),
            "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
            "winner_v22_training_result_lf_sha256": lf_sha256(V22_TRAINING),
            "winner_v32_training_result_lf_sha256": lf_sha256(V32_TRAINING),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "runtime_action_wrapper_authorized": False,
            "pass_authorizes_only": "one separately frozen CPU objective contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(status)
    print(
        f"REPLACEMENT_PASSES={result['summary']['replacement_passes']}/"
        f"{len(replacements)}"
    )
    print(
        f"ORIGINAL_FAILURES_RECOVERED={result['summary']['originally_failing_recovered']}/"
        f"{len(originally_failing)}"
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
