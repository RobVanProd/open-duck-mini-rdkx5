from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v109_preregistration_freezes_the_16_cell_recurrent_source_screen() -> None:
    path = ROOT / "outputs/analysis/winner_v109_recurrent_source_preregistration.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "71b98bd3bfad5c0fe74c645905b0fb5101c7c454154d587b88896d1750f1004d"
    )
    assert payload["status"] == (
        "PREREGISTERED_WINNER_V109_RECURRENT_SOURCE_SCREEN"
    )
    assert payload["failed_checks"] == []
    assert payload["matrix"]["cells"] == 16
    assert payload["matrix"]["sha256"] == (
        "65619603579540a75006a0923c0fe6ab35499c5c02d92c91d91b58bbaa683406"
    )
    assert len(payload["policies"]) == 2
    assert {
        row["checkpoint_id"] for row in payload["matrix"]["rows"]
    } == {"R64_RECURRENT_HALF", "R64_RECURRENT_FINAL"}
    assert {row["plant"] for row in payload["matrix"]["rows"]} == {
        "P30_ALL_JOINT",
        "P31_34",
    }
    assert {
        row["command_x_m_s"] for row in payload["matrix"]["rows"]
    } == {0.0, 0.074, 0.077, 0.08}
    assert payload["authority"]["formal_behavior_cells_authorized"] == 16
    assert payload["authority"]["hosted_training_authorized"] is False
    assert payload["authority"]["robot_clearance"] is False


def test_v109_uses_the_prospective_manufacturer_backed_current_rule() -> None:
    payload = json.loads(
        (
            ROOT / "outputs/analysis/winner_v109_recurrent_source_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["current_gate"] == {
        "conversion_nm_per_a": 0.784532,
        "per_joint_peak_current_a_max": 2.5,
        "rated_current_p95_a": 0.65,
        "rated_current_p95_role": "reported diagnostic only",
        "strict_overcurrent_max_consecutive_ticks": 99,
        "strict_overcurrent_threshold_a": 2.0,
    }
    assert payload["checks"]["prospective_current_rule_exact"] is True
