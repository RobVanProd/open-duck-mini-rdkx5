#!/usr/bin/env python3
"""Validate T159 x=0 preservation in the wrapped action coordinates."""

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
    verify,
)


PREREG = (
    ANALYSIS / "t159b_x0_coordinate_contract_preregistration.json"
)
RESULT = ANALYSIS / "t159b_x0_coordinate_contract_result.json"
MARKDOWN = (
    ANALYSIS / "T159B_X0_COORDINATE_CONTRACT_RESULT_20260729.md"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T159B requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T159B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T159B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T159B_X0_COORDINATE_CONTRACT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T159B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for group in ("source_graphs", "transformed_graphs"):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")

    t159 = json.loads(
        Path(prereg["frozen_inputs"]["t159_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t135b = json.loads(
        Path(prereg["frozen_inputs"]["t135b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t156_vectors = json.loads(
        Path(prereg["frozen_inputs"]["t156_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    contexts = [*t135b["runs"], *t156_vectors["positive_contexts"]]
    rng = np.random.default_rng(20260729)
    contracts = {}
    for step in ("1003520", "2007040"):
        source = ort.InferenceSession(
            prereg["source_graphs"][step]["path"],
            providers=["CPUExecutionProvider"],
        )
        transformed = ort.InferenceSession(
            prereg["transformed_graphs"][step]["path"],
            providers=["CPUExecutionProvider"],
        )
        rows = []
        for context in contexts:
            exact = True
            finite = True
            maximum_delta = 0.0
            for _ in range(
                prereg["samples"][
                    "random_states_per_context_per_checkpoint"
                ]
            ):
                feed = {
                    "obs": rng.normal(size=(1, 115)).astype(np.float32),
                    "previous_action": rng.uniform(
                        -0.98, 0.98, size=(1, 14)
                    ).astype(np.float32),
                    "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                    "calibration_context": np.asarray(
                        context["context"], dtype=np.float32
                    ).reshape(1, 64),
                }
                feed["obs"][
                    :,
                    prereg["samples"]["command_source_observation_index"],
                ] = np.float32(prereg["samples"]["command_x_m_s"])
                expected = source.run(None, feed)
                actual = transformed.run(None, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(expected, actual, strict=True)
                )
                finite &= all(
                    bool(np.all(np.isfinite(value))) for value in actual
                )
                maximum_delta = max(
                    maximum_delta,
                    max(
                        float(np.max(np.abs(left - right)))
                        for left, right in zip(
                            expected,
                            actual,
                            strict=True,
                        )
                    ),
                )
            rows.append(
                {
                    "fit_id": context["fit_id"],
                    "population": context["population"],
                    "samples": prereg["samples"][
                        "random_states_per_context_per_checkpoint"
                    ],
                    "all_three_outputs_bit_exact": exact,
                    "all_outputs_finite": finite,
                    "maximum_abs_delta": maximum_delta,
                }
            )
        contracts[step] = {
            "rows": rows,
            "all_contexts_all_outputs_bit_exact": all(
                row["all_three_outputs_bit_exact"] for row in rows
            ),
            "all_outputs_finite": all(
                row["all_outputs_finite"] for row in rows
            ),
            "samples": sum(row["samples"] for row in rows),
            "cpu_only": (
                source.get_providers()[0] == "CPUExecutionProvider"
                and transformed.get_providers()[0]
                == "CPUExecutionProvider"
            ),
        }
    checks = {
        "both_checkpoints_x0_bit_exact": all(
            row["all_contexts_all_outputs_bit_exact"]
            for row in contracts.values()
        ),
        "all_outputs_finite_cpu": all(
            row["all_outputs_finite"] and row["cpu_only"]
            for row in contracts.values()
        ),
        "graph_and_mechanics_unchanged": (
            all(
                prereg["transformed_graphs"][step]
                == t159["graphs"][step]["transformed"]
                for step in ("1003520", "2007040")
            )
        ),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t159b_x0_coordinate_contract_result.v1"
        ),
        "status": (
            "PASS_T159B_X0_COORDINATE_CONTRACT"
            if passed
            else "HOLD_T159B_X0_COORDINATE_CONTRACT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "graphs_changed": 0,
            "cpu_equivalence_samples": sum(
                row["samples"] for row in contracts.values()
            ),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "positive_endpoint_preregistration": passed,
            "behavior_evaluation": False,
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
        "# T159B x=0 coordinate contract\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Required invariant: transformed/source output bit identity\n"
        "- Graph changes / behavior / optimizer / Colab / robot: "
        "`0/0/0/0/0`\n",
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
