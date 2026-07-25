from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v141_preregistration_reuses_half_and_tests_final() -> None:
    prereg = load("winner_v141_projected_final_behavior_preregistration.json")
    assert sha256(
        "winner_v141_projected_final_behavior_preregistration.json"
    ) == "40ac2e58d9a8058697e81011f66051840bcc3f81fe278f44e0356e2f532709a0"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["reused_half_cells"] == 8
    assert len(prereg["matrix"]["new_final_rows"]) == 8
    assert prereg["candidate_pair"]["half"]["new_cells"] == 0
    assert prereg["candidate_pair"]["half"]["evidence"][
        "all_eight_cells_pass"
    ]
    assert prereg["authority"]["new_final_behavior_cells"] == 8
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["policy_deployment"] is False
