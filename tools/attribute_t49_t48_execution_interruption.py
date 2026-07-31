#!/usr/bin/env python3
"""Record T48's two-cell execution interruption with zero decision weight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t48_final_adapter_core_head_factorial_preregistration.json"
)
T48_RESULT = ANALYSIS / "t48_final_adapter_core_head_factorial_result.json"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t48_final_adapter_core_head_factorial_run_v1"
)
OUTPUT = ANALYSIS / "t49_t48_execution_interruption_attribution.json"
MARKDOWN = (
    ANALYSIS / "T49_T48_EXECUTION_INTERRUPTION_ATTRIBUTION_20260728.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t6_corrected_robustness_screen import (  # noqa: E402
    behavior_row,
    classify_behavior,
    exact_override_readback,
    trace_summary,
)
from run_t8_state_coherent_handoff import (  # noqa: E402
    read_trace,
    state_handoff_summary,
)


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
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def existing_cell(
    prereg: dict[str, Any],
    variant: dict[str, Any],
) -> dict[str, Any]:
    root = CACHE_ROOT / variant["variant_id"]
    evaluation_path = root / "evaluation.json"
    stdout_path = root / "stdout.log"
    trace_path = (
        root
        / "traces"
        / (
            f"x0.077_seed{prereg['cell']['seed']}_"
            f"{Path(variant['policy']['path']).stem}.jsonl"
        )
    )
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("formal") is not True or len(evaluation["runs"]) != 1:
        raise ValueError("T49 found invalid T48 formal output")
    run = evaluation["runs"][0]
    records = read_trace(trace_path)
    behavior = classify_behavior(
        behavior_row(run), prereg["behavior_contract"]
    )
    protection = trace_summary(
        trace_path, prereg["protection_contract"]
    )
    handoff = state_handoff_summary(run, records)
    readback = exact_override_readback(
        run.get("dynamics_override"),
        prereg["cell"]["condition"]["override"],
    )
    trace_valid = (
        protection["ticks_contiguous_from_zero"]
        and protection["rows"] == behavior["samples"]
    )
    cell_green = (
        trace_valid
        and behavior["core_pass"]
        and behavior["replacement_quality_pass"]
        and protection["duration_protection_pass"]
        and protection["maximum_full_measured_vector_excess_rad_s"] == 0.0
        and handoff["all_checks_pass"]
        and readback
    )
    return {
        "variant_id": variant["variant_id"],
        "half_groups": variant["half_groups"],
        "half_group_count": variant["half_group_count"],
        "semantically_equals_half_endpoint": variant[
            "semantically_equals_half_endpoint"
        ],
        "policy": variant["policy"],
        "behavior": behavior,
        "protection": protection,
        "handoff": handoff,
        "override_readback_exact": readback,
        "trace_valid": trace_valid,
        "cell_green": cell_green,
        "execution": {
            "evaluation": receipt(evaluation_path),
            "stdout": receipt(stdout_path),
            "trace": receipt(trace_path),
        },
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T49 output: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    completed_variants = prereg["variants"][:2]
    missing_variant = prereg["variants"][2]
    cells = [
        existing_cell(prereg, variant)
        for variant in completed_variants
    ]
    missing_root = CACHE_ROOT / missing_variant["variant_id"]
    checks = {
        "t48_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL"
        ),
        "exact_first_two_variants_completed": (
            [item["variant_id"] for item in cells]
            == ["FINAL_WITH_HALF_CORE", "FINAL_WITH_HALF_HEAD"]
        ),
        "both_completed_cells_valid": all(
            item["trace_valid"]
            and item["handoff"]["all_checks_pass"]
            and item["override_readback_exact"]
            for item in cells
        ),
        "both_completed_cells_green_diagnostic_only": all(
            item["cell_green"] for item in cells
        ),
        "combined_control_not_started": not missing_root.exists(),
        "t48_result_absent": not T48_RESULT.exists(),
        "formal_behavior_cells_exactly_two": len(cells) == 2,
        "no_retry_or_new_behavior_in_attribution": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t49_t48_execution_interruption_attribution.v1"
        ),
        "status": (
            "PASS_T49_T48_TWO_CELL_EXECUTION_INTERRUPTION_ATTRIBUTION"
            if not failed
            else "HOLD_T49_T48_EXECUTION_INTERRUPTION_ATTRIBUTION"
        ),
        "decision": (
            "CLOSE_T48_ZERO_DECISION_WEIGHT_NO_RETRY_"
            "EARN_T49_MISSING_COMBINED_CONTROL_PREREGISTRATION"
            if not failed
            else "STOP_T49_AND_REVIEW_INTERRUPTION"
        ),
        "classification": {
            "t48_contract_complete": False,
            "t48_policy_decision_weight": 0,
            "formal_behavior_cells_completed": 2,
            "formal_behavior_cells_required": 3,
            "missing_variant_id": missing_variant["variant_id"],
            "termination_cause": (
                "runner_terminated_after_second_completed_cell; exact "
                "process-level cause is not preserved in a durable log"
            ),
            "completed_cells_must_not_be_rerun": True,
        },
        "completed_cells": cells,
        "missing_variant": missing_variant,
        "checks": checks,
        "failed_checks": failed,
        "frozen_inputs": {
            "t48_preregistration": receipt(PREREG),
            "t48_runner": prereg["frozen_inputs"]["runner"],
            "t48_worker": prereg["frozen_inputs"]["worker"],
        },
        "execution": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "missing_combined_control_preregistration": not failed,
            "completed_cell_retry": False,
            "factorial_decision": False,
            "uniform_transform_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T49 T48 execution-interruption attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                "- T48 completed cells: `2/3`",
                "- Core/head cells: valid and green, diagnostic only",
                "- Missing cell: combined core+head control",
                "- T48 decision weight: `0`",
                "- Retry completed cells: `NO`",
                "- New behavior/training/Colab/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"failed_checks={failed}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
