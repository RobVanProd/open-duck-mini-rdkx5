#!/usr/bin/env python3
"""Preregister T184B with the correct 27-tick gait period."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T184 = (
    ANALYSIS / "t184_bilateral_single_support_anatomy_preregistration.json"
)
T184_RESULT = ANALYSIS / "t184_bilateral_single_support_anatomy_result.json"
RECOVERY = ANALYSIS / "t184_period_contract_recovery_20260730.json"
OUTPUT = (
    ANALYSIS
    / "t184b_bilateral_single_support_anatomy_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T184B_BILATERAL_SINGLE_SUPPORT_ANATOMY_RECOVERY_"
    "PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t184_bilateral_single_support_anatomy.py"
TEST = ROOT / "tests" / "test_t184_bilateral_single_support_anatomy.py"


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T184B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T184B preregistration requires clean worktree")
    t184 = _load(T184)
    result = _load(T184_RESULT)
    recovery = _load(RECOVERY)
    for value, field, label in (
        (t184, "preregistered_contract_sha256", "T184 preregistration"),
        (result, "result_sha256", "T184 result"),
        (recovery, "result_sha256", "T184 recovery"),
    ):
        if _canonical_without(value, field) != value[field]:
            raise RuntimeError(f"{label} hash differs")
    if (
        recovery["status"]
        != "INVALIDATE_T184_PERIOD_CONTRACT_BEFORE_T185"
        or recovery["source_result_sha256"] != result["result_sha256"]
    ):
        raise RuntimeError("T184 recovery does not invalidate this result")

    basis = {
        key: value
        for key, value in t184.items()
        if key
        not in (
            "schema_version",
            "status",
            "frozen_inputs",
            "analysis_contract",
            "preregistered_contract_sha256",
        )
    }
    basis["schema_version"] = (
        "open_duck.t184b_bilateral_single_support_anatomy_"
        "recovery_preregistration.v1"
    )
    basis["status"] = (
        "PREREGISTERED_T184B_BILATERAL_SINGLE_SUPPORT_ANATOMY_RECOVERY"
    )
    basis["frozen_inputs"] = {
        "builder": receipt(BUILDER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t184_preregistration": receipt(T184),
        "t184_result": receipt(T184_RESULT),
        "t184_period_recovery": receipt(RECOVERY),
        **{
            key: value
            for key, value in t184["frozen_inputs"].items()
            if key not in ("builder", "runner", "test")
        },
    }
    basis["analysis_contract"] = dict(t184["analysis_contract"])
    basis["analysis_contract"].update(
        {
            "gait_period_ticks": 27,
            "terminal_window_ticks": 54,
            "maximum_ticks_from_last_supported_to_done": 27,
        }
    )
    basis["recovery_contract"] = {
        "only_changes": {
            "gait_period_ticks": [20, 27],
            "terminal_window_ticks": [40, 54],
            "maximum_ticks_from_last_supported_to_done": [20, 27],
        },
        "traces_unchanged": basis["traces"] == t184["traces"],
        "population_unchanged": (
            basis["population"] == t184["population"]
        ),
        "decision_rule_unchanged": (
            basis["decision_rule"] == t184["decision_rule"]
        ),
        "authority_unchanged": (
            basis["authority_after_result"]
            == t184["authority_after_result"]
        ),
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T184B bilateral single-support anatomy recovery "
        "preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Correct gait period: `27` ticks\n"
        "- Correct terminal window: `54` ticks\n"
        "- Correct support-loss allowance: `27` ticks\n"
        "- Traces, population, decision rule, and authority are exact to "
        "T184.\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
