from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import onnx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = (
    ROOT / "tools" / "run_t241_bounded_positive_router_transform.py"
)
SPEC = importlib.util.spec_from_file_location(
    "t241_transform", MODULE_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_output_order_matches_runtime_contract() -> None:
    assert MODULE.OUTPUT_NAMES == [
        "continuous_actions",
        "previous_action_out",
        "h_out",
    ]


def test_transform_adds_bounded_gate(tmp_path: Path) -> None:
    source = Path(
        "D:/CodexArtifacts/open-duck-policy/"
        "t234b_abi_helper_recovery_v1/graphs/1003520/"
        "exact_low_command_final_head.onnx"
    )
    if not source.exists():
        return
    destination = tmp_path / "bounded.onnx"
    result = MODULE.transform(source, destination, 0.17300140857696533)
    assert result["added_initializers"] == [
        "t241_positive_router_upper_bound"
    ]
    assert set(result["changed_old_nodes"]) == {
        "t162_positive_router_gate",
        "t156_positive_router_gate",
    }
    assert len(result["added_nodes"]) == 4
    onnx.checker.check_model(onnx.load(destination))
