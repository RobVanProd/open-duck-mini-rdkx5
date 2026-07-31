#!/usr/bin/env python3
"""Run T241's targeted negative-home-offset behavior matrix."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t242_bounded_router_home_offset_preregistration.json"
RESULT = ANALYSIS / "t242_bounded_router_home_offset_result.json"
MARKDOWN = (
    ANALYSIS / "T242_BOUNDED_ROUTER_HOME_OFFSET_RESULT_20260731.md"
)
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t242_bounded_router_home_offset_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    receipt,
    run_or_load_block,
)
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    sha256,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T242 input: {path}")


def corrected_joint_offset_readback(
    report: dict[str, Any] | None, expected: float
) -> bool:
    report = report or {}
    value = report.get("value")
    readback = report.get("readback") or {}
    before = readback.get("before")
    after = readback.get("after")
    offset = readback.get("offset")
    return bool(
        report.get("enabled") is True
        and report.get("key") == "joint_qpos0_offset_rad"
        and isinstance(value, list)
        and isinstance(offset, list)
        and isinstance(before, list)
        and isinstance(after, list)
        and len(value) == len(offset) == len(before) == len(after) == 14
        and all(item == expected for item in value)
        and all(item == expected for item in offset)
        and all(
            math.isclose(
                float(right) - float(left),
                expected,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
            for left, right in zip(before, after, strict=True)
        )
    )


def corrected_extract_block(
    prereg: dict[str, Any],
    condition: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    result = extract_block(prereg, condition, manifest)
    evaluation = json.loads(
        Path(manifest["evaluation_path"]).read_text(encoding="utf-8")
    )
    runs = evaluation["runs"]
    if len(runs) != 4 or len(result["cells"]) != 4:
        raise RuntimeError("T242 evaluation cell count changed")
    expected = float(condition["override"]["joint_qpos0_offset_rad"])
    for cell, run in zip(result["cells"], runs, strict=True):
        corrected = corrected_joint_offset_readback(
            run.get("dynamics_override"), expected
        )
        cell["legacy_override_readback_exact"] = cell[
            "override_readback_exact"
        ]
        cell["override_readback_exact"] = corrected
        cell["cell_green"] = bool(
            cell["trace_valid"]
            and cell["behavior"]["core_pass"]
            and cell["behavior"]["replacement_quality_pass"]
            and cell["protection"]["duration_protection_pass"]
            and cell["protection"][
                "maximum_full_measured_vector_excess_rad_s"
            ]
            == 0.0
            and cell["handoff"]["all_checks_pass"]
            and corrected
        )
    result["block_green"] = bool(
        result["worker_inputs_exact"]
        and result["execution_platform"] == "cpu"
        and len(result["cells"]) == 4
        and all(cell["cell_green"] for cell in result["cells"])
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or CACHE.exists():
        raise FileExistsError("refusing to overwrite T242 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T242 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T242_BOUNDED_ROUTER_HOME_OFFSET"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T242 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in [
        *prereg["repository_inputs"].values(),
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
        prereg["playground"]["manifest"],
    ]:
        verify(item)

    CACHE.mkdir(parents=True)
    condition = prereg["condition"]
    blocks: list[dict[str, Any]] = []
    started = time.time()
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg, condition, policy, fit, CACHE
            )
            block_result = corrected_extract_block(
                prereg, condition, manifest
            )
            manifest_path = (
                CACHE
                / f"{condition['condition_index']:02d}_{condition['id']}"
                / policy["checkpoint_id"]
                / fit["fit_id"]
                / "manifest.json"
            )
            blocks.append(
                {
                    "condition_id": condition["id"],
                    "condition_index": condition["condition_index"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "step": policy["step"],
                    "fit_id": fit["fit_id"],
                    "cached": cached,
                    "manifest": receipt(manifest_path),
                    "result": block_result,
                }
            )
            print(
                json.dumps(
                    {
                        "block": (
                            f"{policy['checkpoint_id']}:{fit['fit_id']}"
                        ),
                        "green_cells": sum(
                            cell["cell_green"]
                            for cell in block_result["cells"]
                        ),
                        "elapsed_s": time.time() - started,
                    }
                ),
                flush=True,
            )
    summary = condition_summary(condition, blocks)
    passed = bool(summary["condition_green"])
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t242_bounded_router_home_offset_result.v1"
        ),
        "status": (
            "PASS_T242_BOUNDED_ROUTER_HOME_OFFSET"
            if passed
            else "HOLD_T242_BOUNDED_ROUTER_HOME_OFFSET"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": summary,
        "blocks": blocks,
        "readback_correction": {
            "legacy_false_cells": sum(
                not cell["legacy_override_readback_exact"]
                for block in blocks
                for cell in block["result"]["cells"]
            ),
            "corrected_true_cells": sum(
                cell["override_readback_exact"]
                for block in blocks
                for cell in block["result"]["cells"]
            ),
            "behavior_selection_weight": 0,
        },
        "execution": {
            "behavior_cells": 16,
            "wall_seconds": time.time() - started,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "preservation_preregistration": passed,
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
        "# T242 bounded-router home-offset result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{summary['green_cells']}/16`\n"
        f"- Worst tracking p95: "
        f"`{summary['worst_tracking_p95_rad']:.9f}`\n"
        f"- Minimum moving vx: "
        f"`{summary['minimum_moving_vx_m_s']:.9f}`\n"
        "- Training/hosted/robot: `0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
