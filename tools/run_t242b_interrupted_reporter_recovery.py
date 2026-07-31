#!/usr/bin/env python3
"""Recover T242's first completed block without new simulator execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t242b_interrupted_reporter_recovery_preregistration.json"
)
RESULT = (
    ANALYSIS / "t242b_interrupted_reporter_recovery_result.json"
)
MARKDOWN = (
    ANALYSIS / "T242B_INTERRUPTED_REPORTER_RECOVERY_RESULT_20260731.md"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    sha256,
)
from run_t242_bounded_router_home_offset import (  # noqa: E402
    corrected_extract_block,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T242B input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T242B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T242B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T242B_INTERRUPTED_REPORTER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T242B preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    if len(prereg["completed_blocks"]) != 1:
        raise RuntimeError("T242B completed-block count changed")
    completed = prereg["completed_blocks"][0]
    verify(completed["manifest"])

    source = json.loads(
        Path(prereg["frozen_inputs"]["t242_preregistration"]["path"])
        .read_text(encoding="utf-8")
    )
    if (
        source["preregistered_contract_sha256"]
        != prereg["source_t242_contract_sha256"]
    ):
        raise RuntimeError("T242 source contract changed")
    manifest = json.loads(
        Path(completed["manifest"]["path"]).read_text(encoding="utf-8")
    )
    if (
        manifest["block_contract"]["preregistered_contract_sha256"]
        != prereg["source_t242_contract_sha256"]
    ):
        raise RuntimeError("completed block belongs to another contract")
    for item in (
        manifest["evaluation"],
        manifest["stdout"],
        *manifest["traces"],
    ):
        verify(item)

    # T242's reporter expected an obsolete flat key after all four traces and
    # the manifest had already been committed. Add only an in-memory alias.
    recovery_manifest = {
        **manifest,
        "evaluation_path": manifest["evaluation"]["path"],
    }
    block = corrected_extract_block(
        source, source["condition"], recovery_manifest
    )
    green_cells = sum(cell["cell_green"] for cell in block["cells"])
    passed_block = bool(block["block_green"] and green_cells == 4)
    failed_cells = [
        {
            "command_x_m_s": cell["command_x_m_s"],
            "samples": cell["behavior"]["samples"],
            "core_pass": cell["behavior"]["core_pass"],
            "replacement_quality_pass": cell["behavior"][
                "replacement_quality_pass"
            ],
            "mean_local_vx_m_s": cell["behavior"]["mean_local_vx_m_s"],
            "pitch_tracking_p95_rad": cell["behavior"][
                "pitch_tracking_p95_rad"
            ],
            "trace_valid": cell["trace_valid"],
            "cell_green": cell["cell_green"],
        }
        for cell in block["cells"]
        if not cell["cell_green"]
    ]
    decision = (
        prereg["decision_rule"]["all_completed_cells_green"]
        if passed_block
        else prereg["decision_rule"]["failed_completed_cell"]
    )
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t242b_interrupted_reporter_recovery_result.v1"
        ),
        "status": (
            "PASS_T242B_INTERRUPTED_REPORTER_RECOVERY"
            if passed_block
            else "HOLD_T242B_INTERRUPTED_REPORTER_RECOVERY"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_t242_contract_sha256": prereg[
            "source_t242_contract_sha256"
        ],
        "recovery": {
            "completed_blocks_reused": 1,
            "completed_cells_reused": 4,
            "new_behavior_cells": 0,
            "remaining_cells_not_run": 12,
            "no_completed_cell_rerun": True,
            "reporter_alias_in_memory_only": True,
        },
        "block": {
            "checkpoint_id": completed["checkpoint_id"],
            "fit_id": completed["fit_id"],
            "manifest": completed["manifest"],
            "green_cells": green_cells,
            "failed_cells": failed_cells,
            "result": block,
        },
        "execution": {
            "simulator_calls": 0,
            "behavior_cells_reused": 4,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t242c_missing_block_recovery_preregistration": passed_block,
            "resume_t242": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T242B interrupted reporter recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Recovered green cells: `{green_cells}/4`\n"
        f"- Failed commands: "
        f"`{[row['command_x_m_s'] for row in failed_cells]}`\n"
        "- Reused/new/not-run cells: `4/0/12`\n"
        "- Simulator/optimizer/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"green_cells={green_cells}/4")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed_block else 1


if __name__ == "__main__":
    raise SystemExit(main())
