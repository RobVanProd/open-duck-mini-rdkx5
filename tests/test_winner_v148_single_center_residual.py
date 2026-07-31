from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort

from tools.build_winner_v148_single_center_residual import append_residual


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v148_preregisters_one_local_right_ankle_correction() -> None:
    prereg = load("winner_v148_single_center_residual_preregistration.json")
    assert sha256(
        "winner_v148_single_center_residual_preregistration.json"
    ) == "641baad57fead96ab33a9697137f4f47e10324a893f21e59843e50263594258f"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V148_SINGLE_CENTER_RESIDUAL"
    )
    assert prereg["failed_checks"] == []
    assert prereg["mechanism"]["joint"] == (
        "right ankle / action index 13"
    )
    assert prereg["mechanism"]["optimizer_or_training"] is False
    assert prereg["mechanism"]["radius"] == (
        "half the normalized Euclidean distance to the nearest other "
        "aggregate row"
    )
    assert prereg["authority"]["behavior"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v148_residual_graph_gates_exactly_inside_radius(
    tmp_path: Path,
) -> None:
    source = onnx.helper.make_model(
        onnx.helper.make_graph(
            [
                onnx.helper.make_node(
                    "Identity", ["previous_action"], ["continuous_actions"]
                ),
                onnx.helper.make_node(
                    "Identity", ["previous_action"], ["previous_action_out"]
                ),
                onnx.helper.make_node("Identity", ["h_in"], ["h_out"]),
            ],
            "v148_unit_source",
            [
                onnx.helper.make_tensor_value_info(
                    "obs", onnx.TensorProto.FLOAT, [1, 115]
                ),
                onnx.helper.make_tensor_value_info(
                    "previous_action", onnx.TensorProto.FLOAT, [1, 14]
                ),
                onnx.helper.make_tensor_value_info(
                    "h_in", onnx.TensorProto.FLOAT, [1, 64]
                ),
            ],
            [
                onnx.helper.make_tensor_value_info(
                    "continuous_actions", onnx.TensorProto.FLOAT, [1, 14]
                ),
                onnx.helper.make_tensor_value_info(
                    "previous_action_out", onnx.TensorProto.FLOAT, [1, 14]
                ),
                onnx.helper.make_tensor_value_info(
                    "h_out", onnx.TensorProto.FLOAT, [1, 64]
                ),
            ],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 12)],
    )
    center = np.zeros(179, dtype=np.float32)
    scale = np.ones(179, dtype=np.float32)
    correction = np.zeros(14, dtype=np.float32)
    correction[13] = np.float32(0.002)
    model = append_residual(
        source,
        center=center,
        scale=scale,
        radius_squared=0.25,
        correction=correction,
    )
    path = tmp_path / "local.onnx"
    onnx.save(model, path)
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)

    inside = session.run(
        None,
        {
            "obs": np.zeros((1, 115), dtype=np.float32),
            "previous_action": previous,
            "h_in": hidden,
        },
    )
    outside_obs = np.zeros((1, 115), dtype=np.float32)
    outside_obs[0, 0] = 1
    outside = session.run(
        None,
        {
            "obs": outside_obs,
            "previous_action": previous,
            "h_in": hidden,
        },
    )

    assert inside[0][0, 13] == np.float32(0.002)
    assert np.array_equal(inside[0], inside[1])
    assert np.count_nonzero(inside[0]) == 1
    assert np.array_equal(outside[0], previous)
    assert np.array_equal(outside[0], outside[1])
    assert np.array_equal(inside[2], hidden)
    assert np.array_equal(outside[2], hidden)


def test_v148_changes_only_the_frozen_center_element() -> None:
    result = load("winner_v148_single_center_residual_result.json")
    assert sha256("winner_v148_single_center_residual_result.json") == (
        "a7c0087dc18db1b4371b3ea7598bf768bb55fef881b57b0732e97e766be72d3d"
    )
    assert result["status"] == (
        "PASS_WINNER_V148_SINGLE_CENTER_RESIDUAL"
    )
    assert result["failed_checks"] == []
    assert result["aggregate"]["rows"] == 5_400
    assert result["aggregate"]["gate_rows"] == [5_194]
    assert result["aggregate"]["changed_elements"] == [[5_194, 13]]
    assert result["aggregate"]["preservation_linf"] == 0
    assert result["center"]["center_error"] <= 1.0e-7
    assert result["artifact"]["deployed"]["inference"]["pass"] is True
    assert result["decision"] == (
        "EARN_ONE_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR_PREREGISTRATION"
    )
    assert result["authority"]["behavior"] is False
