#!/usr/bin/env python3
"""Preregister read-only attribution of T114's step-zero byte hold."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from tools import (
        build_t112_always_on_trainthrough_preregistration as common,
    )
except ModuleNotFoundError:
    import build_t112_always_on_trainthrough_preregistration as common


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t114b_step_zero_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "T114B_STEP_ZERO_ATTRIBUTION_PREREGISTRATION_20260729.md"
T114 = ANALYSIS / "t114_t113_recovered_training_validation.json"
T112B = ANALYSIS / "t112b_cpu_recovery_result.json"
EXPECTED = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t112_always_on_trainthrough_cpu_v1/"
    "t100c_half_expected_always_on.onnx"
)
CPU_STEP_ZERO = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t112_always_on_trainthrough_cpu_v1/smoke/"
    "2026_07_29_011632_0.onnx"
)
HOSTED_STEP_ZERO = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t113_colab_extracted_20260729/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_054603_0.onnx"
)
SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t114b_step_zero_attribution.py",
    "test": ROOT / "tests" / "test_t114b_step_zero_attribution.py",
    "t114_hold": T114,
    "t112b_cpu_result": T112B,
}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T114B prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T114B preregistration requires clean worktree")

    t114 = json.loads(T114.read_text(encoding="utf-8"))
    t112b = json.loads(T112B.read_text(encoding="utf-8"))
    false_checks = sorted(
        name for name, passed in t114["checks"].items() if not passed
    )
    checks = {
        "t114_is_single_check_hold": (
            t114["status"] == "HOLD_T114_T113_RECOVERED_TRAINING_VALIDATION"
            and t114["failed_checks"] == ["step_zero_raw_onnx_byte_exact"]
            and false_checks == ["step_zero_raw_onnx_byte_exact"]
        ),
        "t112b_step_zero_functional_contract_green": (
            t112b["status"] == "PASS_T112B_READ_ONLY_CPU_RECOVERY"
            and t112b["failed_checks"] == []
            and t112b["causal_contract"]["step_zero_trace"]["bit_exact_rows"]
            == 72
            and t112b["causal_contract"]["step_zero_random_chain"][
                "bit_exact_steps"
            ]
            == 256
        ),
        "cpu_and_hosted_export_byte_exact": (
            common.sha256(CPU_STEP_ZERO)
            == common.sha256(HOSTED_STEP_ZERO)
        ),
        "expected_differs_from_export_bytes": (
            common.sha256(EXPECTED) != common.sha256(HOSTED_STEP_ZERO)
        ),
        "read_only_no_optimizer_behavior_hosted_or_robot": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T114B preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": "open_duck.t114b_step_zero_attribution_preregistration.v1",
        "status": "PREREGISTERED_T114B_STEP_ZERO_READ_ONLY_ATTRIBUTION",
        "question": (
            "Is T114's sole byte-identity failure caused only by protobuf "
            "node metadata, while the CPU and hosted exporters and all "
            "numerical outputs remain exact?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "contract": {
            "expected_model_and_hosted_model_node_count_equal": True,
            "abi_equal": True,
            "initializers_equal": True,
            "only_serialized_node_difference": {
                "index": 27,
                "op_type": "Identity",
                "expected_name": "t109_always_on_negative_adapter",
                "hosted_name": "",
                "inputs": ["negative_adapter_location"],
                "outputs": ["conditional_adapter_location"],
            },
            "cpu_hosted_byte_identity_required": True,
            "random_recurrent_chain_steps": 256,
            "maximum_numerical_error": 0.0,
        },
        "sources": {
            name: common.file_receipt(path)
            for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "expected_transform": common.file_receipt(EXPECTED),
            "cpu_step_zero_export": common.file_receipt(CPU_STEP_ZERO),
            "hosted_step_zero_export": common.file_receipt(HOSTED_STEP_ZERO),
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "CPU and hosted exports are byte-identical; expected and "
                "hosted models have identical ABI, initializers, and nodes "
                "except the preregistered Identity node name; clearing that "
                "name makes the protobuf exact; and 256 recurrent steps are "
                "numerically bit-exact."
            ),
            "pass_decision": (
                "EARN_T115_ALWAYS_ON_TRAINTHROUGH_NOMINAL_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "NO_BEHAVIOR_EVALUATION",
        },
        "authority": {
            "read_only_attribution": True,
            "optimizer_steps": False,
            "behavior_evaluation": False,
            "hosted_training": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = common.canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T114B step-zero attribution preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- T114 false checks: step_zero_raw_onnx_byte_exact only",
                "- CPU / hosted step-zero bytes: exact",
                "- Candidate attribution: one Identity node-name field",
                "- Optimizer / behavior / hosted / robot: 0 / 0 / 0 / 0",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
