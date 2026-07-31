#!/usr/bin/env python3
"""Freeze T49's one missing combined adapter control."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
INTERRUPTION = (
    ANALYSIS / "t49_t48_execution_interruption_attribution.json"
)
T48_PREREG = (
    ANALYSIS
    / "t48_final_adapter_core_head_factorial_preregistration.json"
)
RUNNER = ROOT / "tools" / "run_t49_missing_combined_adapter_control.py"
T48_HELPER = ROOT / "tools" / "run_t48_final_adapter_core_head_factorial.py"
OUTPUT = (
    ANALYSIS
    / "t49_missing_combined_adapter_control_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T49_MISSING_COMBINED_ADAPTER_CONTROL_PREREGISTRATION_20260728.md"
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
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T49 prereg: {path}")
    interruption = json.loads(INTERRUPTION.read_text(encoding="utf-8"))
    t48 = json.loads(T48_PREREG.read_text(encoding="utf-8"))
    variant = next(
        item
        for item in t48["variants"]
        if item["variant_id"] == "FINAL_WITH_HALF_CORE_HEAD"
    )
    completed = interruption["completed_cells"]
    checks = {
        "interruption_green_and_earned_missing_cell": (
            interruption["status"]
            == "PASS_T49_T48_TWO_CELL_EXECUTION_INTERRUPTION_ATTRIBUTION"
            and interruption["decision"]
            == "CLOSE_T48_ZERO_DECISION_WEIGHT_NO_RETRY_"
            "EARN_T49_MISSING_COMBINED_CONTROL_PREREGISTRATION"
        ),
        "exact_two_completed_cells_preserved": (
            [item["variant_id"] for item in completed]
            == ["FINAL_WITH_HALF_CORE", "FINAL_WITH_HALF_HEAD"]
            and all(item["cell_green"] for item in completed)
        ),
        "only_missing_combined_variant_selected": (
            variant["variant_id"] == "FINAL_WITH_HALF_CORE_HEAD"
            and variant["semantically_equals_half_endpoint"]
        ),
        "all_completed_artifacts_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for cell in completed
            for item in cell["execution"].values()
        ),
        "variant_policy_exact": (
            sha256(Path(variant["policy"]["path"]))
            == variant["policy"]["sha256"]
        ),
        "runner_and_helper_present": (
            RUNNER.is_file() and T48_HELPER.is_file()
        ),
        "new_behavior_cells_zero": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t49_missing_combined_adapter_control_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T49_MISSING_COMBINED_ADAPTER_CONTROL"
            if not failed
            else "HOLD_T49_MISSING_COMBINED_ADAPTER_CONTROL_PREREGISTRATION"
        ),
        "question": (
            "Complete T48 without retrying its two finished cells by "
            "running only the missing combined core+head control, then "
            "apply the original frozen precedence to the aggregate."
        ),
        "completed_cells": completed,
        "variant": variant,
        "variants": [variant],
        "execution_order": t48["execution_order"],
        "cell": t48["cell"],
        "fit": t48["fit"],
        "calibrator": t48["calibrator"],
        "reference_feature_table": t48["reference_feature_table"],
        "playground": t48["playground"],
        "support_handoff": t48["support_handoff"],
        "behavior_contract": t48["behavior_contract"],
        "protection_contract": t48["protection_contract"],
        "decision_rule": t48["decision_rule"],
        "checks": checks,
        "failed_checks": failed,
        "frozen_inputs": {
            "interruption_attribution": receipt(INTERRUPTION),
            "t48_preregistration": receipt(T48_PREREG),
            "runner": receipt(RUNNER),
            "t48_helper": receipt(T48_HELPER),
            "worker": t48["frozen_inputs"]["worker"],
        },
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_missing_cpu_cell": not failed,
            "retry_completed_cells": False,
            "uniform_transform_preregistration": False,
            "policy_promotion": False,
            "training": False,
            "colab": False,
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
                "# T49 missing combined adapter control",
                "",
                f"- Status: `{value['status']}`",
                "- Prior valid cells: core and head (`2`), no retry",
                "- New cell: combined core+head control (`1`)",
                "- Aggregate decision only after all three are valid",
                "- Training/Colab/Gate 5/robot: `0/0/0/0`",
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
