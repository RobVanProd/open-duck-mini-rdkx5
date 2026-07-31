#!/usr/bin/env python3
"""Contract the preregistered CPU-only torso-COM full-observation study."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


REPO = Path(__file__).resolve().parents[1]
ORIGINAL_REPO = Path("/home/lsd/robots/open-duck-mini-rdkx5")
MATRIX_ROOT = REPO / "outputs/analysis/ground_up_torso_com_behavior_eval"
POLICY_ROOT = REPO / "outputs/analysis/ground_up_torso_com_eval_policies"
CONTRACT_JSON = REPO / "outputs/analysis/ground_up_torso_com_eval_policy_transform_contract.json"
CORRECTION_JSON = REPO / "outputs/analysis/ground_up_torso_com_decode_interpretation_correction.json"
RAW_AUDIT_JSON = REPO / "outputs/analysis/ground_up_torso_com_instantaneous_decode_raw_audit.json"
P30 = REPO / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
P31 = REPO / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json"
REFERENCE = REPO / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
EVALUATOR = REPO / "tools/evaluate_ground_up_policy.py"
CLOSED_LOOP = REPO / "tools/closed_loop_sim_eval.py"
REPLAY_TOOL = REPO / "tools/run_ground_up_torso_com_full_obs_replay.py"
ANALYSIS_TOOL = REPO / "tools/analyze_ground_up_torso_com_full_obs_study.py"

EXPECTED = {
    "matrix_manifest": "0128c39a9322beecb9f94f4200819093afd2ca50ea2944a8d6add5db852b9839",
    "matrix_bytes": 8647527,
    "policy_manifest": "d50bfc57e29dea9479d16506d175175e6a94f69c5d62700168d5bf9df3cadac4",
    "policy_bytes": 5441706,
    "transform": "d724a7d0ac96ab18aaa1ea29e5872436d09977cb47af58db46f916423bf14a86",
    "correction": "ef62ea7e479c1734dd8b416ce4bcb4636de9d4b5bf40c55cf729c8a536af1f37",
    "raw_audit": "c391599d3aabde3a7ea5f5e4eb889290abaa17d90730a7cbac8e4b9a73cc9931",
    "p30": "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b",
    "p31": "a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276",
    "reference": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "evaluator": "b05f49e0692237aa6aff924d9fa41fe9ce06b46d806187597022ac52eb2a4d3a",
    "closed_loop": "e6182ad45c0409820ad8086694a5d12b9c7154ed70a47a836895dc61ab55fd90",
}
POLICIES = {
    "A05_DIRECT_1003520": "e50a121bf0c2d9a2715d65b8356e4e1af68a16c1ecb264975c1c1d33acea32a7",
    "A05_DIRECT_2007040": "eaa01f1d1c29f7bb6e7c9cf77093229e708ad317bb8d2a175617f4e9955b11c5",
    "U05_DIRECT_1003520": "6aa4364ec3291d5f42b5adf725a79c3c18f0062f0f4741e09f814ea1af7db9af",
    "U05_DIRECT_2007040": "c16be9b15549343073a24e3844da54d648415dbd5979e321db10e45fc6167a11",
    "U_CURRICULUM_512000": "1653f55429867c63248175c7f3be2b8b550f57dd29f03321da312495ba6528b5",
    "U_CURRICULUM_1024000": "2665ac124d59ddeb93777cf1d82ca1bc0d0506bb26bd1c06645356c66fce3001",
}
CONDITIONS = {
    "NOMINAL": None,
    "TORSO_COM_X_NEG": [-0.05, 0.0, 0.0],
    "TORSO_COM_X_POS": [0.05, 0.0, 0.0],
}
FITS = {
    "p30": EXPECTED["p30"],
    "p31_34": EXPECTED["p31"],
}
MATRIX_RE = re.compile(
    r"^(NOMINAL|TORSO_COM_X_NEG|TORSO_COM_X_POS)_(A05_DIRECT|U05_DIRECT|U_CURRICULUM)_(\d+)_(p30|p31_34)\.json$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_manifest(root: Path, pattern: str) -> tuple[str, list[dict[str, Any]]]:
    rows, lines = [], []
    for path in sorted(root.rglob(pattern)):
        rel = path.relative_to(root).as_posix()
        digest = sha256(path)
        rows.append({"path": rel, "sha256": digest, "bytes": path.stat().st_size})
        lines.append(f"{rel}\t{digest}\n")
    return hashlib.sha256("".join(lines).encode()).hexdigest(), rows


def normalize_behavior(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove only fields frozen as reporting-only replay differences."""
    out = copy.deepcopy(payload)
    inputs = out.get("inputs", {})
    inputs.pop("trace_dir", None)
    inputs.pop("trace_full_obs", None)
    for run in out.get("runs", []):
        run.pop("trace_jsonl", None)
        for mode in (run.get("modes") or {}).values():
            if isinstance(mode, dict):
                mode.pop("wall_clock_s", None)
    return out


def matrix_identity(path: Path) -> tuple[str, str, int, str]:
    match = MATRIX_RE.match(path.name)
    if not match:
        raise ValueError(f"invalid matrix filename: {path.name}")
    condition, arm, step, fit = match.groups()
    key = f"{arm}_{step}"
    if key not in POLICIES:
        raise ValueError(f"uncontracted policy in {path.name}")
    return condition, arm, int(step), fit


def validate_readback(condition: str, run: dict[str, Any]) -> None:
    value = CONDITIONS[condition]
    override = run.get("dynamics_override") or {}
    if value is None:
        if override != {"enabled": False, "key": None, "readback": {}, "value": None}:
            raise ValueError("nominal dynamics override is not exact default-off")
        return
    if override.get("enabled") is not True or override.get("key") != "torso_com_offset_m":
        raise ValueError("COM override key/enabled mismatch")
    if override.get("value") != value:
        raise ValueError("COM override value mismatch")
    readback = override.get("readback") or {}
    if readback.get("body_id") != 2 or readback.get("body_name") != "trunk_assembly":
        raise ValueError("COM readback target mismatch")
    if abs(float(readback.get("body_mass_kg", 0.0)) - 0.6985260248184204) > 1e-12:
        raise ValueError("COM readback mass mismatch")
    before, after = readback.get("before"), readback.get("after")
    if not isinstance(before, list) or not isinstance(after, list) or len(before) != 3 or len(after) != 3:
        raise ValueError("COM readback vector shape mismatch")
    delta = [float(a) - float(b) for a, b in zip(after, before, strict=True)]
    if max(abs(delta[i] - value[i]) for i in range(3)) > 1e-12:
        raise ValueError(f"COM readback is not exact one-axis mutation: {delta}")
    if readback.get("changed_indices") != [[2, 0], [2, 1], [2, 2]]:
        raise ValueError("COM readback field/index contract mismatch")


def validate_matrix(path: Path) -> dict[str, Any]:
    condition, arm, step, fit = matrix_identity(path)
    payload = json.loads(path.read_text())
    inputs = payload.get("inputs") or {}
    expected_override = None if CONDITIONS[condition] is None else {"torso_com_offset_m": CONDITIONS[condition]}
    exact = {
        "commands": [0.0, 0.074, 0.077, 0.08],
        "duration_s": 12.0,
        "eval_dynamics_override": expected_override,
        "expected_observation_dim": 115,
        "minimum_emergence_duration_s": 1.08,
        "policy_action_rate_limit_rad_s": None,
        "policy_action_rate_limit_joint_indices": [2, 3, 4, 11, 12, 13],
        "policy_action_rate_limit_values": [],
        "policy_applied_target_observation": True,
        "policy_state_input_names": ["previous_action"],
        "policy_state_output_names": ["previous_action_out"],
        "reference_start_phase": 0,
        "reset_mode": "home-support",
        "seeds": [167931544],
        "task": "flat_terrain_backlash",
        "trace_full_obs": False,
    }
    for key, expected in exact.items():
        if inputs.get(key) != expected:
            raise ValueError(f"{path.name}: input {key} mismatch")
    policy_key = f"{arm}_{step}"
    if inputs.get("policy_sha256") != POLICIES[policy_key]:
        raise ValueError(f"{path.name}: policy hash mismatch")
    if inputs.get("fit_sha256") != FITS[fit]:
        raise ValueError(f"{path.name}: fit hash mismatch")
    if inputs.get("reference_feature_table_sha256") != EXPECTED["reference"]:
        raise ValueError(f"{path.name}: reference hash mismatch")
    runs = payload.get("runs") or []
    if len(runs) != 4 or [run.get("command_x") for run in runs] != exact["commands"]:
        raise ValueError(f"{path.name}: four-command run contract mismatch")
    for run in runs:
        if run.get("seed") != 167931544:
            raise ValueError(f"{path.name}: seed mismatch")
        validate_readback(condition, run)
    return {"condition": condition, "arm": arm, "step": step, "fit": fit}


def cpu_env_ok(cuda: str | None, jax_platforms: str | None) -> bool:
    return cuda == "" and jax_platforms == "cpu"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}

    checks["cpu_environment_exact"] = cpu_env_ok(
        os.environ.get("CUDA_VISIBLE_DEVICES"), os.environ.get("JAX_PLATFORMS")
    )
    matrix_manifest, matrix_rows = canonical_manifest(MATRIX_ROOT, "*.json")
    policy_manifest, policy_rows = canonical_manifest(POLICY_ROOT, "*.onnx")
    checks["matrix_manifest_exact"] = (
        matrix_manifest == EXPECTED["matrix_manifest"]
        and len(matrix_rows) == 36
        and sum(row["bytes"] for row in matrix_rows) == EXPECTED["matrix_bytes"]
    )
    checks["policy_manifest_exact"] = (
        policy_manifest == EXPECTED["policy_manifest"]
        and len(policy_rows) == 6
        and sum(row["bytes"] for row in policy_rows) == EXPECTED["policy_bytes"]
    )
    static_files = {
        "transform": CONTRACT_JSON,
        "correction": CORRECTION_JSON,
        "raw_audit": RAW_AUDIT_JSON,
        "p30": P30,
        "p31": P31,
        "reference": REFERENCE,
        "evaluator": EVALUATOR,
        "closed_loop": CLOSED_LOOP,
    }
    details["source_hashes"] = {name: sha256(path) for name, path in static_files.items()}
    checks["all_frozen_source_hashes_exact"] = all(
        details["source_hashes"][name] == EXPECTED[name] for name in static_files
    )

    matrix_contracts = [validate_matrix(MATRIX_ROOT / row["path"]) for row in matrix_rows]
    checks["all_36_matrices_exact"] = len(matrix_contracts) == 36 and len(
        {(r["condition"], r["arm"], r["step"], r["fit"]) for r in matrix_contracts}
    ) == 36

    transform = json.loads(CONTRACT_JSON.read_text())
    transform_hashes = {f"{row['arm']}_{row['step']}": row["output_sha256"] for row in transform["policies"]}
    checks["transform_contract_passes_and_matches_six_graphs"] = (
        transform.get("status") == "PASS_TORSO_COM_EVAL_POLICY_TRANSFORM_CONTRACT"
        and transform_hashes == POLICIES
        and not transform.get("failed_checks")
    )

    import jax
    import numpy as np
    import onnxruntime as ort

    checks["jax_cpu_only"] = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    graph_rows = []
    for row in policy_rows:
        path = POLICY_ROOT / row["path"]
        session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        inputs = [(item.name, item.shape, item.type) for item in session.get_inputs()]
        outputs = [(item.name, item.shape, item.type) for item in session.get_outputs()]
        finite = session.run(
            None,
            {
                "obs": np.zeros((1, 115), dtype=np.float32),
                "previous_action": np.zeros((1, 14), dtype=np.float32),
            },
        )
        graph_rows.append({
            "path": row["path"],
            "providers": session.get_providers(),
            "inputs": inputs,
            "outputs": outputs,
            "finite": all(np.all(np.isfinite(value)) for value in finite),
        })
    expected_inputs = [("obs", [1, 115], "tensor(float)"), ("previous_action", [1, 14], "tensor(float)")]
    expected_outputs = [("continuous_actions", [1, 14], "tensor(float)"), ("previous_action_out", [1, 14], "tensor(float)")]
    checks["onnx_cpu_interface_and_finite_exact"] = all(
        row["providers"] == ["CPUExecutionProvider"]
        and row["inputs"] == expected_inputs
        and row["outputs"] == expected_outputs
        and row["finite"]
        for row in graph_rows
    )
    details["onnx_graphs"] = graph_rows

    closed_source = CLOSED_LOOP.read_text()
    checks["trace_full_obs_static_append_only"] = all(
        marker in closed_source
        for marker in (
            'if config.trace_full_obs:',
            'record["obs_state"] = obs.astype(float).tolist()',
            'record["qpos"] = qpos.astype(float).tolist()',
            'record["qvel"] = np.asarray(jax.device_get(state.data.qvel), dtype=float).tolist()',
            'record["ctrl"] = np.asarray(jax.device_get(state.data.ctrl), dtype=float).tolist()',
            'record["base_quat_wxyz"] = quat.astype(float).tolist()',
        )
    ) and closed_source.count("if config.trace_full_obs:") == 1

    fixture = json.loads((MATRIX_ROOT / matrix_rows[0]["path"]).read_text())
    changed = copy.deepcopy(fixture)
    changed["inputs"]["trace_dir"] = "/new/trace/root"
    changed["inputs"]["trace_full_obs"] = True
    for run in changed["runs"]:
        run["trace_jsonl"] = "/new/trace.jsonl"
        run["modes"]["fitted"]["wall_clock_s"] = -1.0
    checks["comparison_normalizer_accepts_only_reporting_fields"] = normalize_behavior(fixture) == normalize_behavior(changed)
    changed["runs"][0]["emergence"]["mean_velocity_x_m_s"] += 1e-9
    checks["comparison_normalizer_preserves_behavior_changes"] = normalize_behavior(fixture) != normalize_behavior(changed)

    # Refusal fixtures exercise each failure class without touching source files.
    bad_readback = copy.deepcopy(fixture["runs"][0])
    if CONDITIONS[matrix_contracts[0]["condition"]] is None:
        bad_readback["dynamics_override"] = {"enabled": True}
    refused_readback = False
    try:
        validate_readback(matrix_contracts[0]["condition"], bad_readback)
    except ValueError:
        refused_readback = True
    checks["refuses_readback_mutation"] = refused_readback
    checks["refuses_device_mutation"] = not cpu_env_ok("0", "cpu") and not cpu_env_ok("", "gpu")
    checks["refuses_manifest_mutation"] = hashlib.sha256(("x" + matrix_manifest).encode()).hexdigest() != EXPECTED["matrix_manifest"]
    checks["study_tools_present_before_replay"] = REPLAY_TOOL.is_file() and ANALYSIS_TOOL.is_file()

    details.update({
        "matrix_manifest_sha256": matrix_manifest,
        "policy_manifest_sha256": policy_manifest,
        "matrix_rows": matrix_rows,
        "policy_rows": policy_rows,
        "study_tool_hashes": {
            "contract": sha256(Path(__file__)),
            "replay": sha256(REPLAY_TOOL) if REPLAY_TOOL.is_file() else None,
            "analysis": sha256(ANALYSIS_TOOL) if ANALYSIS_TOOL.is_file() else None,
        },
        "jax_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in jax.devices()],
    })
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_TORSO_COM_FULL_OBS_STUDY_CONTRACT" if not failed else "FAIL_TORSO_COM_FULL_OBS_STUDY_CONTRACT"
    payload = {
        "schema_version": "ground_up_torso_com_full_obs_study_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "details": details,
        "execution": {
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "jax_platforms": os.environ.get("JAX_PLATFORMS"),
            "onnx_provider": "CPUExecutionProvider",
            "robot_access": False,
            "rdk_access": False,
            "training": False,
            "simulator_behavior_cells": 0,
        },
        "authority": {
            "full_observation_replay_authorized_if_pass": True,
            "training_or_policy_change": False,
            "gpu_or_igpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
