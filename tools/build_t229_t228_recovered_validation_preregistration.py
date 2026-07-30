#!/usr/bin/env python3
"""Freeze T229's read-only validation of recovered T228 artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


RECOVERY = Path(
    "D:/CodexArtifacts/open-duck-policy/t228_colab_recovery_20260730"
)
EXTRACTED = (
    RECOVERY / "extracted" / "t228_command_atom_continuation"
)
PREREG_T228 = ANALYSIS / "t228_command_atom_hosted_preregistration.json"
CPU_T227D = ANALYSIS / "t227d_recovered_cpu_validation_result.json"
CPU_T227D_PREREG = (
    ANALYSIS / "t227d_recovered_cpu_validation_preregistration.json"
)
PACKAGE = ANALYSIS / "t228_command_atom_hosted_package_contract.json"
LAUNCH = ANALYSIS / "t228_colab_cli_launch_contract.json"
OUTPUT = (
    ANALYSIS / "t229_t228_recovered_training_validation_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T229_T228_RECOVERED_TRAINING_VALIDATION_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/validate_t228_recovered_training.py"
BASE_VALIDATOR = ROOT / "tools/validate_t216_recovered_training.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T229 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T229 preregistration requires clean worktree")
    prereg = json.loads(PREREG_T228.read_text(encoding="utf-8"))
    cpu = json.loads(CPU_T227D.read_text(encoding="utf-8"))
    cpu_prereg = json.loads(
        CPU_T227D_PREREG.read_text(encoding="utf-8")
    )
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    launch = json.loads(LAUNCH.read_text(encoding="utf-8"))
    hosted_path = RECOVERY / "t228_result.json"
    archive_path = RECOVERY / "t228_artifacts.tar.gz"
    receipt_path = RECOVERY / "t228_launch_receipt.json"
    hosted = json.loads(hosted_path.read_text(encoding="utf-8"))
    launch_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    source = Path(prereg["paths"]["source_checkpoint"])
    source_raw = Path(prereg["paths"]["expected_step_zero_raw"])
    policy_template = Path(
        cpu_prereg["frozen_artifacts"]["cpu_source_remap"]["path"]
    )
    cost_template = Path(
        cpu["training"]["cost_checkpoints"]["0"]["path"]
    )
    checks = {
        "t228_hosted_result_green_pending_cpu_validation": (
            hosted["status"]
            == "PASS_T228_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and all(hosted["checks"].values())
            and hosted["formal_behavior_cells_executed"] == 0
        ),
        "launch_receipt_complete": (
            launch_receipt["status"] == "COMPLETED_T228_COLAB_LAUNCH"
            and launch_receipt["returncode"] == 0
            and launch_receipt["retry"] is False
            and launch_receipt["same_run_resume"] is False
            and launch_receipt["robot_or_rdk_access"] is False
        ),
        "result_and_archive_hashes_match_receipt": (
            receipt(hosted_path)["sha256"]
            == launch_receipt["output_json_sha256"]
            and receipt(archive_path)["sha256"]
            == launch_receipt["output_archive_sha256"]
            == hosted["artifact"]["sha256"]
            and archive_path.stat().st_size == hosted["artifact"]["bytes"]
        ),
        "t227d_authority_green": (
            cpu["status"] == "PASS_T227D_RECOVERED_CPU_VALIDATION"
            and cpu["failed_checks"] == []
            and cpu["decision"]
            == (
                "EARN_T228_COMMAND_ATOM_HOSTED_CONTINUATION_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "package_and_launch_contracts_green": (
            package["status"] == "PASS_T228_COMMAND_ATOM_HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and launch["status"] == "PASS_T228_COLAB_CLI_LAUNCH_CONTRACT"
            and launch["failed_checks"] == []
        ),
        "all_local_artifacts_present": all(
            path.exists()
            for path in (
                EXTRACTED,
                hosted_path,
                archive_path,
                receipt_path,
                source,
                source_raw,
                policy_template,
                cost_template,
                RUNNER,
                BASE_VALIDATOR,
            )
        ),
        "float32_backend_tolerance_derived": (
            float(np.finfo(np.float32).eps)
            == 1.1920928955078125e-7
        ),
        "no_optimizer_simulator_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T229 preregistration checks failed: {failed}")
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "base_validator": receipt(BASE_VALIDATOR),
        "t228_preregistration": receipt(PREREG_T228),
        "t227d_cpu_result": receipt(CPU_T227D),
        "t227d_cpu_preregistration": receipt(CPU_T227D_PREREG),
        "package_contract": receipt(PACKAGE),
        "launch_contract": receipt(LAUNCH),
        "hosted_result": receipt(hosted_path),
        "launch_receipt": receipt(receipt_path),
        "recovery_archive": receipt(archive_path),
        "extracted_work": receipt(EXTRACTED),
        "source_checkpoint": receipt(source),
        "source_raw_onnx": receipt(source_raw),
        "policy_cpu_template": receipt(policy_template),
        "cost_cpu_template": receipt(cost_template),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t229_t228_recovered_training_validation_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T229_T228_RECOVERED_TRAINING_VALIDATION"
        ),
        "question": (
            "Do the recovered T228 exports exactly match the frozen source, "
            "update only the authorized head and critics, preserve the ABI, "
            "and carry a finite derived dual before any behavior evaluation?"
        ),
        "frozen_inputs": frozen,
        "expected": {
            "steps": [0, 1_003_520, 2_007_040],
            "source_checkpoint_sha256": (
                "d0e969cab98cbb8cf779792935c58058019c07d41a5e7ae008"
                "7136830ef21c0c"
            ),
            "source_raw_onnx_sha256": (
                "2dd89adfc487da6ad41008bb2094b3e8d24c2fdff4ba233459"
                "df36879e2aa770"
            ),
            "trainable_actor_group": "negative_adapter_location",
            "command_atom_readback": (
                "T227_COMMAND_ATOM_BANK=configuration_strata=8,"
                "command_strata=4,"
                "command_groups=broad|0.074|0.077|0.080,"
                "cartesian_repetitions=8,reward=unchanged,"
                "cost=unchanged,policy_abi=unchanged,"
                "deployment_graph=unchanged"
            ),
            "step_zero_cost_backend_absolute_tolerance": float(
                np.finfo(np.float32).eps
            ),
            "cost_tolerance_derivation": "numpy.finfo(float32).eps",
            "both_exports_required": True,
            "checkpoint_selection": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "checkpoint_restores": 0,
            "onnx_inferences": 0,
            "optimizer_steps": 0,
            "simulator_transitions": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_cpu_validation": True,
            "composition_preregistration": False,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T229 T228 recovered-training validation preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Scope: read-only CPU validation of all three recovered exports\n"
        "- Cost step-0 tolerance: one float32 machine epsilon\n"
        "- Behavior / hosted / robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
