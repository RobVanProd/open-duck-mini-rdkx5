from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t175_preregistration_when_present() -> None:
    path = ANALYSIS / "t175_head_prefix_mean_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T175_HEAD_PREFIX_MEAN"
    assert value["failed_checks"] == []
    assert len(value["transform"]["head_initializers"]) == 2
    assert value["transform"]["tunable_parameters"] == 0
    assert value["prior_family_boundary"]["sets_disjoint"] is True
    assert value["authority"]["behavior"] is False


def test_t175_result_when_present() -> None:
    path = ANALYSIS / "t175_head_prefix_mean_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T175_HEAD_PREFIX_MEAN"
    assert value["failed_checks"] == []
    assert value["checks"]["all_head_arithmetic_exact"]
    assert value["checks"]["all_inactive_routes_bit_exact"]
    assert value["checks"]["all_x0_outputs_bit_exact"]
    assert value["execution"]["behavior_cells"] == 0
