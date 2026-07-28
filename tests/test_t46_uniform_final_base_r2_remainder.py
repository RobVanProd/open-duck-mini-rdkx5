from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t46_preregisters_only_r2_conditions_four_to_twenty() -> None:
    value = load(
        "t46_uniform_final_base_r2_remainder_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_T46_UNIFORM_FINAL_BASE_R2_REMAINDER"
    )
    assert value["failed_checks"] == []
    assert value["prior_qualification"]["formal_cells"] == 48
    assert value["prior_qualification"]["green_cells"] == 48
    assert value["matrix"]["condition_indices"] == list(range(4, 21))
    assert value["matrix"]["maximum_cells"] == 272
    assert value["matrix"]["both_checkpoints_required"]
    assert not value["matrix"]["checkpoint_cherry_pick"]
    assert not value["matrix"]["reuse_prior_condition_evidence"]
    assert value["authority"]["execute_one_272_cell_cpu_remainder"]
    assert not value["authority"]["gate5_hardware"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t46_result_requires_all_272_cells_if_present() -> None:
    path = ANALYSIS / "t46_uniform_final_base_r2_remainder_result.json"
    if not path.is_file():
        pytest.skip("formal T46 remainder has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["completed_cells"] == (
        16 * summary["completed_conditions"]
    )
    if value["status"].startswith("PASS_"):
        assert summary["completed_conditions"] == 17
        assert summary["completed_cells"] == 272
        assert summary["green_cells"] == 272
        assert value["authority"]["gate5_package_preregistration"]
    else:
        assert summary["green_cells"] < summary["completed_cells"]
        assert not value["authority"]["gate5_package_preregistration"]
    assert not value["authority"]["gate5_hardware"]
    assert not value["authority"]["rdkx5_or_robot"]
