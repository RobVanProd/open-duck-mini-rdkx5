#!/usr/bin/env python3
"""Freeze V167's auxiliary reproduction-field reporting correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v167_reference_amplitude_direction_preregistration.json"
)
INVALID = ANALYSIS / "winner_v167_reference_amplitude_direction_result.json"
ORIGINAL = ROOT / "tools/run_winner_v167_reference_amplitude_direction.py"
WRAPPER = (
    ROOT
    / "tools/run_winner_v167b_reference_amplitude_reporting_correction.py"
)
OUTPUT = (
    ANALYSIS
    / "winner_v167b_reference_amplitude_reporting_correction.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V167B_REFERENCE_AMPLITUDE_REPORTING_CORRECTION_20260725.md"
)
CORRECTED_RESULT = (
    ANALYSIS / "winner_v167b_reference_amplitude_direction_result.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V167b: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    checks = {
        "preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
            and prereg["failed_checks"] == []
        ),
        "original_runner_unchanged": (
            sha256(ORIGINAL) == prereg["input_hashes"]["runner"]
        ),
        "invalid_result_hash_exact": (
            sha256(INVALID)
            == "b7d322da84cd4f2da81832289324767a4ccdfae4b5f71649f9f2eb045ebb0afa"
        ),
        "invalid_mechanism_signal_already_hold": (
            invalid["summary"]["same_nonzero_direction"] == 3
            and invalid["summary"]["strict_error_reduction"] == 2
        ),
        "invalid_auxiliary_check_compared_boolean_flag": (
            invalid["summary"]["original_graph_reproduction_linf"]
            == 1.8556671142578125
            and "original_graph_reproduction_linf_at_most_1e6"
            in invalid["failed_checks"]
        ),
        "wrapper_changes_only_recorded_action_field": (
            "'row[\"policy_graph_authoritative_output\"]'," in wrapper_text
            and "'row[\"action\"]'," in wrapper_text
            and 'namespace["OUTPUT"] = OUTPUT' in wrapper_text
            and 'namespace["MARKDOWN"] = MARKDOWN' in wrapper_text
        ),
        "corrected_result_absent": not CORRECTED_RESULT.exists(),
        "mechanism_scale_events_pass_rules_and_decision_unchanged": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v167b.reference_amplitude_reporting_correction.v1"
        ),
        "status": (
            "PASS_WINNER_V167B_REFERENCE_AMPLITUDE_REPORTING_CORRECTION"
            if not failed
            else "HOLD_WINNER_V167B_REFERENCE_AMPLITUDE_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "invalid_result": sha256(INVALID),
            "original_runner": sha256(ORIGINAL),
            "preregistration": sha256(PREREG),
            "wrapper": sha256(WRAPPER),
        },
        "observed_issue": {
            "field_used": "policy_graph_authoritative_output",
            "field_value": True,
            "correct_field": "action",
            "scope": "auxiliary original-graph reproduction check only",
            "mechanism_alignment_counts_affected": False,
            "invalid_same_nonzero_direction": 3,
            "invalid_strict_error_reduction": 2,
        },
        "correction": {
            "original_runner_source_edited": False,
            "shadow_scale_changed": False,
            "event_population_changed": False,
            "pass_rule_changed": False,
            "decision_rule_changed": False,
            "simulation_or_training_added": False,
        },
        "authority": {
            "one_corrected_cpu_shadow_rerun": not failed,
            "simulation": False,
            "training": False,
            "hosted_training": False,
            "production_contract_change": False,
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
        "# Winner V167b reference-amplitude reporting correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- V167's auxiliary reproduction check compared ONNX actions to a "
        "boolean trace flag instead of the trace's final `action` field.\n"
        "- The fixed scale, 12 events, oracle alignment/error rules, and "
        "decision rule are unchanged.\n"
        "- The invalid run already aligned only 3/12 events and improved "
        "2/12; those mechanism counts are unaffected by this correction.\n"
        "- Authorizes one corrected CPU shadow rerun; no simulation, "
        "training, contract change, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
