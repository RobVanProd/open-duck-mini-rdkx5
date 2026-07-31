#!/usr/bin/env python3
"""Freeze T72's sole 16-cell COM-x-negative behavior falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T72 = ANALYSIS / "t72_signed_core_mirror_result.json"
T70_PREREG = ANALYSIS / "t70_t67_condition7_preregistration.json"
T70_RESULT = ANALYSIS / "t70_t67_condition7_result.json"
T69_PREREG = ANALYSIS / "t69_t67_nominal_matrix_preregistration.json"
RUNNER = ROOT / "tools" / "run_t73_signed_core_mirror_condition7.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
TEST = ROOT / "tests" / "test_t73_signed_core_mirror_condition7.py"
OUTPUT = ANALYSIS / "t73_signed_core_mirror_condition7_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T73_SIGNED_CORE_MIRROR_CONDITION7_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
            raise FileExistsError(f"refusing to overwrite T73: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T73 preregistration requires a clean worktree")

    t72 = json.loads(T72.read_text(encoding="utf-8"))
    t70_prereg = json.loads(T70_PREREG.read_text(encoding="utf-8"))
    t70 = json.loads(T70_RESULT.read_text(encoding="utf-8"))
    t69 = json.loads(T69_PREREG.read_text(encoding="utf-8"))
    policies = [row["policy"] for row in t72["candidates"]]
    condition = t70_prereg["condition"]
    checks = {
        "t72_transform_contract_green": (
            t72["status"] == "PASS_T72_SIGNED_CORE_MIRROR"
            and t72["decision"]
            == "EARN_T73_SIGNED_CORE_MIRROR_CONDITION7_PREREGISTRATION"
            and not t72["failed_checks"]
        ),
        "exact_two_persistent_mirror_endpoints": (
            len(policies) == 2
            and {item["checkpoint_id"] for item in policies}
            == {
                "T72_SIGNED_CORE_MIRROR_HALF",
                "T72_SIGNED_CORE_MIRROR_FINAL",
            }
            and {item["step"] for item in policies}
            == {1_003_520, 2_007_040}
        ),
        "policy_receipts_exact": all(
            Path(item["path"]).is_file()
            and Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies
        ),
        "exact_prior_failed_boundary": (
            condition
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {
                    "torso_com_offset_m": [-0.05, 0.0, 0.0]
                },
            }
            and t70["condition"]["green_cells"] == 6
        ),
        "evaluation_assets_exact": all(
            Path(item["path"]).is_file()
            and sha256(Path(item["path"])) == item["sha256"]
            for item in [
                *t69["fits"],
                t69["calibrator"],
                t69["reference_feature_table"],
            ]
        ),
        "runner_stack_present": all(
            path.is_file()
            for path in (RUNNER, WORKER, ADAPTER, MATRIX_HELPER, TEST)
        ),
        "behavior_not_run": True,
        "training_colab_hardware_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t73_signed_core_mirror_condition7_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T73_SIGNED_CORE_MIRROR_CONDITION7"
            if not failed
            else "HOLD_T73_SIGNED_CORE_MIRROR_CONDITION7_PREREGISTRATION"
        ),
        "question": (
            "Do both signed recurrent-core mirror endpoints pass the exact "
            "16-cell torso-COM-x-negative boundary that selected the "
            "wrong-control-response diagnosis?"
        ),
        "causal_ordering": (
            "Condition 7 runs before nominal or the R2 remainder. Any failed "
            "cell closes the signed mirror mechanism without further behavior."
        ),
        "condition": condition,
        "conditions": [condition],
        "policies": policies,
        "fits": t69["fits"],
        "commands_x_m_s": t69["commands_x_m_s"],
        "seed": t69["seed"],
        "calibrator": t69["calibrator"],
        "reference_feature_table": t69["reference_feature_table"],
        "playground": t69["playground"],
        "support_handoff": t69["support_handoff"],
        "behavior_contract": t69["behavior_contract"],
        "protection_contract": t69["protection_contract"],
        "repository_inputs": t69["repository_inputs"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 16,
            "cpu_only": True,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": {
            "pass": "All 16 condition-7 cells are green.",
            "pass_decision": (
                "EARN_T74_SIGNED_CORE_MIRROR_NOMINAL_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_SIGNED_CORE_MIRROR",
            "no_retry": True,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
            "no_hosted_run_earned": True,
        },
        "frozen_inputs": {
            "t72_transform_result": receipt(T72),
            "t70_preregistration": receipt(T70_PREREG),
            "t70_result": receipt(T70_RESULT),
            "t69_evaluation_contract": receipt(T69_PREREG),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
            "matrix_helper": receipt(MATRIX_HELPER),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_condition7_matrix": not failed,
            "nominal_preregistration": False,
            "training": False,
            "colab": False,
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
                "# T73 signed recurrent-core mirror condition-7 preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Boundary: `TORSO_COM_X_NEG = -0.05 m`",
                "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16 cells`",
                "- All 16 required; no retry or checkpoint selection",
                "- Training / Colab / Gate5 / robot: `0/0/0/0`",
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
