from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v110_preregistration_freezes_complete_16_cell_screen() -> None:
    path = (
        ROOT
        / "outputs/analysis/winner_v110_pitch_guard_behavior_preregistration.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "7698a551fa88cf1b0ca09503f383242e8735ce30436c189876bf4bde4b11b6d0"
    )
    assert payload["status"] == (
        "PREREGISTERED_WINNER_V110_PITCH_GUARD_BEHAVIOR"
    )
    assert payload["failed_checks"] == []
    assert payload["matrix"]["cells"] == 16
    assert payload["matrix"]["sha256"] == (
        "4297e953d16298f62159d7d3b33dc358f0813dd8f3d0d45d10c6963f4ba1ab3b"
    )
    assert len(payload["policies"]) == 2
    assert {
        row["plant"] for row in payload["matrix"]["rows"]
    } == {"P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"}
    assert {
        row["command_x_m_s"] for row in payload["matrix"]["rows"]
    } == {0.0, 0.074, 0.077, 0.08}
    assert payload["gate"]["per_joint_peak_current_a_max"] == 2.5
    assert payload["gate"]["per_joint_peak_torque_nm_max"] == 1.91229675
    assert payload["gate"]["strict_overcurrent_max_consecutive_ticks"] == 99
    assert payload["authority"]["formal_behavior_cells_authorized"] == 16
    assert payload["authority"]["hosted_training_authorized"] is False
    assert payload["authority"]["gate5_authorized"] is False
