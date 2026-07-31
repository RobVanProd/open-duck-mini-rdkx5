from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v24_support_regression_attribution.json"


def test_attribution_is_exact_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION"
    assert value["decision"] == (
        "AUTHORIZE_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    half, final = value["checkpoint_comparisons"]
    assert (half["winner_v22_physical_support_failures"], final["winner_v22_physical_support_failures"]) == (15, 14)
    assert (half["winner_v24_physical_support_failures"], final["winner_v24_physical_support_failures"]) == (20, 20)
    assert (half["added_failure_count"], final["added_failure_count"]) == (5, 6)
    assert (half["recovered_failure_count"], final["recovered_failure_count"]) == (0, 0)
    assert half["shared_failure_onset_delta_ticks_v24_minus_v22"]["maximum"] < 0
    assert final["shared_failure_onset_delta_ticks_v24_minus_v22"]["maximum"] < 0
    assert all(value["checks"].values())
    assert value["execution"] == {
        "new_simulation_cells": 0,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_attribution_source_manifest_is_exact_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        assert item["hash_mode"] == "lf"
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert observed == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]


def test_attribution_selects_diagnostic_not_training() -> None:
    source = (
        ROOT / "tools/build_winner_v24_support_regression_attribution.py"
    ).read_text(encoding="utf-8")
    assert '"new_simulation_cells": 0' in source
    assert '"optimizer_updates": 0' in source
    assert '"execution_now": False' in source
    assert "same_state_directional_support_control" in source
    assert "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION" not in source
    assert "--hardware-authorized" not in source
