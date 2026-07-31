#!/usr/bin/env python3
"""Freeze one formal Winner-v12 support-gate launch after every prerequisite passes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

import build_winner_v12_calibrator_support_gate_cpu_contract as cpu_builder  # noqa: E402


OUTPUT = ANALYSIS / "winner_v12_calibrator_support_gate_launch.json"
MARKDOWN = ANALYSIS / "WINNER_V12_CALIBRATOR_SUPPORT_GATE_LAUNCH_20260721.md"
PREREGISTRATION = ANALYSIS / "winner_v12_calibrator_support_gate_preregistration.json"
FAILURE_ATTRIBUTION = (
    ANALYSIS / "winner_v12_calibrator_support_gate_preexecution_failure_attribution.json"
)
EXPECTED_ZERO_EXECUTION = {
    "formal_support_cells": 0,
    "heldout_repeat_cells": 0,
    "locomotion_training_steps": 0,
    "robot_or_rdk_access": 0,
}
STATIC_SOURCES = {
    "builder": Path("tools/build_winner_v12_calibrator_support_gate_launch.py"),
    "workflow": Path(".github/workflows/winner-v12-calibrator-support-gate.yml"),
    "gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "gate_tests": Path("tests/test_winner_v12_calibrator_support_gate.py"),
    "gate_preregistration": Path(
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
    "zero_cell_checker": Path(
        "tools/check_winner_v12_calibrator_support_gate_cpu_contract.py"
    ),
    "zero_cell_importer": Path(
        "tools/import_winner_v12_calibrator_support_gate_cpu_contract_result.py"
    ),
    "zero_cell_importer_tests": Path(
        "tests/test_winner_v12_calibrator_support_gate_cpu_contract_result_import.py"
    ),
    "zero_cell_workflow": Path(
        ".github/workflows/winner-v12-calibrator-support-gate-cpu-contract.yml"
    ),
    "formal_result_importer": Path(
        "tools/import_winner_v12_calibrator_support_gate_result.py"
    ),
    "formal_result_importer_tests": Path(
        "tests/test_winner_v12_calibrator_support_gate_result_import.py"
    ),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "actuator_bridge": Path("tools/actuator_bridge_model.py"),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_zero_cell_repository_attribution(value: Any) -> None:
    expected_fields = {
        "artifact_zip_bytes",
        "artifact_zip_sha256",
        "checker_lf_sha256",
        "cpu_contract_lf_sha256",
        "cpu_contract_path",
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
        raise ValueError("zero-cell repository attribution schema changed")
    run_id = value["github_run_id"]
    if (
        value["repository"] != "RobVanProd/open-duck-mini-rdkx5"
        or int(run_id) <= 0
        or value["github_run_attempt"] != 1
        or len(str(value["github_run_head_sha"])) != 40
        or any(character not in "0123456789abcdef" for character in value["github_run_head_sha"])
        or int(value["github_artifact_id"]) <= 0
        or value["github_artifact_name"]
        != f"winner-v12-calibrator-support-gate-cpu-contract-{run_id}"
        or value["github_artifact_digest"]
        != f"sha256:{value['artifact_zip_sha256']}"
        or int(value["artifact_zip_bytes"]) <= 0
        or value["cpu_contract_path"]
        != "outputs/analysis/winner_v12_calibrator_support_gate_cpu_contract.json"
        or value["workflow_path"]
        != ".github/workflows/winner-v12-calibrator-support-gate-cpu-contract.yml"
    ):
        raise ValueError("zero-cell repository attribution changed")
    for key in (
        "artifact_zip_sha256",
        "checker_lf_sha256",
        "cpu_contract_lf_sha256",
        "importer_lf_sha256",
        "raw_result_receipt_sha256",
        "raw_result_sha256",
        "workflow_lf_sha256",
    ):
        value_text = str(value[key])
        if len(value_text) != 64 or any(
            character not in "0123456789abcdef" for character in value_text
        ):
            raise ValueError(f"zero-cell {key} SHA-256 changed")


def validate_zero_cell_result(
    result: Mapping[str, Any],
    cpu_contract_lf_sha256: str,
    *,
    require_repository_attribution: bool = True,
) -> None:
    if (
        result.get("schema_version")
        != "winner_v12.calibrator_support_gate_cpu_contract_result.v1"
        or result.get("status")
        != "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT"
        or result.get("decision")
        != "AUTHORIZE_ONE_FROZEN_248_CELL_SUPPORT_GATE_RUN_ONLY"
        or result.get("contract_lf_sha256") != cpu_contract_lf_sha256
    ):
        raise ValueError("zero-cell support-gate result did not authorize one gate")
    checks = result.get("checks")
    if (
        not isinstance(checks, dict)
        or not checks
        or not all(type(value) is bool for value in checks.values())
        or not all(checks.values())
        or result.get("failed_checks") != []
    ):
        raise ValueError("zero-cell support-gate checks did not all pass")
    if result.get("execution") != EXPECTED_ZERO_EXECUTION:
        raise ValueError("zero-cell result executed formal or unauthorized work")
    authority = result.get("authority")
    if (
        not isinstance(authority, dict)
        or authority.get("robot_clearance") is not False
        or authority.get("rdkx5_robot_serial_gpio_i2c_torque_motion") is not False
    ):
        raise ValueError("zero-cell result robot authority changed")
    graphs = result.get("checkpoint_graph_contracts")
    if not isinstance(graphs, list) or [row.get("label") for row in graphs] != [
        "half",
        "final",
    ]:
        raise ValueError("zero-cell checkpoint graph set changed")
    for row in graphs:
        independent = row.get("independent_onnx_contract", {})
        if (
            row.get("support_runner_chain_ticks") != 250
            or row.get("support_runner_all_outputs_finite") is not True
            or row.get("support_runner_previous_action_chain_bit_exact") is not True
            or row.get("support_runner_graph_boundary_exact") is not True
            or row.get("support_runner_jax_onnx_h_at_most_1e_7") is not True
            or not 0.0
            <= float(row.get("support_runner_jax_onnx_h_max_abs_error", 1.0))
            <= 1.0e-7
            or independent.get("abi_exact") is not True
            or independent.get("all_initializers_finite") is not True
            or independent.get("all_chain_outputs_finite") is not True
            or independent.get("training_only_tensors_absent") is not True
            or independent.get("jax_onnx_at_most_1e_7") is not True
            or independent.get("previous_action_out_equals_action_bit_exact")
            is not True
        ):
            raise ValueError(f"zero-cell {row.get('label')} graph proof changed")
    primitives = result.get("transport_primitives")
    if (
        not isinstance(primitives, dict)
        or not primitives
        or not all(type(value) is bool for value in primitives.values())
        or not all(primitives.values())
    ):
        raise ValueError("zero-cell transport proof changed")
    attribution = result.get("repository_attribution")
    if require_repository_attribution:
        validate_zero_cell_repository_attribution(attribution)
        if attribution["cpu_contract_lf_sha256"] != cpu_contract_lf_sha256:
            raise ValueError("zero-cell attribution contract hash changed")
    elif attribution is not None:
        raise ValueError("raw zero-cell result unexpectedly has repository attribution")


def relative_repo_path(path: Path) -> Path:
    try:
        return path.resolve().relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError(
            f"formal-gate input must be repository-backed: {path}"
        ) from error


def source_manifest(dynamic: Mapping[str, Path]) -> dict[str, dict[str, str]]:
    paths = {**STATIC_SOURCES, **dynamic}
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
    parser.add_argument("--cpu-contract", type=Path, required=True)
    parser.add_argument("--zero-cell-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite formal-gate launch: {path}")
    artifact_check = json.loads(args.artifact_check.read_text(encoding="utf-8"))
    cpu_builder.validate_artifact_check(artifact_check)
    cpu_contract = json.loads(args.cpu_contract.read_text(encoding="utf-8"))
    cpu_builder_contract_hash = lf_sha256(args.cpu_contract)
    if (
        cpu_contract.get("status")
        != "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT_FROZEN"
        or cpu_contract.get("execution_now") != EXPECTED_ZERO_EXECUTION
        or cpu_contract.get("verified_checkpoints") is None
        or cpu_contract.get("artifact_verification", {}).get("result_lf_sha256")
        != lf_sha256(args.artifact_check)
        or cpu_contract.get("artifact_verification", {}).get("repository_attribution")
        != artifact_check.get("repository_attribution")
    ):
        raise ValueError("zero-cell CPU contract changed")
    for label in ("half", "final"):
        for kind in ("checkpoint", "onnx", "receipt"):
            verified = artifact_check["verified_checkpoints"][label][kind]
            contracted = cpu_contract["verified_checkpoints"][label][kind]
            if contracted != {
                key: verified[key] for key in ("file", "sha256", "bytes")
            }:
                raise ValueError(
                    f"zero-cell CPU contract changed verified {label} {kind}"
                )
    zero_cell = json.loads(args.zero_cell_result.read_text(encoding="utf-8"))
    validate_zero_cell_result(zero_cell, cpu_builder_contract_hash)
    if zero_cell.get("training_files") != {
        label: {
            f"{kind}_sha256": cpu_contract["verified_checkpoints"][label][kind][
                "sha256"
            ]
            for kind in ("checkpoint", "onnx", "receipt")
        }
        for label in ("half", "final")
    }:
        raise ValueError("zero-cell training-file identities changed")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        or preregistration.get("failed_checks") != []
        or not all(preregistration.get("checks", {}).values())
    ):
        raise ValueError("formal support gate is not preregistered exactly")
    failure_attribution = json.loads(
        FAILURE_ATTRIBUTION.read_text(encoding="utf-8")
    )
    if (
        failure_attribution.get("status")
        != "ATTRIBUTED_WINNER_V12_SUPPORT_GATE_PREEXECUTION_FAILURE"
        or failure_attribution.get("decision")
        != "AUTHORIZE_ONE_PROVENANCE_BOUND_INPUT_BINDING_CORRECTION_ONLY"
        or failure_attribution.get("attempt", {}).get("github_run_id")
        != 29815413956
        or failure_attribution.get("attempt", {}).get("github_run_attempt") != 1
        or failure_attribution.get("execution")
        != {
            "formal_support_cells_completed": 0,
            "heldout_repeat_cells_completed": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or failure_attribution.get("failed_checks") != []
        or not all(failure_attribution.get("checks", {}).values())
    ):
        raise ValueError("failed formal-gate attribution changed")
    sources = source_manifest(
        {
            "artifact_check_result": relative_repo_path(args.artifact_check),
            "zero_cell_cpu_contract": relative_repo_path(args.cpu_contract),
            "zero_cell_cpu_result": relative_repo_path(args.zero_cell_result),
        }
    )
    payload = {
        "schema_version": "winner_v12.calibrator_support_gate_launch.v2",
        "status": "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_LAUNCH_FROZEN",
        "decision": "AUTHORIZE_ONE_FROZEN_248_CELL_SUPPORT_GATE_RUN_ONLY",
        "training_artifact": cpu_contract["artifact_verification"],
        "verified_checkpoints": cpu_contract["verified_checkpoints"],
        "immutable_gate_inputs": cpu_contract["immutable_gate_inputs"],
        "zero_cell_evidence": {
            "contract_lf_sha256": cpu_builder_contract_hash,
            "result_lf_sha256": lf_sha256(args.zero_cell_result),
        },
        "formal_gate": cpu_contract["formal_gate_after_contract"],
        "supersedes_preexecution_failure": {
            "github_run_id": failure_attribution["attempt"]["github_run_id"],
            "failed_launch_lf_sha256": failure_attribution["evidence"][
                "failed_launch_lf_sha256"
            ],
            "formal_support_cells_completed": 0,
            "reason": "wrong preregistration object bound to Episode plant design",
        },
        "execution_now": EXPECTED_ZERO_EXECUTION,
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one formal offline 248-cell support gate plus its 64 frozen heldout repeats",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator formal support-gate launch",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Main cells: `124 per checkpoint × 2 = 248`",
                "- Heldout repeat cells: `64`",
                "- Duration: `250 ticks per cell`",
                "- Formal cells executed at freeze time: `0`",
                "- Locomotion / robot access: `0 / 0`",
                "",
                "Both half and final remain mandatory. There is no closest-result",
                "selection. This launch authorizes exactly one offline formal gate and",
                "does not authorize locomotion, deployment, Gate 5, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
