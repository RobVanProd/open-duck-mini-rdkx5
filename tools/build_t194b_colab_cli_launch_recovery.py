#!/usr/bin/env python3
"""Recover T194's pre-execution driver-literal launch check."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t194_corrected_dynamic_reference_support_hosted_"
    "preregistration.json"
)
PACKAGE_CONTRACT = (
    ANALYSIS
    / "t194_corrected_dynamic_reference_support_hosted_"
    "package_contract.json"
)
PRIOR = ANALYSIS / "t194_colab_cli_launch_contract.json"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t194_corrected_dynamic_reference_support_bundle_20260730.tar.gz"
)
EXECUTOR = ROOT / "tools/execute_t194_colab_cli.py"
OUTPUT = ANALYSIS / "t194b_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "T194B_COLAB_CLI_LAUNCH_CONTRACT_20260730.md"
SESSION = "t194-corrected-dynamic-support-20260730"
PACKAGE_SHA256 = (
    "5e1ea887ec4fcfef81a82d209b033436a7e3cdf42e086fac182fa4ddf4a8c7c3"
)
PACKAGE_BYTES = 4_340_170
MANIFEST_SHA256 = (
    "e839c443cc6dafe920e07c02f8a875b0ecfd484522caf6090398cc57d0ff2469"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T194B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T194B launch recovery requires clean tree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    text = EXECUTOR.read_text(encoding="utf-8")
    prior_other = {
        name: passed
        for name, passed in prior["checks"].items()
        if name != "executor_uses_exact_driver_and_objective"
    }
    checks = {
        "prior_held_only_on_driver_literal_source_check": (
            prior["status"] == "HOLD_T194_COLAB_CLI_LAUNCH_CONTRACT"
            and prior["failed_checks"]
            == ["executor_uses_exact_driver_and_objective"]
            and all(prior_other.values())
            and prior["execution_now"]["colab_sessions_opened"] == 0
            and prior["execution_now"]["optimizer_steps"] == 0
        ),
        "preregistration_unchanged_green": (
            prereg["status"]
            == "PREREGISTERED_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
            "HOSTED_CONTINUATION"
            and prereg["failed_checks"] == []
            and sha256(PREREG) == prior["hashes"]["preregistration"]
        ),
        "package_and_manifest_unchanged_green": (
            package["status"]
            == "PASS_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
            "HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and package["archive"]["sha256"] == PACKAGE_SHA256
            and package["archive"]["bytes"] == PACKAGE_BYTES
            and package["manifest"]["sha256"] == MANIFEST_SHA256
            and sha256(PACKAGE) == PACKAGE_SHA256
            and PACKAGE.stat().st_size == PACKAGE_BYTES
        ),
        "executor_driver_literal_and_objective_now_exact": (
            "colab_t194_corrected_dynamic_reference_support_"
            "continuation.py" in text
            and "PASS_T194_HOSTED_FULL_PREFLIGHT" in text
            and "--winner_t193_corrected_dynamic_reference_support"
            in text
        ),
        "executor_l4_pins_no_retry_and_manifest_checks_preserved": (
            '"L4"' in text
            and '"jax[cuda12]==0.7.2"' in text
            and '"retry": False' in text
            and '"same_run_resume": False' in text
            and "for relative, expected in members.items()" in text
            and MANIFEST_SHA256 in text
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
            "/content/t194-corrected-dynamic-support-20260730.tar.gz",
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
            "/content/t194_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t194_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t194_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": (
            "open_duck.t194b_colab_cli_launch_recovery.v1"
        ),
        "status": (
            "PASS_T194B_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_T194B_COLAB_CLI_LAUNCH_CONTRACT"
        ),
        "recovery": {
            "only_change": (
                "spell the already-correct remote driver path as one "
                "contiguous source literal"
            ),
            "scientific_contract_change": False,
            "package_change": False,
            "hosted_session_previously_opened": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "prior_launch_contract": sha256(PRIOR),
            "preregistration": sha256(PREREG),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "package": PACKAGE_SHA256,
            "manifest": MANIFEST_SHA256,
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
        "artifact_recovery": {
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
        "# T194B Colab CLI launch recovery\n\n"
        f"- Status: `{value['status']}`\n"
        "- Only change: contiguous remote-driver filename literal\n"
        "- Package / manifest / scientific contract: unchanged\n"
        "- Accelerator / launches / retries / resumes: L4 / 1 / 0 / 0\n"
        f"- Executor SHA-256: `{value['hashes']['executor']}`\n"
        "- Behavior / Gate 5 / robot authority: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
