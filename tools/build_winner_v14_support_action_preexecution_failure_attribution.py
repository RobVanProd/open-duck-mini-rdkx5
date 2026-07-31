#!/usr/bin/env python3
"""Attribute the first Winner-v14 diagnostic pre-execution hash stop."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
FORMAL = ANALYSIS / "winner_v13_support_controller_gate_result.json"
OUTPUT = ANALYSIS / "winner_v14_support_action_preexecution_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V14_SUPPORT_ACTION_PREEXECUTION_FAILURE_ATTRIBUTION_20260721.md"
RUN_ID = 29833400247
RUN_HEAD = "c1e0f9cb2a684dd2d86be3733437294d96ba6f0d"
RAW_SHA256 = "350bd845a27bf0257e2569f5bc1027a76f8e0fcb551cffff745cb43068f9ad2a"
LF_SHA256 = "ad6e0ea99cf0d96fbcd336d7984467efccdd430591201d6fd5242a328518ce05"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")
    data = FORMAL.read_bytes()
    if sha256(data) != RAW_SHA256 or sha256(data.replace(b"\r\n", b"\n")) != LF_SHA256:
        raise ValueError("formal result line-ending evidence changed")
    formal = json.loads(data)
    if formal.get("status") != "HOLD_WINNER_V13_SUPPORT_CONTROLLER_GATE":
        raise ValueError("formal result status changed")
    payload = {
        "schema_version": "winner_v14.support_action_preexecution_failure_attribution.v1",
        "status": "INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_PREEXECUTION",
        "decision": "CORRECT_ONLY_FORMAL_RESULT_HASH_MODE_AND_FRESHLY_PREREGISTER",
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": RUN_ID,
            "github_run_attempt": 1,
            "github_run_head_sha": RUN_HEAD,
            "failed_step": "Run exactly one frozen support-action diagnostic",
            "artifact_count": 0,
        },
        "failure": {
            "exception": "ValueError: formal Winner-v13 gate result changed",
            "cause": (
                "The diagnostic compared the Windows working-tree raw SHA-256 of a "
                "tracked JSON file after GitHub checkout had normalized it to LF."
            ),
            "formal_result_windows_raw_sha256": RAW_SHA256,
            "formal_result_lf_sha256": LF_SHA256,
            "correction": (
                "Compare the already source-manifested formal result using LF-normalized "
                "SHA-256 on every platform. No population, scale, threshold, seed, "
                "transform, or selection rule changes."
            ),
        },
        "execution": {
            "optimizer_updates": 0,
            "main_cells": 0,
            "repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
            "result_json_created": False,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one fresh hash-corrected preregistration",
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v14 support-action pre-execution failure attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / attempt: `{RUN_ID} / 1`",
                "- Optimizer / main / repeat / locomotion / robot: `0 / 0 / 0 / 0 / 0`",
                "",
                "The runner stopped at the formal-result hash check before constructing",
                "an episode or executing a diagnostic cell. Git checkout normalized the",
                "tracked JSON from CRLF to LF, while the runner compared the Windows raw",
                "hash. The only permitted correction is an LF-normalized hash comparison",
                "followed by a fresh preregistration and new run.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
