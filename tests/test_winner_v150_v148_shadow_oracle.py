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


def test_v150_preregisters_one_shadow_only_displaced_event_trace() -> None:
    prereg = load("winner_v150_v148_shadow_oracle_preregistration.json")
    assert sha256(
        "winner_v150_v148_shadow_oracle_preregistration.json"
    ) == "3d4421a5e7041faa48cc2ac1603e53a970b49aaad1eebc475c701e1e6492f270"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V150_V148_SHADOW_ORACLE"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["cells"] == 1
    assert prereg["matrix"]["row"]["plant"] == "P30_ALL_JOINT"
    assert prereg["matrix"]["row"]["command_x_m_s"] == 0.074
    assert prereg["matrix"]["row"]["seed"] == 167_931_544
    assert prereg["checks"]["source_has_exact_single_displaced_event"]
    assert prereg["authority"]["one_cpu_shadow_cell"] is True
    assert prereg["authority"]["policy_change"] is False
    assert prereg["authority"]["training"] is False
