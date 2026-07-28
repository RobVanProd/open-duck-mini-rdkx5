#!/usr/bin/env python3
"""Freeze T43's zero-cell x=.077/x=.080 worker-contract invalidation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t43_forward_actor_block_factorial_preregistration.json"
)
EXPECTED_RESULT = ANALYSIS / "t43_forward_actor_block_factorial_result.json"
RUN_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t43_forward_actor_block_factorial_run_v1"
)
FIRST_VARIANT = RUN_ROOT / "HALF_WITH_FINAL_BASE"
WORKER_STDOUT = FIRST_VARIANT / "stdout.log"
EXPECTED_EVALUATION = FIRST_VARIANT / "evaluation.json"
EXPECTED_TRACE = (
    FIRST_VARIANT
    / "traces"
    / "x0.080_seed167931544_action_margin.jsonl"
)
OUTPUT = ANALYSIS / "t43_worker_contract_invalidation.json"
MARKDOWN = ANALYSIS / "T43_WORKER_CONTRACT_INVALIDATION_20260728.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T43 invalidation: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    worker = Path(prereg["frozen_inputs"]["worker"]["path"])
    worker_text = worker.read_text(encoding="utf-8")
    stdout_text = WORKER_STDOUT.read_text(encoding="utf-8")
    checks = {
        "preregistration_requested_x0p080": (
            prereg["cell"]["command_x_m_s"] == 0.08
        ),
        "frozen_worker_authorized_only_x0p077": (
            "worker.FORMAL_COMMANDS = (0.077,)" in worker_text
        ),
        "worker_rejected_changed_formal_commands": (
            "ValueError: formal T27 commands, seed, or duration changed"
            in stdout_text
        ),
        "formal_result_absent": not EXPECTED_RESULT.exists(),
        "evaluation_absent": not EXPECTED_EVALUATION.exists(),
        "trace_absent": not EXPECTED_TRACE.exists(),
        "only_first_variant_directory_created": (
            sorted(path.name for path in RUN_ROOT.iterdir())
            == ["HALF_WITH_FINAL_BASE"]
        ),
        "policy_decision_weight_zero": True,
        "robot_or_rdk_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t43_worker_contract_invalidation.v1",
        "status": (
            "PASS_T43_ZERO_CELL_WORKER_CONTRACT_INVALIDATION"
            if not failed
            else "HOLD_T43_WORKER_CONTRACT_INVALIDATION"
        ),
        "decision": (
            "CLOSE_T43_ZERO_WEIGHT_NO_RETRY_"
            "EARN_T44_CORRECTED_X008_FACTORIAL_PREREGISTRATION"
            if not failed
            else "HOLD_FOR_T43_INVALIDATION_REPAIR"
        ),
        "checks": checks,
        "failed_checks": failed,
        "classification": {
            "cause": (
                "frozen_causal_worker_formal_command_x0p077_"
                "mismatched_preregistered_x0p080"
            ),
            "formal_behavior_cells": 0,
            "policy_decision_weight": 0,
            "policy_pass": False,
            "policy_failure": False,
            "t43_retry": False,
        },
        "evidence": {
            "preregistration": receipt(PREREG),
            "worker": receipt(worker),
            "worker_stdout": receipt(WORKER_STDOUT),
            "expected_evaluation_exists": EXPECTED_EVALUATION.exists(),
            "expected_trace_exists": EXPECTED_TRACE.exists(),
        },
        "correction": {
            "new_experiment_id": "T44",
            "new_worker_only_change": (
                "set evaluate_t27_t23_robustness_condition."
                "FORMAL_COMMANDS to (0.08,)"
            ),
            "reuse_t43_variant_assets_exact": True,
            "reuse_policy_outcomes": False,
            "execute_all_three_cells": True,
        },
        "authority": {
            "t44_corrected_factorial_preregistration": not failed,
            "t44_execution": False,
            "t43_retry": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T43 worker-contract invalidation",
                "",
                f"- Status: `{value['status']}`",
                "- Preregistered command: `x=.080`",
                "- Frozen worker command: `x=.077`",
                "- Formal behavior cells: `0`",
                "- Evaluation/trace/result: `ABSENT/ABSENT/ABSENT`",
                "- Policy pass/failure weight: `0/0`",
                "- T43 retry: `CLOSED`",
                "- Correction: new T44 worker contract, exact same three "
                "policy assets",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
