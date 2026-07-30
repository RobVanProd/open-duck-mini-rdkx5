from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t199_t194_support_credit_autopsy import (  # noqa: E402
    maximum_run,
    support_class,
)


ANALYSIS = ROOT / "outputs" / "analysis"


def test_support_helpers() -> None:
    assert support_class([True, False]) == "left"
    assert support_class([False, True]) == "right"
    assert support_class([True, True]) == "double"
    assert support_class([False, False]) == "flight"
    assert maximum_run([False, True, True, False, True]) == 2
    assert maximum_run([True, True, True]) == 3
    assert maximum_run([]) == 0


def test_t199_preregistration_when_present() -> None:
    path = ANALYSIS / "t199_t194_support_credit_autopsy_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T199_T194_SUPPORT_CREDIT_AUTOPSY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["traces"]) == 5
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False


def test_t199_result_when_present() -> None:
    path = ANALYSIS / "t199_t194_support_credit_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T199_T194_SUPPORT_CREDIT_AUTOPSY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
