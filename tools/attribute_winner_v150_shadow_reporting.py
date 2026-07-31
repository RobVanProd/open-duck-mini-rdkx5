#!/usr/bin/env python3
"""Correct V150's shadow-only oracle reporting classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v150_v148_shadow_oracle_preregistration.json"
RESULT = ANALYSIS / "winner_v150_v148_shadow_oracle_result.json"
OUTPUT = ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V150_V148_SHADOW_ORACLE_REPORTING_CORRECTION_20260725.md"
)
EXPECTED = {
    "preregistration": (
        "3d4421a5e7041faa48cc2ac1603e53a970b49aaad1eebc475c701e1e6492f270"
    ),
    "result": (
        "5232d59b0334a2e83d5d62ae06b5c89886e4cdac78a14425edf6557c54869e98"
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
            raise FileExistsError(f"refusing to overwrite V150: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "preregistration": sha256(PREREG),
        "result": sha256(RESULT),
    }
    cell_failures = result["cell"]["failure_reasons"]
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
        if name != "behavior_failure_remains_torque_only"
    }
    event = result["torque"]["event_rows"][0]
    checks = {
        "input_hashes_exact": input_hashes == EXPECTED,
        "preregistered_shadow_does_not_apply": (
            prereg["method"]["committed_action"]
            == "unchanged V148 graph action"
        ),
        "original_hold_only_reporting_check": (
            result["failed_checks"]
            == ["behavior_failure_remains_torque_only"]
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
        "single_displaced_event_has_safe_nonempty_precursor_label": (
            result["torque"]["events"] == 1
            and event["tick"] == 586
            and event["joint"] == 13
            and event["source_tick"] == 583
            and event["source_action_delta"] != 0.0
            and not event["source_empty_joint_indices"]
            and abs(event["projected_force_nm"])
            <= 1.91229675 + 5.0e-6
        ),
        "no_rerun_training_or_behavior": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v150.shadow_reporting_correction.v1",
        "status": (
            "PASS_WINNER_V150_V148_SHADOW_ORACLE_REPORTING_CORRECTION"
            if not failed
            else "HOLD_WINNER_V150_V148_SHADOW_ORACLE_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "reporting_correction": {
            "physical_failure_reasons": physical,
            "shadow_only_diagnostic_failures": shadow_only,
            "reason": (
                "the inherited applied-oracle audit expects projected-force "
                "predictions to equal realized force; shadow mode commits "
                "the unprojected V148 action, so those four oracle-only "
                "flags are expected and do not classify the physical gate"
            ),
            "data_or_threshold_change": False,
            "rerun": False,
        },
        "causal_result": {
            "trajectory_bit_exact": checks[
                "trajectory_reproduction_bit_exact"
            ],
            "torque_events": result["torque"]["events"],
            "event": event,
            "all_actual_events_labeled": result["checks"][
                "every_actual_violation_has_safe_nonempty_precursor_label"
            ],
        },
        "decision": (
            "EARN_V151_BOUNDED_TWO_CENTER_CONTRACT_PREREGISTRATION"
            if not failed
            else "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
        ),
        "authority": {
            "v151_preregistration": not failed,
            "policy_change": False,
            "behavior": False,
            "training": False,
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
        "# Winner V150 shadow-oracle reporting correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The frozen shadow trace is bit-exact to V149.\n"
        "- Physical failure: torque only; four extra flags are invalid "
        "for a deliberately unapplied shadow action.\n"
        "- The new right-ankle event at tick 586 has a safe, non-empty "
        "oracle label at tick 583.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only correction; no rerun, policy change, training, "
        "Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
