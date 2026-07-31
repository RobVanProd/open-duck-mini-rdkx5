from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t48_preregisters_exact_three_cell_subblock_factorial() -> None:
    value = load(
        "t48_final_adapter_core_head_factorial_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL"
    )
    assert value["failed_checks"] == []
    assert value["execution_order"] == [
        "FINAL_WITH_HALF_CORE",
        "FINAL_WITH_HALF_HEAD",
        "FINAL_WITH_HALF_CORE_HEAD",
    ]
    assert value["groups"]["core"] == [
        "adapter_hidden_bias",
        "adapter_hidden_weight",
        "adapter_obs_weight",
    ]
    assert value["groups"]["head"] == [
        "adapter_bias",
        "adapter_weight",
    ]
    assert value["cell"]["condition"]["condition_index"] == 4
    assert value["cell"]["fit_id"] == "p30"
    assert value["cell"]["command_x_m_s"] == 0.077
    assert all(item["pass"] for item in value["variants"])
    assert not value["variants"][0]["semantically_equals_half_endpoint"]
    assert not value["variants"][1]["semantically_equals_half_endpoint"]
    assert value["variants"][2]["semantically_equals_half_endpoint"]
    assert value["authority"]["execute_three_cpu_cells"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t48_result_requires_three_valid_cells_if_present() -> None:
    path = ANALYSIS / "t48_final_adapter_core_head_factorial_result.json"
    if not path.is_file():
        pytest.skip("formal T48 factorial has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["summary"]["formal_behavior_cells"] == 3
    assert value["summary"]["valid_cells"] == 3
    if value["status"] == "PASS_T48_FINAL_ADAPTER_ONE_SUBBLOCK_CAUSE":
        assert value["summary"]["selected_mechanism_variant_diagnostic"] in {
            "FINAL_WITH_HALF_CORE",
            "FINAL_WITH_HALF_HEAD",
        }
        assert value["authority"]["uniform_transform_preregistration"]
    else:
        assert not value["authority"]["uniform_transform_preregistration"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]
