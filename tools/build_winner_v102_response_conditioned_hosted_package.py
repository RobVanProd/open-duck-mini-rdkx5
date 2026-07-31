#!/usr/bin/env python3
"""Build and hash-freeze the Winner-v102 hosted-training bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
CPU_CONTRACT = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
DRIVER = ROOT / "tools/colab_winner_v102_response_conditioned_curriculum.py"
V96_NETWORK = ROOT / "patches/winner_v96_response_conditioned_networks.py"
SOURCE_ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
PROTECTED_POLICY = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
    "T2_EQUAL_512000.onnx"
)
CONTRACT = ANALYSIS / "winner_v102_response_conditioned_hosted_package_contract.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V102_RESPONSE_CONDITIONED_HOSTED_PACKAGE_CONTRACT_20260722.md"
)
PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
CPU_CONTRACT_SHA256 = (
    "4f44c2ff9de0ee715b09c1c95048bedb0a43f3334eaa70970dac8c08d6e047d0"
)
BUNDLE_NAME = "winner_v102_hosted_bundle"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_manifest(root: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(item for item in root.rglob("*") if item.is_file())
        if path.name != "winner_v102_package_manifest.json"
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    calibrator = args.calibrator.resolve()
    staging = args.staging_root.resolve()
    archive_path = args.output_archive.resolve()
    for path in (staging, archive_path, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v102 package: {path}")

    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    cpu_contract = json.loads(CPU_CONTRACT.read_text(encoding="utf-8"))
    if (
        sha256(PREREGISTRATION) != PREREGISTRATION_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or prereg.get("decision")
        != "AUTHORIZE_ONE_HASH_FROZEN_GPU_CURRICULUM_WITHOUT_RETRY"
        or sha256(CPU_CONTRACT) != CPU_CONTRACT_SHA256
        or cpu_contract.get("status")
        != "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT"
    ):
        raise ValueError("Winner-v102 package prerequisites changed")

    input_paths = {
        "driver": DRIVER,
        "v96_network": V96_NETWORK,
        "cpu_contract": CPU_CONTRACT,
        "composed_manifest": playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "source_archive": SOURCE_ARCHIVE,
        "reference_features": REFERENCE,
        "protected_policy": PROTECTED_POLICY,
        "calibrator": calibrator,
    }
    observed_hashes = {name: sha256(path) for name, path in input_paths.items()}
    if observed_hashes != prereg.get("input_hashes"):
        raise ValueError("Winner-v102 package inputs changed after preregistration")
    for relative, expected in prereg["composed_playground_files"].items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"Winner-v102 composed source changed: {relative}")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    shutil.copy2(DRIVER, bundle / DRIVER.name)
    shutil.copy2(V96_NETWORK, bundle / V96_NETWORK.name)
    shutil.copy2(PREREGISTRATION, bundle / PREREGISTRATION.name)
    shutil.copy2(CPU_CONTRACT, bundle / CPU_CONTRACT.name)
    shutil.copy2(SOURCE_ARCHIVE, assets / SOURCE_ARCHIVE.name)
    shutil.copy2(REFERENCE, assets / REFERENCE.name)
    shutil.copy2(PROTECTED_POLICY, assets / PROTECTED_POLICY.name)
    shutil.copy2(calibrator, assets / "winner_v22_final.onnx")
    shutil.copytree(
        playground,
        bundle / "playground",
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            ".pytest_cache",
            "*.pyc",
            "wandb",
        ),
    )

    members = file_manifest(bundle)
    package_manifest = {
        "schema_version": "winner_v102.hosted_bundle_manifest.v1",
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_contract_sha256": CPU_CONTRACT_SHA256,
        "input_hashes": observed_hashes,
        "member_count_excluding_manifest": len(members),
        "members": members,
        "members_canonical_sha256": canonical_sha256(members),
        "contains_credentials_or_tokens": False,
        "contains_robot_access_material": False,
    }
    manifest_path = bundle / "winner_v102_package_manifest.json"
    manifest_path.write_text(
        json.dumps(package_manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(bundle, arcname=BUNDLE_NAME)
    temporary.replace(archive_path)

    contract = {
        "schema_version": "winner_v102.response_conditioned_hosted_package.v1",
        "status": "PASS_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_PACKAGE",
        "checks": {
            "preregistration_exact": True,
            "cpu_contract_passed_and_exact": True,
            "input_hashes_exact": True,
            "composed_source_exact": True,
            "bundle_manifest_complete": True,
            "credentials_absent": True,
            "robot_access_material_absent": True,
            "training_or_behavior_not_run": True,
        },
        "failed_checks": [],
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "archive": {
            "path": str(archive_path),
            "bytes": archive_path.stat().st_size,
            "sha256": sha256(archive_path),
        },
        "bundle_manifest": {
            "sha256": sha256(manifest_path),
            "member_count_excluding_manifest": len(members),
            "members_canonical_sha256": canonical_sha256(members),
        },
        "execution": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hash_exact_hosted_gpu_curriculum": True,
            "retry_or_resume": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v102 response-conditioned hosted package contract\n\n"
        f"Status: `{contract['status']}`\n\n"
        f"- archive SHA-256: `{contract['archive']['sha256']}`\n"
        f"- archive bytes: `{contract['archive']['bytes']}`\n"
        f"- bundle files: `{len(members) + 1}`\n\n"
        "This contract authorizes one hash-exact GPU curriculum without retry. It "
        "does not authorize behavior evaluation, checkpoint selection, deployment, "
        "Gate 5, RDK-X5 access, robot access, torque, motion, or robot clearance.\n",
        encoding="utf-8",
    )
    print(contract["status"])
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
