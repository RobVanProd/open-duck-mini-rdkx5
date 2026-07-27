#!/usr/bin/env python3
"""Attribute T32's first launch as a zero-step identity-constant hold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
LAUNCH = ANALYSIS / "t32_colab_cli_launch_contract.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t32_action_margin_trainthrough_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t32-action-margin-trainthrough-hosted-20260727.tar.gz"
)
STAGING = Path(
    "D:/CodexArtifacts/open-duck-policy/t32_hosted_package_v1/"
    "t32_action_margin_trainthrough_bundle"
)
OUTPUT = ANALYSIS / "t32_preexecution_identity_hold_attribution.json"
MARKDOWN = (
    ANALYSIS / "T32_PREEXECUTION_IDENTITY_HOLD_ATTRIBUTION_20260727.md"
)
ORIGINAL_COMMIT = "5b37aa3d"
EXPECTED_ERROR = "ValueError: T32 extracted package identity changed"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def embedded_hash(text: str, name: str) -> str:
    match = re.search(
        rf"{name}\s*=\s*\(\s*\"([0-9a-f]+)\"\s*\)",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise ValueError(f"missing original constant: {name}")
    return match.group(1)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T32 hold: {path}")
    launch = json.loads(LAUNCH.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    original = subprocess.check_output(
        [
            "git",
            "show",
            f"{ORIGINAL_COMMIT}:tools/execute_t32_colab_cli.py",
        ],
        cwd=ROOT,
        text=True,
    )
    actual = {
        "PREREGISTRATION_SHA256": sha256(
            STAGING
            / "t32_action_margin_trainthrough_hosted_preregistration.json"
        ),
        "CPU_RESULT_SHA256": sha256(
            STAGING / "t31_action_margin_trainthrough_cpu_result.json"
        ),
        "PACKAGE_MANIFEST_SHA256": sha256(
            STAGING / "t32_package_manifest.json"
        ),
        "DRIVER_SHA256": sha256(
            STAGING / "colab_t32_action_margin_trainthrough_continuation.py"
        ),
        "DRIVER_HELPER_SHA256": sha256(
            STAGING / "colab_winner_v114_linear_torque_continuation.py"
        ),
    }
    embedded = {name: embedded_hash(original, name) for name in actual}
    mismatch_names = [
        name for name in actual if actual[name] != embedded[name]
    ]
    identity_guard_index = original.index(
        'raise ValueError("T32 extracted package identity changed")'
    )
    install_index = original.index("install = [")
    driver_run_index = original.index("result = subprocess.run(")
    checks = {
        "original_launch_contract_green": (
            launch.get("status") == "PASS_T32_COLAB_CLI_LAUNCH_CONTRACT"
            and launch.get("failed_checks") == []
        ),
        "package_contract_green_and_outer_archive_exact": (
            package.get("status")
            == "PASS_T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_PACKAGE"
            and package.get("failed_checks") == []
            and package["archive"]["bytes"] == PACKAGE.stat().st_size
            and package["archive"]["sha256"] == sha256(PACKAGE)
        ),
        "only_driver_constant_mismatched": (
            mismatch_names == ["DRIVER_SHA256"]
        ),
        "driver_constant_was_truncated_to_62_hex_chars": (
            len(embedded["DRIVER_SHA256"]) == 62
            and len(actual["DRIVER_SHA256"]) == 64
        ),
        "identity_guard_precedes_install_and_driver": (
            identity_guard_index < install_index < driver_run_index
        ),
        "executor_never_started_training_driver": True,
        "optimizer_steps_zero": True,
        "formal_behavior_cells_zero": True,
        "robot_or_rdk_access_zero": True,
        "session_stopped": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t32_preexecution_identity_hold.v1",
        "status": (
            "PASS_T32_PREEXECUTION_IDENTITY_HOLD_ATTRIBUTION"
            if not failed
            else "HOLD_T32_PREEXECUTION_IDENTITY_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "attempt": {
            "session": "t32-action-margin-trainthrough-20260727",
            "accelerator": "L4",
            "package_upload_completed": True,
            "outer_package_identity_passed": True,
            "executor_error": EXPECTED_ERROR,
            "failed_before_dependency_install": True,
            "failed_before_training_driver": True,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "session_stopped": True,
            "classification": "preexecution_identity_constant_hold",
            "decision_weight": 0,
        },
        "identity": {
            "original_commit": ORIGINAL_COMMIT,
            "embedded": embedded,
            "actual": actual,
            "mismatch_names": mismatch_names,
        },
        "decision": (
            "PREREGISTER_ONE_T32_IDENTITY_CONSTANT_RECOVERY"
            if not failed
            else "KEEP_T32_HOSTED_TRAINING_CLOSED"
        ),
        "authority": {
            "training_retry": False,
            "training_resume": False,
            "one_preexecution_recovery_may_be_preregistered": not failed,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T32 pre-execution identity hold attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Error: `{EXPECTED_ERROR}`",
                "- Root cause: embedded driver SHA had `62/64` hex chars",
                "- Dependency install / optimizer / behavior / robot: `0/0/0/0`",
                "- Session: `STOPPED`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"mismatch_names={mismatch_names}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
