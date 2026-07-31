#!/usr/bin/env python3
"""Attribute the Winner-v15 CPU proof's float32 cancellation failure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v15_pitch_margin_cpu_proof_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V15_PITCH_MARGIN_CPU_PROOF_FAILURE_ATTRIBUTION_20260721.md"
RUNNER = ROOT / "tools/run_winner_v15_pitch_margin_cpu_contract.py"
OBJECTIVE = ROOT / "patches/winner_v15_pitch_margin_support.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite CPU proof attribution: {path}")
    objective_source = OBJECTIVE.read_text(encoding="utf-8")
    if (
        'terminal_bonus = rewards - np.where(valid, expected, np.float32(0.0))'
        not in objective_source
        or 'rewards[valid] - terminal_bonus[valid]' not in objective_source
    ):
        raise ValueError("failed reward-proof algebra is no longer attributable")
    runner_source = RUNNER.read_text(encoding="utf-8")
    if '"enabled_reward_formula_bit_exact": reward_proof[' not in runner_source:
        raise ValueError("failed CPU proof check is no longer attributable")
    payload = {
        "schema_version": "winner_v15.pitch_margin_cpu_proof_failure_attribution.v1",
        "status": "INVALID_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT_PROOF",
        "decision": "CORRECT_ONLY_SETTLED_BONUS_REWARD_PROOF_AND_FRESHLY_PREREGISTER",
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": 29836320395,
            "github_run_attempt": 1,
            "github_run_head_sha": "b537bc7275c9b465125dac04d9ddf1d6b076d2a5",
            "github_artifact_id": 8497528079,
            "github_artifact_name": "winner-v15-pitch-margin-cpu-29836320395",
            "github_artifact_digest": "sha256:8647ac0b57592e8a4f91896526b4ff84a8f9f3561da80db480639afc09684223",
            "raw_result_sha256": "b53e40c8c81c53a56d36cee61ce917ae7ab210ae93e910a9fc7909e21c416c7a",
        },
        "failure": {
            "reported_status": "HOLD_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT",
            "only_failed_check": "enabled_reward_formula_bit_exact",
            "cause": (
                "The proof added the 250.0 settled bonus in float32, subtracted the "
                "bonus, and required recovery of the pre-bonus fractional reward bit "
                "exactly. Float32 addition to 250 discards low fractional bits, so the "
                "subtraction cannot reconstruct them even though the original reward "
                "assignment is correct."
            ),
            "correction": (
                "Construct the expected final reward directly: analytic pitch-margin "
                "reward on every valid transition, plus float32(250.0) only at the "
                "observed settled-bonus indices; compare that array bit-exactly."
            ),
            "objective_semantics_change": False,
        },
        "substantive_checks": {
            "all_other_checks_passed": True,
            "default_off_bit_exact": True,
            "enabled_transition_action_episode_observation_bit_exact": True,
            "penalty_formula_bit_exact": True,
            "nonzero_penalty_count": 5911,
            "valid_transition_count": 18243,
            "all_stage2_gradients_nonzero": True,
            "all_stage2_leaves_changed": True,
            "stage1_tree_bit_exact_frozen": True,
            "onnx_contract_passed": True,
        },
        "execution": {
            "contract_optimizer_updates": 1,
            "support_training_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "support_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one freshly preregistered proof-corrected CPU contract",
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v15 pitch-margin CPU proof failure attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- GitHub run / artifact: `29836320395 / 8497528079`",
                "- Contract / training updates: `1 / 0`",
                "- Formal support / locomotion / robot access: `0 / 0 / 0`",
                "",
                "All substantive mechanics checks passed. The sole failure was a proof",
                "that tried to recover a fractional reward after adding and subtracting",
                "the 250-point float32 terminal bonus. The only permitted change builds",
                "the expected final reward directly and freshly preregisters the same",
                "objective contract. No reward, policy, population, or threshold changes.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
