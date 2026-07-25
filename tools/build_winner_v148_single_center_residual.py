#!/usr/bin/env python3
"""Build and contract the V148 single-center right-ankle residual."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from audit_winner_v140_preservation_projected_actor import (  # noqa: E402
    make_dynamic_batch,
)
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
import winner_v134_full_actor_teacher_distillation as v134  # noqa: E402
import winner_v145_on_policy_dagger as dagger  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v148_single_center_residual_preregistration.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V147_RESULT = ANALYSIS / "winner_v147_head_only_dagger_cpu_result.json"
OUTPUT = ANALYSIS / "winner_v148_single_center_residual_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V148_SINGLE_CENTER_RESIDUAL_RESULT_20260725.md"
)
CENTER_TICK = 394
CENTER_JOINT = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rename_tensor(model: onnx.ModelProto, old: str, new: str) -> None:
    for node in model.graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new
        for index, name in enumerate(node.output):
            if name == old:
                node.output[index] = new
    for output in model.graph.output:
        if output.name == old:
            output.name = new


def append_residual(
    source: onnx.ModelProto,
    *,
    center: np.ndarray,
    scale: np.ndarray,
    radius_squared: float,
    correction: np.ndarray,
) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    rename_tensor(model, "continuous_actions", "v148_base_actions")
    rename_tensor(
        model, "previous_action_out", "v148_base_previous_action_out"
    )
    values = {
        "v148_center": center[None, :].astype(np.float32),
        "v148_scale": scale[None, :].astype(np.float32),
        "v148_radius_squared": np.asarray(
            [radius_squared], dtype=np.float32
        ),
        "v148_correction": correction[None, :].astype(np.float32),
    }
    model.graph.initializer.extend(
        numpy_helper.from_array(value, name=name)
        for name, value in values.items()
    )
    model.graph.node.extend(
        [
            helper.make_node(
                "Concat",
                ["obs", "h_in"],
                ["v148_feature"],
                axis=1,
                name="v148_concat_feature",
            ),
            helper.make_node(
                "Sub",
                ["v148_feature", "v148_center"],
                ["v148_feature_delta"],
                name="v148_center_delta",
            ),
            helper.make_node(
                "Mul",
                ["v148_feature_delta", "v148_scale"],
                ["v148_normalized_delta"],
                name="v148_normalize_delta",
            ),
            helper.make_node(
                "Mul",
                ["v148_normalized_delta", "v148_normalized_delta"],
                ["v148_squared_delta"],
                name="v148_square_delta",
            ),
            helper.make_node(
                "ReduceSum",
                ["v148_squared_delta"],
                ["v148_distance_squared"],
                axes=[1],
                keepdims=1,
                name="v148_distance",
            ),
            helper.make_node(
                "LessOrEqual",
                ["v148_distance_squared", "v148_radius_squared"],
                ["v148_inside"],
                name="v148_radius_compare",
            ),
            helper.make_node(
                "Cast",
                ["v148_inside"],
                ["v148_gate"],
                to=onnx.TensorProto.FLOAT,
                name="v148_gate_cast",
            ),
            helper.make_node(
                "Mul",
                ["v148_gate", "v148_correction"],
                ["v148_gated_correction"],
                name="v148_gate_correction",
            ),
            helper.make_node(
                "Add",
                ["v148_base_actions", "v148_gated_correction"],
                ["continuous_actions"],
                name="v148_apply_correction",
            ),
            helper.make_node(
                "Identity",
                ["continuous_actions"],
                ["previous_action_out"],
                name="v148_realized_feedback",
            ),
        ]
    )
    for output in model.graph.output:
        if output.name == "v148_base_actions":
            output.name = "continuous_actions"
        elif output.name == "v148_base_previous_action_out":
            output.name = "previous_action_out"
    onnx.checker.check_model(model)
    return model


def infer(path: Path, data: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    return tuple(
        session.run(
            None,
            {
                "obs": data["obs"].astype(np.float32),
                "previous_action": data["previous_action"].astype(np.float32),
                "h_in": data["h_in"].astype(np.float32),
            },
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--source-deployed", type=Path, required=True)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--shadow-trace", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V148: {path}")
    source_raw = args.source_raw.resolve()
    source_deployed = args.source_deployed.resolve()
    teacher_root = args.teacher_run_root.resolve()
    shadow_trace = args.shadow_trace.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v121_transform": sha256(V121_TRANSFORM),
        "v140_result": sha256(V140_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v147_result": sha256(V147_RESULT),
        "v134_loader": sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "v145_loader": sha256(
            TRAINING / "winner_v145_on_policy_dagger.py"
        ),
        "source_raw": sha256(source_raw),
        "source_deployed": sha256(source_deployed),
        "shadow_trace": sha256(shadow_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V148_SINGLE_CENTER_RESIDUAL"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V148 preregistration changed")
    teacher = v134.load_teacher_dataset(teacher_root)
    shadow = dagger.load_shadow_dataset(shadow_trace)
    data = {
        "obs": np.concatenate([teacher["obs"], shadow["obs"]], axis=0),
        "previous_action": np.concatenate(
            [teacher["previous_action"], shadow["previous_action"]], axis=0
        ),
        "h_in": np.concatenate(
            [teacher["h_in"], shadow["h_in"]], axis=0
        ),
    }
    features = np.concatenate([data["obs"], data["h_in"]], axis=1).astype(
        np.float64
    )
    center_index = 4_800 + CENTER_TICK
    center = features[center_index]
    std = np.std(features, axis=0)
    scale = np.where(std >= 1.0e-6, 1.0 / std, 0.0)
    distances = np.sum(
        np.square((features - center[None, :]) * scale[None, :]),
        axis=1,
    )
    distances[center_index] = np.inf
    nearest_squared = float(np.min(distances))
    radius_squared = nearest_squared * 0.25
    gate = (
        np.sum(
            np.square((features - center[None, :]) * scale[None, :]),
            axis=1,
        )
        <= radius_squared
    )
    records = [
        json.loads(line)
        for line in shadow_trace.read_text(encoding="utf-8").splitlines()
        if line
    ]
    oracle = records[CENTER_TICK]["exact_torque_oracle"]
    correction = np.zeros(14, dtype=np.float32)
    correction[CENTER_JOINT] = np.float32(
        oracle["final_action"][CENTER_JOINT]
        - oracle["base_action"][CENTER_JOINT]
    )
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    work.mkdir(parents=True)
    local_raw = work / "winner_v148_single_center_raw.onnx"
    local_deployed = work / "winner_v148_single_center_deployed.onnx"
    model = append_residual(
        onnx.load(source_raw),
        center=center,
        scale=scale,
        radius_squared=radius_squared,
        correction=correction,
    )
    onnx.save(model, local_raw)
    contract = deploy_graph(local_raw, local_deployed, transform)
    source_dynamic = work / "winner_v148_source_dynamic.onnx"
    local_dynamic = work / "winner_v148_local_dynamic.onnx"
    onnx.save(make_dynamic_batch(onnx.load(source_deployed)), source_dynamic)
    onnx.save(make_dynamic_batch(onnx.load(local_deployed)), local_dynamic)
    source_action, source_previous, source_hidden = infer(
        source_dynamic, data
    )
    local_action, local_previous, local_hidden = infer(local_dynamic, data)
    delta = local_action - source_action
    preservation = np.ones(len(delta), dtype=np.bool_)
    preservation[center_index] = False
    target = float(oracle["final_action"][CENTER_JOINT])
    center_error = abs(
        float(local_action[center_index, CENTER_JOINT]) - target
    )
    changed_elements = np.argwhere(np.abs(delta) > 1.0e-7)
    checks = {
        "dataset_exact_5400": data["obs"].shape == (5_400, 115),
        "center_is_shadow_tick394": (
            center_index == 5_194
            and records[CENTER_TICK]["tick"] == CENTER_TICK
        ),
        "center_is_right_ankle_nonempty_oracle_event": (
            CENTER_JOINT in oracle["projected_joint_indices"]
            and CENTER_JOINT
            not in oracle["empty_intersection_joint_indices"]
            and correction[CENTER_JOINT] != 0.0
        ),
        "radius_derived_from_nearest_other_row": (
            nearest_squared > 0.0
            and radius_squared == nearest_squared * 0.25
        ),
        "numpy_gate_fires_exactly_one_row": (
            int(np.sum(gate)) == 1 and bool(gate[center_index])
        ),
        "onnx_changes_exactly_center_right_ankle": (
            changed_elements.tolist() == [[center_index, CENTER_JOINT]]
        ),
        "center_matches_oracle_target": center_error <= 1.0e-7,
        "all_other_aggregate_actions_bit_exact": (
            float(np.max(np.abs(delta[preservation]))) == 0.0
        ),
        "realized_previous_action_exact": bool(
            np.array_equal(local_action, local_previous)
        ),
        "hidden_output_bit_exact": bool(
            np.array_equal(source_hidden, local_hidden)
        ),
        "source_previous_action_contract_preserved": bool(
            np.array_equal(source_action, source_previous)
        ),
        "deployment_contract_green": contract["inference"]["pass"],
        "no_training_behavior_or_hosted_compute": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v148.single_center_residual_result.v1",
        "status": (
            "PASS_WINNER_V148_SINGLE_CENTER_RESIDUAL"
            if not failed
            else "HOLD_WINNER_V148_SINGLE_CENTER_RESIDUAL"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "center": {
            "aggregate_index": center_index,
            "shadow_tick": CENTER_TICK,
            "joint": CENTER_JOINT,
            "correction": float(correction[CENTER_JOINT]),
            "target": target,
            "center_error": center_error,
            "active_features": int(np.sum(scale != 0.0)),
            "nearest_other_distance_squared": nearest_squared,
            "radius_squared": radius_squared,
        },
        "aggregate": {
            "rows": len(features),
            "gate_rows": np.flatnonzero(gate).tolist(),
            "changed_elements": changed_elements.tolist(),
            "preservation_linf": float(
                np.max(np.abs(delta[preservation]))
            ),
        },
        "artifact": {
            "raw": {"path": str(local_raw), "sha256": sha256(local_raw)},
            "deployed": contract,
            "work_root": str(work),
        },
        "decision": (
            "EARN_ONE_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_SINGLE_CENTER_LOCAL_RESIDUAL"
        ),
        "authority": {
            "v149_behavior_preregistration": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V148 single-center residual\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One center: V144 tick 394, right ankle; radius is half the "
        "nearest other aggregate-state distance.\n"
        f"- Correction: `{correction[CENTER_JOINT]}` action units.\n"
        f"- Aggregate preservation L-inf: "
        f"`{payload['aggregate']['preservation_linf']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU graph contract only; no behavior, training, Colab, or "
        "hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
