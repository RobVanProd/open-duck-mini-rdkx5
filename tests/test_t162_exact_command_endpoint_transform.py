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
