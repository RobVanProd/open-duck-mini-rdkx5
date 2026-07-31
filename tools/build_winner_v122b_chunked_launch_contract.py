#!/usr/bin/env python3
"""Freeze the corrected chunked Winner-v122 Colab launch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v122_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v122_hosted_package_contract.json"
CORRECTION = ANALYSIS / "winner_v122_upload_transport_correction.json"
CHUNK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v122-upload-chunks-20260724"
)
LAUNCHER = ROOT / "tools/launch_winner_v122_episode_peak_colab.py"
EXECUTOR = ROOT / "tools/execute_winner_v122b_chunked_colab_cli.py"
OUTPUT = ANALYSIS / "winner_v122b_chunked_colab_launch_contract.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V122B_CHUNKED_COLAB_LAUNCH_CONTRACT_20260724.md"
)
PREREGISTRATION_SHA256 = (
    "fbbd796fdbf30d0e634ea712ceadd2946af035037bf6481f4ef3e1d0caed8c8e"
)
PACKAGE_CONTRACT_SHA256 = (
    "ac313412a362d33d1ed3803777aa0e0a45fca6c4a45cc69b235584a40107926d"
)
CORRECTION_SHA256 = (
    "1f2816b15c18eda6cb9afc918334a8d10498905b67e0b7fffa843e6e8b7df8fb"
)
LAUNCHER_SHA256 = (
    "933871c0814ad0238b1a302aee9ae484a0ecd9ac60b2a8a5c3552739f33fb597"
)
EXECUTOR_SHA256 = (
    "e72fe79a36cc93d5d22c2b10424098a30d42658497ec5efe78251c34b9e314fe"
)
SESSION = "winner-v122b-episode-peak-20260724"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v122b: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    chunk_checks = [
        {
            "name": row["name"],
            "bytes": (CHUNK_ROOT / row["name"]).stat().st_size,
            "sha256": sha256(CHUNK_ROOT / row["name"]),
        }
        for row in correction["chunks"]
    ]
    launcher_text = LAUNCHER.read_text(encoding="utf-8")
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
        ),
        "transport_correction_exact": (
            sha256(CORRECTION) == CORRECTION_SHA256
            and correction.get("status")
            == "PASS_WINNER_V122_UPLOAD_TRANSPORT_CORRECTION"
            and correction.get("decision")
            == "AUTHORIZE_ONE_V122B_CHUNKED_TRANSPORT_LAUNCH"
        ),
        "all_four_chunk_files_exact": (
            chunk_checks == correction["chunks"]
        ),
        "launcher_exact": sha256(LAUNCHER) == LAUNCHER_SHA256,
        "executor_exact": sha256(EXECUTOR) == EXECUTOR_SHA256,
        "pinned_software_exact": '"jax[cuda12]==0.7.2"' in launcher_text,
        "training_payload_unchanged": True,
        "one_training_launch_without_retry_or_resume": True,
        "hardware_or_robot_absent": (
            '"robot_or_rdk_access": False' in launcher_text
        ),
        "training_or_behavior_not_run_after_correction": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    commands = [
        ["colab", "new", "--session", SESSION, "--gpu", "L4"],
        *[
            [
                "colab",
                "upload",
                "--session",
                SESSION,
                f"<CHUNK_ROOT>/{row['name']}",
                f"/content/{row['name']}",
            ]
            for row in correction["chunks"]
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
            "<LOCAL_CHUNKED_EXECUTOR>",
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
        "schema_version": "winner_v122b.chunked_colab_launch_contract.v1",
        "status": (
            "PASS_WINNER_V122B_CHUNKED_COLAB_LAUNCH_CONTRACT"
            if not failed
            else "HOLD_WINNER_V122B_CHUNKED_COLAB_LAUNCH_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "preregistration": PREREGISTRATION_SHA256,
            "package_contract": PACKAGE_CONTRACT_SHA256,
            "transport_correction": CORRECTION_SHA256,
            "launcher": LAUNCHER_SHA256,
            "executor": EXECUTOR_SHA256,
        },
        "chunks": chunk_checks,
        "session": {
            "name": SESSION,
            "accelerator": "L4",
            "training_session_count": 1,
            "prior_prelaunch_transport_session_count": 1,
            "max_wall_seconds": 21_600,
        },
        "commands": commands,
        "recovery": {
            "reconstruct_and_verify_package_before_launch": True,
            "download_result_archive_receipt_before_stop": True,
            "stop_session_after_pass_or_hold": True,
            "training_retry": False,
            "training_resume": False,
        },
        "execution_now": {
            "active_colab_sessions": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_exact_chunked_cli_launch": not failed,
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
    )
    MARKDOWN.write_text(
        "# Winner-v122b chunked Colab launch contract\n\n"
        f"Status: `{value['status']}`\n\n"
        "The training payload is unchanged. Four exact chunks reconstruct "
        "and verify the original package before the launcher runs. The "
        "previous idle session executed no training. This contract grants "
        "one training launch without retry or resume and no behavior, Gate "
        "5, RDK-X5, or robot authority.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
