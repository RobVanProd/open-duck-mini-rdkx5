from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = (
    ROOT / "tools" / "run_t239_x_positive_router_separability.py"
)
SPEC = importlib.util.spec_from_file_location(
    "t239_separability", MODULE_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_renamed_rows_preserve_classification() -> None:
    rows = MODULE.renamed_rows(
        [
            {
                "condition_id": "TORSO_COM_X_POS",
                "score": 1.0,
                "predicted_y_negative": True,
                "expected_y_negative": True,
                "correct": True,
            }
        ]
    )
    assert rows == [
        {
            "condition_id": "TORSO_COM_X_POS",
            "score": 1.0,
            "predicted_x_positive": True,
            "expected_x_positive": True,
            "correct": True,
        }
    ]


def test_frozen_result_closes_one_sided_linear_family() -> None:
    path = ROOT / "outputs" / "analysis" / (
        "t239_x_positive_router_separability_result.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {k: v for k, v in value.items() if k != "result_sha256"}
    assert value["result_sha256"] == MODULE.canonical_sha256(basis)
    assert value["status"] == (
        "HOLD_T239_X_POSITIVE_ROUTER_SEPARABILITY"
    )
    assert value["decision"] == (
        "RETURN_TO_CONTEXT_GEOMETRY_SELECTION_WITHOUT_ROUTER_TRANSFORM"
    )
    assert value["summary"]["cross_fit_correct"] == ["18/20", "18/20"]
    assert value["summary"]["combined_correct"] == "36/40"
    assert value["summary"]["combined_margin"] < 0.0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
