from __future__ import annotations

import importlib.util
import json
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


def test_frozen_result_holds_only_on_random_sensitivity() -> None:
    path = ROOT / "outputs" / "analysis" / (
        "t241_bounded_positive_router_transform_result.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {k: v for k, v in value.items() if k != "result_sha256"}
    assert value["result_sha256"] == MODULE.canonical_sha256(basis)
    assert value["status"] == (
        "HOLD_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM"
    )
    assert value["failed_checks"] == ["random_contract_exact"]
    assert value["checks"]["failed_trace_contract_exact"] is True
    assert all(
        graph["trace_replay"]["every_trace_changed"]
        and graph["trace_replay"]["all_source_replay_exact"]
        and graph["trace_replay"]["all_transformed_finite"]
        for graph in value["graphs"]
    )
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
