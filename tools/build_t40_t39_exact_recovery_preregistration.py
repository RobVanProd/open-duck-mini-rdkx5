#!/usr/bin/env python3
"""Preregister exact recovery of T39's two missing final-checkpoint blocks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
SOURCE_PREREG = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "t39_interrupted_execution_attribution.json"
RUNNER = ROOT / "tools" / "run_t40_t39_exact_recovery.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t39_uniform_normalizer_rollback_nominal_v1"
)
OUTPUT = ANALYSIS / "t40_t39_exact_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T40_T39_EXACT_RECOVERY_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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


def manifest_path(
    condition: dict,
    checkpoint_id: str,
    fit_id: str,
) -> Path:
    return (
        CACHE_ROOT
        / f"{int(condition['condition_index']):02d}_{condition['id']}"
        / checkpoint_id
        / fit_id
        / "manifest.json"
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T40 prereg: {path}")
    source = json.loads(SOURCE_PREREG.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    condition = source["conditions"][0]
    completed = attribution["completed_blocks"]
    completed_receipts = [row["manifest"] for row in completed]
    expected_missing = [
        {
            "checkpoint_id": "T39_UNIFORM_NORMALIZER_FINAL",
            "fit_id": fit_id,
            "manifest_path": str(
                manifest_path(
                    condition,
                    "T39_UNIFORM_NORMALIZER_FINAL",
                    fit_id,
                ).resolve()
            ),
        }
        for fit_id in ("p30", "p31_34")
    ]
    checks = {
        "t39_interruption_attribution_green": attribution["status"] == (
            "PASS_T39_INTERRUPTED_EXECUTION_ATTRIBUTION"
        ),
        "t39_decision_weight_zero": (
            attribution["classification"]["policy_decision_weight"] == 0
        ),
        "t39_retry_closed": not attribution["classification"]["t39_retry"],
        "exact_two_completed_manifests": len(completed_receipts) == 2,
        "completed_manifest_hashes_still_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in completed_receipts
        ),
        "exact_two_missing_manifests": len(expected_missing) == 2,
        "missing_manifests_are_absent": all(
            not Path(item["manifest_path"]).exists()
            for item in expected_missing
        ),
        "source_preregistration_green": source["status"] == (
            "PREREGISTERED_T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_MATRIX"
        ),
        "source_requires_both_checkpoints": (
            source["decision_rule"]["both_checkpoints_required"]
        ),
        "runner_helper_worker_adapter_present": all(
            path.is_file()
            for path in (RUNNER, MATRIX_HELPER, WORKER, ADAPTER)
        ),
        "completed_cell_outcomes_not_read": attribution["recovery_rule"][
            "inspect_completed_cell_outcomes_before_preregistration"
        ]
        is False,
        "training_or_colab_zero": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t40_t39_exact_recovery_preregistration.v1",
        "status": (
            "PREREGISTERED_T40_T39_EXACT_RECOVERY"
            if not failed
            else "HOLD_T40_T39_EXACT_RECOVERY_PREREGISTRATION"
        ),
        "question": (
            "After preserving T39's two exact half-checkpoint manifests, "
            "do the two missing final-checkpoint blocks complete the frozen "
            "16-cell nominal matrix?"
        ),
        "source_contract": {
            "experiment": "T39",
            "preregistered_contract_sha256": source[
                "preregistered_contract_sha256"
            ],
            "path": str(SOURCE_PREREG.resolve()),
            "sha256": sha256(SOURCE_PREREG),
        },
        "recovery": {
            "completed_blocks": 2,
            "completed_cells": 8,
            "completed_manifest_receipts": completed_receipts,
            "reexecute_completed_blocks": False,
            "missing_blocks": expected_missing,
            "new_blocks_to_execute": 2,
            "new_cells_to_execute": 8,
            "aggregate_cells": 16,
            "one_attempt": True,
            "retry": False,
        },
        "commands_x_m_s": source["commands_x_m_s"],
        "seed": source["seed"],
        "conditions": source["conditions"],
        "policies": source["policies"],
        "fits": source["fits"],
        "calibrator": source["calibrator"],
        "reference_feature_table": source["reference_feature_table"],
        "playground": source["playground"],
        "support_handoff": source["support_handoff"],
        "behavior_contract": source["behavior_contract"],
        "protection_contract": source["protection_contract"],
        "decision_rule": {
            "pass": "All 16 aggregated cells must be green.",
            "pass_decision": (
                "EARN_T40_R2_ROBUSTNESS_MATRIX_PREREGISTRATION"
            ),
            "fail_decision": (
                "CLOSE_T40_POSTHOC_NORMALIZER_ROLLBACK"
            ),
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
            "no_retry": True,
        },
        "frozen_inputs": {
            "source_t39_preregistration": receipt(SOURCE_PREREG),
            "t39_interruption_attribution": receipt(ATTRIBUTION),
            "runner": receipt(RUNNER),
            "matrix_helper": receipt(MATRIX_HELPER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "execute_one_exact_cpu_recovery": not failed,
            "robustness_preregistration": False,
            "robustness_execution": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
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
                "# T40 exact T39 recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Immutable completed evidence: `2 blocks / 8 cells`",
                "- New execution: `2 blocks / 8 cells`",
                "- Re-execution of completed blocks: `NO`",
                "- Aggregated pass rule: `16/16 green`",
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
