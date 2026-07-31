#!/usr/bin/env python3
"""Attribute the zero-optimizer Winner-v102 hosted package failure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V102_PREREGISTRATION = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
V102_PACKAGE_CONTRACT = (
    ANALYSIS / "winner_v102_response_conditioned_hosted_package_contract.json"
)
HOLD_RESULT = ANALYSIS / "winner_v102_hosted_hold_result_20260723.json"
HOLD_RECEIPT = (
    ANALYSIS / "winner_v102_hosted_hold_launch_receipt_20260723.json"
)
V96_NETWORK = ROOT / "patches/winner_v96_response_conditioned_networks.py"
V6_NETWORK = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
OUTPUT = ANALYSIS / "winner_v104_hosted_package_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V104_HOSTED_PACKAGE_FAILURE_ATTRIBUTION_20260723.md"

V102_PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
V102_PACKAGE_CONTRACT_SHA256 = (
    "d4218997ab5bc75745c32c3e4b29adda82e5e7846adce82db0e52016c3909ea0"
)
HOLD_RESULT_SHA256 = (
    "c35b9d3ee1d2cee5fb04e2dc5e2bd61a574ab3533594d925ff1f6976d16d327d"
)
HOLD_RECEIPT_SHA256 = (
    "fff8e16ea7da42732d9e38ea357389a9faed84145cb52ed2ad093f22e11fe129"
)
FAILED_PACKAGE_SHA256 = (
    "cbb6dd1ef5c68e013cbc8e0a29bdbb014cff476064f2ac763aedfeeba6b28017"
)
FAILED_PACKAGE_BYTES = 59_176_688
BUNDLE_ROOT = "winner_v102_hosted_bundle"
V96_MEMBER = f"{BUNDLE_ROOT}/winner_v96_response_conditioned_networks.py"
V6_MEMBER = f"{BUNDLE_ROOT}/winner_v6_dynamic_calibration_networks.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failed-package", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite Winner-v104 attribution: {path}"
            )

    failed_package = args.failed_package.resolve()
    preregistration = json.loads(V102_PREREGISTRATION.read_text(encoding="utf-8"))
    package_contract = json.loads(
        V102_PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    result = json.loads(HOLD_RESULT.read_text(encoding="utf-8"))
    receipt = json.loads(HOLD_RECEIPT.read_text(encoding="utf-8"))
    if (
        sha256(V102_PREREGISTRATION) != V102_PREREGISTRATION_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or sha256(V102_PACKAGE_CONTRACT) != V102_PACKAGE_CONTRACT_SHA256
        or package_contract.get("status")
        != "PASS_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_PACKAGE"
        or sha256(HOLD_RESULT) != HOLD_RESULT_SHA256
        or sha256(HOLD_RECEIPT) != HOLD_RECEIPT_SHA256
        or failed_package.stat().st_size != FAILED_PACKAGE_BYTES
        or sha256(failed_package) != FAILED_PACKAGE_SHA256
    ):
        raise ValueError("Winner-v104 attribution inputs changed")

    with tarfile.open(failed_package, "r:gz") as archive:
        members = {member.name.rstrip("/") for member in archive.getmembers()}
    v96_text = V96_NETWORK.read_text(encoding="utf-8")
    if (
        result.get("status")
        != "HOLD_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or result.get("stages") != []
        or result.get("formal_behavior_cells_executed") != 0
        or result.get("error")
        != (
            "ModuleNotFoundError: No module named "
            "'winner_v6_dynamic_calibration_networks'"
        )
        or receipt.get("status") != "HOLD_WINNER_V102_COLAB_LAUNCH"
        or receipt.get("returncode") != 1
        or receipt.get("output_archive_exists") is not False
        or receipt.get("output_json_sha256") != HOLD_RESULT_SHA256
        or V96_MEMBER not in members
        or V6_MEMBER in members
        or "import winner_v6_dynamic_calibration_networks as v6" not in v96_text
        or not V6_NETWORK.is_file()
    ):
        raise ValueError("Winner-v102 failure attribution is not exact")

    value = {
        "schema_version": "winner_v104.hosted_package_failure_attribution.v1",
        "status": "HOLD_WINNER_V104_V102_PACKAGE_IMPORT_CLOSURE",
        "decision": "AUTHORIZE_PACKAGING_CORRECTION_PREREGISTRATION_ONLY",
        "failed_run": {
            "package_bytes": FAILED_PACKAGE_BYTES,
            "package_sha256": FAILED_PACKAGE_SHA256,
            "result_sha256": HOLD_RESULT_SHA256,
            "launch_receipt_sha256": HOLD_RECEIPT_SHA256,
            "l4_session_stopped": True,
            "hosted_processes": 1,
            "stages_started": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "artifact_archive_created": False,
            "robot_or_rdk_access": 0,
        },
        "causal_attribution": {
            "exception": "ModuleNotFoundError",
            "importer": V96_MEMBER,
            "required_module": "winner_v6_dynamic_calibration_networks",
            "required_source_path": V6_NETWORK.relative_to(ROOT).as_posix(),
            "required_source_sha256": sha256(V6_NETWORK),
            "required_archive_member": V6_MEMBER,
            "required_member_present_in_failed_package": False,
            "importer_member_present_in_failed_package": True,
            "policy_or_calibration_math_implicated": False,
            "simulator_or_optimizer_implicated": False,
            "gpu_or_dependency_install_implicated": False,
        },
        "prospective_correction": {
            "add_exact_v6_module_to_bundle": True,
            "add_bundle_import_closure_preflight": True,
            "reuse_exact_v102_training_driver": True,
            "reuse_exact_v102_training_preregistration": True,
            "policy_equations_changed": False,
            "calibrator_equations_changed": False,
            "training_hyperparameters_changed": False,
            "stage_schedule_changed": False,
            "seeds_or_thresholds_changed": False,
            "new_hosted_run_requires_new_preregistration": True,
        },
        "authority": {
            "packaging_correction_preregistration_authorized": True,
            "hosted_retry_authorized_now": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "robot_clearance": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v104 hosted package failure attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        "The single Winner-v102 L4 submission stopped during the first local-module "
        "import. No stage, simulator locomotion step, optimizer step, behavior cell, "
        "or robot/RDK action occurred. The V96 adapter was bundled, but its exact V6 "
        "dependency was not. Only a separately preregistered packaging correction is "
        "authorized; this artifact does not authorize another hosted run.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
