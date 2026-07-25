#!/usr/bin/env python3
"""Preregister the V141 projected-final CPU behavior screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
OUTPUT = ANALYSIS / "winner_v141_projected_final_behavior_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V141_PROJECTED_FINAL_BEHAVIOR_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "41cc51abb21dde2fde8fa4cbf36ad50212794fea0a38eb73b2c3705ee96ac034"
    ),
    "v121_nominal_result": (
        "8bdefb90032facb4a3f3f7c833e608d2b35dac958ac0fcc2bbbd393ddcbb6047"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "v140_projection_result": (
        "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    ),
    "composition_manifest": (
        "39e842470828208dfea08b17d936d3f0e6f0d45b8f9813a1edd139692e4a6f74"
    ),
    "composed_evaluator": (
        "1539ba18b5b207a15538a8a8611475f5c73bcd7164f2fe039cad8b279a587e43"
    ),
    "selected_final_policy": (
        "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V141: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v121 = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_nominal_result": sha256(V121_RESULT),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v140_projection_result": sha256(V140_RESULT),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_final_policy": sha256(policy),
    }
    reused_half = next(
        row
        for row in v121["per_checkpoint"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    final_rows = [
        row
        for row in v126["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_FINAL"
    ]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v140_projection_green": (
            v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
            and v140.get("decision")
            == "EARN_ONE_V141_DUAL_CHECKPOINT_BEHAVIOR_PREREGISTRATION"
        ),
        "frozen_half_prior_evidence_exact_8_of_8": (
            reused_half["all_eight_cells_pass"]
            and reused_half["passing_cells"] == 8
            and reused_half["worst_peak_torque_nm"] <= 1.91229675
        ),
        "new_final_matrix_exact_8": (
            len(final_rows) == 8
            and {float(row["command_x_m_s"]) for row in final_rows}
            == {0.0, 0.074, 0.077, 0.08}
            and len({str(row["plant"]) for row in final_rows}) == 2
        ),
        "no_half_rerun": True,
        "sequential_stop_at_first_failure": True,
        "training_and_oracle_disabled": True,
        "deployment_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v141.projected_final_behavior_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V141_PROJECTED_FINAL_BEHAVIOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "candidate_pair": {
            "half": {
                "policy": "V121_TRAIN_MATCHED_HALF unchanged",
                "policy_sha256": (
                    "d4f280e8ebb4accd5c5c983bbf83042ec0162647efb446f0f6c8bffda42bc17a"
                ),
                "evidence": reused_half,
                "new_cells": 0,
            },
            "final": {
                "policy": str(policy),
                "policy_sha256": input_hashes["selected_final_policy"],
                "v140_alpha": v140["summary"]["selected_alpha"],
                "new_cells": 8,
            },
            "why_not_cherry_pick": (
                "the previously green half remains byte-identical; the known "
                "failing final is repaired by an alpha selected only from the "
                "preexisting preservation constraint, before behavior"
            ),
        },
        "matrix": {
            "reused_half_cells": 8,
            "new_final_rows": final_rows,
            "combined_required": 16,
            "stop": "stop after the first failing new final cell",
        },
        "pass_rule": {
            "combined": "reused half 8/8 plus new projected final 8/8",
            "duration": "all new cells complete 600 ticks",
            "gait": "moving cells retain bilateral transitions and positive vx",
            "tracking": "pitch-chain p95 <=0.20 rad",
            "torque": "peak <=1.91229675 N.m",
            "current": "peak <=2.5 A and >2.0 A runs <=99 ticks",
            "envelopes": "zero saturation, G3 excess, and rate excess",
            "x0": "exact zero graph action",
            "state": "phase 0, h_in zero, previous_action zero",
        },
        "stop_rule": (
            "the first new final-cell failure closes preservation-projected "
            "actor; do not change alpha, preservation boundary, or graph path"
        ),
        "green_followup": (
            "a combined 16/16 result earns only RDK policy-contract alignment "
            "and golden-vector review; no deployment or Gate 5"
        ),
        "authority": {
            "new_final_behavior_cells": 8 if not failed else 0,
            "half_rerun_cells": 0,
            "training": False,
            "hosted_training": False,
            "oracle": False,
            "policy_deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V141 projected-final behavior preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Reuse the byte-identical V121 half's frozen 8/8 evidence; run "
        "eight projected-final cells only.\n"
        "- Stop at first failure. No alpha change, training, oracle, Colab, "
        "deployment, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
