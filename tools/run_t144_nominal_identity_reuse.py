#!/usr/bin/env python3
"""Reuse T102 nominal evidence through T143C's exact nominal branch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t144_nominal_identity_reuse_preregistration.json"
RESULT = ANALYSIS / "t144_nominal_identity_reuse_result.json"
MARKDOWN = ANALYSIS / "T144_NOMINAL_IDENTITY_REUSE_RESULT_20260729.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T144 requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T144: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T144 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T144_NOMINAL_IDENTITY_REUSE"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T144 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    t143c = json.loads(
        Path(prereg["frozen_inputs"]["t143c_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t102 = json.loads(
        Path(prereg["frozen_inputs"]["t102_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t102_prereg = json.loads(
        Path(prereg["frozen_inputs"]["t102_prereg"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    for block in t102["blocks"]:
        verify(block["manifest"], f"t102_manifest:{block['checkpoint_id']}")
    t102_policies = {
        str(item["step"]): {
            key: item[key] for key in ("path", "bytes", "sha256")
        }
        for item in t102_prereg["policies"]
    }
    source_identity = {
        step: t143c["graphs"][step]["nominal_source"] == t102_policies[step]
        for step in sorted(t143c["graphs"])
    }
    nominal_contract = {
        step: [
            row
            for row in t143c["contracts"][step]["rows"]
            if row["population"] == "nominal"
        ]
        for step in sorted(t143c["contracts"])
    }
    checks = {
        "t143c_transform_green": (
            t143c["status"] == "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            and t143c["failed_checks"] == []
        ),
        "t102_nominal_matrix_green": (
            t102["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102["condition"]["green_cells"] == 16
            and t102["condition"]["condition_green"]
        ),
        "nominal_sources_are_exact_t102_policies": all(source_identity.values()),
        "both_fit_contexts_select_t100c_bit_exact": all(
            len(rows) == 2
            and {row["fit_id"] for row in rows} == {"p30", "p31_34"}
            and all(
                row["selected_source"] == "T100C_nominal_dynamic_gate"
                and row["all_outputs_bit_exact"]
                for row in rows
            )
            for rows in nominal_contract.values()
        ),
        "all_t102_manifests_exact": True,
        "new_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    inherited = [
        {
            "source_checkpoint_id": block["checkpoint_id"],
            "step": (
                1_003_520
                if block["checkpoint_id"].endswith("HALF")
                else 2_007_040
            ),
            "fit_id": block["fit_id"],
            "green_cells": sum(
                cell["cell_green"] for cell in block["result"]["cells"]
            ),
            "manifest": block["manifest"],
        }
        for block in t102["blocks"]
    ]
    value: dict[str, Any] = {
        "schema_version": "open_duck.t144_nominal_identity_reuse_result.v1",
        "status": (
            "PASS_T144_NOMINAL_IDENTITY_REUSE"
            if passed
            else "HOLD_T144_NOMINAL_IDENTITY_REUSE"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_identity": source_identity,
        "nominal_contract": nominal_contract,
        "inherited_evidence": {
            "source": "T102_T100C_NOMINAL_MATRIX",
            "condition": t102["condition"],
            "blocks": inherited,
            "cells": 16,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "inherited_behavior_cells": 16,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "negative_endpoint_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T144 nominal identity reuse\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Inherited T102 nominal cells: `16/16 green`\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
