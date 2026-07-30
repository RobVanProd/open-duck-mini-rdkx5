#!/usr/bin/env python3
"""Freeze the cross-family predicted-tilt-box source-transfer audit."""

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


T201B_PREREG = (
    ANALYSIS / "t201b_roll_risk_source_transfer_preregistration.json"
)
T201B_RESULT = ANALYSIS / "t201b_roll_risk_source_transfer_result.json"
T213B_PREREG = (
    ANALYSIS / "t213b_support_continuity_autopsy_preregistration.json"
)
T213B_RESULT = ANALYSIS / "t213b_support_continuity_autopsy_result.json"
T59 = ANALYSIS / "t59_t56_nominal_matrix_result.json"
T190B = ANALYSIS / "t190b_interrupted_execution_recovery_result.json"
T198 = ANALYSIS / "t198_t194_targeted_y_negative_result.json"
T199 = ANALYSIS / "t199_t194_support_credit_autopsy_result.json"
OUTPUT = (
    ANALYSIS
    / "t214b_axis_complete_tilt_source_transfer_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER_"
    "PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t214b_axis_complete_tilt_source_transfer.py"
TEST = ROOT / "tests/test_t214b_axis_complete_tilt_source_transfer.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T214B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T214B preregistration requires clean worktree")

    t201b_prereg = load(T201B_PREREG)
    t201b_result = load(T201B_RESULT)
    t213b_prereg = load(T213B_PREREG)
    t213b_result = load(T213B_RESULT)
    t59 = load(T59)
    t190b = load(T190B)
    t198 = load(T198)
    t199 = load(T199)
    traces = [
        *t201b_prereg["traces"],
        *[{"family": "t210", **row} for row in t213b_prereg["traces"]],
    ]
    failures = [row for row in traces if not row["cell_green"]]
    failure_keys = {
        (
            row["family"],
            row["checkpoint_id"],
            row["fit_id"],
            float(row["command_x_m_s"]),
            int(row["samples"]),
        )
        for row in failures
    }
    checks = {
        "roll_source_transfer_was_green": (
            t201b_result["status"]
            == "PASS_T201B_ROLL_RISK_SOURCE_TRANSFER"
            and t201b_result["separation_rule_passed"]
        ),
        "t210_failure_is_support_then_pitch_roll_collapse": (
            t213b_result["status"]
            == "PASS_T213B_SUPPORT_CONTINUITY_AUTOPSY"
            and t213b_result["classification"]
            == "SUPPORT_CONTINUITY_BREAK_PRECEDES_HEIGHT_AND_ROLL_COLLAPSE"
        ),
        "prior_single_support_curricula_are_closed": (
            t59["decision"] == "CLOSE_T56_DYNAMIC_SINGLE_SUPPORT_CURRICULUM"
            and t59["condition"]["green_cells"] == 10
            and t190b["decision"] == "CLOSE_T186_SINGLE_SUPPORT_CONTINUATION"
            and t198["decision"]
            == "CLOSE_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_CONTINUATION"
            and t199["decision"]
            == "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_OBJECTIVE_CONTINUATION"
        ),
        "thirty_six_traces_thirty_three_passes_three_failures": (
            len(traces) == 36
            and sum(bool(row["cell_green"]) for row in traces) == 33
            and len(failures) == 3
        ),
        "failure_population_exact": failure_keys
        == {
            ("t170", "T170_COMPOSED_FINAL", "p30", 0.08, 281),
            ("t194", "T194_COMPOSED_HALF", "p31_34", 0.077, 308),
            ("t210", "T210_COMPOSED_FINAL", "p30", 0.08, 318),
        },
        "all_trace_files_present": all(
            Path(row["trace"]["path"]).is_file() for row in traces
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T214B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t214b_axis_complete_tilt_source_transfer_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
        ),
        "question": (
            "Does one componentwise predicted roll/pitch safety box, with "
            "axis thresholds derived from every row of all 33 historical "
            "passes, detect all three known T170/T194/T210 falls early "
            "without reopening the closed single-support curricula?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": Path(__file__).resolve(),
                "runner": RUNNER,
                "test": TEST,
                "t201b_preregistration": T201B_PREREG,
                "t201b_result": T201B_RESULT,
                "t213b_preregistration": T213B_PREREG,
                "t213b_result": T213B_RESULT,
                "t59_result": T59,
                "t190b_result": T190B,
                "t198_result": T198,
                "t199_result": T199,
            }.items()
        },
        "traces": traces,
        "analysis": {
            "prediction_horizon_s": 0.08,
            "roll_risk": (
                "abs(body_roll_rad + 0.08 * body_roll_rate_rad_s)"
            ),
            "pitch_risk": (
                "abs(body_pitch_rad + 0.08 * body_pitch_rate_rad_s)"
            ),
            "roll_envelope": (
                "nextafter(maximum roll risk over every row of all "
                "33 passing traces, +infinity)"
            ),
            "pitch_envelope": (
                "nextafter(maximum pitch risk over every row of all "
                "33 passing traces, +infinity)"
            ),
            "box_score": (
                "max(roll_risk / roll_envelope, "
                "pitch_risk / pitch_envelope)"
            ),
            "candidate_cost": "square(max(0, box_score - 1))",
            "per_failure_rule": {
                "minimum_exceedance_rows": 4,
                "minimum_lead_ticks": 4,
                "maximum_strictly_above_box": True,
            },
            "required_dominant_axes_across_failures": ["pitch", "roll"],
            "all_passing_exceedance_rows": 0,
            "selection_weight": 0,
            "threshold_or_horizon_search": False,
        },
        "prior_art_ruling": {
            "t56_dynamic_single_support": "closed_at_10_of_16",
            "t186_same_episode_support_prefix": "closed_at_15_of_16",
            "t194_dynamic_reference_contact": "closed_at_15_of_16",
            "repeat_single_support_curriculum": False,
            "mechanical_distinction": (
                "axis-complete predictive tilt invariant prevents the "
                "observed roll-to-pitch failure-mode substitution"
            ),
        },
        "decision_rule": {
            "all_failures_separable_and_both_axes_required": (
                "EARN_T215B_AXIS_COMPLETE_TILT_DUAL_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_TILT_BOX"
            ),
            "no_optimizer_or_behavior": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_trace_rows": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_source_transfer_audit": True,
            "cpu_contract_preregistration": False,
            "training": False,
            "colab": False,
            "behavior": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T214B axis-complete predicted-tilt source transfer\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: 36 frozen traces (33 pass, 3 fall)\n"
        "- Mechanism: componentwise 80-ms predicted roll/pitch box\n"
        "- Prior art: T56/T186/T194 support curricula remain closed\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: "
        "`0/0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
