from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t162_exact_command_endpoint_transform import (  # noqa: E402
    inference_contract,
    transform,
)


SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t159_mechanics_sagittal_compensation_v1/"
    "1003520/mechanics_compensated_router.onnx"
)
ANALYSIS = ROOT / "outputs" / "analysis"


def contexts() -> list[dict]:
    nominal = json.loads(
        (
            ROOT
            / "outputs"
            / "analysis"
            / "t135b_interrupted_calibration_context_router_recovery_result.json"
        ).read_text(encoding="utf-8")
    )["runs"][0]
    positive = json.loads(
        (
            ROOT
            / "outputs"
            / "analysis"
            / "t156_three_way_positive_router_result.json"
        ).read_text(encoding="utf-8")
    )["positive_contexts"][0]
    return [nominal, positive]


def test_t162_transform_is_exact_for_source_and_endpoint_paths(
    tmp_path: Path,
) -> None:
    output = tmp_path / "t162.onnx"
    structure = transform(SOURCE, output, 0.08)
    assert structure["eight_nodes_inserted"]
    assert structure["actor_observation_rewire_exact"]
    assert structure["all_source_nodes_otherwise_byte_exact"]
    assert structure["existing_initializers_byte_exact"]
    assert structure["three_initializers_added"]
    assert structure["abi_exact"]

    contract = inference_contract(
        SOURCE,
        output,
        contexts(),
        endpoint_command_x_m_s=0.08,
        seed=20260729,
    )
    assert contract["provider"] == "CPUExecutionProvider"
    assert contract["all_outputs_bit_exact"]
    assert contract["all_outputs_finite"]
    assert contract["x0_source_exact"]
    assert contract["nonpositive_context_source_exact"]
    assert contract["positive_moving_endpoint_exact"]


def test_t162_preregistration_and_result_contracts() -> None:
    prereg = json.loads(
        (
            ANALYSIS
            / "t162_exact_command_endpoint_transform_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        prereg["status"]
        == "PREREGISTERED_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
    )
    assert not prereg["failed_checks"]
    assert prereg["transform"]["scalar_search"] is False
    assert prereg["transform"]["external_command_unchanged"]
    assert not prereg["authority"]["behavior_matrix"]

    result_path = (
        ANALYSIS / "t162_exact_command_endpoint_transform_result.json"
    )
    if not result_path.exists():
        return
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
    assert not result["failed_checks"]
    assert all(result["checks"].values())
    assert result["execution"]["behavior_cells"] == 0
    assert result["execution"]["optimizer_steps"] == 0
    assert result["execution"]["hosted_compute_units"] == 0
    assert not result["authority"]["behavior_matrix"]
    assert not result["authority"]["gate5"]
