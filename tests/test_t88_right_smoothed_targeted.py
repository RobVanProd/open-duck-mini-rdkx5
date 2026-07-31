from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t88_preregisters_only_changed_half_targeted_cells() -> None:
    value = load("t88_right_smoothed_targeted_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T88_RIGHT_SMOOTHED_TARGETED_BEHAVIOR"
    )
    assert value["failed_checks"] == []
    assert [item["condition_index"] for item in value["conditions"]] == [
        2,
        4,
    ]
    assert len(value["policies"]) == 1
    assert value["policies"][0]["checkpoint_id"] == (
        "T87_RIGHT_SMOOTHED_HALF"
    )
    assert value["terminal_final_policy"][
        "byte_exact_to_t84_rolling_final"
    ]
    assert value["matrix"]["maximum_new_cells"] == 16
    assert value["matrix"]["combined_cells"] == 32
    assert value["matrix"]["no_new_final_cells"]
    assert value["matrix"]["no_checkpoint_selection"]
    assert all(
        evidence["cells"] == 8 and evidence["green_cells"] == 8
        for evidence in value["immutable_terminal_evidence"]
    )
    assert value["authority"]["one_targeted_cpu_matrix"]
    assert not value["authority"]["training"]
    assert not value["authority"]["gate5"]


def test_t88_result_if_present() -> None:
    path = ANALYSIS / "t88_right_smoothed_targeted_result.json"
    if not path.is_file():
        pytest.skip("T88 targeted behavior has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["new_cells"] <= 16
    assert summary["combined_cells"] <= 32
    if value["status"].startswith("PASS_"):
        assert summary["new_green_cells"] == 16
        assert summary["combined_green_cells"] == 32
        assert summary["all_green"]
        assert value["authority"]["full_r2_revalidation_preregistration"]
    else:
        assert not summary["all_green"]
        assert not value["authority"]["full_r2_revalidation_preregistration"]
    assert not value["authority"]["training"]
    assert not value["authority"]["gate5"]
