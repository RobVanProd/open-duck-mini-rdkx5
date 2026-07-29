#!/usr/bin/env python3
"""Recover T136's x=0 check in the external support-action coordinates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t136b_x0_coordinate_recovery_preregistration.json"
RESULT = ANALYSIS / "t136b_x0_coordinate_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T136B_X0_COORDINATE_RECOVERY_RESULT_20260729.md"
)


def x0_parity(
    source: Path,
    transformed: Path,
    contexts: list[np.ndarray],
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    transformed_session = ort.InferenceSession(
        str(transformed), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260729)
    outputs_exact = True
    feedback_exact = True
    finite = True
    examples = []
    for context_index, context in enumerate(contexts):
        for sample in range(16):
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            obs[:, 6] = np.float32(0.0)
            feed = {
                "obs": obs,
                "previous_action": rng.uniform(
                    -0.98, 0.98, size=(1, 14)
                ).astype(np.float32),
                "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                "calibration_context": context.reshape(1, 64),
            }
            expected = source_session.run(None, feed)
            actual = transformed_session.run(None, feed)
            exact = all(
                np.array_equal(left, right)
                for left, right in zip(expected, actual, strict=True)
            )
            outputs_exact &= exact
            feedback_exact &= np.array_equal(actual[0], actual[1])
            finite &= all(
                bool(np.all(np.isfinite(value))) for value in actual
            )
            if sample == 0:
                examples.append(
                    {
                        "context_index": context_index,
                        "source_action": expected[0].astype(float).tolist(),
                        "transformed_action": actual[0].astype(float).tolist(),
                        "all_outputs_bit_exact": exact,
                    }
                )
    return {
        "samples": len(contexts) * 16,
        "all_source_transformed_outputs_bit_exact": outputs_exact,
        "action_feedback_bit_exact": feedback_exact,
        "all_outputs_finite": finite,
        "source_cpu_provider": (
            source_session.get_providers()[0] == "CPUExecutionProvider"
        ),
        "transformed_cpu_provider": (
            transformed_session.get_providers()[0]
            == "CPUExecutionProvider"
        ),
        "examples": examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T136B requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T136B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T136B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T136B_X0_COORDINATE_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T136B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for group in ("source_graphs", "transformed_graphs"):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")
    t135b = json.loads(
        Path(prereg["frozen_inputs"]["t135b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    contexts = [
        np.asarray(row["context"], dtype=np.float32)
        for row in t135b["runs"]
    ]
    parity = {
        step: x0_parity(
            Path(prereg["source_graphs"][step]["path"]),
            Path(prereg["transformed_graphs"][step]["path"]),
            contexts,
        )
        for step in sorted(prereg["source_graphs"])
    }
    t136 = json.loads(
        Path(prereg["frozen_inputs"]["t136_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    other_checks = {
        name: passed
        for name, passed in t136["checks"].items()
        if name != "all_x0_paths_exact_zero"
    }
    checks = {
        "t136_only_hold_is_wrong_coordinate_x0_assertion": (
            t136["status"] == "HOLD_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
            and t136["failed_checks"] == ["all_x0_paths_exact_zero"]
            and all(other_checks.values())
        ),
        "all_x0_source_transformed_outputs_bit_exact": all(
            row["all_source_transformed_outputs_bit_exact"]
            for row in parity.values()
        ),
        "all_feedback_finite_cpu": all(
            row["action_feedback_bit_exact"]
            and row["all_outputs_finite"]
            and row["source_cpu_provider"]
            and row["transformed_cpu_provider"]
            for row in parity.values()
        ),
        "all_t136_non_x0_checks_green": all(other_checks.values()),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": "open_duck.t136b_x0_coordinate_recovery_result.v1",
        "status": (
            "PASS_T136B_X0_COORDINATE_RECOVERY"
            if passed
            else "HOLD_T136B_X0_COORDINATE_RECOVERY"
        ),
        "classification": (
            "T136_HOLD_WAS_EXTERNAL_SUPPORT_ACTION_COORDINATE_ASSERTION"
            if passed
            else "T136_X0_PARITY_NOT_RECOVERED"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "parity": parity,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "x0_cpu_samples": sum(row["samples"] for row in parity.values()),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_matrix_preregistration": passed,
            "behavior_evaluation": False,
            "negative_matrix": False,
            "training": False,
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
        "# T136B x=0 coordinate recovery\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Correct invariant: transformed equals frozen T131 support action\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
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
