from __future__ import annotations

import importlib.util
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
