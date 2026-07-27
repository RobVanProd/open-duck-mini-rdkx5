#!/usr/bin/env python3
"""Reconcile T30's unregistered mixed outcome without rerunning simulation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t30_t28_margin_causality_preregistration.json"
RAW = ANALYSIS / "t30_t28_margin_causality_result.json"
OUTPUT = ANALYSIS / "t30_t28_margin_causality_reconciliation.json"
OUTPUT_MD = (
    ANALYSIS / "T30_T28_MARGIN_CAUSALITY_RECONCILIATION_20260727.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    behavior = raw["source_cell"]["behavior"]
    non_saturation_core = all(
        passed
        for name, passed in behavior["core_checks"].items()
        if name != "saturation"
    )
    non_saturation_quality = all(
        passed
        for name, passed in behavior["replacement_quality_checks"].items()
        if name != "zero_saturation"
    )
    source_behavior_valid = (
        behavior["samples"] == 600
        and behavior["termination_reason"] == "duration_complete"
        and non_saturation_core
        and non_saturation_quality
        and raw["source_cell"]["protection"]["duration_protection_pass"]
        and raw["source_cell"]["handoff"]["all_checks_pass"]
        and raw["source_cell"]["override_readback_exact"]
        and raw["source_cell"]["trace_valid"]
    )
    source_saturation_only_failure = (
        source_behavior_valid
        and not behavior["core_checks"]["saturation"]
        and not behavior["replacement_quality_checks"]["zero_saturation"]
    )
    wrapped_fell = prereg["wrapped_failure"]["samples"] < 600
    pre_intervention_exact = raw["causal_comparison"][
        "pre_intervention_exact"
    ]
    mixed_outcome = (
        source_saturation_only_failure
        and wrapped_fell
        and pre_intervention_exact
    )
    checks = {
        "raw_result_matches_preregistration": (
            raw["preregistered_contract_sha256"]
            == prereg["preregistered_contract_sha256"]
        ),
        "source_runs_full_duration": source_behavior_valid,
        "source_fails_only_saturation_margin": (
            source_saturation_only_failure
        ),
        "wrapped_policy_falls_early": wrapped_fell,
        "pre_intervention_traces_are_exact": pre_intervention_exact,
        "mixed_outcome_was_not_in_binary_decision_rule": (
            raw["source_cell"]["cell_green"] is False
            and behavior["samples"] == 600
            and prereg["decision_rule"].get("mixed_outcome") is None
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t30_t28_margin_causality_reconciliation.v1"
        ),
        "status": (
            "PASS_T30_MIXED_OUTCOME_RECONCILIATION"
            if not failed_checks and mixed_outcome
            else "HOLD_T30_MIXED_OUTCOME_RECONCILIATION"
        ),
        "decision": (
            "CLOSE_T28_POSTHOC_MARGIN_TRANSFORM"
            if not failed_checks and mixed_outcome
            else "ZERO_POLICY_DECISION_WEIGHT"
        ),
        "supersedes_raw_binary_decision": (
            "RETAIN_T28_CONTINUE_FAILURE_ATTRIBUTION"
        ),
        "raw_result": receipt(RAW),
        "preregistration": receipt(PREREG),
        "facts": {
            "unwrapped_samples": behavior["samples"],
            "unwrapped_termination": behavior["termination_reason"],
            "unwrapped_action_saturation_pct": behavior[
                "action_saturation_pct"
            ],
            "unwrapped_tracking_p95_rad": behavior[
                "pitch_tracking_p95_rad"
            ],
            "wrapped_samples": prereg["wrapped_failure"]["samples"],
            "first_margin_intervention_tick": prereg["wrapped_failure"][
                "first_intervention_tick"
            ],
            "pre_intervention_exact": pre_intervention_exact,
        },
        "interpretation": (
            "The preregistered binary rule omitted a mixed outcome. The "
            "unwrapped source is not gate-green because it crosses the 0.98 "
            "margin, but it walks all 600 ticks. The post-hoc T28 clip removes "
            "that margin failure and creates an early fall. Therefore T28 is "
            "not a deployable repair and is closed; the source is also not a "
            "green candidate."
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "posthoc_t28_candidate_closed": (
                not failed_checks and mixed_outcome
            ),
            "mechanism_contract_review": (
                not failed_checks and mixed_outcome
            ),
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["result_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T30 T28 margin-causality reconciliation",
                "",
                f"status: `{payload['status']}`",
                "",
                f"decision: `{payload['decision']}`",
                "",
                "The preregistered binary rule omitted the observed mixed "
                "case. The unwrapped source walks all 600 ticks but fails the "
                "0.98 margin; the wrapped policy removes that margin crossing "
                "but falls at tick 331. T28 is closed as a post-hoc repair, "
                "and the unwrapped source remains non-green.",
                "",
                "This reporting reconciliation authorizes mechanism-contract "
                "review only. It does not authorize training, Gate 5, "
                "RDK-X5, robot, torque, or motion.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"decision={payload['decision']}")
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={payload['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks and mixed_outcome else 1


if __name__ == "__main__":
    raise SystemExit(main())
