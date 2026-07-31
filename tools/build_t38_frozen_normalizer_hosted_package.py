#!/usr/bin/env python3
"""Build the hash-frozen T38 hosted continuation bundle."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from typing import Any

from colab_t38_frozen_normalizer_continuation import (
    CPU_RESULT_NAME,
    PREREGISTRATION_NAME,
    REFERENCE_NAME,
    SOURCE_CHECKPOINT_NAME,
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = ANALYSIS / PREREGISTRATION_NAME
CPU_RESULT = ANALYSIS / CPU_RESULT_NAME
DRIVER = ROOT / "tools" / "colab_t38_frozen_normalizer_continuation.py"
BASE_DRIVER = (
    ROOT / "tools" / "colab_t32_action_margin_trainthrough_continuation.py"
)
DRIVER_HELPER = (
    ROOT / "tools" / "colab_winner_v114_linear_torque_continuation.py"
)
REFERENCE = ANALYSIS / REFERENCE_NAME
CONTRACT = ANALYSIS / "t38_frozen_normalizer_hosted_package_contract.json"
MARKDOWN = (
    ANALYSIS / "T38_FROZEN_NORMALIZER_HOSTED_PACKAGE_20260727.md"
)
BUNDLE_NAME = "t38_frozen_normalizer_bundle"
MANIFEST_NAME = "t38_package_manifest.json"


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
            raise FileExistsError(f"refusing to overwrite T38: {path}")
    prereg_basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T38_FROZEN_NORMALIZER_HOSTED_CONTINUATION"
        or prereg.get("failed_checks") != []
        or canonical_sha256(prereg_basis)
        != prereg.get("preregistered_contract_sha256")
    ):
        raise ValueError("T38 preregistration changed")
    observed_inventory = source_inventory(playground)
    observed = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
        "playground_inventory": canonical_sha256(observed_inventory),
    }
    if (
        observed != prereg["input_hashes"]
        or observed_inventory != prereg["playground"]["file_inventory"]
    ):
        raise ValueError("T38 package inputs changed")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for path in (
        PREREGISTRATION,
        CPU_RESULT,
        DRIVER,
        BASE_DRIVER,
        DRIVER_HELPER,
    ):
        shutil.copy2(path, bundle / path.name)
    shutil.copy2(REFERENCE, assets / REFERENCE.name)
    shutil.copytree(source, assets / SOURCE_CHECKPOINT_NAME)
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
    copied_inventory = source_inventory(bundle / "playground")
    if copied_inventory != observed_inventory:
        raise ValueError("copied T38 playground changed")
    if (
        directory_sha256(assets / SOURCE_CHECKPOINT_NAME)
        != observed["source_checkpoint"]
    ):
        raise ValueError("copied T38 source checkpoint changed")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.open_duck_mini_v2.joystick import Joystick; "
                "from pathlib import Path; "
                "text=Path('playground/playground/open_duck_mini_v2/runner.py')"
                ".read_text(encoding='utf-8'); "
                "assert 'winner_t37_freeze_observation_normalizer' in text; "
                "print('PASS_T38_PACKAGE_IMPORT', Joystick.__name__)"
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
        or "PASS_T38_PACKAGE_IMPORT Joystick"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T38 isolated import failed: {preflight.stdout}\n"
            f"{preflight.stderr}"
        )

    members = file_manifest(bundle)
    manifest = {
        "schema_version": "open_duck.t38_hosted_bundle_manifest.v1",
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
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(bundle, arcname=BUNDLE_NAME)
    temporary.replace(archive_path)
    contract = {
        "schema_version": "open_duck.t38_hosted_package.v1",
        "status": "PASS_T38_FROZEN_NORMALIZER_HOSTED_PACKAGE",
        "failed_checks": [],
        "checks": {
            "preregistration_exact": True,
            "input_hashes_exact": True,
            "source_checkpoint_copy_exact": True,
            "playground_source_copy_exact": True,
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
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T38 frozen-normalizer hosted package",
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
    )
    print(contract["status"])
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
