#!/usr/bin/env python3
"""Freeze the rolling-midpoint pair's 16-cell nominal persistence gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
ROLLING = ANALYSIS / "t84_t78_rolling_midpoint_result.json"
T80_PREREG = ANALYSIS / "t80_t78_nominal_matrix_preregistration.json"
RUNNER = ROOT / "tools" / "run_t85_rolling_midpoint_nominal_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t85_rolling_midpoint_nominal_matrix.py"
OUTPUT = ANALYSIS / "t85_rolling_midpoint_nominal_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T85_ROLLING_MIDPOINT_NOMINAL_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
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
            raise FileExistsError(f"refusing to overwrite T85: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T85 preregistration requires a clean worktree")
    rolling = json.loads(ROLLING.read_text(encoding="utf-8"))
    basis = json.loads(T80_PREREG.read_text(encoding="utf-8"))
    policies = []
    for checkpoint_id, key, step_value in (
        ("T84_ROLLING_HALF", "rolling_half", 1_003_520),
        ("T84_ROLLING_FINAL", "rolling_final", 2_007_040),
    ):
        wrapped = rolling["policies"][key]["wrapped"]
        path = Path(wrapped["path"])
        if sha256(path) != wrapped["sha256"]:
            raise ValueError(f"changed T85 policy: {path}")
        policies.append(
            {
                "checkpoint_id": checkpoint_id,
                "step": step_value,
                "rolling_window": key,
                **wrapped,
            }
        )
    checks = {
        "t84_rolling_transform_green": (
            rolling["status"]
            == "PASS_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
            and rolling["failed_checks"] == []
            and rolling["decision"]
            == "EARN_T85_ROLLING_MIDPOINT_NOMINAL_PREREGISTRATION_ONLY"
        ),
        "exactly_two_uniformly_transformed_policies": len(policies) == 2,
        "rolling_final_matches_green_t81": (
            rolling["policies"]["rolling_final"]["byte_exact_to_t81_raw"]
        ),
        "formal_full_command_set_unchanged": (
            basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "exact_two_fits": len(basis["fits"]) == 2,
        "runner_worker_adapter_test_present": all(
            path.is_file() for path in (RUNNER, WORKER, ADAPTER, TEST)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t85_rolling_midpoint_nominal_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
            if not failed
            else "HOLD_T85_ROLLING_MIDPOINT_NOMINAL_PREREGISTRATION"
        ),
        "question": (
            "Do both adjacent-window rolling-midpoint policies pass every "
            "command under both measured actuator fits, establishing "
            "post-update persistence?"
        ),
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "conditions": basis["conditions"],
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
            "policies": 2,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 16,
            "execution_order": (
                "rolling half/final -> p30/p31_34 -> 0/.074/.077/.080"
            ),
            "condition_must_complete": True,
            "cpu_only": True,
        },
        "persistence_contract": {
            "both_rolling_exports_required": True,
            "same_transform_rule_at_both_exports": True,
            "no_checkpoint_selection": True,
            "no_coefficient_search": True,
        },
        "decision_rule": {
            "pass": (
                "All 16 cells pass unchanged behavior, corrected duration "
                "protection, handoff, readback, action-margin, and rate checks."
            ),
            "pass_decision": (
                "EARN_T86_ROLLING_MIDPOINT_R2_REVALIDATION_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_T78_ROLLING_ADAPTER_MIDPOINT",
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "frozen_inputs": {
            "t84_rolling_result": receipt(ROLLING),
            "t80_preregistration": receipt(T80_PREREG),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "execute_one_cpu_nominal_matrix": not failed,
            "robustness_preregistration": False,
            "robustness_execution": False,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T85 rolling-midpoint nominal preregistration",
                "",
                f"- Status: `{payload['status']}`",
                "- Cells: `16`",
                "- Policies: rolling half + rolling final, both required",
                "- Fits: `P30 / P31-34`",
                "- Commands: `0 / .074 / .077 / .080 m/s`",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
