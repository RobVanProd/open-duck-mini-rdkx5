#!/usr/bin/env python3
"""Preregister V157's dual-checkpoint nominal persistence matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v157_dual_checkpoint_nominal.py"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V155_RESULT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
V156_CORRECTION = (
    ANALYSIS
    / "winner_v156_state_triggered_causal_behavior_reporting_correction.json"
)
V141_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
OUTPUT = (
    ANALYSIS / "winner_v157_dual_checkpoint_nominal_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V157_DUAL_CHECKPOINT_NOMINAL_PREREGISTRATION_20260725.md"
)


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
            raise FileExistsError(f"refusing to overwrite V157: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v121 = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    v155 = json.loads(V155_RESULT.read_text(encoding="utf-8"))
    v156 = json.loads(V156_CORRECTION.read_text(encoding="utf-8"))
    policy = Path(v155["artifact"]["deployed"]["path"])
    paths = {
        "runner": RUNNER,
        "v121_nominal_result": V121_RESULT,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v141_result": V141_RESULT,
        "v155_result": V155_RESULT,
        "v156_reporting_correction": V156_CORRECTION,
        "v141_runner": V141_RUNNER,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_final_policy": policy,
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
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
    p30_x0 = v141["new_final_cells"][0]
    new_rows = [
        row
        for row in final_rows
        if not (
            str(row["plant"]) == "P30_ALL_JOINT"
            and float(row["command_x_m_s"]) in {0.0, 0.074}
        )
    ]
    checks = {
        "v155_graph_contract_green": (
            v155.get("status")
            == "PASS_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
            and v155.get("failed_checks") == []
        ),
        "v156_causal_cell_green": (
            v156.get("status")
            == "PASS_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_"
            "REPORTING_CORRECTION"
            and v156.get("failed_checks") == []
            and v156.get("decision")
            == "EARN_V157_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
        ),
        "frozen_half_exact_8_of_8": (
            reused_half["all_eight_cells_pass"]
            and reused_half["passing_cells"] == 8
            and reused_half["worst_peak_torque_nm"] <= 1.91229675
        ),
        "reused_p30_x0_green_and_candidate_exact_zero": (
            p30_x0["pass"]
            and float(p30_x0["identity"]["command_x_m_s"]) == 0.0
            and v155["checks"]["x0_deadband_remains_exact"]
        ),
        "complete_final_matrix_exact_8": (
            len(final_rows) == 8
            and {float(row["command_x_m_s"]) for row in final_rows}
            == {0.0, 0.074, 0.077, 0.08}
            and len({str(row["plant"]) for row in final_rows}) == 2
        ),
        "remaining_new_rows_exact_6": (
            len(new_rows) == 6
            and {
                (str(row["plant"]), float(row["command_x_m_s"]))
                for row in new_rows
            }
            == {
                ("P30_ALL_JOINT", 0.077),
                ("P30_ALL_JOINT", 0.08),
                ("P31_34_PITCH_WITH_P30_NONPITCH", 0.0),
                ("P31_34_PITCH_WITH_P30_NONPITCH", 0.074),
                ("P31_34_PITCH_WITH_P30_NONPITCH", 0.077),
                ("P31_34_PITCH_WITH_P30_NONPITCH", 0.08),
            }
        ),
        "sequential_stop_at_first_failure": True,
        "training_oracle_deployment_and_robot_disabled": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v157.dual_checkpoint_nominal_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
            if not failed
            else "HOLD_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
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
                "mechanism": (
                    "V140 plus frozen velocity-gated phase/contact "
                    "right-ankle residual"
                ),
                "reused_cells": 2,
                "new_cells": 6,
            },
            "why_not_cherry_pick": (
                "the half remains byte-identical under the V141 ruling; "
                "the final is one frozen graph tested across every cell"
            ),
        },
        "matrix": {
            "reused_half_cells": 8,
            "reused_final_cells": [
                {
                    "plant": "P30_ALL_JOINT",
                    "command_x_m_s": 0.0,
                    "source": "V141 exact-zero cell",
                },
                {
                    "plant": "P30_ALL_JOINT",
                    "command_x_m_s": 0.074,
                    "source": "V156 corrected causal cell",
                },
            ],
            "new_final_rows": new_rows,
            "combined_required": 16,
            "stop": "stop after the first failing new final cell",
        },
        "pass_rule": {
            "combined": (
                "reused half 8/8 plus reused final 2/2 plus new final 6/6"
            ),
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
            "the first new final-cell failure closes the velocity-gated "
            "phase residual; do not alter its feature, threshold, phase, "
            "contact, radius, amplitude, or graph"
        ),
        "green_followup": (
            "a combined 16/16 result earns only preregistration of the "
            "frozen offline robustness ladder and RDK contract alignment; "
            "no deployment or Gate 5"
        ),
        "authority": {
            "new_final_behavior_cells": 6 if not failed else 0,
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
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V157 dual-checkpoint nominal preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Reuse frozen half 8/8 and two final cells; run six remaining "
        "final cells sequentially.\n"
        "- Stop at first failure. No training, oracle, Colab, deployment, "
        "Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
