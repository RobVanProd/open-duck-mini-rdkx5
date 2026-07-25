from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(ROOT / "tools"))

import compose_winner_v144_shadow_oracle_evaluator as v144  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v144_composition_is_default_on_and_shadow_capable() -> None:
    source = (
        ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"
    ).read_text(encoding="utf-8")
    composed = v144.compose(source)
    compile(composed, "closed_loop_sim_eval_v144_shadow_oracle.py", "exec")
    assert "exact_torque_oracle_apply: bool = True" in composed
    assert composed.count(
        "projected_action, exact_oracle_tick = ("
    ) == 2
    assert "if config.exact_torque_oracle_apply:" in composed
    assert "action = projected_action" in composed
    assert '"apply": bool(config.exact_torque_oracle_apply)' in composed


def test_v144_preregisters_one_read_only_causal_trace() -> None:
    prereg = load("winner_v144_shadow_oracle_preregistration.json")
    assert sha256("winner_v144_shadow_oracle_preregistration.json") == (
        "f4020729716f69bb7a643d6ba98b03f3ac7d2442c8921eb9dc5acd0b99aa3c62"
    )
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V144_SHADOW_ORACLE_CAUSAL_SCREEN"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["cells"] == 1
    assert prereg["matrix"]["ticks"] == 600
    assert prereg["method"]["policy_action_committed"] == (
        "unmodified V140 action"
    )
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v144_v2_corrects_only_preexecution_hash_map() -> None:
    prereg = load("winner_v144_shadow_oracle_preregistration_v2.json")
    assert sha256(
        "winner_v144_shadow_oracle_preregistration_v2.json"
    ) == "f9a501840d5a82c0df86614fb57faabbf96f68b069b980621d7dbd71106643eb"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V144_SHADOW_ORACLE_CAUSAL_SCREEN"
    )
    assert prereg["failed_checks"] == []
    assert prereg["supersedes"]["artifact"] == (
        "winner_v144_shadow_oracle_preregistration.json"
    )
    assert "observed-hash map omitted" in prereg["supersedes"]["reason"]
    assert prereg["matrix"]["cells"] == 1
    assert prereg["method"]["policy_action_committed"] == (
        "unmodified V140 action"
    )
