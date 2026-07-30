#!/usr/bin/env python3
"""Build T194's hash-frozen hosted continuation bundle."""

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
PREREG = (
    ANALYSIS
    / "t194_corrected_dynamic_reference_support_hosted_"
    "preregistration.json"
)
CPU_RESULT = (
    ANALYSIS
    / "t193_corrected_dynamic_reference_support_cpu_result.json"
)
RECOVERY_RESULT = (
    ANALYSIS / "t193b_metric_namespace_recovery_result.json"
)
T171 = ANALYSIS / "t171_t170_recovered_training_validation.json"
DRIVER = (
    ROOT
    / "tools/colab_t194_corrected_dynamic_reference_support_"
    "continuation.py"
)
BASE_T170 = ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
BASE_T78 = ROOT / "tools/colab_t78_endpoint_joint_adapter_continuation.py"
T32_DRIVER = (
    ROOT / "tools/colab_t32_action_margin_trainthrough_continuation.py"
)
HELPER = ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
CONTRACT = (
    ANALYSIS
    / "t194_corrected_dynamic_reference_support_hosted_"
    "package_contract.json"
)
MARKDOWN = (
    ANALYSIS
    / "T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_PACKAGE_"
    "20260730.md"
)
BUNDLE_NAME = "t194_corrected_dynamic_reference_support_bundle"
MANIFEST_NAME = "t194_package_manifest.json"


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
            raise FileExistsError(f"refusing to overwrite T194: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T194 packaging requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
        "HOSTED_CONTINUATION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T194 preregistration identity changed")
    playground = Path(prereg["paths"]["playground"])
    source = Path(prereg["paths"]["source_checkpoint"])
    step_zero = Path(prereg["paths"]["expected_step_zero_raw"])
    reference = Path(prereg["paths"]["reference"])
    gate = Path(prereg["paths"]["hidden_gate_static_asset"])
    inventory = source_inventory(playground)
    observed = {
        "driver": sha256(DRIVER),
        "base_t170_driver": sha256(BASE_T170),
        "base_t78_driver": sha256(BASE_T78),
        "t32_driver": sha256(T32_DRIVER),
        "helper": sha256(HELPER),
        "cpu_result": sha256(CPU_RESULT),
        "recovery_result": sha256(RECOVERY_RESULT),
        "t171_validation": sha256(T171),
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
        raise RuntimeError("T194 package inputs changed")

    bundle = staging / BUNDLE_NAME
    assets = bundle / "assets"
    assets.mkdir(parents=True)
    for path in (
        PREREG,
        CPU_RESULT,
        RECOVERY_RESULT,
        T171,
        DRIVER,
        BASE_T170,
        BASE_T78,
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
        raise RuntimeError("copied T194 playground changed")
    if (
        directory_sha256(assets / "source_checkpoint")
        != observed["source_checkpoint"]
        or sha256(assets / "expected_step_zero_raw.onnx")
        != observed["expected_step_zero_raw"]
        or sha256(assets / gate.name)
        != observed["hidden_gate_static_asset"]
    ):
        raise RuntimeError("copied T194 assets changed")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(bundle), str(bundle / "playground"))
    )
    preflight_source = "\n".join(
        (
            "from pathlib import Path",
            "import colab_t194_corrected_dynamic_reference_support_continuation as driver",
            "cmd = driver.runner_command(",
            "    Path('playground'), Path('out'),",
            "    Path('assets/source_checkpoint'),",
            "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
            ")",
            "assert cmd.count('--winner_t193_corrected_dynamic_reference_support') == 1",
            "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
            "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
            "assert cmd[cmd.index('--ppo_num_envs') + 1] == '256'",
            "assert cmd[cmd.index('--num_timesteps') + 1] == '2007040'",
            "runner = Path('playground/playground/open_duck_mini_v2/runner.py').read_text()",
            "assert 'T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT=' in runner",
            "assert 'T98_HIDDEN_EXPERT_CONTINUATION=' in runner",
            "try:",
            "    driver.validate_inputs(Path('.'))",
            "except RuntimeError as exc:",
            "    assert 'requires one GPU process' in str(exc)",
            "    print('PASS_T194_FULL_IDENTITY_PREFLIGHT')",
            "else:",
            "    raise AssertionError('local preflight unexpectedly GPU')",
        )
    )
    preflight = subprocess.run(
        [sys.executable, "-c", preflight_source],
        cwd=bundle,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if (
        preflight.returncode != 0
        or "PASS_T194_FULL_IDENTITY_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T194 identity preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    members = file_manifest(bundle)
    manifest = {
        "schema_version": "open_duck.t194_hosted_bundle_manifest.v1",
        "preregistration_sha256": sha256(PREREG),
        "cpu_result_sha256": sha256(CPU_RESULT),
        "recovery_result_sha256": sha256(RECOVERY_RESULT),
        "t171_validation_sha256": sha256(T171),
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
        "schema_version": "open_duck.t194_hosted_package.v1",
        "status": (
            "PASS_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_PACKAGE"
        ),
        "failed_checks": [],
        "checks": {
            "preregistration_exact": True,
            "cpu_and_metric_recovery_evidence_exact": True,
            "t170_half_provenance_exact": True,
            "all_inputs_hash_exact": True,
            "copied_playground_inventory_exact": True,
            "full_identity_preflight_passed": True,
            "credentials_or_robot_material_absent": True,
            "training_not_run": True,
        },
        "archive": {
            "path": str(archive_path),
            "bytes": archive_path.stat().st_size,
            "sha256": sha256(archive_path),
        },
        "manifest": {
            "path": str(manifest_path),
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256(manifest_path),
            "members_canonical_sha256": manifest[
                "members_canonical_sha256"
            ],
            "member_count_excluding_manifest": len(members),
        },
        "execution_now": {
            "optimizer_steps": 0,
            "hosted_sessions_opened": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "build_launch_contract": True,
            "hosted_training": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T194 corrected dynamic reference-support hosted package\n\n"
        f"- Status: `{contract['status']}`\n"
        f"- Archive bytes: `{contract['archive']['bytes']}`\n"
        f"- Archive SHA-256: `{contract['archive']['sha256']}`\n"
        f"- Manifest SHA-256: `{contract['manifest']['sha256']}`\n"
        "- Optimizer / hosted sessions / behavior / robot now: "
        "`0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(contract["status"])
    print(f"archive={archive_path}")
    print(f"archive_sha256={contract['archive']['sha256']}")
    print(f"archive_bytes={contract['archive']['bytes']}")
    print(f"manifest_sha256={contract['manifest']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
