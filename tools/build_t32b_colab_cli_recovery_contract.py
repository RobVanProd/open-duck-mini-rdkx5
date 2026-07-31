#!/usr/bin/env python3
"""Freeze one T32 pre-execution identity-constant recovery launch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
ATTRIBUTION = ANALYSIS / "t32_preexecution_identity_hold_attribution.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t32_action_margin_trainthrough_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t32-action-margin-trainthrough-hosted-20260727.tar.gz"
)
EXECUTOR = ROOT / "tools" / "execute_t32_colab_cli.py"
OUTPUT = ANALYSIS / "t32b_colab_cli_recovery_contract.json"
MARKDOWN = ANALYSIS / "T32B_COLAB_CLI_RECOVERY_CONTRACT_20260727.md"
SESSION = "t32b-action-margin-trainthrough-20260727"
PACKAGE_SHA256 = (
    "4c0ffe0e5787eb4db12a6b3112b9f895b9bb736d2526c24daf31fe74689840ed"
)
PACKAGE_BYTES = 3_459_578
DRIVER_SHA256 = (
    "a15ec26c3419d75b2b0417bfd3950947c7d1ae711a050ee33f967f8f1f1f01dd"
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
            raise FileExistsError(f"refusing to overwrite T32b: {path}")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    executor_text = EXECUTOR.read_text(encoding="utf-8")
    match = re.search(
        r"DRIVER_SHA256\s*=\s*\(\s*\"([0-9a-f]+)\"\s*\)",
        executor_text,
        re.MULTILINE,
    )
    corrected_driver_hash = match.group(1) if match else ""
    checks = {
        "preexecution_hold_attributed_with_zero_steps": (
            attribution.get("status")
            == "PASS_T32_PREEXECUTION_IDENTITY_HOLD_ATTRIBUTION"
            and attribution.get("failed_checks") == []
            and attribution["attempt"]["optimizer_steps"] == 0
            and attribution["decision"]
            == "PREREGISTER_ONE_T32_IDENTITY_CONSTANT_RECOVERY"
        ),
        "same_green_package_exact": (
            package.get("status")
            == "PASS_T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_PACKAGE"
            and package.get("failed_checks") == []
            and package["archive"]["sha256"] == PACKAGE_SHA256
            and package["archive"]["bytes"] == PACKAGE_BYTES
            and sha256(PACKAGE) == PACKAGE_SHA256
        ),
        "only_correction_is_complete_driver_hash": (
            corrected_driver_hash == DRIVER_SHA256
            and len(corrected_driver_hash) == 64
        ),
        "executor_still_l4_pinned_and_no_retry": (
            '"L4"' in executor_text
            and '"jax[cuda12]==0.7.2"' in executor_text
            and '"retry": False' in executor_text
            and '"resume": False' in executor_text
            and "no-retry path exists" in executor_text
        ),
        "behavior_and_robot_absent": (
            '"robot_or_rdk_access": False' in executor_text
        ),
        "training_or_behavior_not_run_by_recovery_contract": True,
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
            "/content/t32-action-margin-trainthrough-hosted-20260727.tar.gz",
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
            "/content/t32_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t32_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/t32_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "open_duck.t32b_colab_cli_recovery_contract.v1",
        "status": (
            "PASS_T32B_COLAB_CLI_RECOVERY_CONTRACT"
            if not failed
            else "HOLD_T32B_COLAB_CLI_RECOVERY_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "correction": {
            "field": "DRIVER_SHA256",
            "before_hex_chars": 62,
            "after_hex_chars": 64,
            "value": DRIVER_SHA256,
            "package_change": False,
            "training_change": False,
        },
        "hashes": {
            "attribution": sha256(ATTRIBUTION),
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
            "prior_optimizer_steps": 0,
        },
        "execution_now": {
            "colab_sessions_opened": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_exact_preexecution_recovery": not failed,
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
                "# T32b Colab CLI recovery contract",
                "",
                f"- Status: `{value['status']}`",
                "- Prior optimizer/behavior/robot steps: `0/0/0`",
                "- Correction: `DRIVER_SHA256 62 -> 64 hex chars`",
                f"- Session: `{SESSION}` (`L4`)",
                "- Launches/retries/resumes: `1/0/0`",
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
