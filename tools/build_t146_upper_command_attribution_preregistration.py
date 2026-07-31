#!/usr/bin/env python3
"""Freeze read-only attribution of T145C's upper-command failures."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T145C = ANALYSIS / "t145c_cache_contract_recovery_result.json"
T129_PREREG = ANALYSIS / "t129_negative_only_expert_hosted_preregistration.json"
RUN_STATE = Path(
    "D:/CodexArtifacts/open-duck-policy/t129_colab_extracted_20260729/"
    "t129_negative_only_expert_continuation/run_state.json"
)
TRAINING_LOG = RUN_STATE.parent / "training.log"
OUTPUT = ANALYSIS / "t146_upper_command_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T146_UPPER_COMMAND_ATTRIBUTION_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t146_upper_command_attribution.py"
TEST = ROOT / "tests" / "test_t146_upper_command_attribution.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T146: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T146 preregistration requires clean worktree")
    t145c = json.loads(T145C.read_text(encoding="utf-8"))
    t129 = json.loads(T129_PREREG.read_text(encoding="utf-8"))
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t145c_result": T145C,
        "t129_preregistration": T129_PREREG,
        "t129_run_state": RUN_STATE,
        "t129_training_log": TRAINING_LOG,
    }
    trace_receipts = {
        (
            f"trace_{block['checkpoint_id']}_{block['fit_id']}_"
            f"{cell['command_x_m_s']:.3f}"
        ): {
            "path": cell["protection"]["path"],
            "bytes": Path(cell["protection"]["path"]).stat().st_size,
            "sha256": cell["protection"]["sha256"],
        }
        for block in t145c["blocks"]
        for cell in block["result"]["cells"]
    }
    checks = {
        "t145c_is_closed_eight_of_sixteen": (
            t145c["status"]
            == "HOLD_T145C_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
            and t145c["condition"]["green_cells"] == 8
            and t145c["decision"] == "CLOSE_T129_TRAIN_MATCHED_CONDITIONAL_PATH"
        ),
        "t129_was_exact_negative_always_on": (
            t129["training"]["forward_path"]
            == "negative_adapter_location_always_on"
            and t129["training"]["exact_torso_com_offset_m"]
            == [-0.05, 0.0, 0.0]
            and t129["training"]["command_support_change"] is False
            and t129["training"]["body_configuration_strata"] == 1
        ),
        "all_sixteen_traces_present": (
            len(trace_receipts) == 16
            and all(Path(item["path"]).is_file() for item in trace_receipts.values())
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_new_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T146 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t146_upper_command_attribution_preregistration.v1"
        ),
        "status": "PREREGISTERED_T146_UPPER_COMMAND_ATTRIBUTION",
        "question": (
            "Do the x=.077/.08 failures originate in the common calibration "
            "handoff, or only after sustained command-conditioned walking?"
        ),
        "hypotheses": {
            "handoff": (
                "Failing commands begin from a different physical, applied-target, "
                "previous-action, hidden, or calibration-context state, or fail "
                "before ten bilateral contact transitions."
            ),
            "sustained_command": (
                "All commands begin from an identical handoff state; x=0/.074 "
                "complete; and every .077/.08 failure occurs only after at least "
                "ten total contact transitions and 90 ticks."
            ),
        },
        "thresholds": {
            "minimum_failure_tick_for_sustained_classification": 90,
            "minimum_total_contact_transitions": 10,
            "first_state_absolute_tolerance": 0.0,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "traces": trace_receipts,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "sustained_command_decision": (
                "EARN_T147_COMMAND_GROUP_RISK_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "handoff_decision": (
                "EARN_HANDOFF_COUNTERFACTUAL_PREREGISTRATION_ONLY"
            ),
            "inconclusive_decision": "HOLD_FOR_NEW_CAUSAL_MECHANISM",
        },
        "execution_now": {
            "trace_rows_read": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_trace_attribution": True,
            "cpu_contract_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T146 upper-command attribution preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: all 16 frozen T145C traces and the T129 training receipts\n"
        "- Competing causes: calibration handoff vs sustained command collapse\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
