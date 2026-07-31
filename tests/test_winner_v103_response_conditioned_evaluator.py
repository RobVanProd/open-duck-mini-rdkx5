from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from closed_loop_sim_eval import (  # noqa: E402
    ClosedLoopConfig,
    graph_authoritative_action,
    init_policy_io_state,
    init_response_calibrator_io,
    response_calibration_observation,
)


class Node:
    def __init__(self, name: str, shape: list[int]):
        self.name = name
        self.shape = shape
        self.type = "tensor(float)"


class Session:
    def __init__(self, inputs: list[Node], outputs: list[Node]):
        self._inputs = inputs
        self._outputs = outputs

    def get_inputs(self) -> list[Node]:
        return self._inputs

    def get_outputs(self) -> list[Node]:
        return self._outputs


def response_policy_session() -> Session:
    return Session(
        [
            Node("obs", [1, 115]),
            Node("previous_action", [1, 14]),
            Node("h_in", [1, 64]),
            Node("calibration_context", [1, 64]),
        ],
        [
            Node("continuous_actions", [1, 14]),
            Node("previous_action_out", [1, 14]),
            Node("h_out", [1, 64]),
        ],
    )


def response_policy_config() -> ClosedLoopConfig:
    return ClosedLoopConfig(
        policy_path=Path("response.onnx"),
        fit={},
        playground_root=Path("."),
        command_x=0.074,
        duration_s=0.02,
        bridge_mode="fitted",
        expected_observation_dim=115,
        policy_obs_input_name="obs",
        policy_action_output_name="continuous_actions",
        policy_state_input_names=("h_in", "previous_action"),
        policy_state_output_names=("h_out", "previous_action_out"),
        policy_context_input_name="calibration_context",
        policy_graph_authoritative_output=True,
    )


def test_calibration_observation_changes_only_frozen_slices() -> None:
    source = np.arange(115, dtype=np.float32)
    observed = response_calibration_observation(source)
    expected = source.copy()
    expected[6:13] = 0.0
    expected[99:101] = [1.0, 0.0]
    expected[101:115] = 0.0
    np.testing.assert_array_equal(observed, expected)
    np.testing.assert_array_equal(source, np.arange(115, dtype=np.float32))


def test_graph_authoritative_action_returns_exact_graph_bytes() -> None:
    graph = np.linspace(-1.0, 1.0, 14, dtype=np.float32)[None, :]
    actual = graph_authoritative_action(
        graph,
        expected_action_dim=14,
        previous_action_output=graph.copy(),
    )
    np.testing.assert_array_equal(actual, graph[0])
    assert actual.tobytes() == graph[0].tobytes()


@pytest.mark.parametrize(
    ("action", "chained", "match"),
    [
        (np.full((1, 14), 1.01, dtype=np.float32), None, "outside"),
        (
            np.zeros((1, 14), dtype=np.float32),
            np.ones((1, 14), dtype=np.float32),
            "bit-exact",
        ),
        (np.zeros((14,), dtype=np.float32), None, "shape"),
    ],
)
def test_graph_authoritative_action_fails_closed(
    action: np.ndarray,
    chained: np.ndarray | None,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        graph_authoritative_action(
            action,
            expected_action_dim=14,
            previous_action_output=chained,
        )


def test_response_policy_abi_initializes_only_recurrent_state() -> None:
    state = init_policy_io_state(
        response_policy_session(),
        response_policy_config(),
    )
    assert state["obs_input_name"] == "obs"
    assert state["action_output_name"] == "continuous_actions"
    assert state["state_input_names"] == ["h_in", "previous_action"]
    assert state["state_output_names"] == ["h_out", "previous_action_out"]
    assert state["context_input_name"] == "calibration_context"
    assert state["context_input_shape"] == [1, 64]
    assert state["hidden_state"]["h_in"].shape == (1, 64)
    assert state["hidden_state"]["previous_action"].shape == (1, 14)
    assert all(np.count_nonzero(value) == 0 for value in state["hidden_state"].values())


def test_response_policy_abi_rejects_extra_input() -> None:
    session = response_policy_session()
    session._inputs.append(Node("undeclared", [1, 1]))
    with pytest.raises(ValueError, match="input set changed"):
        init_policy_io_state(session, response_policy_config())


def test_response_calibrator_abi_is_exact() -> None:
    session = Session(
        [
            Node("obs", [1, 115]),
            Node("previous_action", [1, 14]),
            Node("h_in", [1, 64]),
        ],
        [
            Node("calibration_actions", [1, 14]),
            Node("previous_action_out", [1, 14]),
            Node("h_out", [1, 64]),
        ],
    )
    assert init_response_calibrator_io(session) == {
        "input_names": ["obs", "previous_action", "h_in"],
        "output_names": [
            "calibration_actions",
            "previous_action_out",
            "h_out",
        ],
    }
