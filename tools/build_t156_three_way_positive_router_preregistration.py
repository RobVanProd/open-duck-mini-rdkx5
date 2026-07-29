#!/usr/bin/env python3
"""Freeze the zero-training positive-COM three-way router transform."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T135 = ANALYSIS / "t135_calibration_context_router_preregistration.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T143C = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
T151 = ANALYSIS / "t151_command_plateau_full_r2_result.json"
T155 = ANALYSIS / "t155_t154_recovered_training_validation.json"
OUTPUT = ANALYSIS / "t156_three_way_positive_router_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T156_THREE_WAY_POSITIVE_ROUTER_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t156_three_way_positive_router_transform.py"
TEST = ROOT / "tests" / "test_t156_three_way_positive_router.py"
POSITIVE_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t154_colab_extracted_20260729/"
    "t154_positive_only_expert_continuation/training"
)
POSITIVE_GRAPHS = {
    "1003520": (
        POSITIVE_ROOT / "2026_07_29_183922_1003520.onnx"
    ),
    "2007040": (
        POSITIVE_ROOT / "2026_07_29_184434_2007040.onnx"
    ),
}


def positive_hashes(t151: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, set[str]] = {}
    for block in t151["blocks"]:
        if block["condition_id"] != "TORSO_COM_X_POS":
            continue
        fit_id = block["fit_id"]
        for cell in block["result"]["cells"]:
            hashes.setdefault(fit_id, set()).add(
                cell["handoff"]["context_sha256"]
            )
    if set(hashes) != {"p30", "p31_34"} or any(
        len(values) != 1 for values in hashes.values()
    ):
        raise RuntimeError(f"T156 positive context hashes changed: {hashes}")
    return {
        fit_id: next(iter(values))
        for fit_id, values in hashes.items()
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T156: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T156 preregistration requires clean worktree")

    t135 = json.loads(T135.read_text(encoding="utf-8"))
    t135b = json.loads(T135B.read_text(encoding="utf-8"))
    t143c = json.loads(T143C.read_text(encoding="utf-8"))
    t151 = json.loads(T151.read_text(encoding="utf-8"))
    t155 = json.loads(T155.read_text(encoding="utf-8"))
    source_graphs = {
        step: Path(t143c["graphs"][step]["transformed"]["path"])
        for step in ("1003520", "2007040")
    }
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "evaluator": Path(t135["frozen_inputs"]["evaluator"]["path"]),
        "t135_preregistration": T135,
        "t135b_result": T135B,
        "t143c_result": T143C,
        "t151_result": T151,
        "t155_validation": T155,
    }
    expected_hashes = positive_hashes(t151)
    checks = {
        "t135b_context_basis_green": (
            t135b["status"]
            == "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
            and t135b["failed_checks"] == []
        ),
        "t143c_source_green": (
            t143c["status"]
            == "PASS_T143C_RUNNER_RECEIPT_RECOVERY"
            and t143c["failed_checks"] == []
        ),
        "t151_first_failure_positive_com": (
            t151["summary"]["first_failed_condition"]
            == "TORSO_COM_X_POS"
            and t151["summary"]["completed_conditions"] == 8
        ),
        "t155_positive_training_green": (
            t155["status"]
            == "PASS_T155_T154_RECOVERED_TRAINING_VALIDATION"
            and t155["failed_checks"] == []
            and t155["decision"]
            == "EARN_T156_POSITIVE_EXPERT_THREE_WAY_ROUTER_"
            "PREREGISTRATION_ONLY"
        ),
        "two_expected_positive_context_hashes": (
            set(expected_hashes) == {"p30", "p31_34"}
            and all(len(value) == 64 for value in expected_hashes.values())
        ),
        "source_and_positive_graphs_present": all(
            path.is_file()
            for path in (*source_graphs.values(), *POSITIVE_GRAPHS.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T156 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t156_three_way_positive_router_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM"
        ),
        "question": (
            "Can the learned positive-COM expert be selected only by the "
            "existing automatic calibration context while preserving "
            "T143C nominal/negative outputs exactly?"
        ),
        "source_graphs": {
            step: receipt(path) for step, path in source_graphs.items()
        },
        "positive_graphs": {
            step: receipt(path)
            for step, path in POSITIVE_GRAPHS.items()
        },
        "expected_positive_context_hashes": expected_hashes,
        "fits": t135["fits"],
        "playground": t135["playground"],
        "calibrator": t135["calibrator"],
        "reference_feature_table": t135["reference_feature_table"],
        "calibration": {
            "command_x_m_s": 0.074,
            "seed": 167931544,
            "ticks_per_fit": 250,
            "diagnostic_behavior_ticks_per_fit": 1,
            "override": {"torso_com_offset_m": [0.05, 0.0, 0.0]},
        },
        "classifier": {
            "positive_population": "two +0.05m COM contexts",
            "nonpositive_population": (
                "four frozen T135B nominal/negative contexts"
            ),
            "rule": "unit centroid direction with midpoint threshold",
            "required_full_labels": "all six exact",
            "required_leave_one_fit_out_labels": "all six exact",
            "minimum_margin": "strictly greater than zero",
            "scalar_search": False,
        },
        "transform": {
            "nominal_and_negative": (
                "byte-exact T143C selected source outputs"
            ),
            "positive": (
                "T154 positive expert tensors through the unchanged "
                "T143C deployment chain"
            ),
            "abi": "unchanged 115+14+64+64 to 14+14+64",
            "checkpoints": [1003520, 2007040],
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T157_POSITIVE_COM_ENDPOINT_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_POSITIVE_EXPERT_ROUTER",
        },
        "execution_now": {
            "calibration_prefixes": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "two_calibration_only_prefixes": True,
            "one_cpu_graph_transform": True,
            "positive_endpoint_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T156 three-way positive router preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Recover exactly two +COM calibration contexts\n"
        "- Require full and leave-one-fit-out context separation\n"
        "- Preserve T143C nominal/negative outputs bit-exactly\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
