from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v15_pitch_margin_cpu_proof_failure_attribution.json"


def test_cpu_hold_is_attributed_to_proof_only() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "INVALID_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT_PROOF"
    assert value["decision"] == (
        "CORRECT_ONLY_SETTLED_BONUS_REWARD_PROOF_AND_FRESHLY_PREREGISTER"
    )
    assert value["failure"]["only_failed_check"] == "enabled_reward_formula_bit_exact"
    assert value["failure"]["objective_semantics_change"] is False
    assert value["substantive_checks"]["all_other_checks_passed"] is True
    assert value["substantive_checks"]["nonzero_penalty_count"] == 5911
    assert value["execution"]["contract_optimizer_updates"] == 1
    assert value["execution"]["support_training_updates"] == 0
    assert value["authority"]["robot_clearance"] is False
