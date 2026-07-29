#!/usr/bin/env python3
"""Freeze T106 soft-gate policies' 16-cell nominal behavior matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T106_RESULT = ANALYSIS / "t106_soft_gate_transform_result.json"
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t107_soft_gate_nominal_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t107_soft_gate_nominal.py"
OUTPUT = ANALYSIS / "t107_soft_gate_nominal_preregistration.json"
MARKDOWN = ANALYSIS / "T107_SOFT_GATE_NOMINAL_PREREGISTRATION_20260728.md"


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
        raise PermissionError("T107 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T107 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T107 preregistration requires a clean worktree")

    t106 = json.loads(T106_RESULT.read_text(encoding="utf-8"))
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    contract = json.loads(T27_CONTRACT.read_text(encoding="utf-8"))
    policies = []
    for checkpoint_id, step in (
        ("T106_SOFT_GATE_HALF", "1003520"),
        ("T106_SOFT_GATE_FINAL", "2007040"),
    ):
        item = t106["transforms"][step]["output"]
        policies.append(
            {
                "checkpoint_id": checkpoint_id,
                "step": int(step),
                **item,
            }
        )
    condition = basis["conditions"][1]
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "worker": WORKER,
        "adapter": ADAPTER,
        "test": TEST,
        "t106_result": T106_RESULT,
        "t27_preregistration": T27_PREREG,
        "t27_runner_contract": T27_CONTRACT,
    }
    checks = {
        "t106_transform_exactly_green": (
            t106["status"] == "PASS_T106_SOFT_GATE_TRANSFORM"
            and t106["failed_checks"] == []
            and t106["decision"]
            == "EARN_T107_SOFT_GATE_NOMINAL_MATRIX_PREREGISTRATION_ONLY"
        ),
        "exactly_two_soft_gate_policies": len(policies) == 2,
        "all_policy_receipts_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies
        ),
        "condition_is_exact_nominal": (
            condition
            == {
                "condition_index": 2,
                "id": "FLOOR_FRICTION_HI",
                "override": {"floor_friction": 1.0},
            }
        ),
        "t27_runner_contract_green": (
            contract["status"]
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and contract["failed_checks"] == []
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
            "open_duck.t107_soft_gate_nominal_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T107_SOFT_GATE_NOMINAL_MATRIX"
            if not failed
            else "HOLD_T107_SOFT_GATE_NOMINAL_PREREGISTRATION"
        ),
        "question": (
            "Do both continuously gated T100C checkpoints preserve the "
            "complete nominal matrix under both measured actuator fits?"
        ),
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "conditions": [condition],
        "policies": policies,
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "repository_inputs": basis["repository_inputs"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "All 16 cells pass the unchanged frozen behavior, duration "
                "protection, handoff, readback, margin, current/torque, and "
                "rate contracts."
            ),
            "pass_decision": (
                "EARN_T108_SOFT_GATE_NEGATIVE_ENDPOINT_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
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
            "one_cpu_nominal_matrix": not failed,
            "negative_endpoint_preregistration": False,
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
                "# T107 continuous-gate nominal preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`",
                "- Both checkpoints required; no checkpoint selection",
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
