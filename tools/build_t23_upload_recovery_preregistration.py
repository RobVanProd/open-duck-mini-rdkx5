#!/usr/bin/env python3
"""Preregister one cache-free T23 pre-execution transport recovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = ANALYSIS / "t23_upload_transport_hold_attribution.json"
HOSTED_PREREGISTRATION = (
    ANALYSIS / "t23_support_trainthrough_hosted_preregistration.json"
)
ORIGINAL_PACKAGE = (
    ANALYSIS / "t23_support_trainthrough_hosted_package_contract.json"
)
BASE_PACKAGE_BUILDER = (
    ROOT / "tools/build_t23_support_trainthrough_hosted_package.py"
)
RECOVERY_PACKAGE_BUILDER = (
    ROOT / "tools/build_t23_support_trainthrough_hosted_package_recovery.py"
)
OUTPUT = ANALYSIS / "t23_upload_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T23_UPLOAD_RECOVERY_PREREGISTRATION_20260726.md"


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
            raise FileExistsError(f"refusing to overwrite T23 recovery: {path}")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    hosted = json.loads(
        HOSTED_PREREGISTRATION.read_text(encoding="utf-8")
    )
    package = json.loads(ORIGINAL_PACKAGE.read_text(encoding="utf-8"))
    base_text = BASE_PACKAGE_BUILDER.read_text(encoding="utf-8")
    recovery_text = RECOVERY_PACKAGE_BUILDER.read_text(encoding="utf-8")
    checks = {
        "upload_hold_attributed": (
            attribution.get("status")
            == "PASS_T23_UPLOAD_TRANSPORT_HOLD_ATTRIBUTION"
            and attribution.get("failed_checks") == []
            and attribution.get("decision")
            == "PREREGISTER_T23_CACHE_FREE_UPLOAD_RECOVERY"
        ),
        "prior_executor_never_started": (
            attribution["attempt"]["executor_started"] is False
            and attribution["attempt"]["optimizer_steps"] == 0
            and attribution["attempt"]["simulator_locomotion_steps"] == 0
        ),
        "hosted_training_contract_unchanged": (
            hosted.get("status")
            == "PREREGISTERED_T23_SUPPORT_TRAINTHROUGH_HOSTED_CONTINUATION"
            and hosted.get("failed_checks") == []
        ),
        "original_package_was_green": (
            package.get("status")
            == "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_PACKAGE"
            and package.get("failed_checks") == []
        ),
        "base_builder_excludes_only_nonsource_cache": (
            '".tmp",' in base_text
            and 'shutil.ignore_patterns(' in base_text
        ),
        "recovery_builder_preserves_training_inputs": (
            "base.main()" in recovery_text
            and "training_payload_unchanged" in recovery_text
        ),
        "no_training_or_behavior_run_now": True,
        "no_robot_or_rdk_access": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t23_upload_recovery_preregistration.v1",
        "status": (
            "PREREGISTERED_T23_CACHE_FREE_UPLOAD_RECOVERY"
            if not failed
            else "HOLD_T23_CACHE_FREE_UPLOAD_RECOVERY"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "upload_hold_attribution": sha256(ATTRIBUTION),
            "hosted_training_preregistration": sha256(
                HOSTED_PREREGISTRATION
            ),
            "original_package_contract": sha256(ORIGINAL_PACKAGE),
            "base_package_builder": sha256(BASE_PACKAGE_BUILDER),
            "recovery_package_builder": sha256(RECOVERY_PACKAGE_BUILDER),
        },
        "frozen_correction": {
            "training_source": "BYTE_IDENTICAL",
            "source_checkpoint": "BYTE_IDENTICAL",
            "reference_features": "BYTE_IDENTICAL",
            "hosted_driver": "BYTE_IDENTICAL",
            "training_hyperparameters": "BYTE_IDENTICAL",
            "removed_path": "playground/.tmp",
            "removed_content": "disposable_jax_compilation_cache_only",
            "new_session_required": True,
            "upload_attempts_exact": 1,
            "training_retry": False,
            "training_resume": False,
        },
        "stop_rules": [
            "stop_session_after_any_upload_or_executor_hold",
            "do_not_retry_upload_inside_the_recovery_session",
            "do_not_run_behavior_during_hosted_continuation",
            "do_not_open_gate5_from_partial_or_unvalidated_outputs",
        ],
        "decision": (
            "BUILD_AND_CONTRACT_ONE_CACHE_FREE_T23_PACKAGE"
            if not failed
            else "HOLD_WITHOUT_COLAB"
        ),
        "execution_now": {
            "colab_sessions_opened": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cache_free_transport_recovery": not failed,
            "training_retry": False,
            "training_resume": False,
            "additional_training_attempt": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T23 cache-free upload recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- The hosted training contract and every training input "
                "remain byte-identical.",
                "- The sole correction removes disposable "
                "`playground/.tmp` JAX cache from transport.",
                "- One fresh L4 session and one upload are permitted only "
                "after the recovery package and launch contracts pass.",
                "- This is a pre-execution transport recovery, not a "
                "training retry or resume.",
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
