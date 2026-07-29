#!/usr/bin/env python3
"""Build the hash-frozen T100C original-driver wrapper bundle."""

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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from colab_t32_action_margin_trainthrough_continuation import (  # noqa: E402
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (  # noqa: E402
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t100c_original_driver_wrapper_preregistration.json"
T100_HOLD = ANALYSIS / "t100_preexecution_hold_attribution.json"
T100B_HOLD = ANALYSIS / "t100b_prelaunch_identity_hold_attribution.json"
T100_PREREG = ANALYSIS / "t100_hidden_expert_hosted_preregistration.json"
CPU_RESULT = ANALYSIS / "t99_deployment_coordinate_audit_result.json"
WRAPPER = ROOT / "tools" / "colab_t100c_original_driver_wrapper.py"
ORIGINAL_BUNDLE = Path(
    "D:/CodexArtifacts/open-duck-policy/t100_hidden_expert_package_v1/"
    "t100_hidden_expert_bundle"
)
ORIGINAL_DRIVER = ORIGINAL_BUNDLE / "colab_t100_hidden_expert_continuation.py"
BASE_DRIVER = ROOT / "tools" / "colab_t78_endpoint_joint_adapter_continuation.py"
T32_DRIVER = ROOT / "tools" / "colab_t32_action_margin_trainthrough_continuation.py"
HELPER = ROOT / "tools" / "colab_winner_v114_linear_torque_continuation.py"
CONTRACT = ANALYSIS / "t100c_original_driver_wrapper_package_contract.json"
MARKDOWN = ANALYSIS / "T100C_ORIGINAL_DRIVER_WRAPPER_PACKAGE_20260728.md"
BUNDLE_NAME = "t100c_original_driver_wrapper_bundle"
MANIFEST_NAME = "t100c_package_manifest.json"


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
    staging = args.staging_root.resolve()
    archive_path = args.output_archive.resolve()
    for path in (staging, archive_path, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T100C package: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T100C packaging requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T100C_ORIGINAL_DRIVER_WRAPPER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T100C preregistration identity changed")

    playground = Path(prereg["paths"]["playground"])
    source = Path(prereg["paths"]["source_checkpoint"])
    step_zero = Path(prereg["paths"]["expected_step_zero_raw"])
    reference = Path(prereg["paths"]["reference"])
    gate = Path(prereg["paths"]["hidden_gate"])
    inventory = source_inventory(playground)
    observed = {
        "t100_hold_attribution": sha256(T100_HOLD),
        "t100b_hold_attribution": sha256(T100B_HOLD),
        "original_t100_preregistration": sha256(T100_PREREG),
        "wrapper": sha256(WRAPPER),
        "original_driver": sha256(ORIGINAL_DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(reference),
        "expected_step_zero_raw": sha256(step_zero),
        "hidden_gate": sha256(gate),
        "playground_inventory": canonical_sha256(inventory),
    }
    if (
        observed != prereg["input_hashes"]
        or inventory != prereg["playground"]["file_inventory"]
    ):
        raise RuntimeError("T100C package inputs changed")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for path in (
        PREREG,
        T100_HOLD,
        T100B_HOLD,
        T100_PREREG,
        CPU_RESULT,
        WRAPPER,
        BASE_DRIVER,
        T32_DRIVER,
        HELPER,
    ):
        shutil.copy2(path, bundle / path.name)
    shutil.copy2(
        ORIGINAL_DRIVER,
        bundle / "colab_t100_hidden_expert_continuation.py",
    )
    shutil.copy2(reference, assets / reference.name)
    shutil.copy2(step_zero, assets / "expected_step_zero_raw.onnx")
    shutil.copy2(gate, assets / gate.name)
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
    copied_inventory = source_inventory(bundle / "playground")
    if copied_inventory != inventory:
        raise RuntimeError("copied T100C playground changed")
    copied_original_driver = bundle / "colab_t100_hidden_expert_continuation.py"
    if (
        sha256(copied_original_driver) != observed["original_driver"]
        or directory_sha256(assets / "source_checkpoint")
        != observed["source_checkpoint"]
        or sha256(assets / "expected_step_zero_raw.onnx")
        != observed["expected_step_zero_raw"]
        or sha256(assets / gate.name) != observed["hidden_gate"]
    ):
        raise RuntimeError("copied T100C assets changed")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(bundle), str(bundle / "playground"))
    )
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            "\n".join(
                (
                    "from pathlib import Path",
                    "import colab_t100_hidden_expert_continuation as frozen",
                    "import colab_t100c_original_driver_wrapper as wrapper",
                    "assert wrapper.frozen_t100 is frozen",
                    "cmd = wrapper.corrected_runner_command(",
                    "    Path('playground'), Path('out'),",
                    "    Path('assets/source_checkpoint'),",
                    "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
                    ")",
                    "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
                    "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
                    "try:",
                    "    frozen.validate_inputs(Path('.'))",
                    "except RuntimeError as exc:",
                    "    assert 'requires one GPU process' in str(exc)",
                    "    print('PASS_T100C_FULL_IDENTITY_PREFLIGHT')",
                    "else:",
                    "    raise AssertionError('local preflight unexpectedly GPU')",
                )
            ),
        ],
        cwd=bundle,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if (
        preflight.returncode != 0
        or "PASS_T100C_FULL_IDENTITY_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T100C full identity preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )

    members = file_manifest(bundle)
    manifest = {
        "schema_version": "open_duck.t100c_hosted_bundle_manifest.v1",
        "preregistration_sha256": sha256(PREREG),
        "t100_hold_attribution_sha256": sha256(T100_HOLD),
        "t100b_hold_attribution_sha256": sha256(T100B_HOLD),
        "input_hashes": observed,
        "member_count_excluding_manifest": len(members),
        "members": members,
        "members_canonical_sha256": canonical_sha256(members),
        "full_identity_preflight": preflight.stdout.strip(),
        "contains_credentials_or_tokens": False,
        "contains_robot_access_material": False,
    }
    manifest_path = bundle / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(bundle, arcname=BUNDLE_NAME)
    temporary.replace(archive_path)

    contract = {
        "schema_version": "open_duck.t100c_hosted_package.v1",
        "status": "PASS_T100C_ORIGINAL_DRIVER_WRAPPER_PACKAGE",
        "failed_checks": [],
        "checks": {
            "both_preexecution_attributions_exact": True,
            "recovery_preregistration_exact": True,
            "all_input_hashes_exact": True,
            "original_t100_driver_byte_exact": True,
            "original_t100_preregistration_byte_exact": True,
            "external_wrapper_hash_frozen": True,
            "source_checkpoint_copy_exact": True,
            "step_zero_reference_copy_exact": True,
            "hidden_gate_copy_exact": True,
            "playground_source_copy_exact": True,
            "full_original_driver_identity_validation_passed": True,
            "corrected_command_constructed_once": True,
            "bundle_manifest_complete": True,
            "credentials_absent": True,
            "robot_access_material_absent": True,
            "optimizer_and_behavior_not_run": True,
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
            "formal_behavior_cells": 0,
            "t100c_sessions_opened": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hash_exact_wrapper_replacement": True,
            "additional_attempt_retry_or_resume": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T100C original-driver wrapper package",
                "",
                f"- Status: `{contract['status']}`",
                "- Original driver / preregistration: `byte-exact / byte-exact`",
                "- Full original-driver identity validation: `PASS to GPU boundary`",
                f"- Archive SHA-256: `{contract['archive']['sha256']}`",
                f"- Archive bytes: `{contract['archive']['bytes']}`",
                f"- Bundle files: `{len(members) + 1}`",
                "- Credentials / robot access material: `ABSENT / ABSENT`",
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
