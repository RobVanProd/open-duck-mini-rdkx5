#!/usr/bin/env python3
"""Freeze the one-session Winner-v122 Colab CLI launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v122_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v122_hosted_package_contract.json"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v122-hosted-20260724.tar.gz"
)
LAUNCHER = ROOT / "tools/launch_winner_v122_episode_peak_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v122_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v122_colab_cli_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V122_COLAB_CLI_LAUNCH_CONTRACT_20260724.md"
PREREGISTRATION_SHA256 = (
    "fbbd796fdbf30d0e634ea712ceadd2946af035037bf6481f4ef3e1d0caed8c8e"
)
PACKAGE_CONTRACT_SHA256 = (
    "ac313412a362d33d1ed3803777aa0e0a45fca6c4a45cc69b235584a40107926d"
)
PACKAGE_SHA256 = (
    "2ea6bf726c21831137dfbc321c099a166b21bf8b3485038489d80d2a00fe1562"
)
PACKAGE_BYTES = 91_222_310
LAUNCHER_SHA256 = (
    "933871c0814ad0238b1a302aee9ae484a0ecd9ac60b2a8a5c3552739f33fb597"
)
EXECUTOR_SHA256 = (
    "5644e16eb114d461ba6a4380473c5baf82589a79f8b4a81ab3c383ab11faf7c2"
)
SESSION = "winner-v122-episode-peak-20260724"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v122: {path}")
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
            == "PREREGISTERED_WINNER_V122_HOSTED_CONTINUATION"
        ),
        "package_contract_exact": (
            sha256(PACKAGE_CONTRACT) == PACKAGE_CONTRACT_SHA256
            and package_contract.get("status")
            == "PASS_WINNER_V122_HOSTED_PACKAGE"
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
            "colab_winner_v122_episode_peak_continuation.py"
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
            "/content/winner-v122-hosted-20260724.tar.gz",
        ],
        [
            "colab",
            "upload",
            "--session",
            SESSION,
            "<LOCAL_LAUNCHER>",
            "/content/launch_winner_v122_episode_peak_colab.py",
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
            "/content/winner_v122_result.json",
            "<LOCAL_RESULT>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v122_artifacts.tar.gz",
            "<LOCAL_ARCHIVE>",
        ],
        [
            "colab",
            "download",
            "--session",
            SESSION,
            "/content/winner_v122_launch_receipt.json",
            "<LOCAL_RECEIPT>",
        ],
        ["colab", "stop", "--session", SESSION],
    ]
    value = {
        "schema_version": "winner_v122.colab_cli_launch_contract.v1",
        "status": (
            "PASS_WINNER_V122_COLAB_CLI_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V122_COLAB_CLI_LAUNCH_CONTRACT"
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
        "# Winner-v122 Colab CLI launch contract\n\n"
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
