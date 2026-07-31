#!/usr/bin/env python3
"""Derive and embed the frozen +COM sagittal mechanics compensation."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import mujoco
import numpy as np
import onnx
import onnxruntime as ort
from onnx import helper, numpy_helper
from scipy.optimize import root

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi,
    canonical_sha256,
    receipt,
    verify,
)
from run_t156_three_way_positive_router_transform import initializer_map


PREREG = (
    ANALYSIS
    / "t159_mechanics_sagittal_compensation_preregistration.json"
)
RESULT = ANALYSIS / "t159_mechanics_sagittal_compensation_result.json"
MARKDOWN = (
    ANALYSIS / "T159_MECHANICS_SAGITTAL_COMPENSATION_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t159_mechanics_sagittal_compensation_v1"
)
STEPS = ("1003520", "2007040")
ACTION_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def site_pitch(matrix: np.ndarray) -> float:
    value = matrix.reshape(3, 3)
    return float(
        np.arctan2(
            -value[2, 0],
            np.sqrt(value[0, 0] ** 2 + value[1, 0] ** 2),
        )
    )


def mechanics_metrics(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    feet: list[str],
) -> np.ndarray:
    mujoco.mj_forward(model, data)
    sites = [data.site(name) for name in feet]
    return np.asarray(
        [
            np.mean([site.xpos[0] for site in sites]),
            np.mean([site.xpos[2] for site in sites]),
            np.mean([site_pitch(site.xmat) for site in sites]),
            data.subtree_com[0, 0],
        ],
        dtype=np.float64,
    )


def derive_mechanics(prereg: dict[str, Any]) -> dict[str, Any]:
    contract = prereg["mechanics"]
    scene = Path(contract["scene"]["path"])
    nominal_model = mujoco.MjModel.from_xml_path(str(scene))
    shifted_model = mujoco.MjModel.from_xml_path(str(scene))
    key_id = nominal_model.key(contract["home_keyframe"]).id
    if key_id < 0:
        raise RuntimeError("T159 home keyframe missing")
    nominal_data = mujoco.MjData(nominal_model)
    shifted_data = mujoco.MjData(shifted_model)
    nominal_home = nominal_model.key_qpos[key_id].copy()
    shifted_home = shifted_model.key_qpos[key_id].copy()
    nominal_data.qpos[:] = nominal_home
    target = mechanics_metrics(
        nominal_model,
        nominal_data,
        contract["feet_sites"],
    )
    torso_id = shifted_model.body(contract["torso_body_name"]).id
    nominal_torso_ipos = shifted_model.body_ipos[torso_id].copy()
    shifted_model.body_ipos[torso_id, 0] += contract[
        "torso_com_x_offset_m"
    ]
    total_mass = float(mujoco.mj_getTotalmass(shifted_model))
    torso_mass = float(shifted_model.body_mass[torso_id])
    expected_total_com_shift = (
        torso_mass
        / total_mass
        * contract["torso_com_x_offset_m"]
    )
    qpos_addresses = {
        name: int(shifted_model.joint(name).qposadr)
        for name in (
            "left_hip_pitch",
            "right_hip_pitch",
            "left_ankle",
            "right_ankle",
        )
    }

    def set_variables(value: np.ndarray) -> None:
        shifted_data.qpos[:] = shifted_home
        shifted_data.qpos[0] = value[0]
        shifted_data.qpos[3:7] = np.asarray(
            [
                np.cos(value[1] * 0.5),
                0.0,
                np.sin(value[1] * 0.5),
                0.0,
            ]
        )
        shifted_data.qpos[qpos_addresses["left_hip_pitch"]] = (
            shifted_home[qpos_addresses["left_hip_pitch"]] + value[2]
        )
        shifted_data.qpos[qpos_addresses["right_hip_pitch"]] = (
            shifted_home[qpos_addresses["right_hip_pitch"]] - value[2]
        )
        for name in ("left_ankle", "right_ankle"):
            shifted_data.qpos[qpos_addresses[name]] = (
                shifted_home[qpos_addresses[name]] + value[3]
            )

    def residual(value: np.ndarray) -> np.ndarray:
        set_variables(value)
        return (
            mechanics_metrics(
                shifted_model,
                shifted_data,
                contract["feet_sites"],
            )
            - target
        )

    zero = np.zeros(4, dtype=np.float64)
    initial_residual = residual(zero)
    epsilon = float(contract["central_difference_epsilon"])
    identity = np.eye(4, dtype=np.float64)
    jacobian = np.column_stack(
        [
            (
                residual(zero + identity[index] * epsilon)
                - residual(zero - identity[index] * epsilon)
            )
            / (2.0 * epsilon)
            for index in range(4)
        ]
    )
    linear_initialization = np.linalg.solve(
        jacobian,
        -initial_residual,
    )
    solution = root(
        residual,
        linear_initialization,
        method="hybr",
        options={"xtol": float(contract["root_xtol"])},
    )
    final_residual = residual(solution.x)
    bias = np.zeros(14, dtype=np.float32)
    bias[ACTION_NAMES.index("left_hip_pitch")] = np.float32(
        solution.x[2] / contract["action_scale_rad"]
    )
    bias[ACTION_NAMES.index("right_hip_pitch")] = np.float32(
        -solution.x[2] / contract["action_scale_rad"]
    )
    for name in ("left_ankle", "right_ankle"):
        bias[ACTION_NAMES.index(name)] = np.float32(
            solution.x[3] / contract["action_scale_rad"]
        )
    joint_limit_checks = {}
    for name, sign, delta in (
        ("left_hip_pitch", 1.0, solution.x[2]),
        ("right_hip_pitch", -1.0, solution.x[2]),
        ("left_ankle", 1.0, solution.x[3]),
        ("right_ankle", 1.0, solution.x[3]),
    ):
        joint = shifted_model.joint(name)
        value = (
            shifted_home[int(joint.qposadr)] + sign * delta
        )
        limits = shifted_model.jnt_range[joint.id]
        joint_limit_checks[name] = {
            "value_rad": float(value),
            "lower_rad": float(limits[0]),
            "upper_rad": float(limits[1]),
            "inside": bool(limits[0] <= value <= limits[1]),
        }
    return {
        "mujoco_version": mujoco.__version__,
        "torso_id": int(torso_id),
        "torso_mass_kg": torso_mass,
        "total_mass_kg": total_mass,
        "nominal_torso_ipos_m": nominal_torso_ipos.astype(float).tolist(),
        "expected_total_com_shift_m": expected_total_com_shift,
        "observed_initial_com_shift_m": float(initial_residual[3]),
        "target_metrics": target.astype(float).tolist(),
        "initial_residual": initial_residual.astype(float).tolist(),
        "jacobian": jacobian.astype(float).tolist(),
        "jacobian_condition_number": float(np.linalg.cond(jacobian)),
        "linear_initialization": linear_initialization.astype(float).tolist(),
        "solver_success": bool(solution.success),
        "solver_message": str(solution.message),
        "variables": {
            "floating_base_x_m": float(solution.x[0]),
            "floating_base_pitch_rad": float(solution.x[1]),
            "mirrored_hip_pitch_delta_rad": float(solution.x[2]),
            "shared_ankle_pitch_delta_rad": float(solution.x[3]),
        },
        "final_residual": final_residual.astype(float).tolist(),
        "maximum_abs_final_residual": float(
            np.max(np.abs(final_residual))
        ),
        "action_bias": bias.astype(float).tolist(),
        "maximum_abs_action_bias": float(np.max(np.abs(bias))),
        "joint_limit_checks": joint_limit_checks,
    }


def transform(
    source: Path,
    destination: Path,
    action_bias: np.ndarray,
) -> dict[str, Any]:
    before = onnx.load(source)
    model = copy.deepcopy(before)
    candidates = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Tanh"
        and list(node.input) == ["anchored_location"]
        and list(node.output) == ["raw_continuous_actions"]
    ]
    if len(candidates) != 1:
        raise RuntimeError("T159 raw-action tanh changed")
    tanh_index, tanh_node = candidates[0]
    tanh_node.output[0] = "t159_uncompensated_raw_actions"
    additions = {
        "t159_mechanics_action_bias": action_bias.reshape(1, 14),
        "t159_zero_action_bias": np.zeros((1, 14), dtype=np.float32),
        "t159_action_lower": np.asarray([-1.0], dtype=np.float32),
        "t159_action_upper": np.asarray([1.0], dtype=np.float32),
    }
    for name, value in additions.items():
        model.graph.initializer.append(
            numpy_helper.from_array(
                np.asarray(value, dtype=np.float32),
                name,
            )
        )
    inserted = [
        helper.make_node(
            "Where",
            [
                "t156_positive_condition",
                "t159_mechanics_action_bias",
                "t159_zero_action_bias",
            ],
            ["t159_selected_action_bias"],
            name="t159_select_mechanics_bias",
        ),
        helper.make_node(
            "Add",
            [
                "t159_uncompensated_raw_actions",
                "t159_selected_action_bias",
            ],
            ["t159_biased_raw_actions"],
            name="t159_add_mechanics_bias",
        ),
        helper.make_node(
            "Clip",
            [
                "t159_biased_raw_actions",
                "t159_action_lower",
                "t159_action_upper",
            ],
            ["raw_continuous_actions"],
            name="t159_clip_mechanics_action",
        ),
    ]
    for offset, node in enumerate(inserted, start=1):
        model.graph.node.insert(tanh_index + offset, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)

    after = onnx.load(destination)
    old_nodes = list(before.graph.node)
    new_nodes = list(after.graph.node)
    expected_tanh = copy.deepcopy(old_nodes[tanh_index])
    expected_tanh.output[0] = "t159_uncompensated_raw_actions"
    old_index = 0
    source_nodes_exact = True
    for new_index, node in enumerate(new_nodes):
        if tanh_index + 1 <= new_index <= tanh_index + 3:
            continue
        expected = (
            expected_tanh
            if old_index == tanh_index
            else old_nodes[old_index]
        )
        source_nodes_exact &= (
            node.SerializeToString() == expected.SerializeToString()
        )
        old_index += 1
    old_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    new_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "three_nodes_inserted": len(new_nodes) == len(old_nodes) + 3,
        "tanh_output_rewire_exact": (
            expected_tanh.output[0] == "t159_uncompensated_raw_actions"
        ),
        "all_source_nodes_otherwise_byte_exact": source_nodes_exact,
        "existing_initializers_byte_exact": all(
            new_initializers.get(name) == value
            for name, value in old_initializers.items()
        ),
        "four_initializers_added": (
            set(new_initializers) - set(old_initializers) == set(additions)
        ),
        "action_bias_exact": np.array_equal(
            numpy_helper.to_array(
                initializer_map(after)["t159_mechanics_action_bias"]
            ),
            action_bias.reshape(1, 14).astype(np.float32),
        ),
        "abi_exact": abi(before) == abi(after),
    }


def always_on_reference(
    transformed: Path,
    destination: Path,
) -> dict[str, Any]:
    model = onnx.load(transformed)
    candidates = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.name == "t159_select_mechanics_bias"
        and node.op_type == "Where"
    ]
    if len(candidates) != 1:
        raise RuntimeError("T159 bias selector changed")
    index, old = candidates[0]
    replacement = helper.make_node(
        "Identity",
        ["t159_mechanics_action_bias"],
        ["t159_selected_action_bias"],
        name="t159_mechanics_always_on_reference",
    )
    del model.graph.node[index]
    model.graph.node.insert(index, replacement)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    return {
        "transformed": receipt(transformed),
        "reference": receipt(destination),
        "replacement_index": index,
        "source_inputs": list(old.input),
        "identity_exact": (
            list(replacement.input) == ["t159_mechanics_action_bias"]
            and list(replacement.output)
            == ["t159_selected_action_bias"]
        ),
    }


def equivalence_contract(
    source: Path,
    transformed: Path,
    positive_reference: Path,
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    transformed_session = ort.InferenceSession(
        str(transformed), providers=["CPUExecutionProvider"]
    )
    positive_session = ort.InferenceSession(
        str(positive_reference), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260729)
    rows = []
    for context_row in contexts:
        positive = context_row["population"] == "com_x_positive"
        selected = positive_session if positive else source_session
        exact = True
        finite = True
        x0_zero = True
        samples = 0
        for command_x in (0.0, 0.074, 0.077, 0.08):
            for _ in range(16):
                feed = {
                    "obs": rng.normal(size=(1, 115)).astype(np.float32),
                    "previous_action": rng.uniform(
                        -0.98, 0.98, size=(1, 14)
                    ).astype(np.float32),
                    "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                    "calibration_context": np.asarray(
                        context_row["context"], dtype=np.float32
                    ).reshape(1, 64),
                }
                feed["obs"][:, 6] = np.float32(command_x)
                expected = selected.run(None, feed)
                actual = transformed_session.run(None, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(expected, actual, strict=True)
                )
                finite &= all(
                    bool(np.all(np.isfinite(value))) for value in actual
                )
                if command_x == 0.0:
                    x0_zero &= bool(
                        np.array_equal(
                            actual[0],
                            np.zeros((1, 14), dtype=np.float32),
                        )
                        and np.array_equal(
                            actual[1],
                            np.zeros((1, 14), dtype=np.float32),
                        )
                    )
                samples += 1
        rows.append(
            {
                "fit_id": context_row["fit_id"],
                "population": context_row["population"],
                "samples": samples,
                "all_selected_source_outputs_bit_exact": exact,
                "all_outputs_finite": finite,
                "x0_action_and_feedback_exact_zero": x0_zero,
            }
        )
    return {
        "rows": rows,
        "all_selected_source_outputs_bit_exact": all(
            row["all_selected_source_outputs_bit_exact"] for row in rows
        ),
        "all_outputs_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "all_x0_action_and_feedback_exact_zero": all(
            row["x0_action_and_feedback_exact_zero"] for row in rows
        ),
        "samples": sum(row["samples"] for row in rows),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in (
                source_session,
                transformed_session,
                positive_session,
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T159 requires --execute")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T159: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T159 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T159_MECHANICS_SAGITTAL_COMPENSATION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T159 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for step, item in prereg["source_graphs"].items():
        verify(item, f"source_graph:{step}")
    for index, item in enumerate(
        prereg["mechanics"]["xml_dependency_receipts"]
    ):
        verify(item, f"xml_dependency:{index}")

    started = time.time()
    mechanics = derive_mechanics(prereg)
    action_bias = np.asarray(
        mechanics["action_bias"], dtype=np.float32
    )
    t135b = json.loads(
        Path(prereg["frozen_inputs"]["t135b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t156 = json.loads(
        Path(prereg["frozen_inputs"]["t156_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    contexts = [*t135b["runs"], *t156["positive_contexts"]]
    WORK.mkdir(parents=True)
    graphs = {}
    references = {}
    contracts = {}
    for step in STEPS:
        source = Path(prereg["source_graphs"][step]["path"])
        transformed = WORK / step / "mechanics_compensated_router.onnx"
        reference = WORK / step / "mechanics_always_on_reference.onnx"
        graphs[step] = transform(source, transformed, action_bias)
        references[step] = always_on_reference(transformed, reference)
        contracts[step] = equivalence_contract(
            source,
            transformed,
            reference,
            contexts,
        )
    contract = prereg["mechanics"]
    checks = {
        "mechanics_root_converged": mechanics["solver_success"],
        "mechanics_residual_within_bound": (
            mechanics["maximum_abs_final_residual"]
            <= contract["maximum_constraint_residual"]
        ),
        "total_com_shift_matches_mass_law": (
            abs(
                mechanics["observed_initial_com_shift_m"]
                - mechanics["expected_total_com_shift_m"]
            )
            <= 1e-12
        ),
        "all_joint_limits_green": all(
            row["inside"]
            for row in mechanics["joint_limit_checks"].values()
        ),
        "action_bias_within_unit_box": (
            mechanics["maximum_abs_action_bias"]
            <= contract["maximum_absolute_action_bias"]
        ),
        "all_graph_transforms_exact": all(
            row["three_nodes_inserted"]
            and row["tanh_output_rewire_exact"]
            and row["all_source_nodes_otherwise_byte_exact"]
            and row["existing_initializers_byte_exact"]
            and row["four_initializers_added"]
            and row["action_bias_exact"]
            and row["abi_exact"]
            for row in graphs.values()
        ),
        "all_positive_references_exact": all(
            row["identity_exact"] for row in references.values()
        ),
        "all_selected_source_outputs_bit_exact": all(
            row["all_selected_source_outputs_bit_exact"]
            for row in contracts.values()
        ),
        "all_x0_zero_finite_cpu": all(
            row["all_outputs_finite"]
            and row["all_x0_action_and_feedback_exact_zero"]
            and row["cpu_only"]
            for row in contracts.values()
        ),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t159_mechanics_sagittal_compensation_result.v1"
        ),
        "status": (
            "PASS_T159_MECHANICS_SAGITTAL_COMPENSATION"
            if passed
            else "HOLD_T159_MECHANICS_SAGITTAL_COMPENSATION"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "mechanics": mechanics,
        "graphs": graphs,
        "always_on_references": references,
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "mechanics_solves": 1,
            "graphs_transformed": len(graphs),
            "cpu_equivalence_samples": sum(
                row["samples"] for row in contracts.values()
            ),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "positive_endpoint_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T159 mechanics sagittal compensation\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- COM shift: `{mechanics['observed_initial_com_shift_m']:.9f} m`\n"
        f"- Hip action bias: "
        f"`{mechanics['action_bias'][2]:.9f}` / "
        f"`{mechanics['action_bias'][11]:.9f}`\n"
        f"- Ankle action bias: "
        f"`{mechanics['action_bias'][4]:.9f}` / "
        f"`{mechanics['action_bias'][13]:.9f}`\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
