from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t238_home_offset_route_autopsy.py"
SPEC = importlib.util.spec_from_file_location("t238_autopsy", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_router_score() -> None:
    assert MODULE.router_score(
        np.asarray([2.0, 3.0]),
        np.asarray([[4.0], [5.0]]),
        np.asarray([-1.0]),
    ) == 22.0


def test_hidden_gate_scores() -> None:
    values = {
        "hidden_gate_mean": np.asarray([1.0, 1.0]),
        "hidden_gate_scale": np.asarray([2.0, 4.0]),
        "hidden_gate_coefficient": np.asarray([[2.0], [8.0]]),
        "hidden_gate_intercept": np.asarray([-1.0]),
    }
    observed = MODULE.hidden_gate_scores(
        np.asarray([[3.0, 5.0], [1.0, 1.0]]), values
    )
    assert np.array_equal(observed, np.asarray([9.0, -1.0]))


def test_frozen_result_is_terminal_read_only_classification() -> None:
    path = ROOT / "outputs" / "analysis" / (
        "t238_home_offset_route_autopsy_result.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {k: v for k, v in value.items() if k != "result_sha256"}
    assert value["result_sha256"] == MODULE.canonical_sha256(basis)
    assert value["status"] == (
        "PASS_T238_HOME_OFFSET_FALSE_POSITIVE_X_POSITIVE_ROUTE"
    )
    assert value["decision"] == (
        "EARN_T239_X_POSITIVE_ROUTER_SEPARABILITY_PREREGISTRATION_ONLY"
    )
    assert value["classification_pass"] is True
    assert all(value["classification_checks"].values())
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
