#!/usr/bin/env python3
"""Freeze the T71 paired hidden-state causal attribution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T68 = ANALYSIS / "t68_t67_postexport_result.json"
T69_PREREG = ANALYSIS / "t69_t67_nominal_matrix_preregistration.json"
T69_RESULT = ANALYSIS / "t69_t67_nominal_matrix_result.json"
T70_RESULT = ANALYSIS / "t70_t67_condition7_result.json"
AUDITOR = ROOT / "tools" / "audit_t71_t67_com_hidden_causality.py"
TEST = ROOT / "tests" / "test_t71_t67_com_hidden_causality.py"
V1 = ANALYSIS / "t71_t67_com_hidden_causal_preregistration.json"
INVALIDATION = ANALYSIS / "t71_t67_com_hidden_causal_v1_invalidation.json"
OUTPUT = ANALYSIS / "t71_t67_com_hidden_causal_preregistration_v2.json"
MARKDOWN = (
    ANALYSIS / "T71_T67_COM_HIDDEN_CAUSAL_PREREGISTRATION_V2_20260728.md"
)

SAMPLE_TICKS = [0, 8, 16, 32, 64, 80]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(
    value: Any, hash_key: str = "preregistered_contract_sha256"
) -> str:
    payload = dict(value)
    payload.pop(hash_key, None)
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


def trace_receipts(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    traces: dict[str, dict[str, Any]] = {}
    for block in result["blocks"]:
        checkpoint = block["checkpoint_id"]
        fit = block["fit_id"]
        for cell in block["result"]["cells"]:
            command = float(cell["command_x_m_s"])
            key = f"{checkpoint}|{fit}|{command:.3f}"
            path = Path(cell["protection"]["path"])
            if key in traces:
                raise RuntimeError(f"duplicate trace key: {key}")
            traces[key] = receipt(path)
    return traces


def main() -> int:
    for path in (INVALIDATION, OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T71: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T71 preregistration requires a clean worktree")

    v1 = json.loads(V1.read_text(encoding="utf-8"))
    t68 = json.loads(T68.read_text(encoding="utf-8"))
    t69_prereg = json.loads(T69_PREREG.read_text(encoding="utf-8"))
    t69 = json.loads(T69_RESULT.read_text(encoding="utf-8"))
    t70 = json.loads(T70_RESULT.read_text(encoding="utf-8"))
    nominal_traces = trace_receipts(t69)
    shifted_traces = trace_receipts(t70)
    policies = t69_prereg["policies"]
    trace_keys = sorted(nominal_traces)

    checks = {
        "t67_nominal_green": (
            t69["status"] == "PASS_T69_T67_NOMINAL_MATRIX"
            and t69["condition"]["green_cells"] == 16
        ),
        "t67_closed_at_exact_com_boundary": (
            t70["status"] == "HOLD_T70_T67_CONDITION7"
            and t70["decision"] == "CLOSE_T67_ENDPOINT_CORE_CONTINUATION"
            and t70["condition"]["condition_id"] == "TORSO_COM_X_NEG"
            and t70["condition"]["override"]
            == {"torso_com_offset_m": [-0.05, 0.0, 0.0]}
        ),
        "exact_paired_trace_population": (
            len(trace_keys) == 16
            and trace_keys == sorted(shifted_traces)
        ),
        "exact_two_deployment_policies": (
            len(policies) == 2
            and {item["checkpoint_id"] for item in policies}
            == {"T67_ENDPOINT_CORE_HALF", "T67_ENDPOINT_CORE_FINAL"}
        ),
        "policy_receipts_exact": all(
            Path(item["path"]).is_file()
            and Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies
        ),
        "postexport_contract_green": (
            t68["status"] == "PASS_T68_T67_POSTEXPORT_TRANSFORM"
        ),
        "auditor_and_test_present": AUDITOR.is_file() and TEST.is_file(),
        "v1_stopped_before_result": (
            v1["status"]
            == "PREREGISTERED_T71_T67_COM_HIDDEN_CAUSAL_ATTRIBUTION"
            and not (
                ANALYSIS / "t71_t67_com_hidden_causal_result.json"
            ).exists()
        ),
        "no_behavior_or_training_run": True,
        "offline_only": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t71_t67_com_hidden_causal_preregistration.v2",
        "status": (
            "PREREGISTERED_T71_T67_COM_HIDDEN_CAUSAL_ATTRIBUTION"
            if not failed
            else "HOLD_T71_T67_COM_HIDDEN_CAUSAL_PREREGISTRATION"
        ),
        "question": (
            "At the exact torso-COM-x-negative boundary, does T67's recurrent "
            "state distinguish the shifted plant and causally alter the "
            "deployed moving action when the current observation is held "
            "fixed?"
        ),
        "hypotheses": {
            "missing_signal": (
                "The recurrent state does not separate nominal and shifted "
                "plants, or swapping the paired hidden state has no material "
                "effect on the deployed action."
            ),
            "wrong_control_response": (
                "The recurrent state separates the plants and materially "
                "changes the deployed action under an identical observation, "
                "yet the formal shifted-plant behavior still fails."
            ),
        },
        "population": {
            "checkpoints": 2,
            "fits": 2,
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "paired_trace_streams": 16,
            "moving_trace_streams": 12,
            "sample_ticks": SAMPLE_TICKS,
            "moving_postreset_samples": 60,
        },
        "policies": policies,
        "nominal_traces": nominal_traces,
        "shifted_traces": shifted_traces,
        "thresholds": {
            "maximum_trace_replay_abs_error": 1.0e-7,
            "minimum_moving_postreset_hidden_input_rms_median": 1.0e-2,
            "minimum_moving_postreset_hidden_swap_action_rms_median": 5.0e-3,
            "minimum_fraction_moving_postreset_actionable": 0.95,
            "actionable_action_rms_floor": 1.0e-4,
            "maximum_x0_hidden_swap_action_abs": 0.0,
        },
        "decision_rule": {
            "wrong_control_response": (
                "All replay checks pass; hidden separation and same-observation "
                "actionability clear every frozen threshold; x=0 remains "
                "exactly deadbanded."
            ),
            "wrong_control_response_decision": (
                "SELECT_TRANSITION_CONTROL_RESCUE_FALSIFIER"
            ),
            "missing_signal_decision": (
                "SELECT_OBSERVABILITY_OR_STATE_ESTIMATION_FALSIFIER"
            ),
            "no_candidate_advancement": True,
            "no_hosted_run_earned": True,
        },
        "frozen_inputs": {
            "v1_preregistration": receipt(V1),
            "t68_postexport": receipt(T68),
            "t69_preregistration": receipt(T69_PREREG),
            "t69_nominal_result": receipt(T69_RESULT),
            "t70_condition7_result": receipt(T70_RESULT),
            "auditor": receipt(AUDITOR),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "new_simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_paired_trace_attribution": not failed,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    invalidation_basis: dict[str, Any] = {
        "schema_version": "open_duck.t71_t67_com_hidden_causal_v1_invalidation.v1",
        "status": "INVALID_T71_V1_AUDITOR_OUTPUT_ORDER",
        "v1_preregistered_contract_sha256": v1[
            "preregistered_contract_sha256"
        ],
        "reason": (
            "The v1 auditor unpacked unnamed ONNX outputs by list position; "
            "the deployed graph's output order differs from the assumed "
            "continuous_actions,h_out,previous_action_out order."
        ),
        "scope": (
            "Auditor implementation only. No T71 result was written, no "
            "simulator cell ran, and no threshold or decision rule changed."
        ),
        "correction": (
            "Request outputs by their frozen names and freeze this v2 "
            "auditor receipt before execution."
        ),
        "execution": {
            "result_written": False,
            "new_simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    invalidation_basis["invalidation_sha256"] = canonical_sha256(
        invalidation_basis, "invalidation_sha256"
    )
    INVALIDATION.write_text(
        json.dumps(
            invalidation_basis, allow_nan=False, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T71 T67 COM-hidden causal preregistration v2",
                "",
                f"- Status: `{value['status']}`",
                "- Evidence: paired T69 nominal and T70 COM-x-negative traces",
                "- New behavior cells / optimizer / Colab / robot: `0/0/0/0`",
                "- This attribution cannot advance a candidate or earn training.",
                "- v1 stopped before result; v2 corrects named ONNX output routing only.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
