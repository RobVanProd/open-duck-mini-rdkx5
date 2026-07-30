#!/usr/bin/env python3
"""Freeze one T186 half-to-final head-switch behavior cell."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
ADAPTER = ROOT / "tools" / "t192_head_switch_eval_adapter.py"
WORKER = ROOT / "tools" / "evaluate_t192_head_switch_single_cell.py"
RUNNER = ROOT / "tools" / "run_t192_one_period_head_switch.py"
TEST = ROOT / "tests" / "test_t192_one_period_head_switch.py"
T191 = ANALYSIS / "t191_t186_failure_exchange_autopsy_result.json"
T191_PREREG = (
    ANALYSIS / "t191_t186_failure_exchange_autopsy_preregistration.json"
)
T188 = ANALYSIS / "t188_t186_postexport_composition_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t192_one_period_head_switch_preregistration.json"
MARKDOWN = ANALYSIS / "T192_ONE_PERIOD_HEAD_SWITCH_PREREGISTRATION_20260730.md"

sys.path.insert(0, str(ROOT / "tools"))
import t192_head_switch_eval_adapter as adapter  # noqa: E402
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T192: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T192 preregistration requires clean worktree")

    t191 = json.loads(T191.read_text(encoding="utf-8"))
    t191_prereg = json.loads(T191_PREREG.read_text(encoding="utf-8"))
    t188 = json.loads(T188.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t188["graphs"]
    }
    primary = {
        "checkpoint_id": "T186_COMPOSED_HALF",
        "step": 1_003_520,
        **graph_by_step[1_003_520],
    }
    switch = {
        "checkpoint_id": "T186_COMPOSED_FINAL",
        "step": 2_007_040,
        **graph_by_step[2_007_040],
    }
    condition = next(
        row for row in basis["conditions"] if row["id"] == "TORSO_COM_Y_NEG"
    )
    fit = next(row for row in basis["fits"] if row["fit_id"] == "p31_34")
    original_failure = next(
        row
        for row in t191_prereg["traces"]
        if row["checkpoint_id"] == "T186_COMPOSED_HALF"
        and row["fit_id"] == "p31_34"
        and float(row["command_x_m_s"]) == 0.080
    )
    adapter_contract = adapter.contract()
    checks = {
        "t191_exact_and_earned": (
            t191["status"] == "PASS_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
            and not t191["failed_checks"]
            and t191["decision"]
            == (
                "EARN_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "switch_tick_exactly_derived": (
            t191["new_t186_failure"]["derived_one_period_switch_tick"] == 520
            and t191["new_t186_failure"]["support_proximal"]
            and t191["new_t186_failure"]["state_compatible_head_change"]
        ),
        "primary_and_switch_graphs_present": (
            Path(primary["path"]).is_file()
            and Path(switch["path"]).is_file()
            and primary["sha256"] != switch["sha256"]
        ),
        "condition_is_exact_y_negative": (
            condition["condition_index"] == 9
            and condition["override"]
            == {"torso_com_offset_m": [0.0, -0.05, 0.0]}
        ),
        "fit_is_exact_p31_34": fit["fit_id"] == "p31_34",
        "original_failure_exact": (
            original_failure["cell_green"] is False
            and original_failure["samples"] == 547
        ),
        "adapter_has_five_default_off_patches": (
            adapter_contract["patch_count"] == 5
            and "default to None" in adapter_contract["default_off"]
        ),
        "one_fresh_cpu_cell_only": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T192 preregistration checks failed: {failed}")

    repository_inputs = dict(basis["repository_inputs"])
    repository_inputs["worker"] = receipt(WORKER)
    repository_inputs["head_switch_adapter"] = receipt(ADAPTER)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t192_one_period_head_switch_preregistration.v1"
        ),
        "status": "PREREGISTERED_T192_ONE_PERIOD_HEAD_SWITCH",
        "question": (
            "If T186-half controls the exact failing cell through tick 519, "
            "can the ABI-compatible T186-final head recover it when switched "
            "for the final 27-tick gait period?"
        ),
        "policy": primary,
        "switch_policy": switch,
        "switch_tick": 520,
        "condition": condition,
        "fit": fit,
        "commands_x_m_s": [0.080],
        "seed": basis["seed"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "repository_inputs": repository_inputs,
        "original_failure_trace": original_failure["trace"],
        "adapter_contract": adapter_contract,
        "execution_contract": {
            "duration_ticks": 600,
            "primary_ticks": [0, 519],
            "switch_ticks": [520, 599],
            "pre_switch_common_fields_bit_exact_to_original_failure": True,
            "recurrent_state_preserved_at_switch": True,
            "fresh_cache": True,
            "behavior_cells": 1,
            "no_retry": True,
        },
        "decision_rule": {
            "pass": (
                "EARN_T193_CHECKPOINT_CONSISTENCY_TEACHER_"
                "CONTRACT_PREREGISTRATION_ONLY"
            ),
            "behavior_fail": (
                "CLOSE_LATE_HEAD_SWITCH_AND_SELECT_GAIT_STATE_"
                "DISTRIBUTION_CURRICULUM"
            ),
            "integrity_fail": "HOLD_MECHANISM_SELECTION_AND_AUDIT_T192",
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "adapter": ADAPTER,
                "worker": WORKER,
                "runner": RUNNER,
                "test": TEST,
                "t191_result": T191,
                "t191_preregistration": T191_PREREG,
                "t188_composition": T188,
                "t165_basis": BASIS,
                "original_failure_trace": Path(
                    original_failure["trace"]["path"]
                ),
            }.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "checkpoint_consistency_teacher_preregistration": True,
            "behavior": False,
            "training": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "one_cpu_behavior_cell": True,
            "training": False,
            "colab": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T192 one-period head-switch preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Cell: Y-negative / T186-half / P31-34 / x=.080\n"
        "- Switch: T186-final graph at scored tick `520`\n"
        "- Prefix: ticks `0-519` must match the sealed failure exactly\n"
        "- One fresh CPU cell; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
