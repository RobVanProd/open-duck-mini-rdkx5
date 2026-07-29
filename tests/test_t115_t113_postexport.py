from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t115_result_when_present() -> None:
    path = ANALYSIS / "t115_t113_postexport_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if not value["failed_checks"]:
        assert value["status"] == "PASS_T115_T113_POSTEXPORT_TRANSFORM"
        assert value["decision"] == (
            "EARN_T116_ALWAYS_ON_TRAINTHROUGH_NOMINAL_PREREGISTRATION_ONLY"
        )
        assert value["execution"]["formal_behavior_cells"] == 0
        assert all(value["checks"].values())
