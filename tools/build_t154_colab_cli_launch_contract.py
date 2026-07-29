#!/usr/bin/env python3
"""Freeze T154's one-session Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t154_positive_only_expert_hosted_preregistration.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t154_positive_only_expert_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t154_positive_only_expert_bundle_20260729.tar.gz"
)
EXECUTOR = ROOT / "tools" / "execute_t154_colab_cli.py"
OUTPUT = ANALYSIS / "t154_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "T154_COLAB_CLI_LAUNCH_CONTRACT_20260729.md"
SESSION = "t154-positive-only-expert-20260729"
PACKAGE_SHA256 = (
    "3dcdf0598ccc8b586042042f98abf0eb27ab13ac18426edcd1a07931c10f25be"
)
PACKAGE_BYTES = 4_331_099


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T154 launch: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T154 launch contract requires clean tree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    text = EXECUTOR.read_text(encoding="utf-8")
    checks = {
        "preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T154_POSITIVE_ONLY_EXPERT_HOSTED_CONTINUATION"
            and prereg["failed_checks"] == []
        ),
        "package_contract_green": (
            package["status"]
            == "PASS_T154_POSITIVE_ONLY_EXPERT_HOSTED_PACKAGE"
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
            "colab_t154_positive_only_expert.py" in text
            and "PASS_T154_HOSTED_FULL_PREFLIGHT" in text
        ),
        "executor_no_retry_or_same_run_resume": (
            '"retry": False' in text
            and '"same_run_resume": False' in text
            and "no-retry path exists" in text
        ),
        "hardware_or_robot_absent": (
            '"robot_or_rdk_access": False' in text
        ),
        "training_or_behavior_not_run": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    commands = [
        ["colab", "new", "--session", SESSION, "--gpu", "L4"],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            str(PACKAGE),
            "/content/t154-positive-only-expert-20260729.tar.gz",
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
            "/content/t154_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t154_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t154_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "open_duck.t154_colab_cli_launch_contract.v1",
        "status": (
            "PASS_T154_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_T154_COLAB_CLI_LAUNCH_CONTRACT"
        ),
        "checks": checks,
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
        "# T154 Colab CLI launch contract\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Session: `{SESSION}`\n"
        "- Accelerator / launches / retries / resumes: L4 / 1 / 0 / 0\n"
        f"- Package SHA-256: `{PACKAGE_SHA256}`\n"
        f"- Executor SHA-256: `{value['hashes']['executor']}`\n"
        "- Behavior / Gate 5 / robot authority: 0 / 0 / 0\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
