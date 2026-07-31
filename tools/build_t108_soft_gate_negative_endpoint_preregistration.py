#!/usr/bin/env python3
"""Freeze the T106 soft-gate exact negative-COM endpoint matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T107_PREREG = ANALYSIS / "t107_soft_gate_nominal_preregistration.json"
T107_RESULT = ANALYSIS / "t107_soft_gate_nominal_result.json"
R2_BASIS = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t108_soft_gate_negative_endpoint.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t108_soft_gate_negative_endpoint.py"
OUTPUT = ANALYSIS / "t108_soft_gate_negative_endpoint_preregistration.json"
MARKDOWN = ANALYSIS / "T108_SOFT_GATE_NEGATIVE_ENDPOINT_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T108 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T108 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T108 preregistration requires a clean worktree")

    t107_prereg = json.loads(T107_PREREG.read_text(encoding="utf-8"))
    t107 = json.loads(T107_RESULT.read_text(encoding="utf-8"))
    basis = json.loads(R2_BASIS.read_text(encoding="utf-8"))
    contract = json.loads(T27_CONTRACT.read_text(encoding="utf-8"))
    condition = next(
        item for item in basis["conditions"] if item["condition_index"] == 7
    )
    policies = t107_prereg["policies"]
    fits = t107_prereg["fits"]
    commands = t107_prereg["commands_x_m_s"]
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            [condition],
            policies,
            fits,
            commands,
            int(t107_prereg["seed"]),
        )
    finally:
        sys.path.pop(0)
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "matrix_helper": MATRIX_HELPER,
        "worker": WORKER,
        "adapter": ADAPTER,
        "test": TEST,
        "t107_preregistration": T107_PREREG,
        "t107_result": T107_RESULT,
        "r2_basis": R2_BASIS,
        "t27_runner_contract": T27_CONTRACT,
    }
    checks = {
        "t107_nominal_exactly_sixteen_of_sixteen": (
            t107["status"] == "PASS_T107_SOFT_GATE_NOMINAL_MATRIX"
            and t107["condition"]["green_cells"] == 16
            and t107["decision"]
            == "EARN_T108_SOFT_GATE_NEGATIVE_ENDPOINT_PREREGISTRATION_ONLY"
        ),
        "condition_is_exact_negative_com_x": (
            condition
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
            }
        ),
        "runner_contract_green": (
            contract["status"]
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and contract["failed_checks"] == []
        ),
        "matrix_exactly_sixteen_cells": len(plan) == 16,
        "all_policy_and_fit_receipts_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in [*policies, *fits]
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t108_soft_gate_negative_endpoint_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
            if not failed
            else "HOLD_T108_SOFT_GATE_NEGATIVE_ENDPOINT_PREREGISTRATION"
        ),
        "question": (
            "Does the continuous expert mixture repair the exact "
            "torso-COM-X-negative endpoint persistently at both checkpoints?"
        ),
        "condition": condition,
        "policies": policies,
        "fits": fits,
        "calibrator": t107_prereg["calibrator"],
        "reference_feature_table": t107_prereg[
            "reference_feature_table"
        ],
        "playground": t107_prereg["playground"],
        "commands_x_m_s": commands,
        "seed": t107_prereg["seed"],
        "support_handoff": t107_prereg["support_handoff"],
        "behavior_contract": t107_prereg["behavior_contract"],
        "protection_contract": t107_prereg["protection_contract"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "plan_sha256": canonical_sha256(
                {"plan": plan}, "unused"
            ),
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": {
            "pass": (
                "All 16 cells pass the unchanged frozen behavior, duration "
                "protection, handoff, readback, margin, current/torque, and "
                "rate contracts."
            ),
            "pass_decision": (
                "EARN_T109_SOFT_GATE_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_negative_endpoint_matrix": not failed,
            "full_r2_preregistration": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T108 continuous-gate negative endpoint preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Condition: exact `TORSO_COM_X_NEG [-.05, 0, 0] m`",
                "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`",
                "- Both checkpoints required; no selection",
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
