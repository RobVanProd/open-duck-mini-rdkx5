#!/usr/bin/env python3
"""Freeze recovery of T114B's protobuf field-presence implementation error."""

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
OUTPUT = ANALYSIS / "t114c_protobuf_presence_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T114C_PROTOBUF_PRESENCE_RECOVERY_PREREGISTRATION_20260729.md"
T114B_PREREG = ANALYSIS / "t114b_step_zero_attribution_preregistration.json"
T114B_RESULT = ANALYSIS / "t114b_step_zero_attribution_result.json"
SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t114c_protobuf_presence_recovery.py",
    "test": ROOT / "tests" / "test_t114c_protobuf_presence_recovery.py",
    "t114b_preregistration": T114B_PREREG,
    "t114b_result": T114B_RESULT,
}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T114C prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T114C preregistration requires clean worktree")

    prereg = json.loads(T114B_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T114B_RESULT.read_text(encoding="utf-8"))
    false_checks = sorted(
        name for name, passed in result["checks"].items() if not passed
    )
    checks = {
        "t114b_is_single_implementation_hold": (
            result["status"] == "HOLD_T114B_STEP_ZERO_READ_ONLY_ATTRIBUTION"
            and result["failed_checks"]
            == ["clearing_node_name_makes_protobuf_exact"]
            and false_checks == ["clearing_node_name_makes_protobuf_exact"]
        ),
        "t114b_numerical_and_structural_checks_passed": (
            result["checks"]["cpu_and_hosted_export_byte_exact"]
            and result["checks"]["only_node_27_differs"]
            and result["checks"]["node_27_contract_exact"]
            and result["checks"]["random_recurrent_chain_bit_exact"]
        ),
        "preregistered_wording_requires_clear_not_blank_assignment": (
            "clearing that name makes the protobuf exact"
            in prereg["decision_rule"]["pass"]
        ),
        "read_only_no_optimizer_behavior_hosted_or_robot": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T114C preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": "open_duck.t114c_protobuf_presence_recovery_preregistration.v1",
        "status": "PREREGISTERED_T114C_PROTOBUF_PRESENCE_RECOVERY",
        "question": (
            "Does protobuf ClearField('name'), rather than assigning an empty "
            "string that preserves field presence, make the preregistered "
            "normalized graph byte-exact?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "attribution": {
            "classification": "POST_COMPARISON_PROTOBUF_FIELD_PRESENCE_BUG",
            "failed_expression": "normalized.graph.node[27].name = ''",
            "recovery_expression": (
                "normalized.graph.node[27].ClearField('name')"
            ),
            "model_or_threshold_change": False,
        },
        "sources": {
            name: common.file_receipt(path)
            for name, path in SOURCE_FILES.items()
        },
        "assets": prereg["assets"],
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "ClearField makes the normalized expected model byte-exact "
                "to the hosted model; CPU and hosted exports remain byte-"
                "exact; and the frozen 256-step chain remains bit-exact."
            ),
            "pass_decision": (
                "EARN_T115_ALWAYS_ON_TRAINTHROUGH_NOMINAL_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "NO_BEHAVIOR_EVALUATION",
        },
        "authority": {
            "read_only_recovery": True,
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
                "# T114C protobuf presence recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Frozen change: empty-string assignment -> ClearField",
                "- Model / threshold / optimizer / behavior changes: 0 / 0 / 0 / 0",
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
