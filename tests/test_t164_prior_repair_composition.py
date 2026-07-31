from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_t149_negative_context_command_plateau_transform import (  # noqa: E402
    transform,
)
from run_t164_prior_repair_composition import (  # noqa: E402
    cross_graph_contract,
)


ANALYSIS = ROOT / "outputs" / "analysis"
T162_HALF = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t162_exact_command_endpoint_transform_v1/"
    "1003520/command_endpoint_router.onnx"
)
T149_HALF = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t149b_negative_context_command_plateau_v1/"
    "1003520/negative_command_plateau.onnx"
)


def three_contexts() -> list[dict]:
    prior = json.loads(
        (
            ANALYSIS
            / "t135b_interrupted_calibration_context_router_recovery_result.json"
        ).read_text(encoding="utf-8")
    )["runs"]
    positive = json.loads(
        (
            ANALYSIS / "t156_three_way_positive_router_result.json"
        ).read_text(encoding="utf-8")
    )["positive_contexts"]
    return [
        next(row for row in prior if row["population"] == "nominal"),
        next(
            row
            for row in prior
            if row["population"] == "com_x_negative"
        ),
        positive[0],
    ]


def test_t164_composition_preserves_each_disjoint_repair(
    tmp_path: Path,
) -> None:
    composed = tmp_path / "composed.onnx"
    structure = transform(T162_HALF, composed)
    assert structure["nine_nodes_inserted"]
    assert structure["two_raw_obs_consumers_rewired_exact"]
    assert structure["all_other_nodes_byte_exact"]
    assert structure["existing_initializers_byte_exact"]
    assert structure["abi_exact"]

    contract = cross_graph_contract(
        composed,
        T149_HALF,
        T162_HALF,
        three_contexts(),
        seed=20260729,
    )
    assert contract["all_outputs_bit_exact"]
    assert contract["all_outputs_finite"]
    assert contract["negative_matches_t149b"]
    assert contract["nominal_and_positive_match_t162"]
    assert contract["x0_exact"]


def test_t164_preregistration_and_result_scope() -> None:
    prereg = json.loads(
        (
            ANALYSIS / "t164_prior_repair_composition_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        prereg["status"]
        == "PREREGISTERED_T164_PRIOR_REPAIR_COMPOSITION"
    )
    assert not prereg["failed_checks"]
    assert prereg["composition"]["scalar_search"] is False
    assert prereg["execution_now"]["behavior_cells"] == 0
    assert not prereg["authority"]["full_r2"]

    result_path = ANALYSIS / "t164_prior_repair_composition_result.json"
    if not result_path.exists():
        return
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_T164_PRIOR_REPAIR_COMPOSITION"
    assert not result["failed_checks"]
    assert all(result["checks"].values())
    assert result["execution"]["behavior_cells"] == 0
    assert result["execution"]["hosted_compute_units"] == 0
    assert not result["authority"]["behavior_matrix"]
    assert not result["authority"]["gate5"]
