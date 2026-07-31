#!/usr/bin/env python3
"""Freeze the one-session Winner-v105 Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v105_hosted_packaging_correction_preregistration.json"
)
PACKAGE_CONTRACT = (
    ANALYSIS / "winner_v105_response_conditioned_hosted_package_contract.json"
)
LAUNCHER = ROOT / "tools/launch_winner_v105_response_conditioned_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v105_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v105_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V105_COLAB_CLI_LAUNCH_CONTRACT_20260723.md"

PREREGISTRATION_SHA256 = (
    "5cf5a4b449ec9673d2f65122a7a26b957b7240c79d5fb5945b5cf68cb01e279c"
)
PACKAGE_CONTRACT_SHA256 = (
    "f243d3e682532a8858b584e84de1211aaed5abab1039e2d0918a84677434d935"
)
PACKAGE_SHA256 = "30db9b47433543eeeff6e4db6548cd6479916a803891d3aafacd1b63f105be70"
PACKAGE_BYTES = 59_201_279
LAUNCHER_SHA256 = "292a1cc152d9d2762b26c5d490388f7c35d8b5514959bbc950cc76cf9e10e122"
EXECUTOR_SHA256 = "4be9e5e8e5e658c0b1666e1c34669a85f9c79230fbcc1b02194c15e87b9f8edc"
SESSION = "winner-v105-response-20260723"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite Winner-v105 launch contract: {path}"
            )
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    launcher_text = LAUNCHER.read_text(encoding="utf-8")
    executor_text = EXECUTOR.read_text(encoding="utf-8")
    checks = {
        "preregistration_exact": (
            sha256(PREREGISTRATION) == PREREGISTRATION_SHA256
            and preregistration.get("status")
            == "PREREGISTERED_WINNER_V105_HOSTED_PACKAGING_CORRECTION"
        ),
        "package_contract_exact": (
            sha256(PACKAGE_CONTRACT) == PACKAGE_CONTRACT_SHA256
            and package.get("status")
            == "PASS_WINNER_V105_RESPONSE_CONDITIONED_HOSTED_PACKAGE"
            and package.get("archive", {}).get("sha256") == PACKAGE_SHA256
            and package.get("archive", {}).get("bytes") == PACKAGE_BYTES
        ),
        "launcher_exact": sha256(LAUNCHER) == LAUNCHER_SHA256,
        "executor_exact": sha256(EXECUTOR) == EXECUTOR_SHA256,
        "l4_exact": '"L4"' in executor_text,
        "hosted_import_preflight_exact": (
            "PASS_WINNER_V105_HOSTED_IMPORT_CLOSURE" in launcher_text
        ),
        "exact_training_driver_reused": (
            "colab_winner_v102_response_conditioned_curriculum.py"
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
        [
            "colab",
            "new",
            "--session",
            SESSION,
            "--gpu",
            "L4",
        ],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            "<LOCAL_PACKAGE>",
            "/content/winner-v105-response-conditioned-hosted-20260723.tar.gz",
        ],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            "<LOCAL_LAUNCHER>",
            "/content/launch_winner_v105_response_conditioned_colab.py",
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
            "/content/winner_v105_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v105_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v105_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        [
            "colab",
            "stop",
            "--session",
            SESSION,
        ],
    ]
    value = {
        "schema_version": "winner_v105.colab_cli_launch_contract.v1",
        "status": (
            "PASS_WINNER_V105_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V105_COLAB_CLI_LAUNCH_CONTRACT"
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
        "# Winner-v105 Colab CLI launch contract\n\n"
        f"Status: `{value['status']}`\n\n"
        f"- session: `{SESSION}`\n"
        "- accelerator: `L4`\n"
        f"- package SHA-256: `{PACKAGE_SHA256}`\n"
        f"- launcher SHA-256: `{LAUNCHER_SHA256}`\n"
        f"- executor SHA-256: `{EXECUTOR_SHA256}`\n\n"
        "The CLI must create exactly one session, upload the frozen package and "
        "launcher, execute the frozen executor once, recover the result/archive/"
        "receipt, and stop the session. No retry or resume is permitted.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
