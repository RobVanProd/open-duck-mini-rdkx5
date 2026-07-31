#!/usr/bin/env python3
"""Freeze the reporting-only correction to the T13 independent audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t13_shadow_hidden_preregistration.json"
RESULT = ANALYSIS / "t13_shadow_hidden_result.json"
AUDIT_V1 = ANALYSIS / "t13_shadow_hidden_independent_audit.json"
AUDIT_V1_MD = (
    ANALYSIS / "T13_SHADOW_HIDDEN_INDEPENDENT_AUDIT_20260726.md"
)
OUTPUT = ANALYSIS / "t13_audit_correction_amendment.json"
MARKDOWN = ANALYSIS / "T13_AUDIT_CORRECTION_AMENDMENT_20260726.md"


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
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit_v1 = json.loads(AUDIT_V1.read_text(encoding="utf-8"))
    if (
        result["status"]
        != "HOLD_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
        or result["decision"]
        != "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
        or result["failed_checks"]
        != ["both_plant_hidden_states_actionable"]
        or audit_v1["issues"]
        != ["V121_TRAIN_MATCHED_HALF.plant_action_visibility"]
    ):
        raise RuntimeError("T13 correction inputs changed")
    basis = {
        "schema_version": "open_duck.t13_audit_correction.v1",
        "status": "PREREGISTERED_T13_AUDIT_CLASSIFICATION_CORRECTION",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "result": receipt(RESULT),
        "audit_v1": receipt(AUDIT_V1),
        "audit_v1_markdown": receipt(AUDIT_V1_MD),
        "audit_v2_source": receipt(
            ROOT / "tools" / "audit_t13_shadow_hidden_contract.py"
        ),
        "problem": (
            "The v1 auditor independently reproduced the preregistered "
            "half-checkpoint plant-actionability failure, then placed that "
            "expected contract failure in its audit-integrity issues list."
        ),
        "correction": (
            "Keep reproduced contract failures separate from audit "
            "integrity issues. PASS_AUDIT means the auditor agrees with the "
            "formal HOLD; it does not turn the mechanism green."
        ),
        "unchanged": {
            "formal_status": result["status"],
            "formal_decision": result["decision"],
            "failed_checks": result["failed_checks"],
            "thresholds": True,
            "mechanism": True,
            "behavior_authorization": False,
            "training_authorization": False,
        },
        "authority": {
            "simulator_cells": 0,
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
                "# T13 audit classification correction",
                "",
                "The v1 audit reproduced the formal T13 HOLD but classified "
                "the expected failed contract predicate as an audit-integrity "
                "issue. V2 separates those concepts.",
                "",
                "- Formal result: unchanged HOLD",
                "- Mechanism decision: unchanged CLOSE",
                "- New simulator / behavior / training / robot work: `0`",
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
