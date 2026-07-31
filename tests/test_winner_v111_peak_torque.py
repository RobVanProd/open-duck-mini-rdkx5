from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v111_preregisters_cpu_smoke_only() -> None:
    path = (
        ROOT
        / "outputs/analysis/winner_v111_peak_torque_cpu_preregistration.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "a79f0dfbb9ca11c194767f4f7bb91dfda200d1b1397654ed125495cad071c9bb"
    )
    assert payload["status"] == (
        "PREREGISTERED_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
    )
    assert payload["failed_checks"] == []
    assert payload["objective"]["threshold_nm"] == 1.91229675
    assert payload["objective"]["scale"] == -1000.0
    assert payload["objective"]["default_off_scale"] == 0.0
    assert payload["cpu_smoke"]["required_exports"] == [0, 1024]
    assert payload["authority"]["cpu_smoke_authorized"] is True
    assert payload["authority"]["hosted_training_authorized"] is False
    assert payload["authority"]["gate5_authorized"] is False
