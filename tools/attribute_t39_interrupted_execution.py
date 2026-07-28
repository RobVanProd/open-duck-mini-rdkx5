#!/usr/bin/env python3
"""Freeze T39's interrupted 8/16-cell execution with zero policy weight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
EXPECTED_RESULT = (
    ANALYSIS / "t39_uniform_normalizer_rollback_nominal_result.json"
)
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t39_uniform_normalizer_rollback_nominal_v1"
)
OUTPUT = ANALYSIS / "t39_interrupted_execution_attribution.json"
MARKDOWN = ANALYSIS / "T39_INTERRUPTED_EXECUTION_ATTRIBUTION_20260728.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T39 attribution: {path}")
    prereg = load(PREREG)
    manifests = sorted(CACHE_ROOT.rglob("manifest.json"))
    completed = []
    trace_count = 0
    for path in manifests:
        value = load(path)
        contract = value["block_contract"]
        traces = value["traces"]
        trace_count += len(traces)
        completed.append(
            {
                "checkpoint_id": contract["policy"]["checkpoint_id"],
                "fit_id": contract["fit"]["fit_id"],
                "commands_x_m_s": contract["commands_x_m_s"],
                "manifest": receipt(path),
                "evaluation": value["evaluation"],
                "stdout": value["stdout"],
                "traces": traces,
            }
        )
    identities = sorted(
        (row["checkpoint_id"], row["fit_id"]) for row in completed
    )
    expected = sorted(
        [
            ("T39_UNIFORM_NORMALIZER_HALF", "p30"),
            ("T39_UNIFORM_NORMALIZER_HALF", "p31_34"),
        ]
    )
    checks = {
        "preregistration_green": prereg["status"] == (
            "PREREGISTERED_T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_MATRIX"
        ),
        "formal_result_absent": not EXPECTED_RESULT.exists(),
        "exactly_two_complete_manifests": len(manifests) == 2,
        "completed_identity_is_half_both_fits": identities == expected,
        "exactly_eight_trace_receipts": trace_count == 8,
        "each_manifest_has_four_commands": all(
            len(row["traces"]) == 4 for row in completed
        ),
        "final_checkpoint_manifests_absent": not any(
            row["checkpoint_id"] == "T39_UNIFORM_NORMALIZER_FINAL"
            for row in completed
        ),
        "no_cell_outcomes_used_for_recovery_decision": True,
        "no_policy_pass_or_failure_claimed": True,
        "robot_or_rdk_absent": not prereg["authority"]["rdkx5_or_robot"],
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t39_interrupted_execution.v1",
        "status": (
            "PASS_T39_INTERRUPTED_EXECUTION_ATTRIBUTION"
            if not failed
            else "HOLD_T39_INTERRUPTED_EXECUTION_ATTRIBUTION"
        ),
        "decision": (
            "CLOSE_T39_ZERO_WEIGHT_EARN_T40_EXACT_CACHE_RECOVERY_PREREGISTRATION"
            if not failed
            else "HOLD_FOR_T39_INTERRUPTION_ATTRIBUTION_REPAIR"
        ),
        "checks": checks,
        "failed_checks": failed,
        "classification": {
            "execution_state": "interrupted_before_result_aggregation",
            "root_cause": "external_process_exit_unresolved",
            "formal_result_exists": EXPECTED_RESULT.exists(),
            "completed_blocks": 2,
            "completed_cells": 8,
            "missing_blocks": 2,
            "missing_cells": 8,
            "policy_decision_weight": 0,
            "policy_pass": False,
            "policy_failure": False,
            "t39_retry": False,
        },
        "completed_blocks": completed,
        "hashes": {
            "t39_preregistration": sha256(PREREG),
        },
        "recovery_rule": {
            "new_experiment_id": "T40",
            "reuse_only_exact_manifest_receipts": True,
            "do_not_reexecute_completed_blocks": True,
            "execute_only_missing_final_checkpoint_blocks": True,
            "aggregate_all_sixteen_cells_after_completion": True,
            "inspect_completed_cell_outcomes_before_preregistration": False,
        },
        "authority": {
            "t40_exact_recovery_preregistration": not failed,
            "t40_execution": False,
            "t39_retry": False,
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
                "# T39 interrupted execution attribution",
                "",
                f"- Status: `{value['status']}`",
                "- Complete immutable evidence: `8/16 cells`",
                "- T39 result: `ABSENT`",
                "- Policy pass/failure weight: `0/0`",
                "- T39 retry: `CLOSED`",
                "- Recovery: new T40 contract; reuse exact manifests and "
                "execute only the missing eight cells",
                "- Gate 5 / RDK-X5 / robot authority: `CLOSED`",
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
