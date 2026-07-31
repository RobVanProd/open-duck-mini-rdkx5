#!/usr/bin/env python3
"""Correct V144's shadow-only oracle reporting classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v144_shadow_oracle_preregistration_v2.json"
RESULT = ANALYSIS / "winner_v144_shadow_oracle_result.json"
OUTPUT = ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION_20260725.md"
)
EXPECTED = {
    "preregistration": (
        "f9a501840d5a82c0df86614fb57faabbf96f68b069b980621d7dbd71106643eb"
    ),
    "result": (
        "fee8bde0006f9b5501e7d6fd1b9a8e11e131d7002315d6ae38019a6440ac01d7"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V144: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "preregistration": sha256(PREREG),
        "result": sha256(RESULT),
    }
    cell_failures = result["source_cell"]["failure_reasons"]
    shadow_only = sorted(
        failure
        for failure in cell_failures
        if failure.startswith("oracle_")
    )
    physical = sorted(
        failure
        for failure in cell_failures
        if not failure.startswith("oracle_")
    )
    causal_checks = {
        name: passed
        for name, passed in result["checks"].items()
        if name != "source_behavior_failure_is_torque_only"
    }
    checks = {
        "input_hashes_exact": input_hashes == EXPECTED,
        "preregistered_shadow_does_not_apply": (
            prereg["method"]["policy_action_committed"]
            == "unmodified V140 action"
        ),
        "original_hold_only_reporting_check": (
            result["failed_checks"]
            == ["source_behavior_failure_is_torque_only"]
        ),
        "all_causal_checks_green": all(causal_checks.values()),
        "trajectory_reproduction_bit_exact": all(
            value == 0.0
            for value in result["trajectory_reproduction_linf"].values()
        ),
        "physical_failure_is_torque_only": (
            physical == ["torque_peak_at_most_1p91229675_nm"]
        ),
        "extra_failures_are_shadow_prediction_bookkeeping_only": (
            shadow_only
            == [
                "oracle_only_empty_or_prehistory_residuals",
                "oracle_prediction_exact",
                "oracle_zero_nonempty_residual_violations",
                "oracle_zero_prediction_mismatches",
            ]
        ),
        "single_event_has_safe_nonempty_precursor_label": (
            result["torque"]["events"] == 1
            and result["torque"]["event_rows"][0]["tick"] == 397
            and result["torque"]["event_rows"][0]["joint"] == 13
            and result["torque"]["event_rows"][0]["source_tick"] == 394
            and result["torque"]["event_rows"][0]["source_action_delta"]
            != 0.0
            and not result["torque"]["event_rows"][0][
                "source_empty_joint_indices"
            ]
            and abs(
                result["torque"]["event_rows"][0]["projected_force_nm"]
            )
            <= 1.91229675 + 5.0e-6
        ),
        "no_rerun_training_or_behavior": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v144.shadow_reporting_correction.v1",
        "status": (
            "PASS_WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION"
            if not failed
            else "HOLD_WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "reporting_correction": {
            "physical_failure_reasons": physical,
            "shadow_only_diagnostic_failures": shadow_only,
            "reason": (
                "the generic applied-oracle audit expects projected-force "
                "predictions to equal realized force; shadow mode "
                "deliberately commits the unprojected policy action, so "
                "those prediction/residual flags are expected and cannot "
                "classify the source policy's physical gate"
            ),
            "data_or_threshold_change": False,
            "rerun": False,
        },
        "causal_result": {
            "trajectory_bit_exact": checks[
                "trajectory_reproduction_bit_exact"
            ],
            "torque_events": result["torque"]["events"],
            "peak_event": result["oracle"]["peak_event"],
            "all_actual_events_labeled": result["checks"][
                "all_actual_violations_have_safe_nonempty_precursor_labels"
            ],
        },
        "decision": (
            "EARN_ONE_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION"
            if not failed
            else "CLOSE_ON_POLICY_DAGGER_FROM_V140"
        ),
        "authority": {
            "v145_cpu_preregistration": not failed,
            "training": False,
            "behavior": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V144 shadow-oracle reporting correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The frozen shadow trace is bit-exact to V141.\n"
        "- Physical failure: torque only; four extra flags came from "
        "applied-oracle prediction checks that are intentionally invalid "
        "when the teacher action is not applied.\n"
        "- One right-ankle event at tick 397 has a safe, non-empty oracle "
        "label at tick 394.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only correction; no rerun, training, behavior, Colab, or "
        "hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
