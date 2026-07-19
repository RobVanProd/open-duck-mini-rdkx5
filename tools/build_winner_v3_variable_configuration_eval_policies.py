#!/usr/bin/env python3
"""Build and contract the frozen winner-v3 evaluation-policy transforms.

The training archive contains the learned recurrent actor plus its conservative
all-joint previous-action projection.  The replacement preregistration also
requires the already-selected G1 actual-centered pitch guard and the exact
zero-command deadband.  This tool appends only those frozen transforms and
proves their graph and inference contracts before any formal behavior cell is
read.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tarfile
import tempfile

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort

from build_ground_up_actual_centered_guard_screen import append_guard
from build_ground_up_command_deadband_repair import wrap as append_deadband


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
TRAINING_CHECK = ROOT / "outputs/analysis/winner_v3_recurrent_adapter_training_artifact_check.json"
ARCHIVE = ROOT / "outputs/analysis/winner_v3_recurrent_adapter_artifacts.tar.gz"
GUARD_PREREG = ROOT / "outputs/analysis/ground_up_actual_centered_guard_screen_preregistration.json"
DEADBAND_PREREG = ROOT / "outputs/analysis/ground_up_command_deadband_repair_preregistration.json"
OUTPUT_ROOT = ROOT / "outputs/analysis/winner_v3_variable_configuration_eval_policies"
OUTPUT_JSON = ROOT / "outputs/analysis/winner_v3_variable_configuration_eval_policy_transform_contract.json"
OUTPUT_MD = ROOT / "outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT_20260719.md"
STEPS = (1_003_520, 2_007_040)
EXPECTED_SOURCE_HASHES = {
    1_003_520: "3d5e6dd447601246f8f5789ce370a1d63648334536359f367f0cb856ab77b04d",
    2_007_040: "fb725c5e8f45866c9b96e56b2429774f2e1ce73261ffb33ff534d977195544f0",
}
EXPECTED_ARCHIVE_SHA256 = "bee604f002df5082bce579734be5a7983f2b31a6026b1caaa34d64b26ce48d91"
CONSERVATIVE_LIMITS_RAD_S = np.asarray(
    [1.0, 0.75, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 1.25, 1.0, 1.25],
    dtype=np.float32,
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor_shape(value) -> list[int]:
    return [int(dim.dim_value) for dim in value.type.tensor_type.shape.dim]


def graph_io(model: onnx.ModelProto) -> dict[str, dict[str, list[int]]]:
    return {
        "inputs": {item.name: tensor_shape(item) for item in model.graph.input},
        "outputs": {item.name: tensor_shape(item) for item in model.graph.output},
    }


def initializer_values(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def archive_sources() -> dict[int, tuple[str, bytes]]:
    found: dict[int, tuple[str, bytes]] = {}
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.endswith(".onnx"):
                continue
            if "stage3_domain_100_percent" not in member.name:
                continue
            for step in STEPS:
                if Path(member.name).stem.endswith(f"_{step}"):
                    stream = archive.extractfile(member)
                    if stream is None:
                        raise RuntimeError(f"cannot read archive member {member.name}")
                    found[step] = (member.name, stream.read())
    if set(found) != set(STEPS):
        raise RuntimeError(f"persistent ONNX members are not exact: {sorted(found)}")
    return found


def normalize_source_node(node: onnx.NodeProto) -> bytes:
    item = copy.deepcopy(node)
    for index, value in enumerate(item.input):
        if value == "continuous_actions":
            item.input[index] = "velocity_bounded_actions"
    for index, value in enumerate(item.output):
        if value == "continuous_actions":
            item.output[index] = "velocity_bounded_actions"
        elif value == "previous_action_out":
            item.output[index] = "velocity_bounded_previous_action_out"
    return item.SerializeToString()


def source_prefix_exact(source: onnx.ModelProto, transformed: onnx.ModelProto) -> bool:
    return [normalize_source_node(node) for node in source.graph.node] == [
        node.SerializeToString() for node in transformed.graph.node[: len(source.graph.node)]
    ]


def inference_contract(
    source_path: Path,
    guarded_path: Path,
    final_path: Path,
    *,
    home: np.ndarray,
    pitch_indices: np.ndarray,
    command_index: int,
    deadband: float,
    margin: float,
) -> dict[str, object]:
    source = ort.InferenceSession(str(source_path), providers=["CPUExecutionProvider"])
    guarded = ort.InferenceSession(str(guarded_path), providers=["CPUExecutionProvider"])
    final = ort.InferenceSession(str(final_path), providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(20260719)
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    actual_offset = np.zeros((1, 14), dtype=np.float32)
    max_positive_action_error = 0.0
    max_positive_previous_error = 0.0
    max_positive_hidden_error = 0.0
    max_zero_action = 0.0
    max_zero_previous = 0.0
    max_zero_hidden_error = 0.0
    max_guard_excess_rad = 0.0
    max_rate_excess_normalized = 0.0
    all_finite = True
    max_delta = CONSERVATIVE_LIMITS_RAD_S * np.float32(0.02 / 0.25)

    for command_x in (0.0, 0.074, 0.077, 0.080):
        previous.fill(0.0)
        hidden.fill(0.0)
        actual_offset.fill(0.0)
        for tick in range(256):
            obs = rng.normal(0.0, 0.25, size=(1, 115)).astype(np.float32)
            obs[:, command_index] = np.float32(command_x)
            obs[:, 13:27] = actual_offset
            obs[:, -14:] = rng.uniform(-0.75, 0.75, size=(1, 14)).astype(np.float32)
            feed = {"obs": obs, "previous_action": previous, "h_in": hidden}
            source_values = source.run(
                ["continuous_actions", "previous_action_out", "h_out"], feed
            )
            guard_values = guarded.run(
                ["continuous_actions", "previous_action_out", "h_out"], feed
            )
            final_values = final.run(
                ["continuous_actions", "previous_action_out", "h_out"], feed
            )
            all_finite = all_finite and all(
                bool(np.all(np.isfinite(value)))
                for value in (*source_values, *guard_values, *final_values)
            )
            action, previous_out, hidden_out = final_values
            if abs(command_x) <= deadband:
                max_zero_action = max(max_zero_action, float(np.max(np.abs(action))))
                max_zero_previous = max(
                    max_zero_previous, float(np.max(np.abs(previous_out)))
                )
                max_zero_hidden_error = max(
                    max_zero_hidden_error,
                    float(np.max(np.abs(hidden_out - guard_values[2]))),
                )
            else:
                max_positive_action_error = max(
                    max_positive_action_error,
                    float(np.max(np.abs(action - guard_values[0]))),
                )
                max_positive_previous_error = max(
                    max_positive_previous_error,
                    float(np.max(np.abs(previous_out - guard_values[1]))),
                )
                max_positive_hidden_error = max(
                    max_positive_hidden_error,
                    float(np.max(np.abs(hidden_out - guard_values[2]))),
                )
                sent_target = home[None, :] + action * np.float32(0.25)
                actual_target = home[None, :] + actual_offset
                max_guard_excess_rad = max(
                    max_guard_excess_rad,
                    float(
                        np.max(
                            np.abs(sent_target[:, pitch_indices] - actual_target[:, pitch_indices])
                            - margin
                        )
                    ),
                )
                max_rate_excess_normalized = max(
                    max_rate_excess_normalized,
                    float(np.max(np.abs(action - previous) - max_delta[None, :])),
                )
                actual_offset += np.clip(
                    action * np.float32(0.25) - actual_offset, -0.04, 0.04
                )
            previous = previous_out.astype(np.float32)
            hidden = hidden_out.astype(np.float32)

    tolerance = 2.0e-7
    passed = bool(
        all_finite
        and max_positive_action_error == 0.0
        and max_positive_previous_error == 0.0
        and max_positive_hidden_error == 0.0
        and max_zero_action == 0.0
        and max_zero_previous == 0.0
        and max_zero_hidden_error == 0.0
        and max_guard_excess_rad <= tolerance
        and max_rate_excess_normalized <= tolerance
        and final.get_providers()[0] == "CPUExecutionProvider"
    )
    return {
        "provider": final.get_providers()[0],
        "all_finite": all_finite,
        "max_positive_action_error": max_positive_action_error,
        "max_positive_previous_action_error": max_positive_previous_error,
        "max_positive_hidden_error": max_positive_hidden_error,
        "max_zero_action": max_zero_action,
        "max_zero_previous_action": max_zero_previous,
        "max_zero_hidden_vs_guard_error": max_zero_hidden_error,
        "max_actual_centered_guard_excess_rad": max_guard_excess_rad,
        "max_conservative_rate_excess_normalized": max_rate_excess_normalized,
        "tolerance": tolerance,
        "pass": passed,
    }


def main() -> int:
    prereg = json.loads(PREREG.read_text())
    training_check = json.loads(TRAINING_CHECK.read_text())
    guard_prereg = json.loads(GUARD_PREREG.read_text())
    deadband_prereg = json.loads(DEADBAND_PREREG.read_text())
    sources = archive_sources()
    guard = guard_prereg["guard_contract"]
    selected_guard = next(
        row for row in guard_prereg["arms"] if row["name"] == "G1_EXACT_BOUNDARY"
    )
    home = np.asarray(guard["home_target_rad"], dtype=np.float32)
    obs_indices = np.asarray(guard["measured_joint_offset_indices"], dtype=np.int64)
    pitch_indices = np.asarray(guard["pitch_chain_action_indices"], dtype=np.int64)
    margin = float(selected_guard["margin_rad"])
    command_index = int(deadband_prereg["transform"]["command_x_observation_index"])
    deadband = float(deadband_prereg["transform"]["zero_deadband_absolute_command_x"])
    expected_delta = CONSERVATIVE_LIMITS_RAD_S * np.float32(
        guard["control_dt_s"] / guard["action_scale_rad"]
    )

    if OUTPUT_ROOT.exists() or OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        if not OUTPUT_JSON.exists():
            raise RuntimeError("uncontracted winner-v3 evaluation-policy output exists")
        prior = json.loads(OUTPUT_JSON.read_text())
        expected_names = {
            f"R64_ZERO_INIT_RECURRENT_ADAPTER_{step}.onnx" for step in STEPS
        }
        observed_names = (
            {path.name for path in OUTPUT_ROOT.iterdir()}
            if OUTPUT_ROOT.exists()
            else set()
        )
        if not (
            prior.get("status")
            == "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT"
            and int(prior.get("formal_behavior_cells_executed", -1)) == 0
            and observed_names <= expected_names
        ):
            raise RuntimeError("winner-v3 evaluation-policy output is not a zero-outcome HOLD")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for step in STEPS:
        member, value = sources[step]
        source_hash = sha256_bytes(value)
        source_model = onnx.load_model_from_string(value)
        source_initializers = initializer_values(source_model)
        guarded_model = append_guard(
            source_model,
            obs_indices=obs_indices,
            pitch_indices=pitch_indices,
            home=home,
            action_scale=float(guard["action_scale_rad"]),
            margin=margin,
        )
        final_model = append_deadband(
            guarded_model, command_index=command_index, deadband=deadband
        )
        output_path = OUTPUT_ROOT / f"R64_ZERO_INIT_RECURRENT_ADAPTER_{step}.onnx"
        onnx.save(final_model, output_path)
        final_initializers = initializer_values(final_model)

        with tempfile.TemporaryDirectory(prefix="winner_v3_transform_") as temp:
            source_path = Path(temp) / "source.onnx"
            guarded_path = Path(temp) / "guarded.onnx"
            source_path.write_bytes(value)
            onnx.save(guarded_model, guarded_path)
            inference = inference_contract(
                source_path,
                guarded_path,
                output_path,
                home=home,
                pitch_indices=pitch_indices,
                command_index=command_index,
                deadband=deadband,
                margin=margin,
            )

        rows.append(
            {
                "step": step,
                "source_archive_member": member,
                "source_sha256": source_hash,
                "output_path": str(output_path.relative_to(ROOT)),
                "output_sha256": sha256(output_path),
                "source_node_count": len(source_model.graph.node),
                "guard_node_count": len(guarded_model.graph.node) - len(source_model.graph.node),
                "deadband_node_count": len(final_model.graph.node) - len(guarded_model.graph.node),
                "source_nodes_prefix_exact_modulo_frozen_output_rename": source_prefix_exact(
                    source_model, final_model
                ),
                "all_source_initializers_exact": all(
                    name in final_initializers and np.array_equal(array, final_initializers[name])
                    for name, array in source_initializers.items()
                ),
                "source_max_action_delta_exact_conservative_vector": bool(
                    "max_action_delta" in source_initializers
                    and np.array_equal(
                        source_initializers["max_action_delta"], expected_delta[None, :]
                    )
                ),
                "graph_io": graph_io(final_model),
                "inference_contract": inference,
            }
        )

    exact_io = {
        "inputs": {"obs": [1, 115], "previous_action": [1, 14], "h_in": [1, 64]},
        "outputs": {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
    }
    checks = {
        "replacement_preregistration_exact": prereg["status"]
        == "PREREGISTERED_CPU_CONTRACT_FIRST",
        "training_artifact_check_passed": training_check["status"]
        == "PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK",
        "archive_hash_exact": sha256(ARCHIVE) == EXPECTED_ARCHIVE_SHA256,
        "two_persistent_sources_exact": all(
            row["source_sha256"] == EXPECTED_SOURCE_HASHES[int(row["step"])]
            for row in rows
        ),
        "source_rate_projection_is_exact_conservative_vector": all(
            row["source_max_action_delta_exact_conservative_vector"] for row in rows
        ),
        "actual_centered_guard_is_selected_g1": margin == 0.20,
        "deadband_is_exact_prior_contract": command_index == 6 and deadband == 0.01,
        "all_source_initializers_preserved": all(
            row["all_source_initializers_exact"] for row in rows
        ),
        "all_source_nodes_preserved": all(
            row["source_nodes_prefix_exact_modulo_frozen_output_rename"] for row in rows
        ),
        "all_append_exactly_13_guard_and_5_deadband_nodes": all(
            row["guard_node_count"] == 13 and row["deadband_node_count"] == 5
            for row in rows
        ),
        "all_external_abis_exact": all(row["graph_io"] == exact_io for row in rows),
        "all_cpu_inference_contracts_pass": all(
            row["inference_contract"]["pass"] for row in rows
        ),
        "formal_behavior_cells_zero": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT"
        if not failed
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v3.variable_configuration_eval_policy_transform_contract.v1",
        "status": status,
        "failed_checks": failed,
        "checks": checks,
        "formal_behavior_cells_executed": 0,
        "preregistration_sha256": sha256(PREREG),
        "training_artifact_check_sha256": sha256(TRAINING_CHECK),
        "training_archive_sha256": sha256(ARCHIVE),
        "frozen_transform_order": prereg["single_candidate"][
            "baked_post_actor_transforms_in_order"
        ],
        "implementation": {
            "source_graph": "learned recurrent actor with exact conservative all-joint previous-action projection",
            "appended_guard": "selected G1 measured-actual-centered pitch guard at 0.20 rad",
            "appended_deadband": "abs(obs[6]) <= 0.01 emits exact zero action and previous_action_out",
            "h_out_at_zero_command": "preserved from the learned recurrent actor; reset remains exact zero at episode reset",
        },
        "policies": rows,
        "authority": {
            "frozen_cpu_behavior_matrix": not failed,
            "training_or_retry": False,
            "gpu_or_igpu": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v3 Variable-Configuration Evaluation-Policy Transform Contract",
        "",
        f"status: `{status}`",
        "",
        "Formal behavior cells executed: `0`.",
        "",
    ]
    lines.extend(
        f"- `{name}`: `{'PASS' if passed else 'FAIL'}`"
        for name, passed in checks.items()
    )
    lines.extend(["", "## Contracted policies", ""])
    for row in rows:
        lines.append(
            f"- step `{row['step']}`: `{row['output_sha256']}` "
            f"(source `{row['source_sha256']}`)"
        )
    lines.extend(
        [
            "",
            "The learned graph and initializers are unchanged. The frozen G1 guard and "
            "prior x=0 deadband are appended before any formal behavior outcome. A pass "
            "authorizes only the preregistered 1,024-cell CPU evaluation.",
            "",
            "No training, retry, accelerator, hosted allocation, RDK-X5, robot, runtime, "
            "Gate 5, motion, or deployment is authorized.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed, "policies": len(rows)}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
