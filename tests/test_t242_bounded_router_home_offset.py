from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "run_t242_bounded_router_home_offset.py"
SPEC = importlib.util.spec_from_file_location(
    "t242_home_offset", MODULE_PATH
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_scalar_expansion_readback_is_exact() -> None:
    before = [float(index) for index in range(14)]
    report = {
        "enabled": True,
        "key": "joint_qpos0_offset_rad",
        "value": [-0.03] * 14,
        "readback": {
            "before": before,
            "after": [value - 0.03 for value in before],
            "offset": [-0.03] * 14,
        },
    }
    assert MODULE.corrected_joint_offset_readback(report, -0.03)


def test_readback_rejects_wrong_axis() -> None:
    report = {
        "enabled": True,
        "key": "armature_scale",
        "value": [-0.03] * 14,
        "readback": {
            "before": [0.0] * 14,
            "after": [-0.03] * 14,
            "offset": [-0.03] * 14,
        },
    }
    assert not MODULE.corrected_joint_offset_readback(report, -0.03)
