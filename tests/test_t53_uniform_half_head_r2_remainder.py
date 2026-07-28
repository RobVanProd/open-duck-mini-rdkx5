from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t53_preregisters_only_r2_conditions_five_to_twenty() -> None:
    value = load(
        "t53_uniform_half_head_r2_remainder_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_T53_UNIFORM_HALF_HEAD_R2_REMAINDER"
    )
    assert value["failed_checks"] == []
    assert value["prior_qualification"]["formal_cells"] == 64
    assert value["prior_qualification"]["green_cells"] == 64
    assert value["matrix"]["condition_indices"] == list(range(5, 21))
    assert value["matrix"]["maximum_cells"] == 256
    assert value["matrix"]["both_checkpoints_required"]
    assert not value["matrix"]["checkpoint_cherry_pick"]
    assert not value["matrix"]["reuse_prior_condition_evidence"]
    assert value["authority"]["execute_one_256_cell_cpu_remainder"]
    assert not value["authority"]["gate5_hardware"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t53_result_requires_all_256_cells_if_present() -> None:
    path = ANALYSIS / "t53_uniform_half_head_r2_remainder_result.json"
    if not path.is_file():
        pytest.skip("formal T53 remainder has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["completed_cells"] == (
        16 * summary["completed_conditions"]
    )
    if value["status"].startswith("PASS_"):
        assert summary["completed_conditions"] == 16
        assert summary["completed_cells"] == 256
        assert summary["green_cells"] == 256
        assert value["authority"][
            "gate5_deployment_package_preregistration"
        ]
    else:
        assert summary["green_cells"] < summary["completed_cells"]
        assert not value["authority"][
            "gate5_deployment_package_preregistration"
        ]
    assert not value["authority"]["gate5_hardware"]
    assert not value["authority"]["rdkx5_or_robot"]
