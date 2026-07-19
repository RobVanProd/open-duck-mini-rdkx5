#!/usr/bin/env python3
"""Validate winner-v2 native input quantizers before any behavior outcome."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_winner_v2_native_quantized_eval_policies import (  # noqa: E402
    DEFAULT_OUTPUT,
    SOURCE_POLICIES,
    build_all,
    build_wrapper,
    numpy_quantize_observation,
    valid_binary_contacts,
)


PREREG = (
    ROOT
    / "outputs/analysis/winner_v2_native_quantized_checkpoint_selection_preregistration.json"
)
OUTPUT_JSON = ROOT / "outputs/analysis/winner_v2_native_quantized_eval_contract.json"
OUTPUT_MD = ROOT / "outputs/analysis/WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT_20260719.md"
RUNTIME_REPO = ROOT.parent / "open-duck-mini-rdkx5-native-runtime"
RUNTIME_COMMIT = "5834400b7e23cf76c6b8afa7047b8052b60ff3b7"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=repo, stderr=subprocess.STDOUT
    )


def tensor_signature(value) -> tuple:
    shape = tuple(int(dim.dim_value) for dim in value.type.tensor_type.shape.dim)
    return value.name, int(value.type.tensor_type.elem_type), shape


def normalized_node_bytes(node, *, wrapped: bool) -> bytes:
    item = copy.deepcopy(node)
    if wrapped:
        for index, value in enumerate(item.input):
            if value == "native_quantized_obs":
                item.input[index] = "obs"
    return item.SerializeToString()


def quantizer_session(wrapper: Path):
    import onnx
    import onnxruntime as ort

    model = onnx.load(wrapper)
    model.graph.output.append(
        onnx.helper.make_tensor_value_info(
            "native_quantized_obs", onnx.TensorProto.FLOAT, [1, 115]
        )
    )
    handle = tempfile.NamedTemporaryFile(suffix=".onnx", delete=False)
    temp_path = Path(handle.name)
    handle.close()
    onnx.save(model, temp_path)
    session = ort.InferenceSession(
        str(temp_path), providers=["CPUExecutionProvider"]
    )
    return session, temp_path


def test_vectors() -> list[np.ndarray]:
    rng = np.random.default_rng(20260719)
    rows = []
    base = np.zeros(115, dtype=np.float32)
    base[6] = np.float32(0.08)
    base[97:99] = np.float32(1.0)
    rows.append(base)
    for _ in range(64):
        row = rng.normal(0.0, 1.0, size=115).astype(np.float32)
        row[6:13] = np.asarray([0.08, 0, 0, 0, 0, 0, 0], dtype=np.float32)
        row[97:99] = rng.integers(0, 2, size=2).astype(np.float32)
        rows.append(row)
    # Exact float32 half-grid and signed controls for each quantized class.
    from build_winner_v2_native_quantized_eval_policies import (  # noqa: E402
        ACCEL_LSB_M_S2,
        GYRO_LSB_RAD_S,
        POSITION_LSB_RAD,
        VELOCITY_OBS_LSB,
        home_rad,
        SOFT_OFFSETS_RAD,
    )

    half = base.copy()
    half[0:3] = (
        np.asarray([-2.5, -0.5, 2.5], dtype=np.float32) * GYRO_LSB_RAD_S
    )
    half[3:6] = (
        np.asarray([-2.5, -0.5, 2.5], dtype=np.float32) * ACCEL_LSB_M_S2
    )
    origin = home_rad() + SOFT_OFFSETS_RAD + np.float32(np.pi)
    half[13:27] = (
        np.arange(-7, 7, dtype=np.float32) + np.float32(0.5)
    ) * POSITION_LSB_RAD - origin
    half[27:41] = (
        np.arange(-7, 7, dtype=np.float32) + np.float32(0.5)
    ) * VELOCITY_OBS_LSB
    rows.append(half)
    return rows


def check_graph_identity(source_path: Path, wrapper_path: Path) -> dict:
    import onnx

    source = onnx.load(source_path)
    wrapped = onnx.load(wrapper_path)
    prefix_count = len(wrapped.graph.node) - len(source.graph.node)
    source_initializers = {item.name: item.SerializeToString() for item in source.graph.initializer}
    wrapped_initializers = {item.name: item.SerializeToString() for item in wrapped.graph.initializer}
    source_nodes = [normalized_node_bytes(node, wrapped=False) for node in source.graph.node]
    wrapped_suffix = [
        normalized_node_bytes(node, wrapped=True)
        for node in wrapped.graph.node[prefix_count:]
    ]
    return {
        "source_nodes": len(source.graph.node),
        "wrapper_nodes": len(wrapped.graph.node),
        "prefix_nodes": prefix_count,
        "source_initializers": len(source_initializers),
        "wrapper_initializers": len(wrapped_initializers),
        "source_node_suffix_exact": source_nodes == wrapped_suffix,
        "source_initializers_exact": all(
            wrapped_initializers.get(name) == value
            for name, value in source_initializers.items()
        ),
        "input_abi_exact": [tensor_signature(item) for item in wrapped.graph.input]
        == [("obs", 1, (1, 115)), ("previous_action", 1, (1, 14))],
        "output_abi_exact": [tensor_signature(item) for item in wrapped.graph.output]
        == [
            ("continuous_actions", 1, (1, 14)),
            ("previous_action_out", 1, (1, 14)),
        ],
        "all_source_obs_consumers_rewired": not any(
            value == "obs"
            for node in wrapped.graph.node[prefix_count:]
            for value in node.input
        ),
        "prefix_uses_public_obs": any(
            value == "obs"
            for node in wrapped.graph.node[:prefix_count]
            for value in node.input
        ),
    }


def main() -> int:
    import onnxruntime as ort

    prereg = json.loads(PREREG.read_text())
    expected = prereg["frozen_hashes"]
    manifest = build_all(DEFAULT_OUTPUT)
    builder = TOOLS / "build_winner_v2_native_quantized_eval_policies.py"
    checker = Path(__file__).resolve()

    runtime_hashes = {
        "native_sensors.py": sha256_bytes(
            git_blob(RUNTIME_REPO, RUNTIME_COMMIT, "src/open_duck_x5/sensors.py")
        ),
        "native_sts3215.py": sha256_bytes(
            git_blob(RUNTIME_REPO, RUNTIME_COMMIT, "src/open_duck_x5/bus/sts3215.py")
        ),
        "native_legacy_contract_snapshot": sha256_bytes(
            git_blob(
                RUNTIME_REPO,
                RUNTIME_COMMIT,
                "artifacts/contracts/legacy-contract-snapshot.json",
            )
        ),
    }
    local_hashes = {
        "handoff_manifest": sha256(
            ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719/manifest.json"
        ),
        "policy_512000": sha256(SOURCE_POLICIES[512000]),
        "policy_1024000": sha256(SOURCE_POLICIES[1024000]),
        "p30_fit": sha256(
            ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
        ),
        "p31_34_fit": sha256(
            ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json"
        ),
        "reference_table": sha256(
            ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
        ),
        "closed_loop_sim_eval.py": sha256(TOOLS / "closed_loop_sim_eval.py"),
    }
    observed_hashes = {**runtime_hashes, **local_hashes}

    rows = []
    all_vectors = test_vectors()
    default_off_hashes_exact = True
    for item in manifest["policies"]:
        step = int(item["step"])
        source_path = ROOT / item["source"]
        wrapper_path = ROOT / item["wrapper"]
        source_session = ort.InferenceSession(
            str(source_path), providers=["CPUExecutionProvider"]
        )
        wrapper_session = ort.InferenceSession(
            str(wrapper_path), providers=["CPUExecutionProvider"]
        )
        debug_session, debug_path = quantizer_session(wrapper_path)
        max_numpy_error = 0.0
        unchanged_exact = True
        contacts_exact = True
        wrapper_source_exact = True
        action_state_exact = True
        try:
            for index, obs in enumerate(all_vectors):
                if not valid_binary_contacts(obs):
                    raise AssertionError(f"valid test row {index} has nonbinary contacts")
                expected_obs = numpy_quantize_observation(obs[None, :])
                quantized = debug_session.run(
                    ["native_quantized_obs"],
                    {
                        "obs": obs[None, :],
                        "previous_action": np.zeros((1, 14), dtype=np.float32),
                    },
                )[0]
                max_numpy_error = max(
                    max_numpy_error,
                    float(np.max(np.abs(quantized.astype(float) - expected_obs.astype(float)))),
                )
                unchanged_exact &= bool(
                    np.array_equal(quantized[:, 6:13], obs[None, 6:13])
                    and np.array_equal(quantized[:, 41:115], obs[None, 41:115])
                )
                contacts_exact &= bool(
                    np.array_equal(quantized[:, 97:99], obs[None, 97:99])
                )
                previous = np.full((1, 14), index / 1000.0, dtype=np.float32)
                source_outputs = source_session.run(
                    ["continuous_actions", "previous_action_out"],
                    {"obs": quantized, "previous_action": previous},
                )
                wrapper_outputs = wrapper_session.run(
                    ["continuous_actions", "previous_action_out"],
                    {"obs": obs[None, :], "previous_action": previous},
                )
                wrapper_source_exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(source_outputs, wrapper_outputs, strict=True)
                )
                action_state_exact &= np.array_equal(
                    wrapper_outputs[0], wrapper_outputs[1]
                )
        finally:
            debug_path.unlink(missing_ok=True)

        x0_exact = True
        for obs in all_vectors[:16]:
            zero_obs = obs.copy()
            zero_obs[6] = np.float32(0.0)
            outputs = wrapper_session.run(
                ["continuous_actions", "previous_action_out"],
                {
                    "obs": zero_obs[None, :],
                    "previous_action": np.full((1, 14), 0.125, dtype=np.float32),
                },
            )
            x0_exact &= all(np.array_equal(value, np.zeros_like(value)) for value in outputs)

        golden = np.load(
            ROOT
            / f"artifacts/runtime_handoff/rdkx5_native_20260719/golden/T2_EQUAL_{step}_x0.080.npz"
        )["obs"]
        previous = np.zeros((1, 14), dtype=np.float32)
        chain_finite = True
        chain_action_state_exact = True
        for obs in golden[:256]:
            action, state = wrapper_session.run(
                ["continuous_actions", "previous_action_out"],
                {"obs": obs[None, :].astype(np.float32), "previous_action": previous},
            )
            chain_finite &= bool(np.all(np.isfinite(action)) and np.all(np.isfinite(state)))
            chain_action_state_exact &= np.array_equal(action, state)
            previous = np.asarray(state, dtype=np.float32)

        invalid_contacts = np.zeros((1, 115), dtype=np.float32)
        invalid_contacts[0, 97:99] = (0.5, 1.0)
        nonbinary_rejected = not valid_binary_contacts(invalid_contacts)

        with tempfile.TemporaryDirectory() as temp_dir:
            default_off = Path(temp_dir) / source_path.name
            build_wrapper(source_path, default_off, enabled=False)
            default_off_exact = sha256(default_off) == sha256(source_path)
            default_off_hashes_exact &= default_off_exact

        graph = check_graph_identity(source_path, wrapper_path)
        rows.append(
            {
                "step": step,
                "source_path": str(source_path.relative_to(ROOT)),
                "source_sha256": sha256(source_path),
                "wrapper_path": str(wrapper_path.relative_to(ROOT)),
                "wrapper_sha256": sha256(wrapper_path),
                "providers": wrapper_session.get_providers(),
                "graph": graph,
                "test_vectors": len(all_vectors),
                "max_numpy_quantizer_error": max_numpy_error,
                "unchanged_slices_bit_exact": unchanged_exact,
                "binary_contacts_bit_exact": contacts_exact,
                "nonbinary_contact_control_rejected": nonbinary_rejected,
                "wrapper_equals_source_on_quantized_input": wrapper_source_exact,
                "action_equals_state_output": action_state_exact,
                "x0_action_and_state_bit_exact_zero": x0_exact,
                "chained_256_finite": chain_finite,
                "chained_256_action_equals_state": chain_action_state_exact,
                "default_off_byte_exact": default_off_exact,
            }
        )

    checks = {
        "preregistration_status_exact": prereg["status"]
        == "PREREGISTERED_BEFORE_TRANSFORM_OR_BEHAVIOR_OUTCOMES",
        "all_frozen_hashes_exact": all(
            observed_hashes.get(name) == value for name, value in expected.items()
        ),
        "runtime_commit_exists": subprocess.run(
            ["git", "cat-file", "-e", f"{RUNTIME_COMMIT}^{{commit}}"],
            cwd=RUNTIME_REPO,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0,
        "two_wrappers_present": len(rows) == 2,
        "cpu_provider_only_selected": all(
            row["providers"] == ["CPUExecutionProvider"] for row in rows
        ),
        "graph_and_abi_identity": all(
            row["graph"]["source_node_suffix_exact"]
            and row["graph"]["source_initializers_exact"]
            and row["graph"]["input_abi_exact"]
            and row["graph"]["output_abi_exact"]
            and row["graph"]["all_source_obs_consumers_rewired"]
            and row["graph"]["prefix_uses_public_obs"]
            for row in rows
        ),
        "numpy_quantizer_error_at_most_1e7": all(
            row["max_numpy_quantizer_error"] <= 1.0e-7 for row in rows
        ),
        "unchanged_slices_bit_exact": all(
            row["unchanged_slices_bit_exact"] for row in rows
        ),
        "binary_contacts_bit_exact": all(row["binary_contacts_bit_exact"] for row in rows),
        "nonbinary_contact_control_rejected": all(
            row["nonbinary_contact_control_rejected"] for row in rows
        ),
        "wrapper_source_semantics_exact": all(
            row["wrapper_equals_source_on_quantized_input"]
            and row["action_equals_state_output"]
            for row in rows
        ),
        "default_off_byte_exact": default_off_hashes_exact,
        "x0_bit_exact_zero": all(row["x0_action_and_state_bit_exact_zero"] for row in rows),
        "chained_256_finite_and_stateful": all(
            row["chained_256_finite"] and row["chained_256_action_equals_state"]
            for row in rows
        ),
        "zero_formal_behavior_cells": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT"
        if not failed
        else "HOLD_WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT"
    )
    result = {
        "schema_version": "winner_v2.native_quantized_eval_contract.v1",
        "status": status,
        "failed_checks": failed,
        "checks": checks,
        "formal_behavior_cells_executed": 0,
        "runtime_evidence_commit": RUNTIME_COMMIT,
        "observed_frozen_hashes": observed_hashes,
        "preregistration_path": str(PREREG.relative_to(ROOT)),
        "preregistration_sha256": sha256(PREREG),
        "builder_path": str(builder.relative_to(ROOT)),
        "builder_sha256": sha256(builder),
        "checker_path": str(checker.relative_to(ROOT)),
        "checker_sha256": sha256(checker),
        "available_onnxruntime_providers": ort.get_available_providers(),
        "policies": rows,
        "manifest": manifest,
        "authority": {
            "behavior_matrix_authorized_if_pass": not failed,
            "robot_clearance": False,
            "gate_5": "NOT_AUTHORIZED",
            "rdk_x5_or_robot_access": False,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v2 Native-Quantized Eval Contract",
        "",
        f"status: `{status}`",
        "",
        f"Formal behavior cells executed: `{result['formal_behavior_cells_executed']}`.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{name}`: `{'PASS' if passed else 'FAIL'}`"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "## Wrapper readback",
            "",
            "| checkpoint | wrapper SHA-256 | prefix nodes | max NumPy error | providers |",
            "|---:|---|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['step']} | `{row['wrapper_sha256']}` | "
            f"{row['graph']['prefix_nodes']} | {row['max_numpy_quantizer_error']:.12g} | "
            f"`{','.join(row['providers'])}` |"
        )
    lines.extend(
        [
            "",
            "A pass authorizes only the frozen 16-cell CPU behavior matrix. It does not "
            "select a checkpoint before those outcomes and does not authorize Gate 5, "
            "deployment, RDK-X5/robot access, torque, motors, or robot clearance.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines))
    print(OUTPUT_MD.relative_to(ROOT))
    print(OUTPUT_JSON.relative_to(ROOT))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
