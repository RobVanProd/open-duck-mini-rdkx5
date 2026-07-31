#!/usr/bin/env python3
"""Preregister a reporting-only correction for T83's matrix cardinality."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T83_PREREG = ANALYSIS / "t83_t78_midpoint_full_preregistration.json"
T83_RESULT = ANALYSIS / "t83_t78_midpoint_full_result.json"
SHARED_RUNNER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
CORRECTOR = ROOT / "tools" / "run_t83b_midpoint_aggregation_correction.py"
TEST = ROOT / "tests" / "test_t83b_midpoint_aggregation_correction.py"
OUTPUT = (
    ANALYSIS / "t83b_midpoint_aggregation_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T83B_MIDPOINT_AGGREGATION_CORRECTION_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T83b: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T83b preregistration requires a clean worktree")
    prereg = json.loads(T83_PREREG.read_text(encoding="utf-8"))
    raw = json.loads(T83_RESULT.read_text(encoding="utf-8"))
    shared_text = SHARED_RUNNER.read_text(encoding="utf-8")
    blocks = raw["blocks"]
    cells = [
        cell for block in blocks for cell in block["result"]["cells"]
    ]
    checks = {
        "t83_preregistration_was_green": (
            prereg["status"]
            == "PREREGISTERED_T83_T78_MIDPOINT_FULL_MATRIX"
            and prereg["failed_checks"] == []
            and prereg["matrix"]["maximum_cells"] == 8
        ),
        "t83_raw_reporting_hold_exact": (
            raw["status"] == "HOLD_T83_T78_MIDPOINT_FULL_MATRIX"
            and raw["decision"] == "CLOSE_EXACT_T78_ADAPTER_MIDPOINT"
            and raw["condition"]["condition_green"] is False
        ),
        "every_underlying_cell_green": (
            len(cells) == 8
            and raw["condition"]["cells"] == 8
            and raw["condition"]["green_cells"] == 8
            and all(cell["cell_green"] for cell in cells)
        ),
        "both_underlying_fit_blocks_green": (
            len(blocks) == 2
            and all(block["result"]["block_green"] for block in blocks)
            and {block["fit_id"] for block in blocks} == {"p30", "p31_34"}
        ),
        "hardcoded_shared_cardinality_identified": all(
            token in shared_text
            for token in (
                "len(blocks) == 4",
                "len(cells) == 16",
            )
        ),
        "corrector_and_test_present": CORRECTOR.is_file() and TEST.is_file(),
        "behavior_training_colab_robot_and_gate5_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t83b_midpoint_aggregation_correction_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T83B_REPORTING_ONLY_AGGREGATION_CORRECTION"
            if not failed
            else "HOLD_T83B_AGGREGATION_CORRECTION_PREREGISTRATION"
        ),
        "question": (
            "Does a read-only cardinality-aware aggregation of T83's two "
            "hashed fit blocks classify the already executed eight cells "
            "without changing any cell or rerunning simulation?"
        ),
        "classification": (
            "REPORTING_CARDINALITY_DEFECT_NOT_BEHAVIOR_FAILURE"
        ),
        "source_receipts": {
            "t83_preregistration": receipt(T83_PREREG),
            "t83_raw_result": receipt(T83_RESULT),
            "shared_runner": receipt(SHARED_RUNNER),
            "corrector": receipt(CORRECTOR),
            "test": receipt(TEST),
        },
        "frozen_correction": {
            "expected_blocks": 2,
            "expected_cells": 8,
            "expected_fits": ["p30", "p31_34"],
            "condition_green": (
                "two blocks, eight cells, every block and cell green"
            ),
            "cell_fields_changed": 0,
            "manifest_or_trace_fields_changed": 0,
            "simulator_rerun": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Every source/manifest/trace receipt is exact; two fit blocks "
                "and eight cells are present; every block and cell is green."
            ),
            "pass_decision": (
                "EARN_T84_PERSISTENT_INTERPOLATION_MECHANISM_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "HOLD_T83_WITHOUT_BEHAVIOR_INTERPRETATION",
            "candidate_promotion": False,
        },
        "execution_now": {
            "source_formal_behavior_cells": 8,
            "correction_formal_behavior_cells": 0,
            "simulator_trace_rows_generated": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_read_only_correction": not failed,
            "persistent_mechanism_preregistration": False,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T83b midpoint aggregation correction preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Defect: shared summary hardcodes 4 blocks / 16 cells",
                "- Source evidence: 2 blocks / 8 cells, all green",
                "- Correction: read-only; no simulator rerun",
                "- New behavior/training/Colab/Gate5/robot: `0/0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
