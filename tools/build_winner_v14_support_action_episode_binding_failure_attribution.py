#!/usr/bin/env python3
"""Attribute the Winner-v14 diagnostic episode-constructor binding stop."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v14_support_action_episode_binding_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V14_SUPPORT_ACTION_EPISODE_BINDING_FAILURE_ATTRIBUTION_20260721.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")
    source = (ROOT / "tools/run_winner_v14_support_action_diagnostic.py").read_text(
        encoding="utf-8"
    )
    if "episode = base.Episode(" not in source:
        raise ValueError("failed episode binding is no longer attributable")
    payload = {
        "schema_version": "winner_v14.support_action_episode_binding_failure_attribution.v1",
        "status": "INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_EPISODE_BINDING",
        "decision": "CORRECT_ONLY_REVIEWED_EPISODE_TYPE_BINDING_AND_FRESHLY_PREREGISTER",
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": 29833729219,
            "github_run_attempt": 1,
            "github_run_head_sha": "872cd436bfe1735de75a551bb1def5758db72f41",
            "failed_step": "Run exactly one frozen support-action diagnostic",
            "artifact_count": 0,
        },
        "failure": {
            "exception": (
                "AttributeError: module 'run_winner_v12_calibrator_support_gate' "
                "has no attribute 'Episode'"
            ),
            "cause": (
                "The adapter referenced base.Episode, while the reviewed evaluator "
                "constructs smoke.Episode from run_winner_v12_calibrator_cpu_smoke."
            ),
            "correction": "replace only base.Episode with base.smoke.Episode",
        },
        "execution": {
            "optimizer_updates": 0,
            "completed_main_cells": 0,
            "completed_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
            "result_json_created": False,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one fresh one-line-binding-corrected preregistration",
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v14 support-action episode-binding failure attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- GitHub run / attempt: `29833729219 / 1`",
                "- Completed main / repeat cells: `0 / 0`",
                "- Training / locomotion / robot access: `0 / 0 / 0`",
                "",
                "The hash-corrected runner entered the first loop iteration but stopped",
                "before constructing an episode or stepping physics. The reviewed base",
                "runner owns its Episode through the imported CPU-smoke module. Only the",
                "adapter reference changes from `base.Episode` to `base.smoke.Episode`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
