#!/usr/bin/env python3
"""Grade the Phase 2 z=0.002 tracking-margin post-training gates.

This wraps the generic Phase 2 post-training gate grader with thresholds that
match the z=0.002 tracking-margin recovery recipe:

- preserve x=0.08 motion with mean track ratio >= 0.25
- recover strict tracking margin to p95 <= 0.20 rad
- keep zero-command drift bounded
- keep corrected-envelope velocity excess at zero

It is read-only and does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import report_phase2_z005_post_training_gates as generic_gates


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATE_DECISION.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z002_tracking_margin_post_training_gate_decision.json"


def write_z002_markdown(payload: dict, path: Path) -> None:
    generic_gates.write_markdown(payload, path)
    with path.open("a") as handle:
        handle.write("\n")
        handle.write("## z=0.002 Tracking-Margin Interpretation\n\n")
        handle.write(
            "This decision is only a parent-selection gate for the next terrain/push curriculum rung. "
            "It is not a robot promotion gate and does not authorize grounded replay.\n\n"
        )
        handle.write(
            "A pass means the run recovered the z=0.002 tracking margin without freezing below "
            "the motion floor. It must still clear later staged domain-randomization gates before "
            "hardware validation can be considered.\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", help="Path to *_post_training_seed_gates.json")
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--max-tracking-p95", type=float, default=0.20)
    parser.add_argument("--max-velocity-excess", type=float, default=0.0)
    parser.add_argument("--min-track-ratio", type=float, default=0.25)
    parser.add_argument("--max-abs-vx-x0", type=float, default=0.005)
    parser.add_argument("--min-push-success", type=float, default=0.95)
    args = parser.parse_args()

    payload = generic_gates.collect(args)
    manifest = json.loads(Path(args.input_json).read_text())
    payload["status"] = payload["status"].replace(
        "PHASE2_POST_TRAINING_GATES", "PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES"
    )
    payload["workflow"] = manifest.get("workflow")
    payload["gate_role"] = "z002_tracking_margin_parent_selection"
    payload["promotion_allowed"] = payload["status"] == "PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES"
    payload["robot_touched"] = False
    payload["ssh_used"] = False
    payload["deploy_performed"] = False
    payload["training_started"] = False

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_z002_markdown(payload, output_md)
    print(payload["status"])
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
