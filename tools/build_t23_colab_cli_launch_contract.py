#!/usr/bin/env python3
"""Freeze T23's one-session Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t23_support_trainthrough_hosted_preregistration.json"
)
PACKAGE_CONTRACT = (
    ANALYSIS / "t23_support_trainthrough_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t23-support-trainthrough-hosted-20260726.tar.gz"
)
EXECUTOR = ROOT / "tools" / "execute_t23_colab_cli.py"
OUTPUT = ANALYSIS / "t23_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "T23_COLAB_CLI_LAUNCH_CONTRACT_20260726.md"
SESSION = "t23-support-trainthrough-20260726"
PACKAGE_SHA256 = (
    "2ba7612ef2984623f60abac0b4d41efdf18ae711f5f848003b4f125013d658e8"
)
PACKAGE_BYTES = 134_645_185


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T23 launch: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    executor_text = EXECUTOR.read_text(encoding="utf-8")
    checks = {
        "preregistration_green": (
            prereg.get("status")
            == "PREREGISTERED_T23_SUPPORT_TRAINTHROUGH_HOSTED_CONTINUATION"
            and prereg.get("failed_checks") == []
        ),
        "package_contract_green": (
            package.get("status")
            == "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_PACKAGE"
            and package.get("failed_checks") == []
            and package.get("archive", {}).get("sha256") == PACKAGE_SHA256
            and package.get("archive", {}).get("bytes") == PACKAGE_BYTES
        ),
        "package_file_exact": (
            PACKAGE.stat().st_size == PACKAGE_BYTES
            and sha256(PACKAGE) == PACKAGE_SHA256
        ),
        "executor_l4_exact": (
            '"L4"' in executor_text and '"gpu": gpu.stdout.strip()' in executor_text
        ),
        "executor_pinned_software_exact": (
            '"jax[cuda12]==0.7.2"' in executor_text
        ),
        "executor_single_driver_exact": (
            "colab_t23_support_trainthrough_continuation.py"
            in executor_text
        ),
        "executor_no_retry_resume": (
            '"retry": False' in executor_text
            and '"resume": False' in executor_text
        ),
        "hardware_or_robot_absent": (
            '"robot_or_rdk_access": False' in executor_text
        ),
        "training_or_behavior_not_run": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    commands = [
        ["colab", "new", "--session", SESSION, "--gpu", "L4"],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            str(PACKAGE),
            "/content/t23-support-trainthrough-hosted-20260726.tar.gz",
        ],
        [
            "colab",
            "exec",
            "--session",
            SESSION,
            "--file",
            str(EXECUTOR),
            "--timeout",
            "21600",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t23_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t23_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t23_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "open_duck.t23_colab_cli_launch_contract.v1",
        "status": (
            "PASS_T23_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_T23_COLAB_CLI_LAUNCH_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "preregistration": sha256(PREREGISTRATION),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "package": PACKAGE_SHA256,
            "executor": sha256(EXECUTOR),
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
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T23 Colab CLI launch contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Session: `{SESSION}`",
                "- Accelerator: `L4`",
                f"- Package SHA-256: `{PACKAGE_SHA256}`",
                f"- Executor SHA-256: `{value['hashes']['executor']}`",
                "- Launches/retries/resumes: `1/0/0`",
                "- Behavior/Gate5/robot authority: `0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
