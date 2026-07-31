#!/usr/bin/env python3
"""Freeze strict preservation of the sole held Winner-v30 artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v30_one_update_hold_import_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V30_ONE_UPDATE_HOLD_IMPORT_CORRECTION_20260722.md"
SOURCES = {
    "builder": Path("tools/build_winner_v30_one_update_hold_import_correction.py"),
    "importer": Path("tools/import_winner_v30_one_update_hold_artifact.py"),
    "importer_tests": Path("tests/test_winner_v30_one_update_hold_import.py"),
    "v30_contract": Path("outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"),
    "v30_runner": Path("tools/run_winner_v30_prefix_right_pitch_anchor_one_update_cpu_proof.py"),
    "v30_workflow": Path(".github/workflows/winner-v30-prefix-right-pitch-anchor-one-update-cpu-proof.yml"),
    "v29_result": Path("outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_result.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v30 HOLD correction")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v30.one_update_hold_import_correction.v1",
        "status": "FROZEN_WINNER_V30_ONE_UPDATE_HOLD_IMPORT_CORRECTION",
        "decision": "AUTHORIZE_STRICT_IMPORT_OF_UNCHANGED_FIRST_ATTEMPT_HOLD_ONLY",
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": 29889578085,
            "github_run_attempt": 1,
            "github_run_head_sha": "92fe3e88c4d81ebed48a6c9d5e54f774aa25d0cf",
            "github_artifact_id": 8517769530,
            "github_artifact_name": "winner-v30-prefix-right-pitch-anchor-one-update-29889578085",
            "github_artifact_digest": "sha256:50533add5c2f403ec4ffa6d7f82110a930636e47ec9bf7672038b99eece0fb86",
            "artifact_zip_sha256": "50533add5c2f403ec4ffa6d7f82110a930636e47ec9bf7672038b99eece0fb86",
            "artifact_zip_bytes": 246907,
        },
        "expected_raw": {
            "status": "HOLD_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF",
            "decision": "DO_NOT_TRAIN_PREFIX_RIGHT_PITCH_ANCHOR_OBJECTIVE",
            "failed_checks": [
                "exact_v29_anchor_loss_gradient_and_scale_reproduced",
                "exact_v29_update_200_batch_reproduced",
            ],
            "optimizer_count_before": 200,
            "optimizer_count_after": 201,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "correction_scope": {
            "rerun_authorized": False,
            "threshold_changed": False,
            "result_rewritten": False,
            "snapshot_or_graph_promoted": False,
            "strict_import_only": True,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "optimizer_update_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separately preregistered saved-result-only cross-run replay attribution"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v30 one-update HOLD import correction",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- GitHub run / artifact: `29889578085 / 8517769530`",
                "- Artifact ZIP SHA-256: `50533add...0fb86`",
                "- Expected failed checks: `2`",
                "- Rerun / extra optimizer update: `NO / NO`",
                "",
                "This correction only preserves the unchanged first-attempt HOLD artifact.",
                "It changes no threshold or result and authorizes no training or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
