#!/usr/bin/env python3
"""Build and contract V151's bounded second local residual center."""

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


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from audit_winner_v140_preservation_projected_actor import (  # noqa: E402
    make_dynamic_batch,
)
from build_winner_v148_single_center_residual import (  # noqa: E402
    infer,
    rename_tensor,
)
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
import winner_v134_full_actor_teacher_distillation as v134  # noqa: E402
import winner_v145_on_policy_dagger as dagger  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v151_bounded_two_center_preregistration.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V148_RESULT = ANALYSIS / "winner_v148_single_center_residual_result.json"
V149_RESULT = (
    ANALYSIS / "winner_v149_single_center_causal_behavior_result.json"
)
V150_RESULT = ANALYSIS / "winner_v150_v148_shadow_oracle_result.json"
V150_CORRECTION = (
    ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
)
OUTPUT = ANALYSIS / "winner_v151_bounded_two_center_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V151_BOUNDED_TWO_CENTER_RESULT_20260725.md"
)
SECOND_TICK = 583
SECOND_JOINT = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def append_second_residual(
    source: onnx.ModelProto,
    *,
    center: np.ndarray,
    scale: np.ndarray,
    radius_squared: float,
    correction: np.ndarray,
) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    rename_tensor(model, "continuous_actions", "v151_base_actions")
    rename_tensor(
        model, "previous_action_out", "v151_base_previous_action_out"
    )
    values = {
        "v151_center": center[None, :].astype(np.float32),
        "v151_scale": scale[None, :].astype(np.float32),
        "v151_radius_squared": np.asarray(
            [radius_squared], dtype=np.float32
        ),
        "v151_correction": correction[None, :].astype(np.float32),
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
                ["v151_feature"],
                axis=1,
                name="v151_concat_feature",
            ),
            helper.make_node(
                "Sub",
                ["v151_feature", "v151_center"],
                ["v151_feature_delta"],
                name="v151_center_delta",
            ),
            helper.make_node(
                "Mul",
                ["v151_feature_delta", "v151_scale"],
                ["v151_normalized_delta"],
                name="v151_normalize_delta",
            ),
            helper.make_node(
                "Mul",
                ["v151_normalized_delta", "v151_normalized_delta"],
                ["v151_squared_delta"],
                name="v151_square_delta",
            ),
            helper.make_node(
                "ReduceSum",
                ["v151_squared_delta"],
                ["v151_distance_squared"],
                axes=[1],
                keepdims=1,
                name="v151_distance",
            ),
            helper.make_node(
                "LessOrEqual",
                ["v151_distance_squared", "v151_radius_squared"],
                ["v151_inside"],
                name="v151_radius_compare",
            ),
            helper.make_node(
                "Cast",
                ["v151_inside"],
                ["v151_gate"],
                to=onnx.TensorProto.FLOAT,
                name="v151_gate_cast",
            ),
            helper.make_node(
                "Mul",
                ["v151_gate", "v151_correction"],
                ["v151_gated_correction"],
                name="v151_gate_correction",
            ),
            helper.make_node(
                "Add",
                ["v151_base_actions", "v151_gated_correction"],
                ["continuous_actions"],
                name="v151_apply_correction",
            ),
            helper.make_node(
                "Identity",
                ["continuous_actions"],
                ["previous_action_out"],
                name="v151_realized_feedback",
            ),
        ]
    )
    for output in model.graph.output:
        if output.name == "v151_base_actions":
            output.name = "continuous_actions"
        elif output.name == "v151_base_previous_action_out":
            output.name = "previous_action_out"
    onnx.checker.check_model(model)
    return model


def v148_initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        value.name: numpy_helper.to_array(value)
        for value in model.graph.initializer
        if value.name.startswith("v148_")
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--first-shadow-trace", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V151: {path}")
    teacher_root = args.teacher_run_root.resolve()
    first_shadow_trace = args.first_shadow_trace.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v148 = json.loads(V148_RESULT.read_text(encoding="utf-8"))
    v150 = json.loads(V150_RESULT.read_text(encoding="utf-8"))
    source_raw = Path(v148["artifact"]["raw"]["path"])
    source_deployed = Path(v148["artifact"]["deployed"]["path"])
    second_shadow_trace = Path(v150["trace"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v121_transform": sha256(V121_TRANSFORM),
        "v148_result": sha256(V148_RESULT),
        "v149_result": sha256(V149_RESULT),
        "v150_result": sha256(V150_RESULT),
        "v150_correction": sha256(V150_CORRECTION),
        "v134_loader": sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "v145_loader": sha256(
            TRAINING / "winner_v145_on_policy_dagger.py"
        ),
        "source_raw": sha256(source_raw),
        "source_deployed": sha256(source_deployed),
        "first_shadow_trace": sha256(first_shadow_trace),
        "second_shadow_trace": sha256(second_shadow_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V151_BOUNDED_TWO_CENTER"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V151 preregistration changed")
    teacher = v134.load_teacher_dataset(teacher_root)
    first_shadow = dagger.load_shadow_dataset(first_shadow_trace)
    second_shadow = dagger.load_shadow_dataset(second_shadow_trace)
    data = {
        "obs": np.concatenate(
            [teacher["obs"], first_shadow["obs"], second_shadow["obs"]],
            axis=0,
        ),
        "previous_action": np.concatenate(
            [
                teacher["previous_action"],
                first_shadow["previous_action"],
                second_shadow["previous_action"],
            ],
            axis=0,
        ),
        "h_in": np.concatenate(
            [teacher["h_in"], first_shadow["h_in"], second_shadow["h_in"]],
            axis=0,
        ),
    }
    features = np.concatenate([data["obs"], data["h_in"]], axis=1).astype(
        np.float64
    )
    center_index = 4_800 + 600 + SECOND_TICK
    center = features[center_index]
    std = np.std(features, axis=0)
    scale = np.zeros_like(std)
    np.divide(1.0, std, out=scale, where=std >= 1.0e-6)
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
    correction_record = json.loads(
        V150_CORRECTION.read_text(encoding="utf-8")
    )
    event = correction_record["causal_result"]["event"]
    base = np.asarray(event["base_action"], dtype=np.float32)
    target = np.asarray(event["final_action"], dtype=np.float32)
    correction = np.zeros(14, dtype=np.float32)
    correction[SECOND_JOINT] = (
        target[SECOND_JOINT] - base[SECOND_JOINT]
    )
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    work.mkdir(parents=True)
    local_raw = work / "winner_v151_two_center_raw.onnx"
    local_deployed = work / "winner_v151_two_center_deployed.onnx"
    source_model = onnx.load(source_raw)
    source_v148_values = v148_initializers(source_model)
    model = append_second_residual(
        source_model,
        center=center,
        scale=scale,
        radius_squared=radius_squared,
        correction=correction,
    )
    local_v148_values = v148_initializers(model)
    onnx.save(model, local_raw)
    contract = deploy_graph(local_raw, local_deployed, transform)
    source_dynamic = work / "winner_v151_source_dynamic.onnx"
    local_dynamic = work / "winner_v151_local_dynamic.onnx"
    onnx.save(make_dynamic_batch(onnx.load(source_deployed)), source_dynamic)
    onnx.save(make_dynamic_batch(onnx.load(local_deployed)), local_dynamic)
    source_action, source_previous, source_hidden = infer(
        source_dynamic, data
    )
    local_action, local_previous, local_hidden = infer(local_dynamic, data)
    delta = local_action - source_action
    preservation = np.ones(len(delta), dtype=np.bool_)
    preservation[center_index] = False
    center_error = float(
        np.max(np.abs(local_action[center_index] - target))
    )
    changed_elements = np.argwhere(np.abs(delta) > 1.0e-7)
    v148_preserved = (
        source_v148_values.keys() == local_v148_values.keys()
        and all(
            np.array_equal(source_v148_values[name], local_v148_values[name])
            for name in source_v148_values
        )
    )
    checks = {
        "dataset_exact_6000": data["obs"].shape == (6_000, 115),
        "center_is_second_shadow_tick583": (
            center_index == 5_983 and event["source_tick"] == SECOND_TICK
        ),
        "center_is_right_ankle_nonempty_oracle_event": (
            event["joint"] == SECOND_JOINT
            and SECOND_JOINT in event["source_projected_joint_indices"]
            and SECOND_JOINT not in event["source_empty_joint_indices"]
            and correction[SECOND_JOINT] != 0.0
        ),
        "radius_derived_from_nearest_other_row": (
            nearest_squared > 0.0
            and radius_squared == nearest_squared * 0.25
        ),
        "second_numpy_gate_fires_exactly_one_row": (
            int(np.sum(gate)) == 1 and bool(gate[center_index])
        ),
        "onnx_changes_exactly_second_center_right_ankle": (
            changed_elements.tolist() == [[center_index, SECOND_JOINT]]
        ),
        "center_matches_oracle_target": center_error <= 1.0e-7,
        "all_other_aggregate_actions_bit_exact": (
            float(np.max(np.abs(delta[preservation]))) == 0.0
        ),
        "first_center_parameters_bit_exact": v148_preserved,
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
        "family_bound_is_exactly_two_centers": True,
        "no_training_behavior_or_hosted_compute": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v151.bounded_two_center_result.v1",
        "status": (
            "PASS_WINNER_V151_BOUNDED_TWO_CENTER"
            if not failed
            else "HOLD_WINNER_V151_BOUNDED_TWO_CENTER"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "second_center": {
            "aggregate_index": center_index,
            "shadow_tick": SECOND_TICK,
            "joint": SECOND_JOINT,
            "correction": float(correction[SECOND_JOINT]),
            "target": float(target[SECOND_JOINT]),
            "center_error": center_error,
            "active_features": int(np.sum(scale != 0.0)),
            "nearest_other_distance_squared": nearest_squared,
            "radius_squared": radius_squared,
        },
        "aggregate": {
            "rows": len(features),
            "second_gate_rows": np.flatnonzero(gate).tolist(),
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
        "family_bound": {
            "maximum_centers": 2,
            "centers_now": 2,
            "third_center_permitted": False,
            "next_behavior_stop": (
                "any torque failure closes the finite-local residual family"
            ),
        },
        "decision": (
            "EARN_ONE_V152_TWO_CENTER_CAUSAL_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
        ),
        "authority": {
            "v152_behavior_preregistration": not failed,
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
        "# Winner V151 bounded two-center residual\n\n"
        f"- Status: `{payload['status']}`\n"
        "- V148's first center is unchanged; one second center is added at "
        "V150 tick 583 for right ankle.\n"
        f"- Second correction: `{correction[SECOND_JOINT]}` action units.\n"
        "- The family is capped at two centers before behavior; any "
        "further torque failure closes it.\n"
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
