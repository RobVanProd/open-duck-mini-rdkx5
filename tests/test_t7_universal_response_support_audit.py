from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t7_result_and_independent_audit_are_canonical_and_green() -> None:
    result_path = ANALYSIS / "t7_universal_response_support_result.json"
    audit_path = (
        ANALYSIS / "t7_universal_response_support_independent_audit.json"
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    result_basis = {
        key: value for key, value in result.items() if key != "result_sha256"
    }
    audit_basis = {
        key: value for key, value in audit.items() if key != "audit_sha256"
    }
    assert canonical_sha256(result_basis) == result["result_sha256"]
    assert canonical_sha256(audit_basis) == audit["audit_sha256"]
    assert result["status"] == "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
    assert (
        result["decision"]
        == "EARN_STATE_COHERENT_SUPPORT_TO_LOCOMOTION_CPU_SCREEN"
    )
    assert result["passing_cells"] == result["expected_cells"] == 12
    assert all(result["global_checks"].values())
    assert (
        audit["status"]
        == "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT_INDEPENDENT_AUDIT"
    )
    assert audit["issues"] == []
    assert audit["audited_cells"] == 12
    assert all(audit["global_checks"].values())
    assert audit["result_sha256"] == hashlib.sha256(
        result_path.read_bytes()
    ).hexdigest()


def test_t7_raw_artifacts_are_external_and_training_remains_unearned() -> None:
    prereg = json.loads(
        (
            ANALYSIS / "t7_universal_response_support_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    result = json.loads(
        (
            ANALYSIS / "t7_universal_response_support_result.json"
        ).read_text(encoding="utf-8")
    )
    assert prereg["execution_contract"]["cache_root"].startswith(
        r"D:\CodexArtifacts"
    )
    assert result["execution"]["training_steps"] == 0
    assert result["execution"]["robot_or_rdk_access"] == 0
    assert result["authority"]["training_or_hosted_compute"] is False
    assert result["authority"]["gate5"] is False
