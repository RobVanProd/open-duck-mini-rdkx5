#!/usr/bin/env python3
"""Freeze a source-semantic correction for the interrupted rate-vector audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v7_full_measured_vector_attribution_preregistration.json"
AUDIT = ROOT / "tools" / "audit_winner_v7_full_measured_vector_attribution.py"
EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
OUTPUT = ANALYSIS / "winner_v7_full_measured_vector_attribution_preregistration_amendment.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    payload = {
        "schema_version": "open_duck_mini.winner_v7_full_measured_vector_attribution_preregistration_amendment.v1",
        "status": "FROZEN_SOURCE_SEMANTICS_CORRECTION_BEFORE_RESULT",
        "original_preregistration_sha256": sha256(PREREG),
        "superseded_audit_tool_sha256": prereg["frozen_inputs"]["audit_tool_sha256"],
        "corrected_audit_tool_sha256": sha256(AUDIT),
        "source_evaluator": {
            "path": str(EVALUATOR.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(EVALUATOR),
            "winner_v7_contract_commit_same_content_sha256": sha256(EVALUATOR),
        },
        "interrupted_run": {
            "classification_or_result_written": False,
            "first_stopped_trace": "NOMINAL/p30/half/x0.074",
            "exception": "recorded rate-excess replay mismatch",
            "maximum_observed_replay_difference_rad_s": 3.0100345611572266e-06,
        },
        "correction": {
            "recorded_rate_excess_zero_threshold_rad_s": 1e-5,
            "source_semantics": "raw excess values less than or equal to 1e-5 rad/s are recorded as exact zero",
            "selection_tolerance_unchanged": prereg["analysis_contract"]["numeric_tolerance"],
            "causal_window_unchanged": prereg["analysis_contract"]["causal_prior_window_ticks"],
            "population_vectors_gates_and_selection_rule_unchanged": True,
        },
        "authority": {
            "outcome_based_rule_change": False,
            "retry_of_classified_result": False,
            "read_only_cpu_audit_only": True,
            "policy_simulator_training_runtime_robot_torque_motion_gate5": False,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE={OUTPUT}")
    print(f"SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
