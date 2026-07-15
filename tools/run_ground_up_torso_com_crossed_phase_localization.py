#!/usr/bin/env python3
"""Contract and run the preregistered torso-COM crossed phase study."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
BASE_TOOL = REPO / "tools/run_ground_up_torso_com_signed_response.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_CROSSED_PHASE_LOCALIZATION_PREREGISTRATION_20260715.md"
SIGNED_CONTRACT = REPO / "outputs/analysis/ground_up_torso_com_signed_response_contract.json"
SIGNED_RESULT = REPO / "outputs/analysis/ground_up_torso_com_signed_response_result.json"

EXPECTED = {
    "base_tool": "6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d",
    "prereg": "721d57fa4ec7081a22b3224ef4f4e1e099778cc233f25253214ffcf4c76dd6a2",
    "signed_contract": "ed12ddcd9a8fd618c3bd3db6fa0dc403bae5078400c94b6a22fe43869f3ce5fb",
    "signed_result": "8c09ada8ce392c09fcee3cd9e7f449be5b1c50ca28b1640a4a3103755cc3b814",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("signed_response_base", BASE_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load signed-response evaluator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_sources(base: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    actual = {
        "base_tool": sha256(BASE_TOOL),
        "prereg": sha256(PREREG),
        "signed_contract": sha256(SIGNED_CONTRACT),
        "signed_result": sha256(SIGNED_RESULT),
    }
    if actual != EXPECTED:
        raise ValueError(f"crossed frozen-source mismatch: {actual}")
    signed_contract = json.loads(SIGNED_CONTRACT.read_text())
    signed_result = json.loads(SIGNED_RESULT.read_text())
    if signed_contract.get("status") != "PASS_TORSO_COM_SIGNED_RESPONSE_CONTRACT":
        raise ValueError("signed source contract did not pass")
    if signed_result.get("status") != "PASS_TORSO_COM_SIGNED_RESPONSE_COMPLETE":
        raise ValueError("signed source result did not complete")
    if signed_result.get("decision") != "MIXED_SIGN_NO_POLICY_FAMILY_SELECTED":
        raise ValueError("signed source decision mismatch")
    _manifest, _full_result, selected = base.load_sources()
    if len(selected) != 36:
        raise ValueError(f"expected 36 source traces, got {len(selected)}")
    return signed_result, selected


def signed_index(signed_result: dict[str, Any]) -> dict[tuple[Any, ...], dict[str, Any]]:
    index = {
        (
            cell["policy"], cell["fit"], round(float(cell["command_x"]), 3),
            int(cell["tick"]),
        ): cell
        for cell in signed_result["cells"]
    }
    if len(index) != 144:
        raise ValueError(f"signed-cell index mismatch: {len(index)}")
    return index


def crossed_actions(
    states: dict[int, dict[str, np.ndarray]], target_tick: int, donor_tick: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    target = states[target_tick]
    donor = states[donor_tick]
    delta_negative = np.asarray(donor["minus"]) - np.asarray(donor["baseline"])
    delta_positive = np.asarray(donor["plus"]) - np.asarray(donor["baseline"])
    if target_tick == donor_tick:
        # Preserve the exact contracted float32 ONNX outputs on the diagonal.
        negative = np.asarray(donor["minus"]).copy()
        positive = np.asarray(donor["plus"]).copy()
    else:
        negative = np.asarray(target["baseline"]) + delta_negative
        positive = np.asarray(target["baseline"]) + delta_positive
    return negative, positive, delta_negative, delta_positive


def classify(alignment: float | None, disturbance_norm: float, actor_norm: float) -> str:
    if alignment is None or disturbance_norm < 1e-6 or actor_norm < 1e-6:
        return "PHYSICALLY_NEGLIGIBLE"
    if alignment <= -0.25:
        return "CORRECTIVE"
    if alignment >= 0.25:
        return "AMPLIFYING"
    return "ORTHOGONAL_OR_MIXED"


def run_cross_cell(
    *, base: Any, mujoco: Any, env: Any, item: dict[str, Any],
    rows: list[dict[str, Any]], states: dict[int, dict[str, np.ndarray]],
    target_tick: int, donor_tick: int, fit_path: Path,
    prior: dict[str, Any],
) -> dict[str, Any]:
    home = np.asarray(env._default_actuator, dtype=float)
    init_q = np.asarray(env._init_q, dtype=float)
    qpos, qvel, ctrl = base.source_state(rows, target_tick, init_q, home)
    bridge, previous_sent, bridge_error = base.reconstruct_bridge(
        rows, fit_path, home, target_tick
    )
    if bridge_error > 1e-6:
        raise ValueError(f"bridge reconstruction error {bridge_error}")

    negative, positive, delta_negative, delta_positive = crossed_actions(
        states, target_tick, donor_tick
    )
    raw_min = float(min(np.min(negative), np.min(positive)))
    raw_max = float(max(np.max(negative), np.max(positive)))
    if raw_min < -1.0 or raw_max > 1.0:
        raise ValueError(f"crossed action outside frozen range: {raw_min}, {raw_max}")

    future = np.asarray(
        [rows[index]["policy_raw_action"] for index in range(target_tick, target_tick + base.HORIZON)],
        dtype=float,
    )
    actions_negative = future.copy()
    actions_positive = future.copy()
    actions_negative[0] = negative
    actions_positive[0] = positive
    common = {
        "mujoco": mujoco, "model": env.mj_model, "qpos": qpos, "qvel": qvel,
        "ctrl": ctrl, "previous_sent": previous_sent, "home": home,
        "action_scale": float(env._config.action_scale),
        "max_motor_velocity": float(env._config.max_motor_velocity),
        "dt": float(env.dt), "n_substeps": int(env.n_substeps),
    }
    actor_negative = base.simulate(
        **common, bridge=base.clone_bridge(bridge), actions=actions_negative
    )
    actor_positive = base.simulate(
        **common, bridge=base.clone_bridge(bridge), actions=actions_positive
    )
    actor = base.difference(actor_negative, actor_positive)
    disturbance_pitch = np.asarray(prior["disturbance_pitch_rad"], dtype=float)
    actor_pitch = np.asarray(actor["pitch"], dtype=float)
    disturbance_norm = float(np.linalg.norm(disturbance_pitch))
    actor_norm = float(np.linalg.norm(actor_pitch))
    alignment = (
        float(np.dot(disturbance_pitch, actor_pitch) / (disturbance_norm * actor_norm))
        if disturbance_norm >= 1e-6 and actor_norm >= 1e-6 else None
    )
    classification = classify(alignment, disturbance_norm, actor_norm)
    return {
        "policy": f"{item['arm']}_{item['step']}", "arm": item["arm"],
        "step": int(item["step"]), "fit": item["fit"],
        "command_x": float(item["command_x"]),
        "target_tick": int(target_tick), "donor_tick": int(donor_tick),
        "diagonal": target_tick == donor_tick,
        "classification": classification, "alignment_cosine": alignment,
        "disturbance_pitch_norm_rad": disturbance_norm,
        "actor_pitch_norm_rad": actor_norm,
        "disturbance_pitch_rad": disturbance_pitch.tolist(),
        "actor_pitch_rad": actor_pitch.tolist(),
        "actor_pitch_rate": np.asarray(actor["pitch_rate"]).tolist(),
        "actor_height_m": np.asarray(actor["height"]).tolist(),
        "actor_local_vx_m_s": np.asarray(actor["local_vx"]).tolist(),
        "actor_sent_target_difference_rad": np.asarray(actor["sent"]).tolist(),
        "actor_applied_target_difference_rad": np.asarray(actor["applied"]).tolist(),
        "target_baseline_action": np.asarray(states[target_tick]["baseline"]).tolist(),
        "donor_delta_negative": delta_negative.tolist(),
        "donor_delta_positive": delta_positive.tolist(),
        "cross_action_negative": negative.tolist(),
        "cross_action_positive": positive.tolist(),
        "cross_raw_min": raw_min, "cross_raw_max": raw_max,
        "bridge_reconstruction_max_error_rad": bridge_error,
    }


def two_way_sums(matrix: np.ndarray) -> tuple[float, float, float]:
    grand = float(np.mean(matrix))
    row_means = np.mean(matrix, axis=1)
    column_means = np.mean(matrix, axis=0)
    target = float(4.0 * np.sum((row_means - grand) ** 2))
    donor = float(4.0 * np.sum((column_means - grand) ** 2))
    residual = matrix - row_means[:, None] - column_means[None, :] + grand
    interaction = float(np.sum(residual ** 2))
    return target, donor, interaction


def effect_classification(fractions: dict[str, float]) -> str:
    target = fractions["target"]
    donor = fractions["donor"]
    interaction = fractions["interaction"]
    if donor >= 0.60 and donor >= 2.0 * target and donor >= 2.0 * interaction:
        return "DONOR_ACTOR_RESPONSE_DOMINANT"
    if target >= 0.60 and target >= 2.0 * donor and target >= 2.0 * interaction:
        return "TARGET_PLANT_STATE_DOMINANT"
    if interaction >= 0.60 and interaction >= 2.0 * target and interaction >= 2.0 * donor:
        return "CROSSED_INTERACTION_DOMINANT"
    return "DISTRIBUTED_OR_UNRESOLVED"


def contract(output: Path) -> int:
    base = load_base()
    signed_result, selected = frozen_sources(base)
    _jax, _mujoco, env = base.initialize_environment()
    import jax
    import onnxruntime as ort

    checks: dict[str, bool] = {}
    checks["cpu_only"] = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    checks["signed_source_complete"] = (
        len(signed_result["cells"]) == 144
        and signed_result["decision"] == "MIXED_SIGN_NO_POLICY_FAMILY_SELECTED"
    )
    sessions: dict[str, Any] = {}
    provider_exact = True
    for key in base.POLICIES:
        session = ort.InferenceSession(
            str(base.policy_path(key)), providers=["CPUExecutionProvider"]
        )
        provider_exact = provider_exact and session.get_providers() == ["CPUExecutionProvider"]
        sessions[key] = session
    checks["all_six_onnx_cpu_provider_exact"] = provider_exact and len(sessions) == 6

    planned: set[tuple[Any, ...]] = set()
    maximum_baseline_error = 0.0
    maximum_bridge_error = 0.0
    maximum_sent_error = 0.0
    maximum_applied_error = 0.0
    minimum_negative_offset_norm = float("inf")
    minimum_positive_offset_norm = float("inf")
    raw_min = float("inf")
    raw_max = float("-inf")
    raw_action_count = 0
    home = np.asarray(env._default_actuator, dtype=float)

    for item in selected:
        rows = base.load_trace(item)
        key = f"{item['arm']}_{item['step']}"
        states = base.reconstruct_policy(sessions[key], rows)
        fit_path = base.P30 if item["fit"] == "p30" else base.P31
        for tick in base.FORK_TICKS:
            maximum_baseline_error = max(
                maximum_baseline_error,
                float(np.max(np.abs(
                    np.asarray(states[tick]["baseline"])
                    - np.asarray(rows[tick]["policy_raw_action"])
                ))),
            )
            bridge, previous_sent, bridge_error = base.reconstruct_bridge(
                rows, fit_path, home, tick
            )
            maximum_bridge_error = max(maximum_bridge_error, bridge_error)
            baseline_target = home + np.asarray(states[tick]["baseline"]) * float(env._config.action_scale)
            sent = np.clip(
                baseline_target,
                previous_sent - float(env._config.max_motor_velocity) * float(env.dt),
                previous_sent + float(env._config.max_motor_velocity) * float(env.dt),
            )
            maximum_sent_error = max(
                maximum_sent_error,
                float(np.max(np.abs(sent - np.asarray(rows[tick]["sent_target_rad"])))),
            )
            applied = base.clone_bridge(bridge).step(sent, float(env.dt))
            maximum_applied_error = max(
                maximum_applied_error,
                float(np.max(np.abs(applied - np.asarray(rows[tick]["applied_target_rad"])))),
            )

        for donor_tick in base.FORK_TICKS:
            donor = states[donor_tick]
            minimum_negative_offset_norm = min(
                minimum_negative_offset_norm,
                float(np.linalg.norm(np.asarray(donor["minus"]) - np.asarray(donor["baseline"]))),
            )
            minimum_positive_offset_norm = min(
                minimum_positive_offset_norm,
                float(np.linalg.norm(np.asarray(donor["plus"]) - np.asarray(donor["baseline"]))),
            )
            for target_tick in base.FORK_TICKS:
                negative, positive, _delta_negative, _delta_positive = crossed_actions(
                    states, target_tick, donor_tick
                )
                raw_min = min(raw_min, float(np.min(negative)), float(np.min(positive)))
                raw_max = max(raw_max, float(np.max(negative)), float(np.max(positive)))
                raw_action_count += 2
                planned.add((
                    key, item["fit"], round(float(item["command_x"]), 3),
                    int(target_tick), int(donor_tick),
                ))

    checks["selected_36_trace_schemas_exact"] = len(selected) == 36
    checks["complete_576_cell_cartesian_index"] = len(planned) == 576
    checks["planned_144_diagonal_432_off_diagonal"] = (
        sum(key[-2] == key[-1] for key in planned) == 144
        and sum(key[-2] != key[-1] for key in planned) == 432
    )
    checks["planned_1152_raw_actions_exact"] = raw_action_count == 1152
    checks["all_crossed_raw_actions_inside_policy_range"] = raw_min >= -1.0 and raw_max <= 1.0
    checks["all_donor_offsets_nonzero"] = (
        minimum_negative_offset_norm > 0.0 and minimum_positive_offset_norm > 0.0
    )
    checks["baseline_recurrent_reconstruction_exact"] = maximum_baseline_error <= 1e-6
    checks["bridge_queue_reconstruction_exact"] = maximum_bridge_error <= 1e-6
    checks["sent_target_reconstruction_exact"] = maximum_sent_error <= 1e-6
    checks["applied_target_reconstruction_exact"] = maximum_applied_error <= 1e-6
    checks["formal_crossed_cells_not_executed"] = True

    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_TORSO_COM_CROSSED_PHASE_CONTRACT"
        if not failed else "FAIL_TORSO_COM_CROSSED_PHASE_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_crossed_phase_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": {
            "tool_sha256": sha256(Path(__file__)),
            "selected_traces": len(selected), "planned_cells": len(planned),
            "planned_diagonal_cells": 144, "planned_off_diagonal_cells": 432,
            "planned_first_branch_raw_actions": raw_action_count,
            "crossed_raw_action_min": raw_min, "crossed_raw_action_max": raw_max,
            "minimum_negative_offset_norm": minimum_negative_offset_norm,
            "minimum_positive_offset_norm": minimum_positive_offset_norm,
            "maximum_baseline_action_error": maximum_baseline_error,
            "maximum_bridge_error_rad": maximum_bridge_error,
            "maximum_sent_target_error_rad": maximum_sent_error,
            "maximum_applied_target_error_rad": maximum_applied_error,
            "devices": [str(device) for device in jax.devices()],
            "source_hashes": EXPECTED,
        },
        "execution": {
            "cpu_only": True, "formal_cells_executed": 0,
            "training": False, "robot_or_rdk": False,
        },
        "authority": {
            "formal_576_cell_study_if_pass": True, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


def category_counts(cells: list[dict[str, Any]]) -> dict[str, int]:
    names = (
        "CORRECTIVE", "AMPLIFYING", "ORTHOGONAL_OR_MIXED", "PHYSICALLY_NEGLIGIBLE"
    )
    return {name: sum(cell["classification"] == name for cell in cells) for name in names}


def policy_effects(cells: list[dict[str, Any]], ticks: tuple[int, ...]) -> dict[str, Any]:
    sums = np.zeros(3, dtype=float)
    groups: list[dict[str, Any]] = []
    group_keys = sorted({(cell["fit"], round(float(cell["command_x"]), 3)) for cell in cells})
    for fit, command in group_keys:
        subset = [
            cell for cell in cells
            if cell["fit"] == fit and round(float(cell["command_x"]), 3) == command
        ]
        index = {(cell["target_tick"], cell["donor_tick"]): cell for cell in subset}
        if len(index) != 16:
            raise ValueError(f"incomplete policy effect group: {fit}, {command}")
        matrix = np.asarray([
            [index[(target, donor)]["alignment_cosine"] for donor in ticks]
            for target in ticks
        ], dtype=float)
        group_sums = np.asarray(two_way_sums(matrix))
        sums += group_sums
        groups.append({
            "fit": fit, "command_x": command, "alignment_matrix": matrix.tolist(),
            "ss_target": float(group_sums[0]), "ss_donor": float(group_sums[1]),
            "ss_interaction": float(group_sums[2]),
        })
    denominator = float(np.sum(sums))
    if denominator <= 0.0:
        raise ValueError("zero deterministic effect sum")
    fractions = {
        "target": float(sums[0] / denominator),
        "donor": float(sums[1] / denominator),
        "interaction": float(sums[2] / denominator),
    }
    grid_counts = {}
    for target in ticks:
        for donor in ticks:
            grid_counts[f"target_{target}_donor_{donor}"] = category_counts([
                cell for cell in cells
                if cell["target_tick"] == target and cell["donor_tick"] == donor
            ])
    return {
        "classification": effect_classification(fractions),
        "fractions": fractions,
        "sums_of_squares": {
            "target": float(sums[0]), "donor": float(sums[1]),
            "interaction": float(sums[2]), "total": denominator,
        },
        "category_counts": category_counts(cells),
        "grid_counts": grid_counts, "groups": groups,
    }


def study(contract_path: Path, output: Path, markdown: Path) -> int:
    contract_payload = json.loads(contract_path.read_text())
    if contract_payload.get("status") != "PASS_TORSO_COM_CROSSED_PHASE_CONTRACT":
        raise ValueError("passing crossed-phase contract required")
    if contract_payload["details"]["tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("crossed-phase tool changed after contract")

    base = load_base()
    signed_result, selected = frozen_sources(base)
    prior_index = signed_index(signed_result)
    _jax, mujoco, env = base.initialize_environment()
    import onnxruntime as ort

    sessions: dict[str, Any] = {}
    for key in base.POLICIES:
        session = ort.InferenceSession(
            str(base.policy_path(key)), providers=["CPUExecutionProvider"]
        )
        if session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError(f"non-CPU ONNX provider for {key}")
        sessions[key] = session

    cells: list[dict[str, Any]] = []
    for trace_index, item in enumerate(selected, start=1):
        rows = base.load_trace(item)
        key = f"{item['arm']}_{item['step']}"
        states = base.reconstruct_policy(sessions[key], rows)
        fit_path = base.P30 if item["fit"] == "p30" else base.P31
        print(
            f"[{trace_index}/36] {key} {item['fit']} x={item['command_x']}",
            flush=True,
        )
        for target_tick in base.FORK_TICKS:
            prior = prior_index[(
                key, item["fit"], round(float(item["command_x"]), 3), target_tick
            )]
            for donor_tick in base.FORK_TICKS:
                cells.append(run_cross_cell(
                    base=base, mujoco=mujoco, env=env, item=item, rows=rows,
                    states=states, target_tick=target_tick, donor_tick=donor_tick,
                    fit_path=fit_path, prior=prior,
                ))
    if len(cells) != 576:
        raise ValueError(f"formal crossed-cell count mismatch: {len(cells)}")

    diagonal_pitch_error = 0.0
    diagonal_alignment_error = 0.0
    diagonal_class_mismatches = 0
    for cell in (row for row in cells if row["diagonal"]):
        prior = prior_index[(
            cell["policy"], cell["fit"], round(float(cell["command_x"]), 3),
            cell["target_tick"],
        )]
        diagonal_pitch_error = max(
            diagonal_pitch_error,
            float(np.max(np.abs(
                np.asarray(cell["actor_pitch_rad"])
                - np.asarray(prior["actor_pitch_rad"])
            ))),
        )
        if cell["alignment_cosine"] is None or prior["alignment_cosine"] is None:
            if cell["alignment_cosine"] != prior["alignment_cosine"]:
                diagonal_alignment_error = float("inf")
        else:
            diagonal_alignment_error = max(
                diagonal_alignment_error,
                abs(float(cell["alignment_cosine"]) - float(prior["alignment_cosine"])),
            )
        diagonal_class_mismatches += cell["classification"] != prior["classification"]

    diagonal_valid = (
        diagonal_pitch_error <= 1e-12
        and diagonal_alignment_error <= 1e-12
        and diagonal_class_mismatches == 0
    )
    negligible_cells = sum(
        cell["classification"] == "PHYSICALLY_NEGLIGIBLE" for cell in cells
    )

    policies: dict[str, Any] = {}
    if diagonal_valid and negligible_cells == 0:
        for key in sorted(base.POLICIES):
            subset = [cell for cell in cells if cell["policy"] == key]
            if len(subset) != 96:
                raise ValueError(f"policy crossed-cell count mismatch: {key}, {len(subset)}")
            policies[key] = policy_effects(subset, base.FORK_TICKS)

    if not diagonal_valid:
        status = "INVALID_TORSO_COM_CROSSED_PHASE_DIAGONAL_REPRODUCTION"
        decision = "INVALID_DIAGONAL_REPRODUCTION"
    elif negligible_cells:
        status = "INVALID_TORSO_COM_CROSSED_PHASE_NEGLIGIBLE_CELL"
        decision = "INVALID_NEGLIGIBLE_CROSS_CELL"
    else:
        status = "PASS_TORSO_COM_CROSSED_PHASE_COMPLETE"
        classifications = [row["classification"] for row in policies.values()]
        if all(value == "DONOR_ACTOR_RESPONSE_DOMINANT" for value in classifications):
            decision = "SUPPORT_PREREGISTERED_ACTOR_ACTION_ATTRIBUTION_STUDY"
        elif all(value == "TARGET_PLANT_STATE_DOMINANT" for value in classifications):
            decision = "SUPPORT_PREREGISTERED_PHASED_PLANT_AUTHORITY_STUDY"
        elif all(value == "CROSSED_INTERACTION_DOMINANT" for value in classifications):
            decision = "SUPPORT_PREREGISTERED_JOINT_PHASE_INTERACTION_STUDY"
        else:
            decision = "CROSSED_LOCALIZATION_UNRESOLVED_NO_FAMILY_SELECTED"

    aggregate_grid = {}
    for target in base.FORK_TICKS:
        for donor in base.FORK_TICKS:
            aggregate_grid[f"target_{target}_donor_{donor}"] = category_counts([
                cell for cell in cells
                if cell["target_tick"] == target and cell["donor_tick"] == donor
            ])
    arms = {}
    for arm in ("U_CURRICULUM", "A05_DIRECT", "U05_DIRECT"):
        siblings = {
            key: row["classification"] for key, row in policies.items()
            if key.startswith(arm + "_")
        }
        arms[arm] = {
            "checkpoints": siblings,
            "both_checkpoints_agree": bool(siblings) and len(set(siblings.values())) == 1,
        }

    payload = {
        "schema_version": "ground_up_torso_com_crossed_phase.v1",
        "status": status, "decision": decision,
        "policies": policies, "arms": arms,
        "aggregate_category_counts": category_counts(cells),
        "aggregate_grid_counts": aggregate_grid,
        "validity": {
            "diagonal_cells": sum(cell["diagonal"] for cell in cells),
            "off_diagonal_cells": sum(not cell["diagonal"] for cell in cells),
            "diagonal_pitch_max_abs_error_rad": diagonal_pitch_error,
            "diagonal_alignment_max_abs_error": diagonal_alignment_error,
            "diagonal_classification_mismatches": diagonal_class_mismatches,
            "negligible_cells": negligible_cells,
        },
        "cells": cells,
        "sources": {
            "contract_sha256": sha256(contract_path),
            "signed_result_sha256": sha256(SIGNED_RESULT),
            "base_tool_sha256": sha256(BASE_TOOL),
        },
        "thresholds": {
            "cell_corrective_max": -0.25, "cell_amplifying_min": 0.25,
            "minimum_pitch_vector_norm_rad": 1e-6,
            "dominant_fraction_minimum": 0.60,
            "dominant_ratio_to_each_other_effect": 2.0,
            "diagonal_reproduction_tolerance": 1e-12,
        },
        "execution": {
            "cpu_only": True, "formal_cells": len(cells), "training": False,
            "robot_or_rdk": False, "p_value": None,
        },
        "authority": {
            "next_preregistration_only": True, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Ground-Up Torso-COM Crossed Phase-Localization Result", "",
        f"status: `{status}`", f"decision: `{decision}`", "",
        "| policy | classification | target fraction | donor fraction | interaction fraction |",
        "|---|---|---:|---:|---:|",
    ]
    for key, row in policies.items():
        fractions = row["fractions"]
        lines.append(
            f"| {key} | `{row['classification']}` | {fractions['target']:.6f} | "
            f"{fractions['donor']:.6f} | {fractions['interaction']:.6f} |"
        )
    lines.extend([
        "", "Validity:", "",
        f"- diagonal pitch maximum error: {diagonal_pitch_error:.17g} rad;",
        f"- diagonal alignment maximum error: {diagonal_alignment_error:.17g};",
        f"- diagonal classification mismatches: {diagonal_class_mismatches};",
        f"- negligible crossed cells: {negligible_cells}.", "",
        "No p-value or training reward is used. The frozen decision authorizes "
        "at most its named next read-only preregistration.", "",
    ])
    markdown.write_text("\n".join(lines))
    print(json.dumps({
        "status": status, "decision": decision,
        "aggregate": payload["aggregate_category_counts"],
    }, sort_keys=True))
    return 0 if status == "PASS_TORSO_COM_CROSSED_PHASE_COMPLETE" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("contract", "study"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "contract":
        return contract(args.output)
    if args.contract is None or args.markdown is None:
        parser.error("study mode requires --contract and --markdown")
    return study(args.contract, args.output, args.markdown)


if __name__ == "__main__":
    raise SystemExit(main())
