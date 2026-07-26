#!/usr/bin/env python3
"""Freeze the post-outcome T9 independent-audit label correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t9_command_aware_prefix_bypass_preregistration.json"
RESULT = ANALYSIS / "t9_command_aware_prefix_bypass_result.json"
ORIGINAL_AUDIT = (
    ANALYSIS / "t9_command_aware_prefix_bypass_independent_audit.json"
)
ORIGINAL_MARKDOWN = (
    ANALYSIS
    / "T9_COMMAND_AWARE_PREFIX_BYPASS_INDEPENDENT_AUDIT_20260726.md"
)
OUTPUT = ANALYSIS / "t9_command_aware_prefix_bypass_audit_correction.json"
MARKDOWN = (
    ANALYSIS
    / "T9_COMMAND_AWARE_PREFIX_BYPASS_AUDIT_CORRECTION_20260726.md"
)


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


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T9 audit correction")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    original = json.loads(ORIGINAL_AUDIT.read_text(encoding="utf-8"))
    expected_issues = [
        "bypass_checks:('V121_TRAIN_MATCHED_HALF', 'p30')",
        "bypass_checks:('V121_TRAIN_MATCHED_HALF', 'p31_34')",
        "bypass_checks:('V121_TRAIN_MATCHED_FINAL', 'p30')",
        "bypass_checks:('V121_TRAIN_MATCHED_FINAL', 'p31_34')",
    ]
    if (
        result["status"] != "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
        or result["new_passing_cells"] != 4
        or result["combined_passing_cells"] != 16
        or original["issues"] != expected_issues
        or original["new_passing_cells"] != 4
        or original["combined_passing_cells"] != 16
        or original["classification"]["status"]
        != "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
    ):
        raise RuntimeError("unexpected T9 audit correction basis")
    basis = {
        "original_audit": {
            **receipt(ORIGINAL_AUDIT),
            "markdown": receipt(ORIGINAL_MARKDOWN),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
            "preregistered_auditor": prereg["repository_inputs"][
                "independent_auditor"
            ],
            "issues": original["issues"],
            "new_passing_cells": original["new_passing_cells"],
            "combined_passing_cells": original["combined_passing_cells"],
            "classification": original["classification"],
        },
        "cause": {
            "formula_or_threshold_error": False,
            "raw_trace_or_result_error": False,
            "cell_classification_error": False,
            "comparison_error": (
                "the independent auditor used shorter semantic dictionary keys "
                "than the runner for the same fourteen true bypass checks"
            ),
        },
        "authorized_change": {
            "old_keys": [
                "zero_context_bypass",
                "context_shape_finite",
                "phase_reset",
                "hidden_zero",
                "previous_action_zero",
                "observer_exact",
                "actions_zero",
                "state_chains",
                "graph_authoritative",
                "full_obs",
                "applied_slot_continuity",
            ],
            "new_keys": [
                "zero_context_bypass_enabled",
                "context_shape_and_finite",
                "phase_reset_exact",
                "initial_hidden_zero",
                "initial_previous_action_zero",
                "applied_target_observer_exact",
                "actions_exact_zero",
                "recurrent_chains_exact",
                "graph_authoritative_no_host_delta",
                "full_observation_traced",
                "applied_target_slot_continuity",
            ],
            "boolean_values_changed": False,
            "behavior_or_result_changed": False,
        },
        "corrected_auditor": receipt(
            ROOT / "tools" / "audit_t9_command_aware_prefix_bypass.py"
        ),
        "decision_invariance": {
            "original_recomputed_new_passing_cells": 4,
            "original_recomputed_combined_passing_cells": 16,
            "original_recomputed_status": (
                "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
            ),
            "original_recomputed_decision": (
                "EARN_RESPONSE_CONDITIONED_V121_CONTINUATION_CPU_CONTRACT"
            ),
            "status_cannot_change": True,
            "decision_cannot_change": True,
        },
        "authority": {
            "rerun_corrected_independent_audit": True,
            "training_or_hosted_compute": False,
            "robot_rdkx5_gate5_torque_motion": False,
        },
    }
    payload = {
        "schema_version": "open_duck.t9_audit_correction.v1",
        "status": "T9_POSTOUTCOME_AUDIT_LABEL_CORRECTION",
        **basis,
        "correction_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T9 independent-audit label correction",
        "",
        f"- Status: `{payload['status']}`",
        f"- Contract SHA-256: `{payload['correction_contract_sha256']}`",
        "- Original audit preserved: yes",
        "- Recomputed cells before correction: `4/4` new, `16/16` combined",
        "- Result status/decision can change: no",
        "",
        "The original auditor independently recomputed every boolean as true "
        "and classified all four new cells as passes. Its only issues came from "
        "comparing semantically identical dictionaries with different key "
        "labels. This correction aligns labels only; formulas, thresholds, raw "
        "traces, cell outcomes, result status, and authority are unchanged.",
    ]
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"contract_sha256={payload['correction_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
