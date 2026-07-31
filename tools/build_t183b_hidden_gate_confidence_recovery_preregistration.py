#!/usr/bin/env python3
"""Preregister T183B with only the alpha trace receipt normalized."""

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


T183 = ANALYSIS / "t183_hidden_gate_confidence_preregistration.json"
RECOVERY = ANALYSIS / "t183_receipt_schema_recovery_20260730.json"
OUTPUT = (
    ANALYSIS / "t183b_hidden_gate_confidence_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T183B_HIDDEN_GATE_CONFIDENCE_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t183_hidden_gate_confidence.py"
TEST = ROOT / "tests" / "test_t183_hidden_gate_confidence.py"


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
            raise FileExistsError(f"refusing to overwrite T183B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T183B preregistration requires clean worktree")
    t183 = _load(T183)
    recovery = _load(RECOVERY)
    if (
        _canonical_without(t183, "preregistered_contract_sha256")
        != t183["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T183 preregistration hash differs")
    if (
        _canonical_without(recovery, "result_sha256")
        != recovery["result_sha256"]
        or recovery["status"] != "HOLD_T183_RECEIPT_SCHEMA_BEFORE_RESULT"
    ):
        raise RuntimeError("T183 recovery is invalid")
    old_trace = t183["unlabeled_alpha_case"]["candidate_trace"]
    normalized = recovery["normalized_receipt"]
    if (
        old_trace["path"] != normalized["path"]
        or old_trace["sha256"] != normalized["sha256"]
        or Path(normalized["path"]).stat().st_size != normalized["bytes"]
    ):
        raise RuntimeError("T183B normalized receipt does not match T183")

    basis = {
        key: value
        for key, value in t183.items()
        if key
        not in (
            "preregistered_contract_sha256",
            "status",
            "schema_version",
            "frozen_inputs",
        )
    }
    basis["schema_version"] = (
        "open_duck.t183b_hidden_gate_confidence_recovery_"
        "preregistration.v1"
    )
    basis["status"] = (
        "PREREGISTERED_T183B_HIDDEN_GATE_CONFIDENCE_RECOVERY"
    )
    basis["frozen_inputs"] = {
        "builder": receipt(BUILDER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t183_preregistration": receipt(T183),
        "t183_receipt_schema_recovery": receipt(RECOVERY),
        **{
            key: value
            for key, value in t183["frozen_inputs"].items()
            if key not in ("builder", "runner", "test")
        },
    }
    basis["unlabeled_alpha_case"] = dict(t183["unlabeled_alpha_case"])
    basis["unlabeled_alpha_case"]["candidate_trace"] = normalized
    basis["recovery_contract"] = {
        "only_change": (
            "unlabeled alpha trace receipt gains independently verified "
            "bytes while path and SHA remain exact"
        ),
        "analysis_contract_unchanged": (
            basis["analysis_contract"] == t183["analysis_contract"]
        ),
        "labeled_cases_unchanged": (
            basis["labeled_cases"] == t183["labeled_cases"]
        ),
        "unlabeled_shared_cases_unchanged": (
            basis["unlabeled_shared_cases"]
            == t183["unlabeled_shared_cases"]
        ),
        "decision_rule_unchanged": (
            basis["decision_rule"] == t183["decision_rule"]
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
        "# T183B hidden-gate confidence recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Only change: add the independently verified byte count to the "
        "unlabeled T182B alpha-trace receipt.\n"
        "- Feature, traces, labels, thresholds, decision rules, and authority "
        "are unchanged from T183.\n"
        "- Behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
