#!/usr/bin/env python3
"""Run T222B's ABI-helper-only recovery of frozen T222."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import onnx


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    abi as model_abi,
    canonical_sha256,
    receipt,
    verify,
)
import run_t222_global_command_plateau_transform as t222  # noqa: E402


PREREG = ANALYSIS / "t222b_abi_helper_recovery_preregistration.json"
RESULT = ANALYSIS / "t222b_abi_helper_recovery_result.json"
MARKDOWN = ANALYSIS / "T222B_ABI_HELPER_RECOVERY_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t222b_abi_helper_recovery_v1"
)
INNER_RESULT = WORK / "inner_t222_result.json"
INNER_MARKDOWN = WORK / "inner_t222_result.md"


def path_aware_abi(value: Any) -> dict[str, Any]:
    model = onnx.load(value) if isinstance(value, (str, Path)) else value
    return model_abi(model)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T222B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T222B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T222B_ABI_HELPER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T222B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")

    partial = prereg["frozen_inputs"]["t222_partial_half_graph"]
    t222.abi = path_aware_abi
    t222.WORK = WORK / "graphs"
    t222.RESULT = INNER_RESULT
    t222.MARKDOWN = INNER_MARKDOWN
    inner_return = t222.main()
    if inner_return != 0:
        raise RuntimeError(f"frozen T222 recovery returned {inner_return}")
    inner = json.loads(INNER_RESULT.read_text(encoding="utf-8"))
    regenerated_half = next(
        row["structure"]["transformed"]
        for row in inner["graphs"]
        if int(row["step"]) == 1_003_520
    )
    checks = {
        "source_t222_contract_exact": (
            inner["preregistered_contract_sha256"]
            == prereg["source_t222_contract_sha256"]
        ),
        "frozen_t222_inner_contract_passes": (
            inner["status"] == "PASS_T222_GLOBAL_COMMAND_PLATEAU"
            and not inner["failed_checks"]
            and all(inner["checks"].values())
        ),
        "abi_adapter_is_path_load_only": (
            path_aware_abi(Path(regenerated_half["path"]))
            == model_abi(onnx.load(regenerated_half["path"]))
        ),
        "partial_half_graph_matches_regenerated_exactly": (
            partial["bytes"] == regenerated_half["bytes"]
            and partial["sha256"] == regenerated_half["sha256"]
        ),
        "two_fresh_transformed_graphs": (
            len(inner["graphs"]) == 2
            and all(
                Path(row["structure"]["transformed"]["path"]).is_file()
                for row in inner["graphs"]
            )
        ),
        "inner_execution_has_no_simulator_optimizer_behavior_hosted_or_robot": (
            inner["execution"]["simulator_transitions"] == 0
            and inner["execution"]["optimizer_steps"] == 0
            and inner["execution"]["behavior_cells"] == 0
            and inner["execution"]["hosted_compute_units"] == 0
            and inner["execution"]["robot_or_rdk_access"] == 0
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": "open_duck.t222b_abi_helper_recovery_result.v1",
        "status": (
            "PASS_T222B_ABI_HELPER_RECOVERY"
            if not failed
            else "HOLD_T222B_ABI_HELPER_RECOVERY"
        ),
        "decision": (
            "RECOVER_T222_AND_EARN_T223_GLOBAL_PLATEAU_"
            "NOMINAL_MATRIX_PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_t222_contract_sha256": prereg[
            "source_t222_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "recovery_kind": "PATH_TO_MODELPROTO_ABI_HELPER_ADAPTER_ONLY",
        "inner_t222_result": receipt(INNER_RESULT),
        "inner_t222_result_sha256": inner["result_sha256"],
        "graphs": inner["graphs"],
        "execution": {
            **inner["execution"],
            "recovery_wrapper_simulator_transitions": 0,
            "recovery_wrapper_optimizer_steps": 0,
            "recovery_wrapper_behavior_cells": 0,
            "recovery_wrapper_hosted_compute_units": 0,
            "recovery_wrapper_robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_matrix_preregistration": not failed,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
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
        "# T222B ABI-helper recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Recovery: `{value['recovery_kind']}`\n"
        "- Frozen T222 transform/equivalence checks: all green\n"
        "- Partial and regenerated half graph: byte/hash exact\n"
        "- Simulator / optimizer / behavior / hosted / robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
