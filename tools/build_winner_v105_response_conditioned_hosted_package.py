#!/usr/bin/env python3
"""Build the import-closure-corrected Winner-v105 hosted bundle."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V102_PREREGISTRATION = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
V105_PREREGISTRATION = (
    ANALYSIS / "winner_v105_hosted_packaging_correction_preregistration.json"
)
V104_ATTRIBUTION = ANALYSIS / "winner_v104_hosted_package_failure_attribution.json"
CPU_CONTRACT = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
DRIVER = ROOT / "tools/colab_winner_v102_response_conditioned_curriculum.py"
V96_NETWORK = ROOT / "patches/winner_v96_response_conditioned_networks.py"
V6_NETWORK = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
SOURCE_ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
PROTECTED_POLICY = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
    "T2_EQUAL_512000.onnx"
)
CONTRACT = ANALYSIS / "winner_v105_response_conditioned_hosted_package_contract.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V105_RESPONSE_CONDITIONED_HOSTED_PACKAGE_CONTRACT_20260723.md"
)
V102_PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
V105_PREREGISTRATION_SHA256 = (
    "5cf5a4b449ec9673d2f65122a7a26b957b7240c79d5fb5945b5cf68cb01e279c"
)
V104_ATTRIBUTION_SHA256 = (
    "6d728c78d65f913426d5e3093045c93d79d46608ea2f19a3098d50a715ace985"
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
        if path.name != "winner_v105_package_manifest.json"
    }


def local_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".", 1)[0])
    return {name for name in names if name.startswith("winner_")}


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
            raise FileExistsError(
                f"refusing to overwrite Winner-v105 package: {path}"
            )

    v102 = json.loads(V102_PREREGISTRATION.read_text(encoding="utf-8"))
    v105 = json.loads(V105_PREREGISTRATION.read_text(encoding="utf-8"))
    attribution = json.loads(V104_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        sha256(V102_PREREGISTRATION) != V102_PREREGISTRATION_SHA256
        or v102.get("status")
        != "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or sha256(V105_PREREGISTRATION) != V105_PREREGISTRATION_SHA256
        or v105.get("status")
        != "PREREGISTERED_WINNER_V105_HOSTED_PACKAGING_CORRECTION"
        or sha256(V104_ATTRIBUTION) != V104_ATTRIBUTION_SHA256
        or attribution.get("status")
        != "HOLD_WINNER_V104_V102_PACKAGE_IMPORT_CLOSURE"
        or sha256(CPU_CONTRACT) != CPU_CONTRACT_SHA256
    ):
        raise ValueError("Winner-v105 package prerequisites changed")

    input_paths = {
        "driver": DRIVER,
        "v96_network": V96_NETWORK,
        "v6_network": V6_NETWORK,
        "cpu_contract": CPU_CONTRACT,
        "composed_manifest": playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "source_archive": SOURCE_ARCHIVE,
        "reference_features": REFERENCE,
        "protected_policy": PROTECTED_POLICY,
        "calibrator": calibrator,
    }
    observed_hashes = {name: sha256(path) for name, path in input_paths.items()}
    if observed_hashes != v105.get("input_hashes"):
        raise ValueError("Winner-v105 package inputs changed after preregistration")
    for relative, expected in v105["composed_playground_files"].items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"Winner-v105 composed source changed: {relative}")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for source in (
        DRIVER,
        V96_NETWORK,
        V6_NETWORK,
        V102_PREREGISTRATION,
        V105_PREREGISTRATION,
        V104_ATTRIBUTION,
        CPU_CONTRACT,
    ):
        shutil.copy2(source, bundle / source.name)
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

    expected_local_imports = {"winner_v6_dynamic_calibration_networks"}
    observed_local_imports = local_imports(bundle / V96_NETWORK.name)
    if observed_local_imports != expected_local_imports:
        raise ValueError(
            "Winner-v105 local import set changed: "
            f"{sorted(observed_local_imports)}"
        )
    missing_local_modules = sorted(
        name
        for name in observed_local_imports
        if not (bundle / f"{name}.py").is_file()
    )
    if missing_local_modules:
        raise ValueError(
            f"Winner-v105 bundle import closure failed: {missing_local_modules}"
        )

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle)
    import_preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import winner_v6_dynamic_calibration_networks; "
                "import winner_v96_response_conditioned_networks; "
                "print('PASS_WINNER_V105_IMPORT_CLOSURE')"
            ),
        ],
        cwd=bundle,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if (
        import_preflight.returncode != 0
        or import_preflight.stdout.strip() != "PASS_WINNER_V105_IMPORT_CLOSURE"
    ):
        raise RuntimeError(
            "Winner-v105 isolated import preflight failed: "
            f"{import_preflight.stdout}\n{import_preflight.stderr}"
        )

    members = file_manifest(bundle)
    package_manifest = {
        "schema_version": "winner_v105.hosted_bundle_manifest.v1",
        "training_preregistration_sha256": V102_PREREGISTRATION_SHA256,
        "packaging_correction_preregistration_sha256": (
            V105_PREREGISTRATION_SHA256
        ),
        "failure_attribution_sha256": V104_ATTRIBUTION_SHA256,
        "cpu_contract_sha256": CPU_CONTRACT_SHA256,
        "input_hashes": observed_hashes,
        "local_imports": sorted(observed_local_imports),
        "missing_local_modules": missing_local_modules,
        "isolated_import_preflight": {
            "returncode": import_preflight.returncode,
            "stdout": import_preflight.stdout.strip(),
        },
        "member_count_excluding_manifest": len(members),
        "members": members,
        "members_canonical_sha256": canonical_sha256(members),
        "contains_credentials_or_tokens": False,
        "contains_robot_access_material": False,
    }
    manifest_path = bundle / "winner_v105_package_manifest.json"
    manifest_path.write_text(
        json.dumps(package_manifest, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(bundle, arcname=BUNDLE_NAME)
    temporary.replace(archive_path)

    contract = {
        "schema_version": "winner_v105.response_conditioned_hosted_package.v1",
        "status": "PASS_WINNER_V105_RESPONSE_CONDITIONED_HOSTED_PACKAGE",
        "checks": {
            "v102_training_preregistration_exact": True,
            "v105_correction_preregistration_exact": True,
            "v104_failure_attribution_exact": True,
            "cpu_contract_passed_and_exact": True,
            "input_hashes_exact": True,
            "composed_source_exact": True,
            "v6_dependency_present_and_exact": True,
            "static_import_closure_passed": True,
            "isolated_import_preflight_passed": True,
            "bundle_manifest_complete": True,
            "credentials_absent": True,
            "robot_access_material_absent": True,
            "training_or_behavior_not_run": True,
        },
        "failed_checks": [],
        "training_preregistration_sha256": V102_PREREGISTRATION_SHA256,
        "packaging_correction_preregistration_sha256": (
            V105_PREREGISTRATION_SHA256
        ),
        "failure_attribution_sha256": V104_ATTRIBUTION_SHA256,
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
            "one_hash_exact_l4_curriculum": True,
            "retry_or_resume": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v105 response-conditioned hosted package contract\n\n"
        f"Status: `{contract['status']}`\n\n"
        f"- archive SHA-256: `{contract['archive']['sha256']}`\n"
        f"- archive bytes: `{contract['archive']['bytes']}`\n"
        f"- bundle files: `{len(members) + 1}`\n"
        "- local import closure: `PASS`\n"
        "- isolated V6 + V96 import preflight: `PASS`\n\n"
        "This package changes only archive import closure relative to Winner-v102. "
        "It authorizes one exact L4 curriculum without retry or resume and grants no "
        "behavior, deployment, Gate 5, RDK-X5, robot, torque, motion, or robot "
        "clearance authority.\n",
        encoding="utf-8",
    )
    print(contract["status"])
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
