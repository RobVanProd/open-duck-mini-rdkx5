from __future__ import annotations

import importlib.util
import json
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


def test_frozen_result_recovers_behavior_preregistration_only() -> None:
    path = ROOT / "outputs" / "analysis" / (
        "t241b_random_sensitivity_recovery_result.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {k: v for k, v in value.items() if k != "result_sha256"}
    assert value["result_sha256"] == MODULE.canonical_sha256(basis)
    assert value["status"] == (
        "PASS_T241B_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
    )
    assert value["decision"] == (
        "EARN_T242_BOUNDED_ROUTER_HOME_OFFSET_MATRIX_"
        "PREREGISTRATION_ONLY"
    )
    assert all(value["checks"].values())
    assert value["execution"]["onnx_transforms"] == 0
    assert value["execution"]["inference_rows"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
