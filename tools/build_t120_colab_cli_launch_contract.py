#!/usr/bin/env python3
"""Freeze T120's one-session Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t120_joint_soft_router_hosted_preregistration.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t120_joint_soft_router_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t120_joint_soft_router_bundle_20260729.tar.gz"
)
EXECUTOR = ROOT / "tools" / "execute_t120_colab_cli.py"
OUTPUT = ANALYSIS / "t120_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "T120_COLAB_CLI_LAUNCH_CONTRACT_20260729.md"
SESSION = "t120-joint-soft-router-20260729"
PACKAGE_SHA256 = (
    "596599321c2f8933c6344f25a44455fa11546d97a511a9c8eb9b866292577f00"
)
PACKAGE_BYTES = 4_322_347


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T120 launch: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T120 launch contract requires clean tree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    text = EXECUTOR.read_text(encoding="utf-8")
    checks = {
        "preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T120_JOINT_SOFT_ROUTER_HOSTED_CONTINUATION"
            and prereg["failed_checks"] == []
        ),
        "package_contract_green": (
            package["status"]
            == "PASS_T120_JOINT_SOFT_ROUTER_HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and package["archive"]["sha256"] == PACKAGE_SHA256
            and package["archive"]["bytes"] == PACKAGE_BYTES
        ),
        "package_file_exact": (
            PACKAGE.stat().st_size == PACKAGE_BYTES
            and sha256(PACKAGE) == PACKAGE_SHA256
        ),
        "executor_l4_and_pinned_software": (
            '"L4"' in text and '"jax[cuda12]==0.7.2"' in text
        ),
        "executor_uses_exact_driver": (
            "colab_t120_joint_soft_router_trainthrough.py" in text
            and "PASS_T120_HOSTED_FULL_PREFLIGHT" in text
        ),
        "executor_no_retry_or_same_run_resume": (
            '"retry": False' in text
            and '"same_run_resume": False' in text
            and "no-retry path exists" in text
        ),
        "hardware_or_robot_absent": '"robot_or_rdk_access": False' in text,
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
            str(PACKAGE),
            "/content/t120-joint-soft-router-20260729.tar.gz",
        ],
        [
            "colab",
            "exec",
            "--session",
            SESSION,
            "--file",
            str(EXECUTOR),
            "--timeout",
            "43200",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t120_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t120_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t120_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "open_duck.t120_colab_cli_launch_contract.v1",
        "status": (
            "PASS_T120_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_T120_COLAB_CLI_LAUNCH_CONTRACT"
        ),
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "hashes": {
            "preregistration": sha256(PREREG),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "package": PACKAGE_SHA256,
            "executor": sha256(EXECUTOR),
        },
        "package_bytes": PACKAGE_BYTES,
        "session": {
            "name": SESSION,
            "accelerator": "L4",
            "count": 1,
            "max_wall_seconds": 43_200,
            "maximum_compute_units_at_prior_rate": 6.42,
        },
        "commands": commands,
        "recovery": {
            "download_result_archive_receipt_before_stop": True,
            "stop_session_after_pass_or_hold": True,
            "retry": False,
            "same_run_resume": False,
        },
        "execution_now": {
            "colab_sessions_opened": 0,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_exact_cli_launch": not failed,
            "additional_attempt_retry_or_same_run_resume": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
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
                "# T120 Colab CLI launch contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Session: `{SESSION}`",
                "- Accelerator / launches / retries / resumes: L4 / 1 / 0 / 0",
                f"- Package SHA-256: `{PACKAGE_SHA256}`",
                f"- Executor SHA-256: `{value['hashes']['executor']}`",
                "- Behavior / Gate 5 / robot authority: 0 / 0 / 0",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
