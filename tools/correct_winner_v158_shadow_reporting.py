#!/usr/bin/env python3
"""Correct V158's oracle-applied checks for a shadow-only census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v158_x077_shadow_census_preregistration.json"
RAW_RESULT = ANALYSIS / "winner_v158_x077_shadow_census_result.json"
OUTPUT = ANALYSIS / "winner_v158_x077_shadow_census_reporting_correction.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V158_X077_SHADOW_CENSUS_REPORTING_CORRECTION_20260725.md"
)
EXPECTED_SHADOW_FAILURES = {
    "oracle_only_empty_or_prehistory_residuals",
    "oracle_prediction_exact",
    "oracle_zero_nonempty_residual_violations",
    "oracle_zero_prediction_mismatches",
    "torque_peak_at_most_1p91229675_nm",
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
            raise FileExistsError(f"refusing to overwrite V158: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    raw = json.loads(RAW_RESULT.read_text(encoding="utf-8"))
    events = raw["torque"]["event_rows"]
    false_metric_checks = {
        name
        for name, value in raw["cell"]["metrics"]["checks"].items()
        if not value
    }
    checks = {
        "raw_hold_is_reporting_only": (
            raw.get("status") == "HOLD_WINNER_V158_X077_SHADOW_CENSUS"
            and raw.get("failed_checks") == ["torque_failure_reproduced"]
        ),
        "preregistration_requires_shadow_not_application": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V158_X077_SHADOW_CENSUS"
            and prereg["method"]["application"] is False
        ),
        "only_expected_shadow_and_torque_checks_false": (
            false_metric_checks == EXPECTED_SHADOW_FAILURES
            and set(raw["cell"]["failure_reasons"])
            == EXPECTED_SHADOW_FAILURES
        ),
        "all_raw_shadow_validity_checks_green": all(
            bool(value)
            for name, value in raw["checks"].items()
            if name != "torque_failure_reproduced"
        ),
        "actual_torque_failure_present": (
            len(events) == 2
            and raw["cell"]["torque_gate"]["check"] is False
            and raw["cell"]["torque_gate"]["worst_peak_torque_nm"]
            > 1.91229675
        ),
        "two_events_are_left_knee_and_right_ankle": (
            [(event["tick"], event["joint"]) for event in events]
            == [(30, 3), (208, 13)]
        ),
        "both_events_have_safe_nonempty_precursors": all(
            event["source_tick"] is not None
            and event["source_action_delta"] != 0.0
            and event["joint"] in event["source_projected_joint_indices"]
            and event["joint"] not in event["source_empty_joint_indices"]
            and abs(event["projected_force_nm"]) <= 1.91229675 + 5.0e-6
            for event in events
        ),
        "policy_action_unchanged": raw["checks"][
            "shadow_action_never_applied"
        ],
        "read_only_no_rerun_training_hosted_compute_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v158.x077_shadow_census_reporting_correction.v1"
        ),
        "status": (
            "PASS_WINNER_V158_X077_SHADOW_CENSUS_REPORTING_CORRECTION"
            if not failed
            else "HOLD_WINNER_V158_X077_SHADOW_CENSUS_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "runner": sha256(Path(__file__).resolve()),
            "preregistration": sha256(PREREG),
            "raw_result": sha256(RAW_RESULT),
            "trace": raw["trace"]["sha256"],
        },
        "reporting_issue": (
            "the reused exact-oracle cell classifier expects oracle "
            "corrections to be applied; V158 deliberately ran shadow-only, "
            "so its four application-success checks and the original torque "
            "gate must remain false"
        ),
        "census": {
            "events": events,
            "violating_joints": raw["torque"]["violating_joints"],
            "peak_nm": raw["torque"]["peak_nm"],
            "projected_joint_events": raw["oracle"][
                "projected_joint_events"
            ],
            "projected_by_joint": raw["oracle"]["projected_by_joint"],
            "maximum_clip_linf": raw["oracle"]["maximum_clip_linf"],
        },
        "diagnosis": (
            "the x=.077 failure is multi-joint and command-dependent: the "
            "left-knee startup precursor requires +0.019204855 action and "
            "the later right-ankle precursor requires +0.011286139, far "
            "outside V155's frozen +0.002124012 one-joint correction"
        ),
        "decision": (
            "EARN_V159_POLICY_SPACE_REDESIGN_AUDIT"
            if not failed
            else "ESCALATE_DIRECTLY_TO_GAIT_LEVEL_REDESIGN"
        ),
        "authority": {
            "mechanism_classification": not failed,
            "training": False,
            "hosted_training": False,
            "candidate_behavior": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V158 shadow-census reporting correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Shadow actions were intentionally not applied; the inherited "
        "oracle-application checks are therefore expected to fail.\n"
        "- Two actual violations are fully labeled: left knee tick 30 and "
        "right ankle tick 208.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only correction; no rerun, training, Colab, deployment, "
        "Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
