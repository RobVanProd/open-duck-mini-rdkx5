from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v163_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v163_feasibility_preserving_falsifier_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "44904cbe0f2e53cd7955fb3163971cc6025a81e13031e6273c65f8a1ff4d2d9e"
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
    )
    assert value["failed_checks"] == []
    assert value["proposal"]["new_training"] is False
    assert value["proposal"]["aggregated_ppo_iterations"] == 32
    assert value["backtracking"]["alphas_descending"] == [
        1.0,
        0.5,
        0.25,
        0.125,
        0.0625,
        0.03125,
    ]
    assert value["backtracking"]["minimum_nontrivial_alpha"] == 1.0 / 32
    assert value["backtracking"]["retry_or_finer_ladder"] is False
    assert value["matrix"]["moving_cells"] == 6
    assert value["matrix"]["x0_cells_reused"] == 2
    assert value["authority"]["hosted_training"] is False


def test_v163_result_when_present() -> None:
    path = (
        ANALYSIS / "winner_v163_feasibility_preserving_falsifier_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER",
        "HOLD_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER",
    }
    assert value["cpu_only"] is True
    assert 1 <= value["summary"]["alphas_attempted"] <= 6
    assert value["authority"]["training"] is False
    assert value["authority"]["hosted_training"] is False
    if value["status"].startswith("PASS_"):
        assert value["accepted"]["all_eight_nominal_cells_pass"]
        assert value["accepted"]["source_reserve_strictly_improved"]
        assert value["decision"] == (
            "EARN_V164_FEASIBILITY_PRESERVING_UPDATE_CPU_CONTRACT_ONLY"
        )
    else:
        assert value["decision"] == (
            "CLOSE_FEASIBILITY_PRESERVING_FIRST_PROPOSAL_NO_RETRY"
        )
