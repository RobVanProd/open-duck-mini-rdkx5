from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from tools.run_winner_v109_recurrent_source_screen import (
    prospective_current_metrics,
)


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v109_preregistration_freezes_the_16_cell_recurrent_source_screen() -> None:
    path = ROOT / "outputs/analysis/winner_v109_recurrent_source_preregistration.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "b64578fa873d5397dfa96c4e089ec6757b255e30a69a90d2a353306d14933736"
    )
    assert payload["status"] == (
        "PREREGISTERED_WINNER_V109_RECURRENT_SOURCE_SCREEN"
    )
    assert payload["failed_checks"] == []
    assert payload["matrix"]["cells"] == 16
    assert payload["matrix"]["sha256"] == (
        "9835cd79c64dd1a2b7ccbd1cc05d91a6c1b31dcfef31faf7ab1d2bfdf85ef11e"
    )
    assert len(payload["policies"]) == 2
    assert {
        row["checkpoint_id"] for row in payload["matrix"]["rows"]
    } == {"R64_RECURRENT_HALF", "R64_RECURRENT_FINAL"}
    assert {row["plant"] for row in payload["matrix"]["rows"]} == {
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
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


def test_v109_current_gate_uses_peak_and_strict_consecutive_duration() -> None:
    force = np.zeros((600, 14), dtype=float)
    force[10:109, 0] = 2.1 * 0.784532
    metrics = prospective_current_metrics(force)
    assert metrics["pass"] is True
    assert metrics["worst_strict_over_2a_run_ticks"] == 99

    force[109, 0] = 2.1 * 0.784532
    metrics = prospective_current_metrics(force)
    assert metrics["pass"] is False
    assert metrics["checks"][
        "overcurrent_gt_2a_at_most_99_consecutive_ticks"
    ] is False


def test_v109_current_gate_keeps_rated_p95_diagnostic_only() -> None:
    force = np.full((600, 14), 0.7 * 0.784532, dtype=float)
    metrics = prospective_current_metrics(force)
    assert metrics["worst_p95_current_a_diagnostic_only"] > 0.65
    assert metrics["pass"] is True


def test_v109_current_gate_rejects_peak_above_manufacturer_limit() -> None:
    force = np.zeros((600, 14), dtype=float)
    force[40, 3] = 2.50001 * 0.784532
    metrics = prospective_current_metrics(force)
    assert metrics["pass"] is False
    assert metrics["checks"]["current_peak_at_most_2p5"] is False


def test_v109_result_rejects_the_behavioral_source_on_peak_current_only() -> None:
    path = ROOT / "outputs/analysis/winner_v109_recurrent_source_result.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "dd79fc3976e1e8aae37aba7a0838c20c2e10f34ab1337526c9eaea3d4860cf5b"
    )
    assert payload["status"] == "PASS_WINNER_V109_RECURRENT_SOURCE_SCREEN"
    assert payload["failed_validity_checks"] == []
    assert payload["decision"]["status"] == "REJECT_RECURRENT_SOURCE"
    assert payload["summary"]["passing_cells"] == 4
    assert payload["summary"]["failures_by_reason"] == {
        "current_peak_at_most_2p5": 12
    }
    assert payload["summary"]["worst_tracking_p95_rad"] < 0.20
    assert payload["summary"]["worst_peak_current_a"] > 2.5
    assert payload["summary"]["worst_strict_over_2a_run_ticks"] == 9
    assert payload["authority"]["gate5_authorized"] is False
    assert payload["authority"]["robot_clearance"] is False
