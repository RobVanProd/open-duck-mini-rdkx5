#!/usr/bin/env python3
"""Build the hash-frozen V175 hosted continuation bundle."""

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
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v175_hosted_preregistration.json"
V173_PREREG = (
    ANALYSIS
    / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
)
V173_RESULT = ANALYSIS / "winner_v173_lexicographic_tangent_cpu_result.json"
V174_RESULT = ANALYSIS / "winner_v174_tangent_nominal_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v175_tangent_continuation.py"
CONTRACT = ANALYSIS / "winner_v175_hosted_package_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V175_HOSTED_PACKAGE_CONTRACT_20260725.md"
BUNDLE_NAME = "winner_v175_tangent_bundle"
MANIFEST_NAME = "winner_v175_package_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
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
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    staging = args.staging_root.resolve()
    archive_path = args.output_archive.resolve()
    for path in (staging, archive_path, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V175: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V175_HOSTED_CONTINUATION"
        or prereg.get("failed_checks") != []
        or prereg.get("authority", {}).get(
            "one_hosted_gpu_continuation_after_package_contract"
        )
        is not True
    ):
        raise ValueError("V175 hosted preregistration is not green")
    observed = {
        "driver": sha256(DRIVER),
        "v173_cpu_preregistration": sha256(V173_PREREG),
        "v173_cpu_result": sha256(V173_RESULT),
        "v174_nominal_result": sha256(V174_RESULT),
        "composed_manifest": sha256(
            playground / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    if observed != prereg["input_hashes"]:
        raise ValueError("V175 package inputs changed")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for path in (PREREG, V173_PREREG, V173_RESULT, V174_RESULT, DRIVER):
        shutil.copy2(path, bundle / path.name)
    shutil.copy2(REFERENCE, assets / REFERENCE.name)
    shutil.copytree(source, assets / "source_checkpoint")
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
    if directory_sha256(assets / "source_checkpoint") != observed[
        "source_checkpoint"
    ]:
        raise ValueError("copied V175 source checkpoint changed")
    composed_manifest = json.loads(
        (
            bundle / "playground/WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    for relative, expected in composed_manifest[
        "final_python_hashes"
    ].items():
        if sha256(bundle / "playground" / relative) != expected:
            raise ValueError(f"copied V175 source changed: {relative}")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.open_duck_mini_v2.joystick import "
                "winner_v127_dense_torque_exceedance_cost; "
                "from playground.common import "
                "winner_v127_constrained_ppo_train, "
                "winner_v173_lexicographic_tangent; "
                "print('PASS_WINNER_V175_PACKAGE_IMPORT')"
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
        or "PASS_WINNER_V175_PACKAGE_IMPORT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"V175 isolated import failed: {preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    members = file_manifest(bundle)
    manifest = {
        "schema_version": "winner_v175.hosted_bundle_manifest.v1",
        "preregistration_sha256": sha256(PREREG),
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
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(bundle, arcname=BUNDLE_NAME)
    temporary.replace(archive_path)
    contract = {
        "schema_version": "winner_v175.hosted_package.v1",
        "status": "PASS_WINNER_V175_HOSTED_PACKAGE",
        "failed_checks": [],
        "checks": {
            "preregistration_green": True,
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
        "authority": {
            "one_hash_exact_hosted_continuation": True,
            "retry_or_resume": False,
            "behavior_evaluation": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V175 hosted package\n\n"
        f"- Status: `{contract['status']}`\n"
        f"- Archive bytes: `{contract['archive']['bytes']}`\n"
        f"- Archive SHA-256: `{contract['archive']['sha256']}`\n"
        "- Credentials and robot access material: absent.\n"
        "- Authority: one no-retry hosted continuation only.\n",
        encoding="utf-8",
    )
    print(contract["status"])
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
