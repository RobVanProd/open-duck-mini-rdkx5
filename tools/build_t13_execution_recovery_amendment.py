#!/usr/bin/env python3
"""Freeze the narrow recovery from T13's reporting-only runner failure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t13_shadow_hidden_preregistration.json"
OUTPUT = ANALYSIS / "t13_execution_recovery_amendment.json"
MARKDOWN = ANALYSIS / "T13_EXECUTION_RECOVERY_AMENDMENT_20260726.md"
FAILED_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t13_shadow_hidden_contract_v1"
)
FAILED_STDERR = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t13_shadow_hidden_contract_v1.stderr.log"
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
    path = path.resolve()
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    completed = sorted(FAILED_ROOT.rglob("evaluation.json"))
    traces = sorted(FAILED_ROOT.rglob("tick0.jsonl"))
    if len(completed) != 1 or len(traces) != 1:
        raise RuntimeError("unexpected T13 partial execution population")
    failure_text = FAILED_STDERR.read_text(encoding="utf-8")
    if (
        "TypeError: float() argument must be a string or a real number"
        not in failure_text
        or "sent_target_rate_excess_rad_s" not in failure_text
    ):
        raise RuntimeError("T13 failure signature changed")
    basis = {
        "schema_version": "open_duck.t13_execution_recovery_amendment.v1",
        "status": "PREREGISTERED_T13_EXECUTION_RECOVERY",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "failed_execution": {
            "work_root": str(FAILED_ROOT),
            "completed_prefix_cells": 1,
            "formal_result_written": False,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
            "decision_weight": 0,
            "selection_use_forbidden": True,
            "evaluation": receipt(completed[0]),
            "trace": receipt(traces[0]),
            "stderr": receipt(FAILED_STDERR),
            "failure_class": (
                "reporting aggregation treated a per-joint rate-excess "
                "vector as a scalar after the simulator cell completed"
            ),
        },
        "original_runner": prereg["sources"]["runner"],
        "recovery_runner": receipt(
            ROOT / "tools" / "run_t13_shadow_hidden_contract.py"
        ),
        "correction": {
            "rate_excess": (
                "take maximum absolute value over the already logged "
                "per-joint vector"
            ),
            "one_tick_status": (
                "require PASS_MODE_EVALUATED and no worker error; the "
                "candidate behavior status is intentionally not scored by T13"
            ),
            "mechanism_changed": False,
            "thresholds_changed": False,
            "matrix_changed": False,
            "policy_or_prefix_changed": False,
        },
        "authorized_recovery": {
            "attempts_exact": 1,
            "fresh_work_root": (
                r"D:\CodexArtifacts\open-duck-policy"
                r"\t13_shadow_hidden_contract_v2"
            ),
            "reuse_partial_v1_forbidden": True,
            "all_four_cells_must_be_recomputed": True,
        },
        "unchanged_contract": {
            "pass_rule": prereg["pass_rule"],
            "decision_rule": prereg["decision_rule"],
            "partial_results_selection_weight": 0,
        },
        "execution_now": {
            "formal_decision_cells": 0,
            "scored_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "amendment_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T13 execution recovery amendment",
                "",
                "The first T13 process completed one prefix cell, then the "
                "reporter attempted to cast a 14-joint rate-excess vector to "
                "a scalar. No formal result was written.",
                "",
                "- Partial cell decision weight: `0`",
                "- Mechanism / matrix / thresholds: unchanged",
                "- Recovery: exactly one fresh four-cell run",
                "- Optimizer / hosted / robot: `0 / 0 / 0`",
                (
                    "- Amendment SHA-256: "
                    f"`{value['amendment_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["amendment_contract_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
