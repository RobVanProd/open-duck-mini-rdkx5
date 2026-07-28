from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t89_preregisters_diagnostic_remainder_only() -> None:
    value = load("t89_terminal_final_r2_remainder_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T89_TERMINAL_FINAL_R2_REMAINDER_DIAGNOSTIC"
    )
    assert value["failed_checks"] == []
    assert value["interpretation"]["diagnostic_only"]
    assert value["interpretation"][
        "single_checkpoint_cannot_satisfy_persistence"
    ]
    assert [item["condition_index"] for item in value["conditions"]] == (
        list(range(5, 21))
    )
    assert value["matrix"]["maximum_new_cells"] == 128
    assert value["matrix"]["cells_per_condition"] == 8
    assert value["matrix"]["strictly_sequential_conditions"]
    assert value["matrix"]["stop_after_first_failed_condition"]
    immutable = value["immutable_conditions_one_through_four"]
    assert immutable["cells"] == 32
    assert immutable["green_cells"] == 32
    assert value["authority"]["one_cpu_diagnostic_remainder"]
    assert not value["authority"]["training"]
    assert not value["authority"]["candidate_promotion"]
    assert not value["authority"]["gate5"]


def test_t89_result_if_present() -> None:
    path = ANALYSIS / "t89_terminal_final_r2_remainder_result.json"
    if not path.is_file():
        pytest.skip("T89 remainder has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["new_cells"] == (
        8 * summary["completed_new_conditions"]
    )
    assert summary["combined_cells"] == summary["new_cells"] + 32
    if value["status"].startswith("PASS_"):
        assert summary["combined_cells"] == 160
        assert summary["combined_green_cells"] == 160
        assert summary["terminal_final_all_twenty_green"]
        assert value["authority"][
            "persistence_stabilization_cpu_contract_preregistration"
        ]
    else:
        assert summary["first_failed_condition"] is not None
        assert not value["authority"][
            "persistence_stabilization_cpu_contract_preregistration"
        ]
    assert not value["authority"]["training"]
    assert not value["authority"]["candidate_promotion"]
    assert not value["authority"]["gate5"]
