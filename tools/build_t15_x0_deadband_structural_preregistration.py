#!/usr/bin/env python3
"""Freeze T15's read-only x=0 deadband structural audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t15_x0_deadband_structural_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T15_X0_DEADBAND_STRUCTURAL_PREREGISTRATION_20260726.md"
)
RUNNER = ROOT / "tools" / "audit_t15_x0_deadband_structural.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T15 preregistration")

    inputs = {
        "t6_result": ANALYSIS / "t6_corrected_robustness_screen_result.json",
        "t7_result": ANALYSIS / "t7_universal_response_support_result.json",
        "t9_result": ANALYSIS / "t9_command_aware_prefix_bypass_result.json",
        "t9_runner": ROOT / "tools" / "run_t9_command_aware_prefix_bypass.py",
        "t10_network": (
            ROOT / "patches" / "t10_response_conditioned_v121_networks.py"
        ),
        "runner": RUNNER,
    }
    missing = [
        path.relative_to(ROOT).as_posix()
        for path in inputs.values()
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"missing T15 inputs: {missing}")

    t6 = json.loads(inputs["t6_result"].read_text(encoding="utf-8"))
    t7 = json.loads(inputs["t7_result"].read_text(encoding="utf-8"))
    t9 = json.loads(inputs["t9_result"].read_text(encoding="utf-8"))
    checks = {
        "t6_has_no_frozen_robust_survivor": (
            t6["status"] == "PASS_T6_NO_FROZEN_ROBUST_SURVIVOR"
            and t6["selected_survivor"] is None
        ),
        "t7_universal_support_is_green": (
            t7["status"] == "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
            and t7["passing_cells"] == t7["expected_cells"] == 12
        ),
        "t9_unconditional_x0_bypass_is_green_nominally": (
            t9["status"] == "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
            and t9["new_passing_cells"] == t9["new_expected_cells"] == 4
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)

    basis = {
        "schema_version": (
            "open_duck.t15_x0_deadband_structural_preregistration.v1"
        ),
        "status": "PREREGISTERED_T15_X0_DEADBAND_STRUCTURAL_AUDIT",
        "checks": checks,
        "failed_checks": failed,
        "question": (
            "Does the unconditional x=0 exact-zero deadband make the "
            "TORSO_COM_X_NEG x=0 gate policy-independent and therefore "
            "structurally impossible, even though the already-frozen "
            "universal support action holds the same plant condition?"
        ),
        "causal_basis": {
            "t6_observation": (
                "T6 reports sixteen x=0 cells spanning four policy pairs, "
                "two checkpoints, and two actuator fits under the same "
                "negative-COM condition."
            ),
            "t9_mechanism": (
                "T9 deliberately bypasses the response prefix at x=0 and "
                "requires the authoritative action chain to remain exact zero."
            ),
            "t7_counterexample": (
                "T7 applies the exact universal support action for 600 ticks "
                "under nominal and both signed COM endpoints."
            ),
            "scope": (
                "This is an audit of an action-branch invariant, not a new "
                "policy, threshold, simulator run, or relaxation of the "
                "moving-command robustness gate."
            ),
        },
        "population": {
            "t6_x0_cells": 16,
            "policy_families": ["V121", "V123", "V128", "V177"],
            "checkpoints_per_family": 2,
            "actuator_fits": ["p30", "p31_34"],
            "condition": "TORSO_COM_X_NEG",
            "command_x_m_s": 0.0,
            "t7_counterexample_cells": {
                "condition": "TORSO_COM_X_NEG",
                "fits": ["p30", "p31_34"],
                "repeats_per_fit": 2,
                "duration_ticks": 600,
            },
        },
        "pass_rule": {
            "all_16_t6_x0_cells_present": True,
            "all_16_actions_exact_zero_on_every_recorded_tick": True,
            "all_16_cells_fail_with_identical_behavior_metrics": True,
            "each_checkpoint_pair_is_fit_invariant": True,
            "all_four_t7_negative_com_support_cells_pass": True,
            "t7_support_mean_abs_vx_at_most_m_s": 0.001,
            "t7_support_rate_excess_exact_zero": True,
            "t7_support_duration_protection_green": True,
            "all_bound_trace_hashes_match_committed_receipts": True,
        },
        "decision_rule": {
            "pass": (
                "Classify the unconditional x=0 exact-zero deadband as a "
                "structural blocker for variable-configuration clearance. "
                "Reopen only the x=0 branch for a separately preregistered "
                "configuration-aware support-retention CPU contract. This "
                "does not reopen moving-command wrappers and earns no "
                "training or hosted run."
            ),
            "fail": (
                "Keep the x=0 deadband frozen and close configuration-aware "
                "support retention; do not alter the population, action "
                "definition, thresholds, or source artifacts."
            ),
            "partial_results_selection_weight": 0,
            "no_threshold_changes_after_execution": True,
        },
        "input_hashes": {
            name: sha256(path)
            for name, path in sorted(inputs.items())
        },
        "authority": {
            "read_only": True,
            "cpu_only": True,
            "optimizer_steps": 0,
            "new_behavior_cells": 0,
            "hosted_or_colab_compute": False,
            "checkpoint_selection": False,
            "deployment_or_gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "new_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T15 x=0 deadband structural audit preregistration",
                "",
                (
                    "T15 tests whether the unconditional exact-zero x=0 "
                    "branch makes the negative-COM zero-command gate "
                    "policy-independent while an already-reviewed support "
                    "action supplies a physical counterexample."
                ),
                "",
                "- Evidence: committed T6, T7, and T9 results plus bound D: traces",
                "- New simulator cells / optimizer steps: `0 / 0`",
                "- Hosted compute / robot access: `0 / 0`",
                (
                    "- Pass earns only a separately preregistered CPU "
                    "contract for the x=0 branch."
                ),
                (
                    f"- Canonical SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT.relative_to(ROOT))
    print(MARKDOWN.relative_to(ROOT))
    print(value["preregistered_contract_sha256"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
