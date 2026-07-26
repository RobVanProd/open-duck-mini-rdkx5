from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_t6_corrected_robustness_screen import audit  # noqa: E402


def test_completed_t6_result_passes_independent_audit() -> None:
    result = audit()
    assert result["status"] == "PASS_T6_INDEPENDENT_AUDIT"
    assert result["issues"] == []
    assert result["counts"] == {
        "manifests": 16,
        "evaluations": 16,
        "traces": 64,
        "cells": 64,
        "green_cells": 1,
        "exact_override_readbacks": 64,
        "candidates": 4,
        "survivors": 0,
    }


def test_independent_auditor_does_not_import_t6_runner() -> None:
    source = (
        ROOT / "tools/audit_t6_corrected_robustness_screen.py"
    ).read_text(encoding="utf-8")
    forbidden = "run_" + "t6_corrected_robustness_screen"
    assert forbidden not in source


def test_tampered_result_is_rejected(tmp_path: Path) -> None:
    original = json.loads(
        (
            ROOT
            / "outputs/analysis/t6_corrected_robustness_screen_result.json"
        ).read_text(encoding="utf-8")
    )
    original["completed_cells"] = 63
    tampered = tmp_path / "tampered.json"
    tampered.write_text(
        json.dumps(original, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    result = audit(result_path=tampered)
    assert result["status"] == "FAIL_T6_INDEPENDENT_AUDIT"
    assert "result_canonical_sha256" in result["issues"]
    assert "result_completed_cells" in result["issues"]
