#!/usr/bin/env python3
"""Build and contract the frozen reset-estimator evaluation policy graphs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort

from build_ground_up_actual_centered_guard_screen import append_guard
from build_ground_up_command_deadband_repair import wrap as wrap_deadband


STEPS = (1_003_520, 2_007_040)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initializer_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: np.asarray(numpy_helper.to_array(item))
            for item in model.graph.initializer}


def graph_prefix_exact(source: onnx.ModelProto, transformed: onnx.ModelProto) -> bool:
    return all(left.op_type == right.op_type and list(left.attribute) == list(right.attribute)
               for left, right in zip(source.graph.node, transformed.graph.node))


def contract(source_path: Path, guarded_path: Path, final_path: Path, *,
             obs_indices: np.ndarray, pitch_indices: np.ndarray, home: np.ndarray,
             action_scale: float, margin: float, deadband_index: int,
             max_delta: np.ndarray) -> dict:
    source = ort.InferenceSession(str(source_path), providers=["CPUExecutionProvider"])
    guarded = ort.InferenceSession(str(guarded_path), providers=["CPUExecutionProvider"])
    final = ort.InferenceSession(str(final_path), providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(20260715)
    previous = np.zeros((1, 14), dtype=np.float32)
    actual_offset = np.zeros((1, 14), dtype=np.float32)
    maxima = {"nonpitch": 0.0, "guard": 0.0, "rate": 0.0, "state": 0.0,
              "deadband_zero_action": 0.0, "deadband_zero_state": 0.0,
              "deadband_positive_action": 0.0, "deadband_positive_state": 0.0}
    finite = True
    nonpitch = np.asarray([index for index in range(14)
                           if index not in set(pitch_indices.tolist())])
    for command_x in (0.0, 0.074, 0.077, 0.080):
        for _ in range(64):
            obs = rng.normal(0.0, 0.5, size=(1, 116)).astype(np.float32)
            obs[:, obs_indices] = actual_offset
            obs[:, deadband_index] = command_x
            source_action, _ = source.run(None, {"obs": obs, "previous_action": previous})
            guard_action, guard_state = guarded.run(None, {"obs": obs, "previous_action": previous})
            action, state = final.run(None, {"obs": obs, "previous_action": previous})
            finite = finite and all(np.isfinite(value).all()
                                    for value in (source_action, guard_action, guard_state, action, state))
            actual_target = home.reshape(1, -1) + actual_offset
            sent_target = home.reshape(1, -1) + guard_action * action_scale
            maxima["nonpitch"] = max(maxima["nonpitch"], float(np.max(
                np.abs(guard_action[:, nonpitch] - source_action[:, nonpitch]))))
            maxima["guard"] = max(maxima["guard"], float(np.max(
                np.abs(sent_target[:, pitch_indices] - actual_target[:, pitch_indices]) - margin)))
            maxima["rate"] = max(maxima["rate"], float(np.max(
                np.abs(guard_action - previous) - max_delta)))
            maxima["state"] = max(maxima["state"], float(np.max(np.abs(guard_action - guard_state))))
            if command_x == 0.0:
                maxima["deadband_zero_action"] = max(maxima["deadband_zero_action"],
                                                       float(np.max(np.abs(action))))
                maxima["deadband_zero_state"] = max(maxima["deadband_zero_state"],
                                                      float(np.max(np.abs(state))))
            else:
                maxima["deadband_positive_action"] = max(maxima["deadband_positive_action"],
                    float(np.max(np.abs(action - guard_action))))
                maxima["deadband_positive_state"] = max(maxima["deadband_positive_state"],
                    float(np.max(np.abs(state - guard_state))))
            actual_offset += np.clip(guard_action * action_scale - actual_offset, -0.04, 0.04)
            previous = guard_state
    passed = (finite and maxima["nonpitch"] == 0.0 and maxima["guard"] <= 2e-7
              and maxima["rate"] <= 2e-7 and maxima["state"] == 0.0
              and maxima["deadband_zero_action"] == 0.0
              and maxima["deadband_zero_state"] == 0.0
              and maxima["deadband_positive_action"] == 0.0
              and maxima["deadband_positive_state"] == 0.0
              and source.get_providers() == guarded.get_providers() == final.get_providers()
              == ["CPUExecutionProvider"])
    return {"pass": passed, "all_finite": finite, "maxima": maxima,
            "providers": final.get_providers()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--guard-spec", type=Path, required=True)
    parser.add_argument("--deadband-spec", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    guard = json.loads(args.guard_spec.read_text())["guard_contract"]
    deadband = json.loads(args.deadband_spec.read_text())["transform"]
    obs_indices = np.asarray(guard["measured_joint_offset_indices"], dtype=np.int64)
    pitch_indices = np.asarray(guard["pitch_chain_action_indices"], dtype=np.int64)
    home = np.asarray(guard["home_target_rad"], dtype=np.float32)
    action_scale = float(guard["action_scale_rad"]); margin = 0.20
    deadband_index = int(deadband["command_x_observation_index"])
    deadband_value = float(deadband["zero_deadband_absolute_command_x"])
    expected_onnx = {int(Path(row["name"]).stem.rsplit("_", 1)[1]): row
                     for row in manifest["arm"]["onnx"]}
    args.output_root.mkdir(parents=True, exist_ok=True)
    source_bytes = {}
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.startswith(
                "ground_up_reset_estimator_outputs/RESET_EST_LATCH_U05/") or not member.name.endswith(".onnx"):
                continue
            step = int(Path(member.name).stem.rsplit("_", 1)[1])
            if step in STEPS:
                stream = archive.extractfile(member)
                if stream is None:
                    raise RuntimeError(member.name)
                source_bytes[step] = (member.name, stream.read())
    rows = []
    with tempfile.TemporaryDirectory(prefix="reset_estimator_transform_") as temporary:
        scratch = Path(temporary)
        for step in STEPS:
            member, value = source_bytes[step]
            source_path = scratch / f"source_{step}.onnx"; source_path.write_bytes(value)
            source_model = onnx.load_model_from_string(value)
            source_inits = initializer_map(source_model)
            max_delta = source_inits["max_action_delta"].reshape(1, 14)
            guarded_model = append_guard(source_model, obs_indices=obs_indices,
                                         pitch_indices=pitch_indices, home=home,
                                         action_scale=action_scale, margin=margin)
            guarded_path = scratch / f"guarded_{step}.onnx"; onnx.save(guarded_model, guarded_path)
            final_model = wrap_deadband(guarded_model, deadband_index, deadband_value)
            final_path = args.output_root / f"RESET_EST_LATCH_U05_{step}.onnx"
            onnx.save(final_model, final_path)
            final_inits = initializer_map(final_model)
            source_initializers_exact = all(name in final_inits and np.array_equal(data, final_inits[name])
                                            for name, data in source_inits.items())
            source_prefix = graph_prefix_exact(source_model, final_model)
            inference = contract(source_path, guarded_path, final_path,
                                 obs_indices=obs_indices, pitch_indices=pitch_indices,
                                 home=home, action_scale=action_scale, margin=margin,
                                 deadband_index=deadband_index, max_delta=max_delta)
            rows.append({
                "step": step, "archive_member": member,
                "source_sha256": hashlib.sha256(value).hexdigest(),
                "expected_source_sha256": expected_onnx[step]["sha256"],
                "output_path": str(final_path.resolve()), "output_sha256": sha256(final_path),
                "source_input_shape": [dim.dim_value for dim in source_model.graph.input[0].type.tensor_type.shape.dim],
                "source_initializers_preserved": source_initializers_exact,
                "source_node_prefix_exact": source_prefix,
                "source_initializer_obs_shapes": {name: list(source_inits[name].shape)
                    for name in ("obs_mean", "obs_std")},
                "left_ankle_normalized_delta": float(source_inits["max_action_delta"][0, 4]),
                "appended_nodes": len(final_model.graph.node) - len(source_model.graph.node),
                "inference_contract": inference,
            })
    checks = {
        "artifact_manifest_pass_and_behavior_unevaluated": manifest.get("status")
        == "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY" and manifest.get("behavior_status") == "UNEVALUATED",
        "exact_two_postupdate_sources": len(rows) == 2 and [row["step"] for row in rows] == list(STEPS),
        "source_hashes_exact": all(row["source_sha256"] == row["expected_source_sha256"] for row in rows),
        "source_116d_and_normalizers_exact": all(row["source_input_shape"] == [1, 116]
            and row["source_initializer_obs_shapes"] == {"obs_mean": [116], "obs_std": [116]} for row in rows),
        "source_initializers_and_node_prefix_preserved": all(row["source_initializers_preserved"]
                                                              and row["source_node_prefix_exact"] for row in rows),
        "guard_and_deadband_append_exact": all(row["appended_nodes"] == 18 for row in rows),
        "conservative_left_ankle_already_present": all(row["left_ankle_normalized_delta"]
                                                        == float(np.float32(0.12)) for row in rows),
        "all_cpu_inference_contracts_pass": all(row["inference_contract"]["pass"] for row in rows),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "ground_up_reset_com_estimator_eval_policy_transform.v1",
        "status": "PASS_RESET_ESTIMATOR_EVAL_POLICY_TRANSFORM_CONTRACT" if not failed else "FAIL_RESET_ESTIMATOR_EVAL_POLICY_TRANSFORM_CONTRACT",
        "checks": checks, "failed_checks": failed, "policies": rows,
        "execution": {"cpu_only": True, "behavior_cells": 0, "training_steps": 0,
                      "colab": False, "local_gpu_or_igpu": False, "robot_or_rdk": False},
        "authority": {"complete_frozen_cpu_behavior_matrix_if_pass": True,
                      "training": False, "colab": False, "robot_or_rdk": False},
    }
    args.output_json.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
