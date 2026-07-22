from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/analysis/winner_v24_gae_one_ulp_attribution.json"
BUILDER = ROOT / "tools/build_winner_v24_gae_one_ulp_attribution.py"


def test_attribution_is_read_only_and_prospective() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "np.spacing(np.float32(250.0))" in source
    assert '"old_result_rewritten": False' in source
    assert '"threshold_relaxed": False' in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source


def test_attribution_result_is_exact_when_present() -> None:
    if not OUTPUT.exists():
        return
    value = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V24_GAE_ONE_ULP_ATTRIBUTION"
    assert value["decision"] == "AUTHORIZE_BASELINE_ANCHORED_SYMMETRIC_FAILURE_CPU_CONTRACT_ONLY"
    assert value["evidence"]["return_error_over_ulp"] == 1.0
    assert value["execution"]["new_simulation_cells"] == 0
    assert value["execution"]["optimizer_updates"] == 0
