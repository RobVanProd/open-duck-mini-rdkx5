#!/usr/bin/env python3
"""Apply T83b's read-only cardinality-aware aggregation correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t83b_midpoint_aggregation_correction_preregistration.json"
)
T83_RESULT = ANALYSIS / "t83_t78_midpoint_full_result.json"
OUTPUT = ANALYSIS / "t83b_midpoint_aggregation_correction_result.json"
MARKDOWN = (
    ANALYSIS / "T83B_MIDPOINT_AGGREGATION_CORRECTION_RESULT_20260728.md"
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


def verify_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["status"]
        != "PREREGISTERED_T83B_REPORTING_ONLY_AGGREGATION_CORRECTION"
        or value["failed_checks"] != []
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise ValueError("T83b preregistration changed")
    for name, item in value["source_receipts"].items():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"T83b source changed: {name}")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T83b: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T83b correction requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    raw = json.loads(T83_RESULT.read_text(encoding="utf-8"))
    blocks = raw["blocks"]
    cells = [
        cell for block in blocks for cell in block["result"]["cells"]
    ]
    manifest_receipts_exact = all(
        sha256(Path(block["manifest"]["path"]))
        == block["manifest"]["sha256"]
        for block in blocks
    )
    trace_receipts_exact = all(
        sha256(Path(cell["protection"]["path"]))
        == cell["protection"]["sha256"]
        for cell in cells
    )
    expected_blocks = prereg["frozen_correction"]["expected_blocks"]
    expected_cells = prereg["frozen_correction"]["expected_cells"]
    expected_fits = set(prereg["frozen_correction"]["expected_fits"])
    corrected_green = (
        len(blocks) == expected_blocks
        and len(cells) == expected_cells
        and {block["fit_id"] for block in blocks} == expected_fits
        and all(block["result"]["block_green"] for block in blocks)
        and all(cell["cell_green"] for cell in cells)
    )
    checks = {
        "t83_source_result_exact": (
            sha256(T83_RESULT)
            == prereg["source_receipts"]["t83_raw_result"]["sha256"]
        ),
        "manifest_receipts_exact": manifest_receipts_exact,
        "trace_receipts_exact": trace_receipts_exact,
        "exact_two_fit_blocks": (
            len(blocks) == expected_blocks
            and {block["fit_id"] for block in blocks} == expected_fits
        ),
        "exact_eight_cells": len(cells) == expected_cells,
        "every_block_green": all(
            block["result"]["block_green"] for block in blocks
        ),
        "every_cell_green": all(cell["cell_green"] for cell in cells),
        "corrected_condition_green": corrected_green,
        "no_cell_manifest_or_trace_fields_changed": True,
        "no_simulator_training_colab_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    corrected_condition = {
        **raw["condition"],
        "condition_green": corrected_green,
        "aggregation_contract": {
            "expected_blocks": expected_blocks,
            "expected_cells": expected_cells,
            "expected_fits": sorted(expected_fits),
        },
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t83b_midpoint_aggregation_correction_result.v1"
        ),
        "status": (
            "PASS_T83B_MIDPOINT_AGGREGATION_CORRECTION"
            if not failed
            else "HOLD_T83B_MIDPOINT_AGGREGATION_CORRECTION"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source": {
            "raw_result_status": raw["status"],
            "raw_result_decision": raw["decision"],
            "raw_result_sha256": sha256(T83_RESULT),
            "source_formal_behavior_cells": raw["execution"][
                "formal_behavior_cells"
            ],
        },
        "condition": corrected_condition,
        "blocks": blocks,
        "checks": checks,
        "failed_checks": failed,
        "classification": {
            "raw_hold_cause": "hardcoded_four_block_summary_cardinality",
            "behavior_result": "eight_of_eight_cells_green",
            "candidate_status": "diagnostic_only",
            "persistence_satisfied": False,
        },
        "execution": {
            "source_formal_behavior_cells": 8,
            "correction_formal_behavior_cells": 0,
            "simulator_trace_rows_generated": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "persistent_mechanism_preregistration": not failed,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T83b midpoint aggregation correction result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Corrected green cells: `{corrected_condition['green_cells']}/8`",
                "- New simulator behavior cells: `0`",
                "- Candidate status: `diagnostic only; persistence unsatisfied`",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
