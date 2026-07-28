from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t49_preregisters_only_missing_combined_cell() -> None:
    value = load(
        "t49_missing_combined_adapter_control_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_T49_MISSING_COMBINED_ADAPTER_CONTROL"
    )
    assert value["failed_checks"] == []
    assert [item["variant_id"] for item in value["completed_cells"]] == [
        "FINAL_WITH_HALF_CORE",
        "FINAL_WITH_HALF_HEAD",
    ]
    assert value["variant"]["variant_id"] == (
        "FINAL_WITH_HALF_CORE_HEAD"
    )
    assert value["variant"]["semantically_equals_half_endpoint"]
    assert value["authority"]["execute_one_missing_cpu_cell"]
    assert not value["authority"]["retry_completed_cells"]
    assert not value["authority"]["gate5"]


def test_t49_result_aggregates_three_cells_if_present() -> None:
    path = ANALYSIS / "t49_missing_combined_adapter_control_result.json"
    if not path.is_file():
        pytest.skip("formal T49 missing cell has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["summary"]["prior_formal_behavior_cells_reused"] == 2
    assert value["summary"]["new_formal_behavior_cells"] == 1
    assert value["summary"]["aggregate_formal_behavior_cells"] == 3
    assert value["summary"]["valid_cells"] == 3
    if value["status"] == (
        "PASS_T49_COMPLETED_ADAPTER_ONE_SUBBLOCK_CAUSE"
    ):
        assert value["summary"][
            "selected_mechanism_variant_diagnostic"
        ] in {"FINAL_WITH_HALF_CORE", "FINAL_WITH_HALF_HEAD"}
        assert value["authority"]["uniform_transform_preregistration"]
    else:
        assert not value["authority"]["uniform_transform_preregistration"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]
