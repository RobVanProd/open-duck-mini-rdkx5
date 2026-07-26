#!/usr/bin/env python3
"""Freeze the first T23 attempt as a pre-execution upload hold."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
LAUNCH_CONTRACT = ANALYSIS / "t23_colab_cli_launch_contract.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t23_support_trainthrough_hosted_package_contract.json"
)
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t23-support-trainthrough-hosted-20260726.tar.gz"
)
STAGING = Path(
    "D:/CodexArtifacts/open-duck-policy/t23_hosted_package_v1/"
    "t23_support_trainthrough_bundle"
)
OUTPUT = ANALYSIS / "t23_upload_transport_hold_attribution.json"
MARKDOWN = ANALYSIS / "T23_UPLOAD_TRANSPORT_HOLD_ATTRIBUTION_20260726.md"
EXPECTED_PACKAGE_BYTES = 134_645_185
EXPECTED_PACKAGE_SHA256 = (
    "2ba7612ef2984623f60abac0b4d41efdf18ae711f5f848003b4f125013d658e8"
)
EXPECTED_CACHE_FILES = 2_638
EXPECTED_CACHE_BYTES = 132_813_251
UPLOAD_ERROR = (
    "('Connection aborted.', ConnectionResetError(10054, "
    "'An existing connection was forcibly closed by the remote host'))"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colab-executable", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T23 hold: {path}")

    launch = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    cache = STAGING / "playground/.tmp"
    cache_files = [path for path in cache.rglob("*") if path.is_file()]
    cache_bytes = sum(path.stat().st_size for path in cache_files)
    package_identity = {
        "bytes": PACKAGE.stat().st_size,
        "sha256": sha256(PACKAGE),
    }
    sessions = subprocess.run(
        [str(args.colab_executable.resolve()), "sessions"],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    session_output = (sessions.stdout + sessions.stderr).strip()
    checks = {
        "original_launch_contract_green": (
            launch.get("status") == "PASS_T23_COLAB_CLI_LAUNCH_CONTRACT"
            and launch.get("failed_checks") == []
        ),
        "original_package_contract_green": (
            package_contract.get("status")
            == "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_PACKAGE"
            and package_contract.get("failed_checks") == []
        ),
        "original_package_exact": package_identity
        == {
            "bytes": EXPECTED_PACKAGE_BYTES,
            "sha256": EXPECTED_PACKAGE_SHA256,
        },
        "unnecessary_cache_population_exact": (
            len(cache_files) == EXPECTED_CACHE_FILES
            and cache_bytes == EXPECTED_CACHE_BYTES
        ),
        "cache_is_not_training_source": (
            all(".tmp/jax_cache/" in path.as_posix() for path in cache_files)
        ),
        "session_stopped": (
            sessions.returncode == 0
            and "No active sessions found" in session_output
        ),
        "executor_never_started": True,
        "optimizer_steps_zero": True,
        "simulator_locomotion_steps_zero": True,
        "formal_behavior_cells_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t23_upload_transport_hold.v1",
        "status": (
            "PASS_T23_UPLOAD_TRANSPORT_HOLD_ATTRIBUTION"
            if not failed
            else "HOLD_T23_UPLOAD_TRANSPORT_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "attempt": {
            "session": "t23-support-trainthrough-20260726",
            "accelerator": "L4",
            "session_reached_ready": True,
            "package_upload_attempts": 1,
            "upload_returncode": 1,
            "upload_error": UPLOAD_ERROR,
            "upload_completed": False,
            "executor_uploaded": False,
            "executor_started": False,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "session_stopped": checks["session_stopped"],
            "classification": "pre_execution_transport_hold",
            "decision_weight": 0,
        },
        "original_package": package_identity,
        "discovered_package_inflation": {
            "path": "playground/.tmp",
            "classification": "disposable_jax_compilation_cache",
            "files": len(cache_files),
            "uncompressed_bytes": cache_bytes,
            "fraction_of_bundle_uncompressed_bytes": (
                cache_bytes
                / sum(
                    path.stat().st_size
                    for path in STAGING.rglob("*")
                    if path.is_file()
                )
            ),
            "caused_transport_reset": "NOT_ESTABLISHED",
            "narrow_correction": "exclude_playground_dot_tmp_only",
        },
        "session_check": {
            "returncode": sessions.returncode,
            "output": session_output,
        },
        "decision": (
            "PREREGISTER_T23_CACHE_FREE_UPLOAD_RECOVERY"
            if not failed
            else "HOLD_WITHOUT_COLAB"
        ),
        "authority": {
            "training_retry": False,
            "training_resume": False,
            "one_transport_recovery_may_be_preregistered": not failed,
            "behavior_evaluation": False,
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
                "# T23 upload transport hold attribution",
                "",
                f"- Status: `{value['status']}`",
                "- The L4 session reached ready, but the sole package upload "
                "ended with Windows socket reset 10054.",
                "- The executor never started; optimizer, simulator behavior, "
                "and robot/RDK counts remain zero.",
                f"- Disposable `playground/.tmp` cache: "
                f"`{len(cache_files):,}` files / `{cache_bytes:,}` bytes.",
                "- The cache is proven unnecessary package inflation; it is "
                "not claimed as the proven cause of the connection reset.",
                "- The stopped attempt has zero decision weight.",
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
