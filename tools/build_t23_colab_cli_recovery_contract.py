#!/usr/bin/env python3
"""Freeze T23's one-session cache-free Colab CLI recovery contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
HOSTED_PREREGISTRATION = (
    ANALYSIS / "t23_support_trainthrough_hosted_preregistration.json"
)
RECOVERY_PREREGISTRATION = (
    ANALYSIS / "t23_upload_recovery_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "t23_upload_transport_hold_attribution.json"
PACKAGE_CONTRACT = (
    ANALYSIS
    / "t23_support_trainthrough_hosted_package_recovery_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t23-support-trainthrough-hosted-v2-20260726.tar.gz"
)
EXECUTOR = ROOT / "tools/execute_t23_colab_cli_recovery.py"
OUTPUT = ANALYSIS / "t23_colab_cli_recovery_contract.json"
MARKDOWN = ANALYSIS / "T23_COLAB_CLI_RECOVERY_CONTRACT_20260726.md"
SESSION = "t23-support-trainthrough-v2-20260726"
PACKAGE_SHA256 = (
    "6c503f1ce7bddda912cf0b381c229fc066607a71e9072865588f603e3a63d9e4"
)
PACKAGE_BYTES = 3_408_121


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T23B launch: {path}")
    hosted = json.loads(
        HOSTED_PREREGISTRATION.read_text(encoding="utf-8")
    )
    recovery = json.loads(
        RECOVERY_PREREGISTRATION.read_text(encoding="utf-8")
    )
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    executor_text = EXECUTOR.read_text(encoding="utf-8")
    recovery_basis = {
        key: value
        for key, value in recovery.items()
        if key != "preregistered_contract_sha256"
    }
    checks = {
        "hosted_training_contract_green": (
            hosted.get("status")
            == "PREREGISTERED_T23_SUPPORT_TRAINTHROUGH_HOSTED_CONTINUATION"
            and hosted.get("failed_checks") == []
        ),
        "first_attempt_attributed_zero_weight": (
            attribution.get("status")
            == "PASS_T23_UPLOAD_TRANSPORT_HOLD_ATTRIBUTION"
            and attribution["attempt"]["executor_started"] is False
            and attribution["attempt"]["decision_weight"] == 0
            and attribution["attempt"]["session_stopped"] is True
        ),
        "transport_recovery_preregistered_exact": (
            recovery.get("status")
            == "PREREGISTERED_T23_CACHE_FREE_UPLOAD_RECOVERY"
            and recovery.get("failed_checks") == []
            and canonical_sha256(recovery_basis)
            == recovery.get("preregistered_contract_sha256")
        ),
        "recovery_package_contract_green": (
            package.get("status")
            == "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_RECOVERY_PACKAGE"
            and package.get("failed_checks") == []
            and package.get("archive", {}).get("sha256") == PACKAGE_SHA256
            and package.get("archive", {}).get("bytes") == PACKAGE_BYTES
            and package.get("checks", {}).get("temporary_cache_excluded")
            is True
            and package.get("checks", {}).get("training_payload_unchanged")
            is True
        ),
        "recovery_package_file_exact": (
            PACKAGE.stat().st_size == PACKAGE_BYTES
            and sha256(PACKAGE) == PACKAGE_SHA256
        ),
        "executor_l4_exact": (
            '"L4"' in executor_text
            and '"gpu": gpu.stdout.strip()' in executor_text
        ),
        "executor_pinned_software_exact": (
            '"jax[cuda12]==0.7.2"' in executor_text
        ),
        "executor_single_driver_exact": (
            "colab_t23_support_trainthrough_continuation.py"
            in executor_text
        ),
        "executor_cache_free_identity_exact": (
            PACKAGE_SHA256 in executor_text
            and "temporary_cache_absent" in executor_text
            and "playground/.tmp" in executor_text
        ),
        "executor_no_retry_resume": (
            '"retry": False' in executor_text
            and '"resume": False' in executor_text
        ),
        "hardware_or_robot_absent": (
            '"robot_or_rdk_access": False' in executor_text
        ),
        "training_or_behavior_not_run_now": True,
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
            "/content/t23-support-trainthrough-hosted-v2-20260726.tar.gz",
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
            "/content/t23b_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t23b_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t23b_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "open_duck.t23b_colab_cli_launch_contract.v1",
        "status": (
            "PASS_T23B_COLAB_CLI_RECOVERY_CONTRACT"
            if not failed
            else "HOLD_T23B_COLAB_CLI_RECOVERY_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "hosted_preregistration": sha256(HOSTED_PREREGISTRATION),
            "upload_hold_attribution": sha256(ATTRIBUTION),
            "recovery_preregistration": sha256(
                RECOVERY_PREREGISTRATION
            ),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "package": PACKAGE_SHA256,
            "executor": sha256(EXECUTOR),
        },
        "package_bytes": PACKAGE_BYTES,
        "session": {
            "name": SESSION,
            "accelerator": "L4",
            "fresh_session_count": 1,
            "prior_preexecution_transport_session_count": 1,
            "max_wall_seconds": 21_600,
        },
        "commands": commands,
        "recovery": {
            "cache_free_package": True,
            "training_payload_unchanged": True,
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
            "one_exact_cache_free_cli_launch": not failed,
            "additional_training_attempt": False,
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
                "# T23 cache-free Colab CLI recovery contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Session: `{SESSION}`",
                "- Accelerator: `L4`",
                f"- Package SHA-256: `{PACKAGE_SHA256}`",
                f"- Package bytes: `{PACKAGE_BYTES}`",
                f"- Executor SHA-256: `{value['hashes']['executor']}`",
                "- Fresh launches/retries/resumes: `1/0/0`",
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
