from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v162_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "winner_v162_uniform_trust_nominal_preregistration.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "084ec5ee5dabba05e36b9117c8db6f1c4806fcc3cf8ddcce8ca3e79935887cce"
    )
    assert result["status"] == (
        "PREREGISTERED_WINNER_V162_UNIFORM_TRUST_NOMINAL"
    )
    assert result["failed_checks"] == []
    assert result["matrix"]["cells"] == 16
    assert result["authority"]["training"] is False


def test_v162_result_when_present() -> None:
    path = ANALYSIS / "winner_v162_uniform_trust_nominal_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "3a9fe947295905df9775496cd394b07d08006b67642b4355acfa5ffe0ce870f6"
    )
    assert result["status"] == "HOLD_WINNER_V162_UNIFORM_TRUST_NOMINAL"
    assert result["failed_checks"] == [
        "both_checkpoints_all_eight_cells_pass"
    ]
    assert result["summary"]["completed_cells"] == 4
    assert result["summary"]["passing_cells"] == 3
    assert result["cells"][-1]["identity"]["command_x_m_s"] == 0.08
    assert result["cells"][-1]["failure_reasons"] == [
        "torque_peak_at_most_1p91229675_nm"
    ]
    assert result["decision"] == (
        "CLOSE_UNIFORM_TRUST_PROJECTION_NO_ALPHA_RETRY"
    )
    assert result["authority"]["training"] is False
