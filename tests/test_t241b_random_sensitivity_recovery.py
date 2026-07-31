from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = (
    ROOT / "tools" / "run_t241b_random_sensitivity_recovery.py"
)
SPEC = importlib.util.spec_from_file_location(
    "t241b_recovery", MODULE_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_recovery_paths_are_distinct() -> None:
    assert MODULE.PREREG.name.startswith("t241b_")
    assert MODULE.OUTPUT.name.startswith("t241b_")
    assert MODULE.PREREG != MODULE.OUTPUT
