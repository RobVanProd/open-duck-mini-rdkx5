from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t240_bounded_positive_router.py"
SPEC = importlib.util.spec_from_file_location(
    "t240_bounded_router", MODULE_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_derive_upper_is_float32_midpoint() -> None:
    rows = [
        {
            "condition_id": "TORSO_COM_X_POS",
            "fit_id": "p30",
            "score": 0.1,
        },
        {
            "condition_id": "HOME_JOINT_OFFSET_NEG",
            "fit_id": "p30",
            "score": 0.3,
        },
        {"condition_id": "ARMATURE_LO", "fit_id": "p30", "score": -0.2},
    ]
    assert MODULE.derive_upper(rows) == np.float32(0.2)


def test_bounded_classification_rejects_upper_false_positive() -> None:
    rows = [
        {
            "condition_id": "TORSO_COM_X_POS",
            "fit_id": "p30",
            "score": 0.1,
        },
        {
            "condition_id": "HOME_JOINT_OFFSET_NEG",
            "fit_id": "p30",
            "score": 0.3,
        },
        {"condition_id": "ARMATURE_LO", "fit_id": "p30", "score": -0.2},
    ]
    classified = MODULE.classify(rows, np.float32(0.2))
    assert [row["predicted_x_positive"] for row in classified] == [
        True,
        False,
        False,
    ]
    assert all(row["correct"] for row in classified)
