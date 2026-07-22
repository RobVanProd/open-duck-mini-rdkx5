#!/usr/bin/env python3
"""Run the frozen Winner-v35 full-horizon source-continuation diagnostic."""

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


PREREGISTRATION = ANALYSIS / "winner_v35_full_horizon_source_continuation_preregistration.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_TRAINING = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
V34_RESULT = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_result.json"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = v34.CONFIGURATION_IDS
CHECKPOINTS = v34.CHECKPOINTS
RIGHT_PITCH_INDICES = v34.RIGHT_PITCH_INDICES
PREFIX_TICKS = 8
TICKS = 250
ACTION_DELTA_EPS = 1.0e-6


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status") != "PREREGISTERED_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_FULL_HORIZON_SOURCE_CONTINUATION_ONLY"
    ):
        raise ValueError("Winner-v35 is not preregistered")
    diagnostic = value.get("diagnostic", {})
    required = {
        "candidate_checkpoints": [
            {"label": "half", "update": 251},
            {"label": "final", "update": 301},
        ],
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "prefix_ticks": list(range(PREFIX_TICKS)),
        "prefix_replaced_action_indices": list(RIGHT_PITCH_INDICES),
        "source_continuation_ticks": {"first": 8, "last": 249},
        "duration_ticks": TICKS,
        "expected_hybrid_cells": 60,
        "action_delta_epsilon": ACTION_DELTA_EPS,
    }
    if any(diagnostic.get(name) != expected for name, expected in required.items()):
        raise ValueError("Winner-v35 diagnostic dimensions changed")
    if value.get("execution_now") != {
        "hybrid_support_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v35 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v35 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v35 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v35 source manifest changed")


def run_hybrid_cell(
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
    candidate_session: Any,
    source_session: Any,
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
        raise ValueError("Winner-v35 cell does not start with both feet loaded")
    transport = reviewed_gate.ObservationTransport(None, None)
    action_delay = reviewed_gate.DelayedActionQueue(0)
    observation = transport.observe(episode.observation())
    previous_action = np.zeros((14,), dtype=np.float32)
    candidate_h = np.zeros((64,), dtype=np.float32)
    source_h = np.zeros((64,), dtype=np.float32)
    indices = np.asarray(RIGHT_PITCH_INDICES, dtype=np.int64)
    observations: list[np.ndarray] = []
    actions: list[np.ndarray] = []
    source_hidden: list[np.ndarray] = []
    prefix_deltas: list[float] = []
    handoff_delta = 0.0
    all_actions_bounded = True
    terminal = None
    for tick in range(TICKS):
        source_action, source_h_out = v25.infer(
            source_session, observation, previous_action, source_h
        )
        if tick <= PREFIX_TICKS:
            candidate_action, candidate_h_out = v25.infer(
                candidate_session, observation, previous_action, candidate_h
            )
        else:
            candidate_action = None
            candidate_h_out = candidate_h
        if tick < PREFIX_TICKS:
            if candidate_action is None:
                raise AssertionError("Winner-v35 prefix candidate is absent")
            realized = candidate_action.copy()
            realized[indices] = source_action[indices]
            prefix_deltas.append(
                float(np.max(np.abs(source_action[indices] - candidate_action[indices])))
            )
        else:
            realized = source_action.copy()
            if tick == PREFIX_TICKS:
                if candidate_action is None:
                    raise AssertionError("Winner-v35 handoff candidate is absent")
                handoff_delta = float(np.max(np.abs(source_action - candidate_action)))
        bounded = np.array_equal(
            realized, smoke.bounded_action_numpy(realized, previous_action)
        )
        all_actions_bounded &= bounded
        if not bounded:
            raise ValueError("Winner-v35 composed action violates graph boundary")
        delayed = action_delay.push(realized)
        valid, next_raw, evidence = reviewed_gate.step_episode(episode, realized, delayed)
        observations.append(observation.copy())
        actions.append(realized.copy())
        source_hidden.append(source_h_out.copy())
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
        if next_raw is None:
            raise AssertionError("valid Winner-v35 transition lacks next observation")
        observation = transport.observe(next_raw)
        previous_action = realized
        source_h = source_h_out
        if tick < PREFIX_TICKS:
            candidate_h = candidate_h_out
    summary = episode.summary()
    arrays = {
        "observations": np.asarray(observations, dtype=np.float32),
        "actions": np.asarray(actions, dtype=np.float32),
        "source_hidden": np.asarray(source_hidden, dtype=np.float32),
    }
    return {
        "configuration_id": configuration["id"],
        "configuration_sha256": reviewed_gate.canonical_sha256(configuration),
        "plant": plant,
        "prefix_replaced_action_indices": list(RIGHT_PITCH_INDICES),
        "prefix_ticks": PREFIX_TICKS,
        "source_continuation_first_tick": PREFIX_TICKS,
        "maximum_prefix_replaced_action_delta": max(prefix_deltas),
        "tick8_handoff_action_delta": handoff_delta,
        "tick8_handoff_changes_action": handoff_delta > ACTION_DELTA_EPS,
        "all_actions_bounded": bool(all_actions_bounded),
        "terminal": terminal,
        "episode": summary,
        "support_pass": reviewed_gate.support_pass(summary) and terminal is None,
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
            "Winner-v35 requires --offline-cpu-only --read-only-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v35 result")

    import jax
    import mujoco
    import onnxruntime as ort

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v35 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v32 = json.loads(V32_TRAINING.read_text(encoding="utf-8"))
    v34_result = json.loads(V34_RESULT.read_text(encoding="utf-8"))
    v28_result = json.loads(V28_RESULT.read_text(encoding="utf-8"))
    if (
        v22.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v32.get("status") != "PASS_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_ARTIFACT"
        or v34_result.get("decision") != "CLOSE_RIGHT_PITCH_PREFIX_REPLACEMENT_MECHANISM"
        or v28_result.get("selected_group") != "RIGHT_PITCH_CHAIN"
    ):
        raise ValueError("Winner-v35 source authority changed")
    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v35 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v35 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )
    if not set(CONFIGURATION_IDS).issubset(configurations):
        raise ValueError("Winner-v35 configuration union changed")

    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    source_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    v25.validate_artifact(source_path, source_graph, source_path.name)
    source_session = v25.graph_session(ort, source_path)
    v34_reference = {
        (row["checkpoint"], row["configuration_id"], row["plant"]): row
        for row in v34_result["cell_results"]
        if row["arm"] == "RIGHT_PITCH_REPLACED"
    }

    rows: list[dict[str, Any]] = []
    for label, update in CHECKPOINTS:
        _, graph_path = v34.candidate_paths(
            args.v32_training_work_root, v32, label, update
        )
        candidate_session = v25.graph_session(ort, graph_path)
        for configuration_id in CONFIGURATION_IDS:
            for plant in smoke.PLANTS:
                cell = run_hybrid_cell(
                    mujoco=mujoco,
                    smoke=smoke,
                    reviewed_gate=reviewed_gate,
                    scene=scene,
                    configuration=configurations[configuration_id],
                    plant=plant,
                    calibrator_design=calibrator_design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    candidate_session=candidate_session,
                    source_session=source_session,
                )
                reference = v34_reference[(label, configuration_id, plant)]
                cell["checkpoint"] = label
                cell["checkpoint_update"] = update
                cell["v34_support_pass"] = bool(reference["support_pass"])
                cell["v34_terminal_tick"] = (
                    None if reference["terminal"] is None else reference["terminal"]["tick"]
                )
                rows.append(cell)

    previously_failing = [row for row in rows if not row["v34_support_pass"]]
    previously_passing = [row for row in rows if row["v34_support_pass"]]
    validity_checks = {
        "exact_60_hybrid_cells": len(rows) == 60,
        "every_tick8_handoff_changes_an_action": all(
            row["tick8_handoff_changes_action"] for row in rows
        ),
        "all_actions_obey_graph_boundary": all(row["all_actions_bounded"] for row in rows),
    }
    efficacy_checks = {
        "all_60_hybrid_cells_pass_support": all(row["support_pass"] for row in rows),
        "all_55_v34_failures_recovered": len(previously_failing) == 55
        and all(row["support_pass"] for row in previously_failing),
        "all_5_v34_passes_preserved": len(previously_passing) == 5
        and all(row["support_pass"] for row in previously_passing),
    }
    checks = {**validity_checks, **efficacy_checks}
    valid = all(validity_checks.values())
    passed = valid and all(efficacy_checks.values())
    if not valid:
        status = "INVALID_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        classification = "INVALID_SOURCE_CONTINUATION_FEASIBILITY"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        classification = "FULL_HORIZON_HYBRID_TEACHER_FEASIBLE"
        decision = "AUTHORIZE_HYBRID_TEACHER_REPRESENTATION_CPU_CONTRACT_PREREGISTRATION_ONLY"
    else:
        status = "HOLD_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        classification = "HYBRID_TEACHER_NOT_FULL_HORIZON_FEASIBLE"
        decision = "CLOSE_V28_HYBRID_TEACHER_ROUTE"
    result = {
        "schema_version": "winner_v35.full_horizon_source_continuation_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "configuration_ids": list(CONFIGURATION_IDS),
        "candidate_checkpoints": [
            {"label": label, "update": update} for label, update in CHECKPOINTS
        ],
        "source_checkpoint": {
            "label": "winner_v22_final",
            "update": 100,
            "onnx_sha256": source_graph["sha256"],
        },
        "cell_results": rows,
        "summary": {
            "hybrid_support_passes": sum(row["support_pass"] for row in rows),
            "v34_failing_cells": len(previously_failing),
            "v34_failures_recovered": sum(row["support_pass"] for row in previously_failing),
            "v34_passing_cells": len(previously_passing),
            "v34_passes_preserved": sum(row["support_pass"] for row in previously_passing),
            "minimum_tick8_handoff_action_delta": min(
                row["tick8_handoff_action_delta"] for row in rows
            ),
            "maximum_tick8_handoff_action_delta": max(
                row["tick8_handoff_action_delta"] for row in rows
            ),
        },
        "execution": {
            "hybrid_support_cells": len(rows),
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v28_result_lf_sha256": lf_sha256(V28_RESULT),
            "winner_v34_result_lf_sha256": lf_sha256(V34_RESULT),
            "winner_v22_training_result_lf_sha256": lf_sha256(V22_TRAINING),
            "winner_v32_training_result_lf_sha256": lf_sha256(V32_TRAINING),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "runtime_hybrid_or_action_wrapper_authorized": False,
            "pass_authorizes_only": "one separately frozen CPU teacher-representation contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(status)
    print(f"HYBRID_SUPPORT_PASSES={result['summary']['hybrid_support_passes']}/60")
    print(
        f"V34_FAILURES_RECOVERED={result['summary']['v34_failures_recovered']}/"
        f"{len(previously_failing)}"
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
