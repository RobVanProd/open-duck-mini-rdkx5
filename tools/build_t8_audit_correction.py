#!/usr/bin/env python3
"""Freeze the post-outcome T8 independent-audit frame correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
AMENDMENT = ANALYSIS / "t8_state_coherent_handoff_abi_amendment.json"
RESULT = ANALYSIS / "t8_state_coherent_handoff_result.json"
ORIGINAL_AUDIT = (
    ANALYSIS / "t8_state_coherent_handoff_independent_audit.json"
)
ORIGINAL_MARKDOWN = (
    ANALYSIS / "T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT_20260726.md"
)
OUTPUT = ANALYSIS / "t8_state_coherent_handoff_audit_correction.json"
MARKDOWN = (
    ANALYSIS / "T8_STATE_COHERENT_HANDOFF_AUDIT_CORRECTION_20260726.md"
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
        raise FileExistsError("refusing to overwrite the T8 audit correction")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    original = json.loads(ORIGINAL_AUDIT.read_text(encoding="utf-8"))
    expected_issues = [
        "cell_classification:('V121_TRAIN_MATCHED_FINAL', 'p30'):3",
        "cell_classification:('V121_TRAIN_MATCHED_FINAL', 'p31_34'):3",
        "result_passing_cells",
    ]
    if (
        result["status"] != "HOLD_T8_STATE_COHERENT_HANDOFF"
        or result["passing_cells"] != 12
        or original["issues"] != expected_issues
        or original["independent_classification"]["status"]
        != "HOLD_T8_STATE_COHERENT_HANDOFF"
    ):
        raise RuntimeError("unexpected T8 result/audit correction basis")
    x0_failures = [
        cell
        for block in result["blocks"]
        for cell in block["result"]["cells"]
        if cell["command_x_m_s"] == 0.0 and not cell["cell_green"]
    ]
    if len(x0_failures) != 4 or any(
        cell["protection"]["maximum_full_measured_vector_excess_rad_s"]
        <= 0.0
        for cell in x0_failures
    ):
        raise RuntimeError("T8 hold is not invariant to the audit correction")
    basis = {
        "original_audit": {
            **receipt(ORIGINAL_AUDIT),
            "markdown": receipt(ORIGINAL_MARKDOWN),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
            "abi_amendment_contract_sha256": amendment[
                "amendment_contract_sha256"
            ],
            "issues": original["issues"],
            "passing_cells": original["passing_cells"],
            "classification": original["independent_classification"],
        },
        "cause": {
            "affected_cells": [
                ["V121_TRAIN_MATCHED_FINAL", "p30", 0.08],
                ["V121_TRAIN_MATCHED_FINAL", "p31_34", 0.08],
            ],
            "incorrect_quantity": (
                "world-X displacement, which becomes negative after yaw"
            ),
            "frozen_gate_quantity": "body-frame forward progress",
            "correct_reconstruction": (
                "sum(recorded local_linvel_m_s[0] * 0.02 s)"
            ),
            "reproduced_body_forward_progress_m": [
                1.2727714599855244,
                1.2692105245217682,
            ],
        },
        "authorized_change": {
            "old_audit_progress": "base_x[-1] - base_x[0]",
            "new_audit_progress": "sum(local_linvel_m_s[:,0]) * 0.02",
            "behavior_or_result_change": False,
            "raw_trace_change": False,
        },
        "corrected_auditor": receipt(
            ROOT / "tools" / "audit_t8_state_coherent_handoff.py"
        ),
        "decision_invariance": {
            "original_result_status": result["status"],
            "original_result_decision": result["decision"],
            "four_x0_failures_unchanged": True,
            "corrected_maximum_possible_passing_cells": 12,
            "all_16_required_for_pass": True,
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
        "schema_version": "open_duck.t8_audit_correction.v1",
        "status": "T8_POSTOUTCOME_AUDIT_BODY_FRAME_CORRECTION",
        **basis,
        "correction_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T8 independent-audit body-frame correction",
        "",
        f"- Status: `{payload['status']}`",
        f"- Contract SHA-256: `{payload['correction_contract_sha256']}`",
        "- Original audit preserved: yes",
        "- Result status/decision can change: no",
        "",
        "The first auditor used world-X displacement in two x=.08 cells that "
        "yawed during the 12-second run. The frozen gait gate uses body-frame "
        "progress. Integrating the already-recorded local forward velocity at "
        "the frozen 20 ms step reproduces the evaluator's +1.27277/+1.26921 m.",
        "",
        "The four x=0 rate-excess failures are unaffected, so T8 remains a "
        "12/16 hold and direct zero-training handoff remains closed. This "
        "correction authorizes only a rerun of the independent auditor.",
    ]
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"contract_sha256={payload['correction_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
