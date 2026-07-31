from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t233_upper_z_context_separability.py"
SPEC = importlib.util.spec_from_file_location("t233_separability", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(condition: str, fit: str, value: float) -> dict:
    return {
        "condition_id": condition,
        "fit_id": fit,
        "context": [value, 0.0],
    }


def test_cross_fit_classifier_exact() -> None:
    train = [
        row("CONTROL", "a", 0.0),
        row("OTHER", "a", 0.25),
        row("POS", "a", 1.0),
    ]
    test = [
        row("CONTROL", "b", 0.0),
        row("OTHER", "b", 0.2),
        row("POS", "b", 0.9),
    ]
    result = MODULE.classifier(
        train, test, positive="POS", control="CONTROL"
    )
    assert result["test_correct"] == result["test_cells"] == 3
    assert result["true_positives"] == 1
    assert result["false_positives"] == 0
    assert result["training_margin"] > 0.0


def test_combined_classifier_exact() -> None:
    cells = [
        row("CONTROL", "a", 0.0),
        row("OTHER", "a", 0.25),
        row("POS", "a", 1.0),
        row("CONTROL", "b", 0.0),
        row("OTHER", "b", 0.2),
        row("POS", "b", 0.9),
    ]
    result = MODULE.combined_classifier(
        cells, positive="POS", control="CONTROL"
    )
    assert result["correct_cells"] == result["cells"] == 6
    assert result["true_positives"] == 2
    assert result["false_positives"] == 0
    assert result["margin"] > 0.0
