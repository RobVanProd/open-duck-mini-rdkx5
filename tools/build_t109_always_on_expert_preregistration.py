#!/usr/bin/env python3
"""Freeze T109's exact always-on T100C expert transform."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T101_RESULT = ANALYSIS / "t101_t100c_postexport_result.json"
T104_RESULT = ANALYSIS / "t104_t100c_gate_dynamics_result.json"
T108_RESULT = ANALYSIS / "t108_soft_gate_negative_endpoint_result.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t109_always_on_expert_transform.py"
TEST = ROOT / "tests" / "test_t109_always_on_expert.py"
OUTPUT = ANALYSIS / "t109_always_on_expert_preregistration.json"
MARKDOWN = ANALYSIS / "T109_ALWAYS_ON_EXPERT_PREREGISTRATION_20260728.md"


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
        raise PermissionError("T109 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T109 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T109 preregistration requires a clean worktree")

    t101 = json.loads(T101_RESULT.read_text(encoding="utf-8"))
    t104 = json.loads(T104_RESULT.read_text(encoding="utf-8"))
    t108 = json.loads(T108_RESULT.read_text(encoding="utf-8"))
    policies = {
        step: t101["deployments"][step]["wrapped"]
        for step in ("0", "1003520", "2007040")
    }
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t101_result": T101_RESULT,
        "t104_result": T104_RESULT,
        "t108_result": T108_RESULT,
    }
    checks = {
        "t104_proves_false_inactive_gate_rows": (
            t104["status"] == "PASS_T104_T100C_GATE_DYNAMICS_AUDIT"
            and t104["decision_inputs"][
                "negative_com_false_inactive_fraction_post_warmup"
            ]
            > 0.05
        ),
        "t108_closes_partial_continuous_mixture": (
            t108["status"] == "HOLD_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
            and t108["condition"]["green_cells"] == 4
            and t108["decision"]
            == "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM"
        ),
        "hard_gate_precedent_is_nine_of_sixteen": (
            json.loads(
                (ANALYSIS / "t103_t100c_negative_endpoint_result.json")
                .read_text(encoding="utf-8")
            )["condition"]["green_cells"]
            == 9
        ),
        "exact_three_source_graphs": len(policies) == 3,
        "all_source_receipts_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies.values()
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
            "open_duck.t109_always_on_expert_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T109_ALWAYS_ON_EXPERT_TRANSFORM"
            if not failed
            else "HOLD_T109_ALWAYS_ON_EXPERT_PREREGISTRATION"
        ),
        "question": (
            "Is T100C's learned negative residual a universal correction "
            "whose only defect was intermittent routing?"
        ),
        "policies": policies,
        "transform": {
            "replace": (
                "Where(negative_com_gate, negative_adapter_location, 0)"
            ),
            "with": "Identity(negative_adapter_location)",
            "head_scale": 1.0,
            "new_input_or_output": False,
            "new_recurrent_state": False,
            "initializer_change": False,
            "action_protection_order_change": False,
            "scalar_search": False,
        },
        "contract": {
            "maximum_step0_output_error": 1.0e-7,
            "maximum_x0_output_error": 1.0e-7,
            "maximum_active_branch_output_error": 1.0e-7,
            "minimum_inactive_branch_output_delta": 1.0e-6,
            "sample_ticks": [0, 8, 16, 32, 64, "last"],
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T110_ALWAYS_ON_EXPERT_NOMINAL_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T100C_ALWAYS_ON_EXPERT",
            "training_selection_weight": 0,
            "no_behavior_or_training": True,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "graphs_transformed": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_graph_transform": not failed,
            "nominal_preregistration": False,
            "behavior": False,
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
                "# T109 always-on expert preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Exact transform: gated head -> full-strength head",
                "- Scale/search/new state/new ABI: `1 / 0 / 0 / 0`",
                "- Behavior / training / Colab / robot: `0 / 0 / 0 / 0`",
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
