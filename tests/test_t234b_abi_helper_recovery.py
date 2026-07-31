from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import onnx
from onnx import helper


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t234b_abi_helper_recovery.py"
SPEC = importlib.util.spec_from_file_location("t234b_recovery", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_adapted_abi_accepts_model() -> None:
    model = helper.make_model(helper.make_graph([], "empty", [], []))
    assert MODULE.adapted_abi(model) == {}


def test_adapted_abi_accepts_path(tmp_path: Path) -> None:
    model = helper.make_model(helper.make_graph([], "empty", [], []))
    path = tmp_path / "model.onnx"
    onnx.save(model, path)
    assert MODULE.adapted_abi(path) == {}
