#!/usr/bin/env python3
"""Freeze the zero-cell Winner-v12 support-gate CPU contract after verification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v12_calibrator_support_gate_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
GATE_TESTS = ROOT / "tests/test_winner_v12_calibrator_support_gate.py"
DEFAULT_OUTPUT = ANALYSIS / "winner_v12_calibrator_support_gate_cpu_contract.json"
DEFAULT_MARKDOWN = (
    ANALYSIS / "WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT_20260721.md"
)
EXPECTED_WORK_ROOT_NAME = "winner-v12-full-calibrator-training-work"
ARTIFACT_CHECK_WORKFLOW = (
    ROOT
    / ".github/workflows/winner-v12-full-calibrator-training-artifact-check.yml"
)
ARTIFACT_CHECK_IMPORTER = (
    ROOT / "tools/import_winner_v12_full_calibrator_training_artifact_check.py"
)
CANONICAL_FIT = ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
MODEL_RELATIVE = "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml"
SCENE_RELATIVE = "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
MODEL_SHA256 = "660fa8e4ac0d977806e881d008090e7153cd0608dbee05b88f957a91bde6f655"
SCENE_SHA256 = "65324e27a3a84e2e42d1073bfc636f9cdbf6bef7b1f20c1b5a886b8fd58fcc71"
EXPECTED_INPUTS = [
    {"name": "obs", "shape": [1, 115]},
    {"name": "previous_action", "shape": [1, 14]},
    {"name": "h_in", "shape": [1, 64]},
]
EXPECTED_OUTPUTS = [
    {"name": "calibration_actions", "shape": [1, 14]},
    {"name": "previous_action_out", "shape": [1, 14]},
    {"name": "h_out", "shape": [1, 64]},
]
GIT_OID_RE = re.compile(r"[0-9a-f]{40}")
SOURCE_PATHS = {
    "workflow": Path(
        ".github/workflows/winner-v12-calibrator-support-gate-cpu-contract.yml"
    ),
    "builder": Path("tools/build_winner_v12_calibrator_support_gate_cpu_contract.py"),
    "checker": Path("tools/check_winner_v12_calibrator_support_gate_cpu_contract.py"),
    "artifact_verifier": Path(
        "tools/check_winner_v12_full_calibrator_training_artifact.py"
    ),
    "artifact_check_launch": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_artifact_check_launch.json"
    ),
    "artifact_check_workflow": Path(
        ".github/workflows/winner-v12-full-calibrator-training-artifact-check.yml"
    ),
    "artifact_check_importer": Path(
        "tools/import_winner_v12_full_calibrator_training_artifact_check.py"
    ),
    "zero_cell_result_importer": Path(
        "tools/import_winner_v12_calibrator_support_gate_cpu_contract_result.py"
    ),
    "zero_cell_result_importer_tests": Path(
        "tests/test_winner_v12_calibrator_support_gate_cpu_contract_result_import.py"
    ),
    "formal_gate_launch_builder": Path(
        "tools/build_winner_v12_calibrator_support_gate_launch.py"
    ),
    "formal_gate_launch_builder_tests": Path(
        "tests/test_winner_v12_calibrator_support_gate_launch.py"
    ),
    "support_gate_preregistration": Path(
        "outputs/analysis/winner_v12_calibrator_support_gate_preregistration.json"
    ),
    "calibrator_design_preregistration": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "failed_formal_gate_attribution": Path(
        "outputs/analysis/"
        "winner_v12_calibrator_support_gate_preexecution_failure_attribution.json"
    ),
    "failed_formal_gate_attribution_tests": Path(
        "tests/"
        "test_winner_v12_calibrator_support_gate_preexecution_failure_attribution.py"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "gate_tests": Path("tests/test_winner_v12_calibrator_support_gate.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "actuator_bridge": Path("tools/actuator_bridge_model.py"),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def require_sha256(value: Any, label: str) -> None:
    text = str(value)
    if len(text) != 64 or any(
        character not in "0123456789abcdef" for character in text
    ):
        raise ValueError(f"{label} SHA-256 is malformed")


def require_git_oid(value: Any, label: str) -> None:
    if GIT_OID_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} Git object ID is malformed")


def validate_checkpoint_identity(label: str, identity: Mapping[str, Any]) -> None:
    expected_update = {"half": 50, "final": 100}[label]
    if set(identity) != {"label", "update", "checkpoint", "onnx", "receipt"}:
        raise ValueError(f"{label} verified identity schema changed")
    if identity["label"] != label or identity["update"] != expected_update:
        raise ValueError(f"{label} verified boundary changed")
    expected_files = {
        "checkpoint": f"winner_v12_calibrator_{label}.npz",
        "onnx": f"winner_v12_calibrator_{label}.onnx",
        "receipt": f"winner_v12_calibrator_{label}_receipt.json",
    }
    for kind in ("checkpoint", "receipt"):
        value = identity[kind]
        if set(value) != {"file", "sha256", "bytes"}:
            raise ValueError(f"{label} {kind} identity schema changed")
        if value["file"] != expected_files[kind] or int(value["bytes"]) <= 0:
            raise ValueError(f"{label} {kind} identity changed")
        require_sha256(value["sha256"], f"{label} {kind}")
    graph = identity["onnx"]
    expected_graph_fields = {
        "file",
        "sha256",
        "bytes",
        "inputs",
        "outputs",
        "abi_exact",
        "all_initializers_finite",
        "all_chain_outputs_finite",
        "training_only_tensors_absent",
        "jax_onnx_max_abs_error",
        "jax_onnx_at_most_1e_7",
        "previous_action_out_equals_action_bit_exact",
    }
    if set(graph) != expected_graph_fields:
        raise ValueError(f"{label} ONNX identity schema changed")
    if (
        graph["file"] != expected_files["onnx"]
        or int(graph["bytes"]) <= 0
        or graph["inputs"] != EXPECTED_INPUTS
        or graph["outputs"] != EXPECTED_OUTPUTS
        or graph["abi_exact"] is not True
        or graph["all_initializers_finite"] is not True
        or graph["all_chain_outputs_finite"] is not True
        or graph["training_only_tensors_absent"] is not True
        or graph["jax_onnx_at_most_1e_7"] is not True
        or graph["previous_action_out_equals_action_bit_exact"] is not True
        or not 0.0 <= float(graph["jax_onnx_max_abs_error"]) <= 1.0e-7
    ):
        raise ValueError(f"{label} ONNX verification did not pass exactly")
    require_sha256(graph["sha256"], f"{label} ONNX")


def validate_verification_attribution(value: Any) -> None:
    expected_fields = {
        "artifact_check_launch_lf_sha256",
        "artifact_check_launch_path",
        "artifact_zip_bytes",
        "artifact_zip_sha256",
        "github_artifact_digest",
        "github_artifact_id",
        "github_artifact_name",
        "github_run_attempt",
        "github_run_head_sha",
        "github_run_id",
        "importer_lf_sha256",
        "raw_result_receipt_sha256",
        "raw_result_sha256",
        "repository",
        "workflow_lf_sha256",
        "workflow_path",
    }
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise ValueError("artifact-check verification attribution schema changed")
    if (
        value["repository"] != "RobVanProd/open-duck-mini-rdkx5"
        or int(value["github_run_id"]) <= 0
        or value["github_run_attempt"] != 1
        or int(value["github_artifact_id"]) <= 0
        or value["github_artifact_name"]
        != (
            "winner-v12-full-calibrator-training-artifact-check-"
            f"{value['github_run_id']}"
        )
        or int(value["artifact_zip_bytes"]) <= 0
        or value["github_artifact_digest"]
        != f"sha256:{value['artifact_zip_sha256']}"
        or value["artifact_check_launch_path"]
        != "outputs/analysis/winner_v12_full_calibrator_training_artifact_check_launch.json"
        or value["workflow_path"]
        != ".github/workflows/winner-v12-full-calibrator-training-artifact-check.yml"
    ):
        raise ValueError("artifact-check verification attribution changed")
    require_git_oid(value["github_run_head_sha"], "verification GitHub run head")
    for key in (
        "artifact_check_launch_lf_sha256",
        "artifact_zip_sha256",
        "importer_lf_sha256",
        "raw_result_receipt_sha256",
        "raw_result_sha256",
        "workflow_lf_sha256",
    ):
        require_sha256(value[key], key)
    if (
        value["workflow_lf_sha256"] != lf_sha256(ARTIFACT_CHECK_WORKFLOW)
        or value["importer_lf_sha256"] != lf_sha256(ARTIFACT_CHECK_IMPORTER)
    ):
        raise ValueError("artifact-check verification implementation changed")


def validate_artifact_check(
    result: Mapping[str, Any], *, require_verification_attribution: bool = True
) -> None:
    if (
        result.get("schema_version")
        != "winner_v12.full_calibrator_training_artifact_check.v1"
        or result.get("status")
        != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK"
        or result.get("decision") != "AUTHORIZE_FROZEN_124_CELL_CALIBRATOR_GATE_ONLY"
    ):
        raise ValueError("full-training artifact check did not authorize the gate")
    checks = result.get("checks")
    if (
        not isinstance(checks, dict)
        or not checks
        or not all(type(value) is bool for value in checks.values())
        or not all(checks.values())
        or result.get("failed_checks") != []
    ):
        raise ValueError("full-training artifact verification is incomplete")
    if result.get("execution") != {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("artifact verification execution authority changed")
    authority = result.get("authority")
    if (
        not isinstance(authority, dict)
        or authority.get("artifact_verification_only") is not True
        or authority.get("robot_clearance") is not False
        or authority.get("rdkx5_robot_serial_gpio_i2c_torque_motion") is not False
    ):
        raise ValueError("artifact verification authority changed")
    artifact = result.get("artifact_zip")
    if (
        not isinstance(artifact, dict)
        or int(artifact.get("bytes", 0)) <= 0
        or int(artifact.get("member_count", 0)) < 415
    ):
        raise ValueError("artifact ZIP identity is incomplete")
    require_sha256(artifact.get("sha256"), "artifact ZIP")
    require_sha256(result.get("training_result_sha256"), "training result")
    attribution = result.get("repository_attribution")
    if (
        not isinstance(attribution, dict)
        or set(attribution)
        != {
            "repository",
            "github_run_id",
            "github_run_attempt",
            "github_run_head_sha",
            "github_artifact_id",
            "github_artifact_name",
            "github_artifact_digest",
        }
        or attribution["repository"] != "RobVanProd/open-duck-mini-rdkx5"
        or int(attribution["github_run_id"]) <= 0
        or attribution["github_run_attempt"] != 1
        or int(attribution["github_artifact_id"]) <= 0
        or attribution["github_artifact_name"]
        != f"winner-v12-full-calibrator-training-{attribution['github_run_id']}"
        or attribution["github_artifact_digest"] != f"sha256:{artifact['sha256']}"
    ):
        raise ValueError("artifact repository attribution changed")
    require_git_oid(attribution["github_run_head_sha"], "GitHub run head")
    checkpoints = result.get("verified_checkpoints")
    if not isinstance(checkpoints, dict) or set(checkpoints) != {"half", "final"}:
        raise ValueError("verified half/final identity set changed")
    for label in ("half", "final"):
        validate_checkpoint_identity(label, checkpoints[label])
    verification = result.get("verification_repository_attribution")
    if require_verification_attribution:
        validate_verification_attribution(verification)
    elif verification is not None:
        raise ValueError("raw artifact check unexpectedly contains import attribution")


def bind_training_files(
    training_work_root: Path, verified: Mapping[str, Any]
) -> dict[str, Any]:
    if training_work_root.name != EXPECTED_WORK_ROOT_NAME:
        raise ValueError("training work-root identity changed")
    bound: dict[str, Any] = {}
    for label in ("half", "final"):
        identity = verified[label]
        files = {}
        for kind in ("checkpoint", "onnx", "receipt"):
            expected = identity[kind]
            path = training_work_root / expected["file"]
            if not path.is_file():
                raise FileNotFoundError(path)
            observed = {
                "file": path.name,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            if observed != {key: expected[key] for key in ("file", "sha256", "bytes")}:
                raise ValueError(f"{label} {kind} differs from artifact verification")
            files[kind] = observed
        bound[label] = {
            "label": label,
            "update": identity["update"],
            **files,
            "onnx_abi": {
                key: identity["onnx"][key]
                for key in (
                    "inputs",
                    "outputs",
                    "abi_exact",
                    "all_initializers_finite",
                    "all_chain_outputs_finite",
                    "training_only_tensors_absent",
                    "jax_onnx_max_abs_error",
                    "jax_onnx_at_most_1e_7",
                    "previous_action_out_equals_action_bit_exact",
                )
            },
        }
    return bound


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError as error:
        raise ValueError(f"contract input must be repository-backed: {path}") from error


def source_manifest(artifact_check: Path) -> dict[str, dict[str, str]]:
    paths = {
        **SOURCE_PATHS,
        "artifact_check_result": Path(relative_repo_path(artifact_check)),
    }
    return {
        name: {
            "path": str(relative).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / relative),
        }
        for name, relative in paths.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-check", type=Path, required=True)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite frozen contract: {path}")
    artifact_check = json.loads(args.artifact_check.read_text(encoding="utf-8"))
    validate_artifact_check(artifact_check)
    checkpoints = bind_training_files(
        args.training_work_root, artifact_check["verified_checkpoints"]
    )
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        or preregistration.get("decision") != "AUTHORIZE_SUPPORT_GATE_CPU_CONTRACT_ONLY"
        or preregistration.get("failed_checks") != []
        or not all(preregistration.get("checks", {}).values())
    ):
        raise ValueError("support-gate preregistration did not pass exactly")
    sources = source_manifest(args.artifact_check)
    contract = {
        "schema_version": "winner_v12.calibrator_support_gate_cpu_contract.v1",
        "status": "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT_FROZEN",
        "decision": "AUTHORIZE_ONE_ZERO_CELL_SUPPORT_GATE_CPU_CONTRACT_RUN_ONLY",
        "artifact_verification": {
            "result_lf_sha256": lf_sha256(args.artifact_check),
            "artifact_zip_sha256": artifact_check["artifact_zip"]["sha256"],
            "artifact_zip_bytes": artifact_check["artifact_zip"]["bytes"],
            "training_result_sha256": artifact_check["training_result_sha256"],
            "repository_attribution": artifact_check["repository_attribution"],
        },
        "verified_checkpoints": checkpoints,
        "immutable_gate_inputs": {
            "canonical_p30_fit": {
                "path": str(CANONICAL_FIT.relative_to(ROOT)).replace("\\", "/"),
                "lf_sha256": lf_sha256(CANONICAL_FIT),
            },
            "playground_model": {
                "relative_path": MODEL_RELATIVE,
                "sha256": MODEL_SHA256,
            },
            "playground_scene": {
                "relative_path": SCENE_RELATIVE,
                "sha256": SCENE_SHA256,
            },
        },
        "software_versions": {
            "python": "3.12.13",
            "jax": "0.7.2",
            "jaxlib": "0.7.2",
            "mujoco": "3.9.0",
            "numpy": "2.0.2",
            "onnx": "1.22.0",
            "onnxruntime": "1.27.0",
        },
        "formal_gate_after_contract": {
            "checkpoint_labels": ["half", "final"],
            "main_cells_per_checkpoint": 124,
            "main_cells_total": 248,
            "heldout_repeat_cells_total": 64,
            "duration_ticks_per_cell": 250,
            "all_cells_at_both_checkpoints_must_pass": True,
        },
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one zero-cell pinned Linux/JAX support-gate implementation contract",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator support-gate CPU contract",
                "",
                f"- Status: `{contract['status']}`",
                f"- Decision: `{contract['decision']}`",
                f"- Contract SHA-256: `{lf_sha256(args.output)}`",
                "- Formal support cells executed now: `0`",
                "- Robot or RDK access: `0`",
                "",
                "This contract binds the independently verified half/final checkpoint",
                "and ONNX identities. It authorizes one pinned zero-cell integration check",
                "only; it does not itself authorize the 248-cell gate or locomotion.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": contract["status"], "sha256": lf_sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
