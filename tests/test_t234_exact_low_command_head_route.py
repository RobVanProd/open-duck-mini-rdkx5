from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper, TensorProto


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t234_exact_low_command_head_route.py"
SPEC = importlib.util.spec_from_file_location("t234_route", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_replace_initializer() -> None:
    graph = helper.make_graph(
        [],
        "test",
        [],
        [],
        [
            numpy_helper.from_array(
                np.asarray([1.0], dtype=np.float32), "value"
            )
        ],
    )
    model = helper.make_model(graph)
    MODULE.replace_initializer(
        model, "value", np.asarray([2.0], dtype=np.float32)
    )
    observed = numpy_helper.to_array(model.graph.initializer[0])
    assert np.array_equal(observed, np.asarray([2.0], dtype=np.float32))


def test_exact_command_float32() -> None:
    value = np.asarray([np.float32(0.074)], dtype=np.float32)
    assert value.dtype == np.float32
    assert float(value[0]) == 0.07400000095367432
