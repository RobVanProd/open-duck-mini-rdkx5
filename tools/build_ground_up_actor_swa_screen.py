#!/usr/bin/env python3
"""Build and contract-check the preregistered actor-only SWA ONNX screen."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


PITCH_INDICES = np.asarray([2, 3, 4, 11, 12, 13])


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def initializer_map(model: onnx.ModelProto) -> dict[str, onnx.TensorProto]:
    return {item.name: item for item in model.graph.initializer}


def arrays(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        name: np.asarray(numpy_helper.to_array(item))
        for name, item in initializer_map(model).items()
    }


def replace_array(model: onnx.ModelProto, name: str, value: np.ndarray) -> None:
    items = initializer_map(model)
    old = items[name]
    replacement = numpy_helper.from_array(value.astype(numpy_helper.to_array(old).dtype), name)
    for index, item in enumerate(model.graph.initializer):
        if item.name == name:
            model.graph.initializer[index].CopyFrom(replacement)
            return
    raise KeyError(name)


def graph_signature(model: onnx.ModelProto) -> dict:
    return {
        "inputs": [(item.name, str(item.type)) for item in model.graph.input],
        "outputs": [(item.name, str(item.type)) for item in model.graph.output],
        "nodes": [
            (node.op_type, tuple(node.input), tuple(node.output))
            for node in model.graph.node
        ],
        "initializers": [
            (item.name, tuple(item.dims), item.data_type)
            for item in model.graph.initializer
        ],
    }


def load_sources(archive_path: Path, arm: str) -> dict[int, tuple[str, bytes, onnx.ModelProto]]:
    result = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        members = sorted(
            (
                member
                for member in archive.getmembers()
                if member.isfile()
                and member.name.startswith(f"ground_up_tracking_tail_outputs/{arm}/")
                and member.name.endswith(".onnx")
            ),
            key=lambda member: member.name,
        )
        for member in members:
            name = Path(member.name).name
            step = int(Path(name).stem.rsplit("_", 1)[1])
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"cannot read {member.name}")
            value = stream.read()
            result[step] = (member.name, value, onnx.load_model_from_string(value))
    if set(result) != {0, 512000, 1024000}:
        raise RuntimeError(f"unexpected source steps for {arm}: {sorted(result)}")
    return result


def inference_contract(path: Path, max_delta: np.ndarray) -> dict:
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    names = [item.name for item in session.get_inputs()]
    outputs = [item.name for item in session.get_outputs()]
    if names != ["obs", "previous_action"]:
        raise RuntimeError(f"unexpected inputs for {path}: {names}")
    if outputs != ["continuous_actions", "previous_action_out"]:
        raise RuntimeError(f"unexpected outputs for {path}: {outputs}")
    rng = np.random.default_rng(20260714)
    previous = np.zeros((1, 14), dtype=np.float32)
    max_state_output_error = 0.0
    max_delta_excess = 0.0
    all_finite = True
    for _ in range(16):
        obs = rng.normal(0.0, 1.0, size=(1, 115)).astype(np.float32)
        action, state = session.run(None, {"obs": obs, "previous_action": previous})
        all_finite = all_finite and bool(np.all(np.isfinite(action)) and np.all(np.isfinite(state)))
        max_state_output_error = max(
            max_state_output_error, float(np.max(np.abs(action - state)))
        )
        max_delta_excess = max(
            max_delta_excess,
            float(np.max(np.abs(action - previous) - max_delta.reshape(1, -1))),
        )
        previous = state
    return {
        "provider": session.get_providers()[0],
        "inputs": names,
        "outputs": outputs,
        "all_finite": all_finite,
        "max_state_output_error": max_state_output_error,
        "max_delta_excess": max_delta_excess,
        "pass": all_finite and max_state_output_error == 0.0 and max_delta_excess <= 2e-7,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    archive_path = Path(prereg["inputs"]["archive"]["path"])
    actor_names = prereg["transform"]["actor_initializers"]
    rates = {item["name"]: item["pitch_multiplier"] for item in prereg["rate_variants"]}
    archive_hash_pass = sha256(archive_path) == prereg["inputs"]["archive"]["sha256"]
    args.output_root.mkdir(parents=True, exist_ok=True)

    source_contract = {}
    policies = []
    for arm, expected_hashes in prereg["inputs"]["arms"].items():
        sources = load_sources(archive_path, arm)
        source_hashes = {
            "step0_member_sha256": sha256_bytes(sources[0][1]),
            "half_member_sha256": sha256_bytes(sources[512000][1]),
            "final_member_sha256": sha256_bytes(sources[1024000][1]),
        }
        models = [sources[step][2] for step in (0, 512000, 1024000)]
        signatures = [graph_signature(model) for model in models]
        names_exact = all(set(arrays(model)) == set(arrays(models[0])) for model in models)
        source_contract[arm] = {
            "member_names": {str(step): sources[step][0] for step in sources},
            "hashes": source_hashes,
            "hashes_match": source_hashes == expected_hashes,
            "graphs_identical": signatures[0] == signatures[1] == signatures[2],
            "initializer_names_exact": names_exact,
        }
        source_arrays = [arrays(model) for model in models]
        checkpoint_specs = (
            ("HALF_CUMULATIVE", 512000, (0, 1)),
            ("FINAL_CUMULATIVE", 1024000, (0, 1, 2)),
        )
        for checkpoint_name, current_step, average_indices in checkpoint_specs:
            current_index = 1 if current_step == 512000 else 2
            for rate_name, multiplier in rates.items():
                model = copy.deepcopy(models[current_index])
                expected_actor = {}
                for name in actor_names:
                    value = np.mean(
                        np.stack([source_arrays[index][name] for index in average_indices]),
                        axis=0,
                        dtype=np.float64,
                    ).astype(source_arrays[current_index][name].dtype)
                    expected_actor[name] = value
                    replace_array(model, name, value)
                expected_delta = source_arrays[current_index]["max_action_delta"].copy()
                expected_delta.reshape(-1)[PITCH_INDICES] *= multiplier
                replace_array(model, "max_action_delta", expected_delta)
                onnx.checker.check_model(model)
                output_dir = args.output_root / rate_name
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{arm}_{checkpoint_name}.onnx"
                onnx.save(model, output_path)
                built = arrays(onnx.load(str(output_path)))
                current = source_arrays[current_index]
                actor_error = max(
                    float(np.max(np.abs(built[name] - expected_actor[name])))
                    for name in actor_names
                )
                nonactor_names = set(current) - set(actor_names) - {"max_action_delta"}
                nonactor_exact = all(np.array_equal(built[name], current[name]) for name in nonactor_names)
                delta_error = float(np.max(np.abs(built["max_action_delta"] - expected_delta)))
                inference = inference_contract(output_path, expected_delta)
                policies.append(
                    {
                        "arm": arm,
                        "checkpoint": checkpoint_name,
                        "rate": rate_name,
                        "pitch_multiplier": multiplier,
                        "path": str(output_path.resolve()),
                        "sha256": sha256(output_path),
                        "actor_arithmetic_max_error": actor_error,
                        "nonactor_current_checkpoint_exact": nonactor_exact,
                        "max_action_delta_error": delta_error,
                        "graph_identical_to_current": graph_signature(model)
                        == graph_signature(models[current_index]),
                        "inference_contract": inference,
                    }
                )

    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "archive_hash_matches": archive_hash_pass,
        "all_source_member_hashes_match": all(item["hashes_match"] for item in source_contract.values()),
        "all_source_graphs_identical_within_arm": all(item["graphs_identical"] for item in source_contract.values()),
        "all_source_initializer_names_exact": all(item["initializer_names_exact"] for item in source_contract.values()),
        "exactly_eight_policies_built": len(policies) == prereg["matrix"]["onnx_policies"],
        "all_actor_arithmetic_exact": all(item["actor_arithmetic_max_error"] == 0.0 for item in policies),
        "all_nonactor_initializers_exact": all(item["nonactor_current_checkpoint_exact"] for item in policies),
        "all_rate_deltas_exact": all(item["max_action_delta_error"] == 0.0 for item in policies),
        "all_graphs_identical": all(item["graph_identical_to_current"] for item in policies),
        "all_stateful_inference_contracts_pass": all(item["inference_contract"]["pass"] for item in policies),
        "all_cpu_provider": all(item["inference_contract"]["provider"] == "CPUExecutionProvider" for item in policies),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_ACTOR_SWA_TRANSFORM_CONTRACT" if not failed else "FAIL_ACTOR_SWA_TRANSFORM_CONTRACT"
    payload = {
        "schema_version": "ground_up_actor_swa_transform_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "source_contract": source_contract,
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
    lines = [
        "# Ground-Up Actor-SWA Transform Contract",
        "",
        f"status: `{status}`",
        "",
    ]
    lines.extend(f"- {name}: `{passed}`" for name, passed in checks.items())
    lines.extend(
        [
            "",
            "Passing authorizes only the preregistered 48-cell CPU behavior screen.",
            "No training, Colab, local GPU, RDK-X5, or robot access is authorized.",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed": failed, "policies": len(policies)}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
