from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import t8_state_coherent_eval_adapter as adapter  # noqa: E402
from evaluate_t8_state_coherent_handoff import (  # noqa: E402
    COMMANDS,
    emergence_evidence,
    parse_commands,
)


def test_adapter_is_narrow_default_off_and_hash_locked() -> None:
    contract = adapter.contract()
    assert contract["source_sha256"] == (
        "352ea320936c83801fa47f76e35faea36a68f1d7f45c11b1869292e1955f4114"
    )
    assert contract["patched_source_sha256"] == (
        "1c7de5aba3b498975c3ef02c13599d176527028caaa0058172760125734e5a88"
    )
    assert contract["patch_count"] == 6
    module = adapter.load_module()
    field = module.ClosedLoopConfig.__dataclass_fields__[
        "response_preserve_handoff_state"
    ]
    assert field.default is False


def test_worker_refuses_command_selection_drift() -> None:
    assert parse_commands("0.0,0.074,0.077,0.08") == COMMANDS
    try:
        parse_commands("0.0,0.08")
    except ValueError as exc:
        assert "commands changed" in str(exc)
    else:
        raise AssertionError("T8 accepted a changed command matrix")


def test_emergence_evidence_requires_bilateral_transition_and_progress() -> None:
    result = {
        "modes": {
            "fitted": {
                "termination_reason": "duration_complete",
                "forward_motion": {
                    "body_forward_progress_m": 0.6,
                    "progress_x_m": 0.6,
                    "mean_velocity_x_m_s": 0.05,
                    "elapsed_s": 12.0,
                },
                "foot_clearance": {
                    "feet": {
                        "left": {
                            "stance_samples": 300,
                            "swing_samples": 300,
                            "contact_transition_count": 4,
                        },
                        "right": {
                            "stance_samples": 300,
                            "swing_samples": 300,
                            "contact_transition_count": 4,
                        },
                    },
                    "support": {"support_transition_count": 8},
                },
                "joints": {
                    str(index): {
                        "action": {"std": 0.1},
                        "action_abs": {"min": 0.0},
                    }
                    for index in range(14)
                },
            }
        }
    }
    observed = emergence_evidence(result, 0.08, 12.0)
    assert observed["pass"] is True
    result["modes"]["fitted"]["foot_clearance"]["feet"]["right"][
        "contact_transition_count"
    ] = 0
    observed = emergence_evidence(result, 0.08, 12.0)
    assert observed["pass"] is False
    assert "right_has_no_contact_transition" in observed["reasons"]


def test_external_asset_manifest_is_bit_exact_when_present() -> None:
    path = Path(
        r"D:\CodexArtifacts\open-duck-policy"
        r"\t8_state_coherent_handoff_assets_v2\manifest.json"
    )
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["execution"] == {
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "simulator_behavior_cells": 0,
    }
    assert len(manifest["policies"]) == 2
    for policy in manifest["policies"]:
        parity = policy["parity"]
        assert parity["ticks"] == 1024
        assert parity["all_outputs_bit_exact"] is True
        assert parity["zero_command_actions_exact_zero"] is True
        assert set(parity["maximum_abs_errors"].values()) == {0.0}
        assert parity["wrapped_io"]["inputs"]["calibration_context"] == [1, 64]


def test_frozen_t8_preregistration_is_canonical_when_present() -> None:
    path = (
        ROOT
        / "outputs"
        / "analysis"
        / "t8_state_coherent_handoff_preregistration.json"
    )
    if not path.is_file():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "question",
            "causal_basis",
            "repository_inputs",
            "playground",
            "assets",
            "calibrator",
            "candidate",
            "matrix",
            "handoff_contract",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    observed = hashlib.sha256(
        json.dumps(
            basis,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    assert observed == value["preregistered_contract_sha256"]
    assert value["matrix"]["total_cells"] == 16
    assert value["authority"]["training_or_hosted_compute"] is False


def test_t8_preoutcome_abi_amendment_is_narrow_and_canonical() -> None:
    path = (
        ROOT
        / "outputs"
        / "analysis"
        / "t8_state_coherent_handoff_abi_amendment.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "original_preregistration",
            "preoutcome_evidence",
            "onnx_abi",
            "authorized_change",
            "corrected_files",
            "unchanged_contract",
            "authority",
        )
    }
    observed = hashlib.sha256(
        json.dumps(
            basis,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    assert observed == value["amendment_contract_sha256"]
    assert value["preoutcome_evidence"][
        "behavior_cells_with_decision_weight"
    ] == 0
    assert value["preoutcome_evidence"]["jsonl_trace_files"] == 0
    assert value["authorized_change"]["new_state_inputs"] == [
        "h_in",
        "previous_action",
    ]
    assert value["authorized_change"]["new_state_outputs"] == [
        "h_out",
        "previous_action_out",
    ]
    assert value["unchanged_contract"]["training_steps"] == 0


def test_t8_result_audit_and_failure_localization_are_canonical() -> None:
    analysis = ROOT / "outputs" / "analysis"
    result_path = analysis / "t8_state_coherent_handoff_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result_basis = {
        key: value
        for key, value in result.items()
        if key != "result_sha256"
    }
    assert hashlib.sha256(
        json.dumps(
            result_basis,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest() == result["result_sha256"]
    assert result["status"] == "HOLD_T8_STATE_COHERENT_HANDOFF"
    assert (
        result["decision"]
        == "CLOSE_DIRECT_STATE_COHERENT_V121_HANDOFF_WITHOUT_TRAINING"
    )
    assert result["completed_cells"] == result["expected_cells"] == 16
    assert result["passing_cells"] == 12
    assert result["summary"]["all_handoff_contracts_pass"] is True
    assert result["execution"]["training_steps"] == 0
    assert result["execution"]["robot_or_rdk_access"] == 0

    original_audit = json.loads(
        (
            analysis / "t8_state_coherent_handoff_independent_audit.json"
        ).read_text(encoding="utf-8")
    )
    assert original_audit["passing_cells"] == 10
    assert original_audit["independent_classification"]["status"] == (
        "HOLD_T8_STATE_COHERENT_HANDOFF"
    )
    correction = json.loads(
        (
            analysis / "t8_state_coherent_handoff_audit_correction.json"
        ).read_text(encoding="utf-8")
    )
    assert correction["decision_invariance"]["status_cannot_change"] is True
    assert correction["decision_invariance"]["decision_cannot_change"] is True

    audit = json.loads(
        (
            analysis
            / "t8_state_coherent_handoff_independent_audit_v2.json"
        ).read_text(encoding="utf-8")
    )
    audit_basis = {
        key: value for key, value in audit.items() if key != "audit_sha256"
    }
    assert hashlib.sha256(
        json.dumps(
            audit_basis,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest() == audit["audit_sha256"]
    assert audit["status"] == (
        "PASS_T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT"
    )
    assert audit["issues"] == []
    assert audit["audited_cells"] == 16
    assert audit["passing_cells"] == 12

    failure = json.loads(
        (
            analysis / "t8_state_coherent_handoff_failure_analysis.json"
        ).read_text(encoding="utf-8")
    )
    assert failure["status"] == "T8_FAILURE_LOCALIZED_X0_PREFIX_TRANSITION"
    assert all(failure["checks"].values())
    assert failure["selected_next_falsifier"]["training_steps"] == 0
    assert failure["selected_next_falsifier"][
        "new_behavior_cells_required"
    ] == 4
