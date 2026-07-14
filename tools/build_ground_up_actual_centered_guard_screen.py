#!/usr/bin/env python3
"""Build and contract-check actual-position-centered ONNX target guards."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import tarfile

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import onnxruntime as ort


STEPS = (512000, 1024000)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def graph_io(model: onnx.ModelProto) -> dict:
    return {
        "inputs": [item.name for item in model.graph.input],
        "outputs": [item.name for item in model.graph.output],
    }


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def load_sources(archive_path: Path, arm: str) -> dict[int, tuple[str, bytes, onnx.ModelProto]]:
    found = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        members = sorted(
            (
                item for item in archive.getmembers()
                if item.isfile()
                and item.name.startswith(f"ground_up_tracking_tail_outputs/{arm}/")
                and item.name.endswith(".onnx")
            ),
            key=lambda item: item.name,
        )
        for member in members:
            step = int(Path(member.name).stem.rsplit("_", 1)[1])
            if step not in STEPS:
                continue
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"cannot read {member.name}")
            value = stream.read()
            found[step] = (member.name, value, onnx.load_model_from_string(value))
    if set(found) != set(STEPS):
        raise RuntimeError(f"unexpected source steps for {arm}: {sorted(found)}")
    return found


def rename_tensor(model: onnx.ModelProto, old: str, new: str) -> None:
    for node in model.graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new
        for index, name in enumerate(node.output):
            if name == old:
                node.output[index] = new


def append_guard(
    source: onnx.ModelProto,
    *,
    obs_indices: np.ndarray,
    pitch_indices: np.ndarray,
    home: np.ndarray,
    action_scale: float,
    margin: float,
) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    rename_tensor(model, "previous_action_out", "velocity_bounded_previous_action_out")
    rename_tensor(model, "continuous_actions", "velocity_bounded_actions")
    guard_margin = np.full((1, 14), 1.0e6, dtype=np.float32)
    guard_margin.reshape(-1)[pitch_indices] = margin
    pitch_mask = np.zeros((1, 14), dtype=np.bool_)
    pitch_mask.reshape(-1)[pitch_indices] = True
    values = {
        "guard_joint_obs_indices": obs_indices.astype(np.int64),
        "guard_home": home.reshape(1, 14).astype(np.float32),
        "guard_action_scale": np.asarray([action_scale], dtype=np.float32),
        "guard_margin": guard_margin,
        "guard_pitch_mask": pitch_mask,
        "guard_action_min": np.asarray([-1.0], dtype=np.float32),
        "guard_action_max": np.asarray([1.0], dtype=np.float32),
    }
    model.graph.initializer.extend(
        numpy_helper.from_array(value, name=name) for name, value in values.items()
    )
    model.graph.node.extend(
        [
            helper.make_node(
                "Gather", ["obs", "guard_joint_obs_indices"], ["guard_joint_offsets"],
                axis=1, name="guard_gather_joint_offsets",
            ),
            helper.make_node(
                "Add", ["guard_home", "guard_joint_offsets"], ["guard_actual_target"],
                name="guard_actual_target_add",
            ),
            helper.make_node(
                "Mul", ["velocity_bounded_actions", "guard_action_scale"],
                ["guard_desired_offset"], name="guard_desired_offset_mul",
            ),
            helper.make_node(
                "Add", ["guard_home", "guard_desired_offset"], ["guard_desired_target"],
                name="guard_desired_target_add",
            ),
            helper.make_node(
                "Sub", ["guard_actual_target", "guard_margin"], ["guard_target_min"],
                name="guard_target_min_sub",
            ),
            helper.make_node(
                "Add", ["guard_actual_target", "guard_margin"], ["guard_target_max"],
                name="guard_target_max_add",
            ),
            helper.make_node(
                "Max", ["guard_desired_target", "guard_target_min"],
                ["guard_target_above_min"], name="guard_target_maximum",
            ),
            helper.make_node(
                "Min", ["guard_target_above_min", "guard_target_max"],
                ["guard_clipped_target"], name="guard_target_minimum",
            ),
            helper.make_node(
                "Sub", ["guard_clipped_target", "guard_home"], ["guard_clipped_offset"],
                name="guard_clipped_offset_sub",
            ),
            helper.make_node(
                "Div", ["guard_clipped_offset", "guard_action_scale"],
                ["guard_pitch_actions_unclipped"], name="guard_action_div",
            ),
            helper.make_node(
                "Clip", ["guard_pitch_actions_unclipped", "guard_action_min", "guard_action_max"],
                ["guard_pitch_actions"], name="guard_action_clip",
            ),
            helper.make_node(
                "Where", ["guard_pitch_mask", "guard_pitch_actions", "velocity_bounded_actions"],
                ["continuous_actions"], name="guard_pitch_select",
            ),
            helper.make_node(
                "Identity", ["continuous_actions"], ["previous_action_out"],
                name="guard_realized_state_feedback",
            ),
        ]
    )
    for output in model.graph.output:
        if output.name == "velocity_bounded_actions":
            output.name = "continuous_actions"
        elif output.name == "velocity_bounded_previous_action_out":
            output.name = "previous_action_out"
    onnx.checker.check_model(model)
    return model


def contract_policy(
    source_path: Path,
    guarded_path: Path,
    *,
    home: np.ndarray,
    action_scale: float,
    obs_indices: np.ndarray,
    pitch_indices: np.ndarray,
    margin: float,
    max_delta: np.ndarray,
) -> dict:
    source = ort.InferenceSession(str(source_path), providers=["CPUExecutionProvider"])
    guarded = ort.InferenceSession(str(guarded_path), providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(20260714)
    previous = np.zeros((1, 14), dtype=np.float32)
    actual_offset = np.zeros((1, 14), dtype=np.float32)
    max_nonpitch_error = 0.0
    max_guard_excess = 0.0
    max_rate_excess = 0.0
    max_state_error = 0.0
    all_finite = True
    nonpitch = np.asarray([i for i in range(14) if i not in set(pitch_indices.tolist())])
    for _ in range(256):
        obs = rng.normal(0.0, 0.5, size=(1, 115)).astype(np.float32)
        obs[:, obs_indices] = actual_offset
        source_action, _ = source.run(None, {"obs": obs, "previous_action": previous})
        action, state = guarded.run(None, {"obs": obs, "previous_action": previous})
        actual_target = home.reshape(1, -1) + actual_offset
        sent_target = home.reshape(1, -1) + action * action_scale
        all_finite = all_finite and bool(np.all(np.isfinite(action)) and np.all(np.isfinite(state)))
        max_nonpitch_error = max(
            max_nonpitch_error, float(np.max(np.abs(action[:, nonpitch] - source_action[:, nonpitch])))
        )
        max_guard_excess = max(
            max_guard_excess,
            float(np.max(np.abs(sent_target[:, pitch_indices] - actual_target[:, pitch_indices]) - margin)),
        )
        max_rate_excess = max(
            max_rate_excess, float(np.max(np.abs(action - previous) - max_delta))
        )
        max_state_error = max(max_state_error, float(np.max(np.abs(action - state))))
        desired_actual = action * action_scale
        actual_offset += np.clip(desired_actual - actual_offset, -0.04, 0.04)
        previous = state
    return {
        "all_finite": all_finite,
        "max_nonpitch_action_error": max_nonpitch_error,
        "max_guard_excess_rad": max_guard_excess,
        "max_rate_excess_action_units": max_rate_excess,
        "max_state_output_error": max_state_error,
        "pass": (
            all_finite
            and max_nonpitch_error == 0.0
            and max_guard_excess <= 2e-7
            and max_rate_excess <= 2e-7
            and max_state_error == 0.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    source_spec = prereg["source_policies"]
    contract = prereg["guard_contract"]
    archive = Path(source_spec["archive"])
    archive_ok = sha256(archive) == source_spec["archive_sha256"]
    obs_indices = np.asarray(contract["measured_joint_offset_indices"], dtype=np.int64)
    pitch_indices = np.asarray(contract["pitch_chain_action_indices"], dtype=np.int64)
    home = np.asarray(contract["home_target_rad"], dtype=np.float32)
    action_scale = float(contract["action_scale_rad"])
    args.output_root.mkdir(parents=True, exist_ok=True)
    policies = []
    source_hashes = {}
    for arm in source_spec["tail_arms"]:
        sources = load_sources(archive, arm)
        for step in STEPS:
            member_name, member_bytes, source_model = sources[step]
            source_hashes[f"{arm}_{step}"] = {
                "member": member_name,
                "sha256": sha256_bytes(member_bytes),
            }
            source_path = args.output_root / f".{arm}_{step}_source.onnx"
            source_path.write_bytes(member_bytes)
            source_inits = initializers(source_model)
            max_delta = source_inits["max_action_delta"].reshape(1, 14)
            for guard in prereg["arms"]:
                model = append_guard(
                    source_model,
                    obs_indices=obs_indices,
                    pitch_indices=pitch_indices,
                    home=home,
                    action_scale=action_scale,
                    margin=float(guard["margin_rad"]),
                )
                output_dir = args.output_root / guard["name"]
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{arm}_{step}.onnx"
                onnx.save(model, output_path)
                guarded_inits = initializers(model)
                source_initializers_exact = all(
                    name in guarded_inits and np.array_equal(value, guarded_inits[name])
                    for name, value in source_inits.items()
                )
                source_nodes_prefix_exact = all(
                    left.op_type == right.op_type
                    and list(left.attribute) == list(right.attribute)
                    for left, right in zip(source_model.graph.node, model.graph.node)
                )
                inference = contract_policy(
                    source_path,
                    output_path,
                    home=home,
                    action_scale=action_scale,
                    obs_indices=obs_indices,
                    pitch_indices=pitch_indices,
                    margin=float(guard["margin_rad"]),
                    max_delta=max_delta,
                )
                policies.append(
                    {
                        "guard": guard["name"],
                        "margin_rad": guard["margin_rad"],
                        "arm": arm,
                        "step": step,
                        "path": str(output_path.resolve()),
                        "sha256": sha256(output_path),
                        "graph_io": graph_io(model),
                        "source_initializers_exact": source_initializers_exact,
                        "source_node_types_and_attributes_prefix_exact": source_nodes_prefix_exact,
                        "appended_node_count": len(model.graph.node) - len(source_model.graph.node),
                        "inference_contract": inference,
                    }
                )
            source_path.unlink()
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "archive_hash_matches": archive_ok,
        "exactly_twelve_policies_built": len(policies) == prereg["matrix"]["onnx_policies"],
        "all_graph_interfaces_exact": all(
            item["graph_io"] == {"inputs": ["obs", "previous_action"], "outputs": ["continuous_actions", "previous_action_out"]}
            for item in policies
        ),
        "all_source_initializers_exact": all(item["source_initializers_exact"] for item in policies),
        "all_source_node_prefixes_preserved": all(item["source_node_types_and_attributes_prefix_exact"] for item in policies),
        "all_append_exactly_thirteen_nodes": all(item["appended_node_count"] == 13 for item in policies),
        "all_reachable_inference_contracts_pass": all(item["inference_contract"]["pass"] for item in policies),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_ACTUAL_CENTERED_GUARD_TRANSFORM_CONTRACT" if not failed else "FAIL_ACTUAL_CENTERED_GUARD_TRANSFORM_CONTRACT"
    payload = {
        "schema_version": "ground_up_actual_centered_guard_transform_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": source_hashes,
        "policies": policies,
        "authority": {
            "cpu_behavior_eval": not failed,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Actual-Centered Guard Transform Contract", "", f"status: `{status}`", ""]
    lines.extend(f"- {name}: `{passed}`" for name, passed in checks.items())
    lines.extend(["", "Passing authorizes only the preregistered 72-cell CPU behavior screen.", "No training, Colab, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed": failed, "policies": len(policies)}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
