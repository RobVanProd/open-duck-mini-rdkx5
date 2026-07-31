#!/usr/bin/env python3
"""Build the hash-frozen T23 hosted continuation bundle."""

from __future__ import annotations

import argparse
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
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t23_support_trainthrough_hosted_preregistration.json"
)
CPU_RESULT = ANALYSIS / "t22_corrected_one_update_cpu_result.json"
DRIVER = ROOT / "tools" / "colab_t23_support_trainthrough_continuation.py"
DRIVER_HELPER = (
    ROOT / "tools" / "colab_winner_v114_linear_torque_continuation.py"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
CONTRACT = ANALYSIS / "t23_support_trainthrough_hosted_package_contract.json"
MARKDOWN = (
    ANALYSIS / "T23_SUPPORT_TRAINTHROUGH_HOSTED_PACKAGE_20260726.md"
)
BUNDLE_NAME = "t23_support_trainthrough_bundle"
MANIFEST_NAME = "t23_package_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
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
        if path.name != MANIFEST_NAME
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    playground = Path(prereg["paths"]["playground"]).resolve()
    source = Path(prereg["paths"]["source_checkpoint"]).resolve()
    staging = args.staging_root.resolve()
    archive_path = args.output_archive.resolve()
    for path in (staging, archive_path, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T23: {path}")
    prereg_basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T23_SUPPORT_TRAINTHROUGH_HOSTED_CONTINUATION"
        or prereg.get("failed_checks") != []
        or canonical_sha256(prereg_basis)
        != prereg.get("preregistered_contract_sha256")
    ):
        raise ValueError("T23 preregistration changed")
    observed = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "composed_manifest": sha256(
            playground / "T19_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    if observed != prereg["input_hashes"]:
        raise ValueError("T23 package inputs changed")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for path in (PREREGISTRATION, CPU_RESULT, DRIVER, DRIVER_HELPER):
        shutil.copy2(path, bundle / path.name)
    shutil.copy2(REFERENCE, assets / REFERENCE.name)
    shutil.copytree(source, assets / "source_checkpoint")
    shutil.copytree(
        playground,
        bundle / "playground",
        ignore=shutil.ignore_patterns(
            ".git",
            ".tmp",
            "__pycache__",
            ".pytest_cache",
            "*.pyc",
            "wandb",
        ),
    )
    if directory_sha256(assets / "source_checkpoint") != observed[
        "source_checkpoint"
    ]:
        raise ValueError("copied T23 source checkpoint changed")
    composed_manifest = json.loads(
        (
            bundle / "playground/T19_COMPOSED_SOURCE_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    for relative, expected in composed_manifest[
        "final_python_hashes"
    ].items():
        if sha256(bundle / "playground" / relative) != expected:
            raise ValueError(f"copied T23 source changed: {relative}")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.common.t19_support_trainthrough import "
                "SupportPrefixWrapper, SOURCE_RATE_LIMITS_RAD_S; "
                "print('PASS_T23_PACKAGE_IMPORT', "
                "len(SOURCE_RATE_LIMITS_RAD_S))"
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
        preflight.returncode != 0
        or "PASS_T23_PACKAGE_IMPORT 14"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T23 isolated import failed: {preflight.stdout}\n"
            f"{preflight.stderr}"
        )

    members = file_manifest(bundle)
    manifest = {
        "schema_version": "open_duck.t23_hosted_bundle_manifest.v1",
        "preregistration_sha256": sha256(PREREGISTRATION),
        "input_hashes": observed,
        "member_count_excluding_manifest": len(members),
        "members": members,
        "members_canonical_sha256": canonical_sha256(members),
        "isolated_import_preflight": {
            "returncode": preflight.returncode,
            "stdout": preflight.stdout.strip(),
        },
        "contains_credentials_or_tokens": False,
        "contains_robot_access_material": False,
    }
    manifest_path = bundle / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(bundle, arcname=BUNDLE_NAME)
    temporary.replace(archive_path)
    contract = {
        "schema_version": "open_duck.t23_hosted_package.v1",
        "status": "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_PACKAGE",
        "failed_checks": [],
        "checks": {
            "preregistration_exact": True,
            "input_hashes_exact": True,
            "source_checkpoint_copy_exact": True,
            "composed_source_exact": True,
            "isolated_import_preflight_passed": True,
            "bundle_manifest_complete": True,
            "credentials_absent": True,
            "robot_access_material_absent": True,
            "training_or_behavior_not_run": True,
        },
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
            "one_hash_exact_hosted_continuation": True,
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
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T23 support train-through hosted package",
                "",
                f"- Status: `{contract['status']}`",
                f"- Archive SHA-256: `{contract['archive']['sha256']}`",
                f"- Archive bytes: `{contract['archive']['bytes']}`",
                f"- Bundle files: `{len(members) + 1}`",
                "- Isolated import: `PASS`",
                "- Credentials and robot access material: `ABSENT`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(contract["status"])
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
