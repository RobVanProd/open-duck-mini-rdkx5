#!/usr/bin/env python3
"""Freeze the one-session Winner-v112 Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v112_peak_torque_hosted_preregistration.json"
)
PACKAGE_CONTRACT = (
    ANALYSIS / "winner_v112_peak_torque_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v112-peak-torque-hosted-20260724.tar.gz"
)
LAUNCHER = ROOT / "tools/launch_winner_v112_peak_torque_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v112_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v112_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V112_COLAB_CLI_LAUNCH_CONTRACT_20260724.md"
PREREGISTRATION_SHA256 = (
    "44feeb999de22ab7a4ad2438eeb1db27d1c2e683b0cee6f83030e78caa344817"
)
PACKAGE_CONTRACT_SHA256 = (
    "b22de9fca8044962b9f9d75709a5105a611db0e02f6c21a2951fc6e4422ae0f6"
)
PACKAGE_SHA256 = (
    "f39bea69840436b5ca8cc2a3000b6006ceaac1fa403588c94024e6caa5709401"
)
PACKAGE_BYTES = 51_971_655
LAUNCHER_SHA256 = (
    "6f4a1715b29bbf714de2ac48769702fe22f9b837e33ad5e6af6940b0824dc988"
)
EXECUTOR_SHA256 = (
    "3486f558dacd9fc7c167da2eef04e73ce8ba08fd814ce483b9d2e8e5f24045bb"
)
SESSION = "winner-v112-peak-torque-20260724"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v112: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    launcher_text = LAUNCHER.read_text(encoding="utf-8")
    executor_text = EXECUTOR.read_text(encoding="utf-8")
    checks = {
        "preregistration_exact": (
            sha256(PREREGISTRATION) == PREREGISTRATION_SHA256
            and prereg.get("status")
            == "PREREGISTERED_WINNER_V112_PEAK_TORQUE_HOSTED_CONTINUATION"
        ),
        "package_contract_exact": (
            sha256(PACKAGE_CONTRACT) == PACKAGE_CONTRACT_SHA256
            and package_contract.get("status")
            == "PASS_WINNER_V112_PEAK_TORQUE_HOSTED_PACKAGE"
            and package_contract.get("archive", {}).get("sha256")
            == PACKAGE_SHA256
            and package_contract.get("archive", {}).get("bytes")
            == PACKAGE_BYTES
        ),
        "package_file_exact": (
            PACKAGE.stat().st_size == PACKAGE_BYTES
            and sha256(PACKAGE) == PACKAGE_SHA256
        ),
        "launcher_exact": sha256(LAUNCHER) == LAUNCHER_SHA256,
        "executor_exact": sha256(EXECUTOR) == EXECUTOR_SHA256,
        "l4_exact": '"L4"' in executor_text,
        "pinned_software_exact": '"jax[cuda12]==0.7.2"' in launcher_text,
        "single_frozen_driver_exact": (
            "colab_winner_v112_peak_torque_continuation.py"
            in launcher_text
        ),
        "no_retry_or_resume": (
            '"retry": False' in launcher_text
            and '"resume": False' in launcher_text
        ),
        "hardware_or_robot_absent": (
            '"robot_or_rdk_access": False' in launcher_text
        ),
        "training_or_behavior_not_run": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    commands = [
        ["colab", "new", "--session", SESSION, "--gpu", "L4"],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            "<LOCAL_PACKAGE>",
            "/content/winner-v112-peak-torque-hosted-20260724.tar.gz",
        ],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            "<LOCAL_LAUNCHER>",
            "/content/launch_winner_v112_peak_torque_colab.py",
        ],
        [
            "colab",
            "exec",
            "--session",
            SESSION,
            "--file",
            "<LOCAL_EXECUTOR>",
            "--timeout",
            "21600",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v112_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v112_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v112_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "winner_v112.colab_cli_launch_contract.v1",
        "status": (
            "PASS_WINNER_V112_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V112_COLAB_CLI_LAUNCH_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "preregistration": PREREGISTRATION_SHA256,
            "package_contract": PACKAGE_CONTRACT_SHA256,
            "package": PACKAGE_SHA256,
            "launcher": LAUNCHER_SHA256,
            "executor": EXECUTOR_SHA256,
        },
        "package_bytes": PACKAGE_BYTES,
        "session": {
            "name": SESSION,
            "accelerator": "L4",
            "count": 1,
            "max_wall_seconds": 21_600,
        },
        "commands": commands,
        "recovery": {
            "download_result_archive_receipt_before_stop": True,
            "stop_session_after_pass_or_hold": True,
            "retry": False,
            "resume": False,
        },
        "execution_now": {
            "colab_sessions_opened": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_exact_cli_launch": not failed,
            "additional_attempt": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v112 Colab CLI launch contract\n\n"
        f"Status: `{value['status']}`\n\n"
        f"- session: `{SESSION}`\n"
        "- accelerator: `L4`\n"
        f"- package SHA-256: `{PACKAGE_SHA256}`\n"
        f"- launcher SHA-256: `{LAUNCHER_SHA256}`\n"
        f"- executor SHA-256: `{EXECUTOR_SHA256}`\n\n"
        "The CLI may create exactly one L4 session, execute the frozen "
        "continuation once, recover result/archive/receipt, and stop it. "
        "Retry, resume, behavior selection, Gate 5, and robot access remain "
        "unauthorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
