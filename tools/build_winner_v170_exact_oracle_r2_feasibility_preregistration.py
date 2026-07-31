#!/usr/bin/env python3
"""Freeze the one-cell V170 exact-oracle first-R2 feasibility screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v170_exact_oracle_r2_feasibility_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_PREREGISTRATION_20260725.md"
)
RUNNER = TOOLS / "run_winner_v170_exact_oracle_r2_feasibility.py"
V126_RUNNER = TOOLS / "run_winner_v126_exact_oracle_behavior.py"
V131_RUNNER = TOOLS / "run_winner_v131_two_fit_oracle_behavior.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V131_CONTRACT = ANALYSIS / "winner_v131_two_fit_oracle_cpu_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V160_RESULT = ANALYSIS / "winner_v160_remaining_shadow_census_result.json"
V168_RESULT = (
    ANALYSIS / "winner_v168_fit_conditioned_policy_bank_cpu_result.json"
)
V169_RESULT = ANALYSIS / "winner_v169_v128_final_r2_anchor_result.json"
PROJECTOR = TOOLS / "exact_torque_oracle_two_fit.py"


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
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    v131_contract = json.loads(V131_CONTRACT.read_text(encoding="utf-8"))
    v131_result = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v160 = json.loads(V160_RESULT.read_text(encoding="utf-8"))
    v168 = json.loads(V168_RESULT.read_text(encoding="utf-8"))
    v169 = json.loads(V169_RESULT.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V170: {path}")

    row = {
        "calibration_ticks": 0,
        "checkpoint_id": "V140_SELECTED_FINAL",
        "plant": "P31_34_PITCH_WITH_P30_NONPITCH",
        "command_x_m_s": 0.077,
        "seed": 167931544,
        "duration_ticks": 600,
        "home_return_ticks": 0,
        "oracle_schedule_ticks": None,
        "configuration": {"floor_friction": 0.5},
        "policy_sha256": v140["artifacts"]["selected_deployed"]["sha256"],
        "step": 2_007_040,
        "transport": {
            "additional_action_delay_ticks": 0,
            "imu_delay_ticks": 0,
            "native_quantization": False,
            "sensor_noise_scales": None,
        },
    }
    input_paths = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "v126_runner": V126_RUNNER,
        "v131_runner": V131_RUNNER,
        "two_fit_projector": PROJECTOR,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v131_cpu_contract": V131_CONTRACT,
        "v131_behavior_result": V131_RESULT,
        "v140_result": V140_RESULT,
        "v160_result": V160_RESULT,
        "v168_result": V168_RESULT,
        "v169_result": V169_RESULT,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_policy": policy,
    }
    checks = {
        "v131_two_fit_oracle_contract_green": (
            v131_contract.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT"
            and not v131_contract.get("failed_checks")
        ),
        "v131_nominal_oracle_screen_already_complete": (
            v131_result.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
        ),
        "v140_policy_exact": (
            sha256(policy)
            == "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
            == row["policy_sha256"]
        ),
        "v160_localizes_remaining_v140_events": (
            v160.get("aggregate", {}).get("actual_violation_events") == 9
            and v160.get("aggregate", {}).get("empty_intersection_events")
            == 0
        ),
        "v168_closes_fit_conditioned_full_actor": (
            v168.get("decision")
            == "CLOSE_FIT_CONDITIONED_TWO_POLICY_FULL_ACTOR_SMOKE_NO_RETRY"
        ),
        "v169_first_r2_anchor_failed_behavior": (
            v169.get("decision") == "CLOSE_V128_FINAL_AS_ROBUSTNESS_ANCHOR"
            and not v169.get("checks", {}).get("both_behavior_matrices_pass")
        ),
        "first_r2_condition_exact": row["configuration"]
        == {"floor_friction": 0.5},
        "representative_earliest_failure_cell_exact": (
            row["plant"] == "P31_34_PITCH_WITH_P30_NONPITCH"
            and row["command_x_m_s"] == 0.077
            and row["duration_ticks"] == 600
        ),
        "one_cell_only": True,
        "oracle_apply_true": True,
        "cpu_only_no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v170.exact_oracle_r2_feasibility_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY"
            if not failed
            else "HOLD_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_"
            "PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "external_inputs": {
            "playground": v126["external_inputs"]["playground"],
            "evaluator_root": str(evaluator_root),
            "policy": str(policy),
        },
        "matrix": {"cells": 1, "rows": [row]},
        "causal_reconciliation": {
            "accepted": (
                "the exact two-fit simulator oracle is the cheapest decisive "
                "falsifier for whether a nearby torque-safe gait exists"
            ),
            "not_repeated": (
                "V121 nominal two-fit oracle behavior already passed in V131; "
                "V132-V168 subsequently tested and closed the derived teacher "
                "and actor-edit routes"
            ),
            "current_question": (
                "can the V140 gait remain a complete forward walk at the first "
                "frozen R2 condition when the exact oracle action is applied?"
            ),
        },
        "method": {
            "policy": "bit-exact V140 selected final",
            "active_fit": "P31/34 pitch with P30 non-pitch",
            "shadow_fit": "P30 all-joint",
            "oracle": "exact two-fit all-tick projection, applied",
            "dynamics": {"floor_friction": 0.5},
            "command_x_m_s": 0.077,
            "duration_ticks": 600,
            "selection_weight": 0,
        },
        "pass_rule": [
            "one complete contiguous 600-tick CPU trace with exact floor-friction readback",
            "duration, gait, positive-forward-motion, tracking, saturation, rate, and envelope gates all pass unchanged",
            "all 600 applied-oracle rows are robust-safe for both fits",
            "zero two-fit empty intersections",
            "strict measured torque peak <= 1.91229675 N.m and current peak <= 2.5 A",
        ],
        "green_decision": (
            "earn only V171 offline safe-architecture design; no training, "
            "candidate, later R2 condition, or Gate 5 authority"
        ),
        "stop_rule": (
            "a valid cell failure closes the premise that a torque-safe policy "
            "sufficiently near the V140 gait survives the first R2 condition; "
            "do not run another fit, command, seed, projection, or training "
            "retry in this formulation"
        ),
        "authority": {
            "one_cpu_screen": not failed,
            "safe_architecture_design": False,
            "training": False,
            "hosted_training": False,
            "candidate_selection": False,
            "later_r2_condition": False,
            "full_matrix": False,
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
        "# Winner V170 exact-oracle first-R2 feasibility preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One CPU cell: V140 selected final, P31/34, x=.077, floor "
        "friction .5, 600 ticks.\n"
        "- The exact two-fit oracle is applied; all behavior and physical "
        "limits remain unchanged.\n"
        "- V121 nominal oracle work is not repeated because V131 already "
        "completed it and later teacher/actor routes are closed.\n"
        "- Green earns architecture design only. Failure closes this nearby "
        "safe-gait premise without a second cell or hosted run.\n"
        "- No training, Colab, hardware, motion, candidate selection, later "
        "R2 condition, or Gate 5.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
