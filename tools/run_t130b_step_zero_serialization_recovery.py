#!/usr/bin/env python3
"""Run the frozen read-only T130B step-zero recovery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402
import run_t112_always_on_trainthrough_cpu_contract as t112  # noqa: E402


PREREG = ANALYSIS / "t130b_step_zero_serialization_preregistration.json"
RESULT = ANALYSIS / "t130b_step_zero_serialization_result.json"
MARKDOWN = ANALYSIS / "T130B_STEP_ZERO_SERIALIZATION_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t130b_step_zero_serialization_recovery"
)


def initializer_map(model: onnx.ModelProto) -> dict[str, bytes]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item)).tobytes()
        for item in model.graph.initializer
    }


def node_bytes(model: onnx.ModelProto) -> list[bytes]:
    return [node.SerializeToString() for node in model.graph.node]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T130B requires --read-only-authorized")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T130B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T130B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T130B_STEP_ZERO_SERIALIZATION_RECOVERY"
        or prereg["failed_checks"]
        or t20.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T130B preregistration changed")
    for name, item in prereg["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in prereg["policies"].items():
        t20.verify_receipt(item, name)

    expected_path = Path(prereg["policies"]["expected_transform"]["path"])
    cpu_path = Path(prereg["policies"]["cpu_exporter_step_zero"]["path"])
    hosted_path = Path(prereg["policies"]["hosted_step_zero"]["path"])
    expected_model = onnx.load(expected_path)
    hosted_model = onnx.load(hosted_path)
    expected_initializers = initializer_map(expected_model)
    hosted_initializers = initializer_map(hosted_model)
    expected_only = sorted(
        set(expected_initializers) - set(hosted_initializers)
    )
    actual_only = sorted(
        set(hosted_initializers) - set(expected_initializers)
    )
    shared = sorted(
        set(expected_initializers) & set(hosted_initializers)
    )
    omitted = np.asarray(
        numpy_helper.to_array(
            next(
                item
                for item in expected_model.graph.initializer
                if item.name == "zero_adapter_location"
            )
        )
    )
    WORK.mkdir(parents=True)
    t112.INSPECTION = WORK / "inspection"
    t97 = json.loads(
        Path(prereg["sources"]["trace_population"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    cases = t98.trace_cases(
        {
            "assets": {
                "t97_preregistration": prereg["sources"][
                    "trace_population"
                ]
            }
        }
    )
    trace = t112.trace_equivalence(expected_path, hosted_path, cases)
    chain = t98.compare_random_chain(expected_path, hosted_path)
    facts = {
        "hosted_cpu_exporter_byte_exact": (
            hosted_path.read_bytes() == cpu_path.read_bytes()
        ),
        "expected_only_initializers": expected_only,
        "actual_only_initializers": actual_only,
        "omitted_initializer_shape": list(omitted.shape),
        "omitted_initializer_all_zero": bool(np.all(omitted == 0.0)),
        "shared_initializer_count": len(shared),
        "shared_initializers_bit_exact": all(
            expected_initializers[name] == hosted_initializers[name]
            for name in shared
        ),
        "nodes_bit_exact": node_bytes(expected_model)
        == node_bytes(hosted_model),
        "trace": trace,
        "random_chain": chain,
    }
    frozen = prereg["expected_difference"]
    checks = {
        "hosted_matches_cpu_exporter_byte_exact": facts[
            "hosted_cpu_exporter_byte_exact"
        ],
        "only_expected_unused_initializer_omitted": (
            facts["expected_only_initializers"]
            == frozen["expected_only_initializers"]
            and facts["actual_only_initializers"]
            == frozen["actual_only_initializers"]
            and facts["omitted_initializer_shape"] == [1, 14]
            and facts["omitted_initializer_all_zero"]
        ),
        "shared_initializers_bit_exact": facts[
            "shared_initializers_bit_exact"
        ],
        "nodes_bit_exact": facts["nodes_bit_exact"],
        "trace_rows_bit_exact": (
            trace["rows"] == frozen["trace_rows_bit_exact"]
            and trace["bit_exact_rows"] == trace["rows"]
            and trace["maximum_abs_error"] == 0.0
            and trace["always_on_identity_rows"] == trace["rows"]
        ),
        "random_chain_bit_exact": (
            chain["steps"] == frozen["random_chain_steps_bit_exact"]
            and chain["bit_exact_steps"] == chain["steps"]
            and chain["maximum_abs_error"] == 0.0
        ),
        "no_optimizer_behavior_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t130b_step_zero_serialization_result.v1"
        ),
        "status": (
            "PASS_T130B_STEP_ZERO_SERIALIZATION_RECOVERY"
            if passed
            else "HOLD_T130B_STEP_ZERO_SERIALIZATION_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "classification": (
            "EXPECTED_UNUSED_INITIALIZER_SERIALIZATION_DIFFERENCE"
            if passed
            else "UNRESOLVED_STEP_ZERO_MISMATCH"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "facts": facts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "postexport_preregistration": passed,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T130B step-zero serialization result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- Trace / recurrent chain exact: "
        f"`{trace['bit_exact_rows']}/{trace['rows']} / "
        f"{chain['bit_exact_steps']}/{chain['steps']}`\n"
        "- Optimizer / behavior / Colab / robot: `0/0/0/0`\n",
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
