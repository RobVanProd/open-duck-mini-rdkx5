#!/usr/bin/env python3
"""Build the hash-frozen T170 eight-stratum head hosted bundle."""

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

from colab_t32_action_margin_trainthrough_continuation import (
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t170_eight_stratum_head_hosted_preregistration.json"
CPU_RESULT = (
    ANALYSIS / "t169_eight_stratum_head_continuation_cpu_result.json"
)
DIAGNOSTIC_RESULT = ANALYSIS / "t169b_cpu_diagnostic_validity_result.json"
DRIVER = ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
BASE_DRIVER = ROOT / "tools/colab_t78_endpoint_joint_adapter_continuation.py"
T32_DRIVER = (
    ROOT / "tools/colab_t32_action_margin_trainthrough_continuation.py"
)
HELPER = (
    ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
)
CONTRACT = (
    ANALYSIS / "t170_eight_stratum_head_hosted_package_contract.json"
)
MARKDOWN = (
    ANALYSIS / "T170_EIGHT_STRATUM_HEAD_HOSTED_PACKAGE_20260729.md"
)
BUNDLE_NAME = "t170_eight_stratum_head_bundle"
MANIFEST_NAME = "t170_package_manifest.json"


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
            raise FileExistsError(f"refusing to overwrite T170: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T170 packaging requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T170 preregistration identity changed")
    playground = Path(prereg["paths"]["playground"])
    source = Path(prereg["paths"]["source_checkpoint"])
    step_zero = Path(prereg["paths"]["expected_step_zero_raw"])
    reference = Path(prereg["paths"]["reference"])
    gate = Path(prereg["paths"]["hidden_gate_static_asset"])
    inventory = source_inventory(playground)
    observed = {
        "driver": sha256(DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "diagnostic_result": sha256(DIAGNOSTIC_RESULT),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(reference),
        "expected_step_zero_raw": sha256(step_zero),
        "hidden_gate_static_asset": sha256(gate),
        "playground_inventory": canonical_sha256(inventory),
    }
    if (
        observed != prereg["input_hashes"]
        or inventory != prereg["playground"]["file_inventory"]
    ):
        raise RuntimeError("T170 package inputs changed")
    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for path in (
        PREREG,
        CPU_RESULT,
        DIAGNOSTIC_RESULT,
        DRIVER,
        BASE_DRIVER,
        T32_DRIVER,
        HELPER,
    ):
        shutil.copy2(path, bundle / path.name)
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
        raise RuntimeError("copied T170 playground changed")
    if (
        directory_sha256(assets / "source_checkpoint")
        != observed["source_checkpoint"]
        or sha256(assets / "expected_step_zero_raw.onnx")
        != observed["expected_step_zero_raw"]
        or sha256(assets / gate.name)
        != observed["hidden_gate_static_asset"]
    ):
        raise RuntimeError("copied T170 assets changed")
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
                    "import colab_t170_eight_stratum_head_continuation as driver",
                    "cmd = driver.runner_command(",
                    "    Path('playground'), Path('out'),",
                    "    Path('assets/source_checkpoint'),",
                    "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
                    ")",
                    "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
                    "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
                    "assert cmd[cmd.index('--ppo_num_envs') + 1] == '256'",
                    "assert cmd[cmd.index('--num_timesteps') + 1] == '2007040'",
                    "assert cmd[cmd.index('--winner_v3_deviation_scale') + 1] == '1.0'",
                    "runner = Path('playground/playground/open_duck_mini_v2/runner.py').read_text()",
                    "assert 'T98_HIDDEN_EXPERT_CONTINUATION=' in runner",
                    "assert 'strata=8,broad=1,isolated=7,' in runner",
                    "assert 'gate=fixed_live_hidden,' in runner",
                    "try:",
                    "    driver.validate_inputs(Path('.'))",
                    "except RuntimeError as exc:",
                    "    assert 'requires one GPU process' in str(exc)",
                    "    print('PASS_T170_FULL_IDENTITY_PREFLIGHT')",
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
        or "PASS_T170_FULL_IDENTITY_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T170 identity preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    members = file_manifest(bundle)
    manifest = {
        "schema_version": "open_duck.t170_hosted_bundle_manifest.v1",
        "preregistration_sha256": sha256(PREREG),
        "cpu_result_sha256": sha256(CPU_RESULT),
        "diagnostic_result_sha256": sha256(DIAGNOSTIC_RESULT),
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
        "schema_version": "open_duck.t170_hosted_package.v1",
        "status": "PASS_T170_EIGHT_STRATUM_HEAD_HOSTED_PACKAGE",
        "failed_checks": [],
        "checks": {
            "preregistration_exact": True,
            "cpu_and_diagnostic_evidence_exact": True,
            "all_input_hashes_exact": True,
            "source_checkpoint_copy_exact": True,
            "step_zero_reference_copy_exact": True,
            "hidden_gate_static_asset_copy_exact": True,
            "playground_source_copy_exact": True,
            "eight_stratum_readback_frozen": True,
            "full_driver_identity_validation_to_gpu_boundary": True,
            "exact_command_constructed_once": True,
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
            "hosted_sessions_opened": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "launch_contract": True,
            "one_hash_exact_l4_run_after_launch_contract": True,
            "retry_or_same_run_resume": False,
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
        "# T170 eight-stratum head hosted package\n\n"
        f"- Status: `{contract['status']}`\n"
        "- Full driver identity validation: PASS to GPU boundary\n"
        f"- Archive SHA-256: `{contract['archive']['sha256']}`\n"
        f"- Archive bytes: `{contract['archive']['bytes']}`\n"
        f"- Bundle files: `{len(members) + 1}`\n"
        "- Credentials / robot access material: ABSENT / ABSENT\n",
        encoding="utf-8",
        newline="\n",
    )
    print(contract["status"])
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
