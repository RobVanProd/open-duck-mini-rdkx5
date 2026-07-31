from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t232_t228_nominal_failure_autopsy.py"
SPEC = importlib.util.spec_from_file_location("t232_autopsy", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_stats_exact() -> None:
    value = MODULE.stats(np.asarray([-2.0, 0.0, 2.0]))
    assert value["rms"] == np.sqrt(8.0 / 3.0)
    assert value["max_abs"] == 2.0


def test_longest_run() -> None:
    assert MODULE.longest_run(
        np.asarray([False, True, True, False, True, True, True])
    ) == 3


def test_head_parameter_names() -> None:
    values = {
        "nominal_condition_negative_adapter_weight": np.zeros((64, 14)),
        "nominal_condition_negative_adapter_bias": np.zeros((14,)),
    }
    weight, bias = MODULE.head_params(values)
    assert weight.shape == (64, 14)
    assert bias.shape == (14,)
