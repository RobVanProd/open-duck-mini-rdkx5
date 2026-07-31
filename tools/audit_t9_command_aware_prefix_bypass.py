#!/usr/bin/env python3
"""Independently audit T9 and its reused T8 moving-cell evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t9_command_aware_prefix_bypass_preregistration.json"
RESULT = ANALYSIS / "t9_command_aware_prefix_bypass_result.json"
ORIGINAL_AUDIT = (
    ANALYSIS / "t9_command_aware_prefix_bypass_independent_audit.json"
)
AUDIT_CORRECTION = (
    ANALYSIS / "t9_command_aware_prefix_bypass_audit_correction.json"
)
AUDIT = (
    ANALYSIS / "t9_command_aware_prefix_bypass_independent_audit_v2.json"
)
MARKDOWN = (
    ANALYSIS
    / "T9_COMMAND_AWARE_PREFIX_BYPASS_INDEPENDENT_AUDIT_V2_20260726.md"
)
PITCH_INDICES = (2, 3, 4, 11, 12, 13)


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


def append_if(issues: list[str], condition: bool, label: str) -> None:
    if not condition:
        issues.append(label)


def load_audit_correction(prereg: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(AUDIT_CORRECTION.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "original_audit",
            "cause",
            "authorized_change",
            "corrected_auditor",
            "decision_invariance",
            "authority",
        )
    }
    if (
        value.get("status") != "T9_POSTOUTCOME_AUDIT_LABEL_CORRECTION"
        or canonical_sha256(basis) != value["correction_contract_sha256"]
        or value["original_audit"]["preregistered_contract_sha256"]
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("invalid T9 audit correction")
    corrected = value["corrected_auditor"]
    if (
        Path(corrected["path"]).resolve() != Path(__file__).resolve()
        or sha256(Path(__file__)) != corrected["sha256"]
    ):
        raise RuntimeError("T9 corrected auditor changed")
    return value


def longest_run(mask: np.ndarray) -> int:
    current = 0
    longest = 0
    for value in mask:
        current = current + 1 if bool(value) else 0
        longest = max(longest, current)
    return longest


def exact_readback(run: dict[str, Any]) -> bool:
    report = run.get("dynamics_override") or {}
    readback = report.get("readback") or {}
    before = np.asarray(readback.get("before"), dtype=np.float64)
    after = np.asarray(readback.get("after"), dtype=np.float64)
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [0.0, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and before.shape == after.shape == (3,)
        and np.array_equal(before, after)
    )


def audit_cell(
    prereg: dict[str, Any],
    run: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    ticks = [row["tick"] for row in rows]
    actions = np.asarray([row["action"] for row in rows], dtype=np.float32)
    observations = np.asarray(
        [row["obs_state"] for row in rows], dtype=np.float32
    )
    applied = np.asarray(
        [row["applied_target_rad"] for row in rows], dtype=np.float32
    )
    previous_in = np.asarray(
        [
            row["policy_state_input"]["previous_action"][0]
            for row in rows
        ],
        dtype=np.float32,
    )
    previous_out = np.asarray(
        [
            row["policy_state_output"]["previous_action_out"][0]
            for row in rows
        ],
        dtype=np.float32,
    )
    hidden_in = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in rows],
        dtype=np.float32,
    )
    hidden_out = np.asarray(
        [row["policy_state_output"]["h_out"][0] for row in rows],
        dtype=np.float32,
    )
    velocity = np.asarray(
        [row["local_linvel_m_s"][0] for row in rows], dtype=float
    )
    pitch = np.asarray([row["body_pitch_rad"] for row in rows], dtype=float)
    height = np.asarray([row["base_height_m"] for row in rows], dtype=float)
    tracking = np.abs(
        np.asarray([row["tracking_error_rad"] for row in rows], dtype=float)
    )
    force = np.abs(
        np.asarray([row["actuator_force_nm"] for row in rows], dtype=float)
    )
    rate = np.maximum(
        np.asarray(
            [row["sent_target_rate_excess_rad_s"] for row in rows],
            dtype=float,
        ),
        np.asarray(
            [row["conservative_rate_excess_rad_s"] for row in rows],
            dtype=float,
        ),
    )
    saturation = np.asarray(
        [row["action_saturated"] for row in rows], dtype=np.int64
    )
    response = (
        ((run.get("modes") or {}).get("fitted") or {}).get(
            "response_calibration"
        )
        or {}
    )
    zero_context_sha = hashlib.sha256(
        np.zeros((1, 64), dtype=np.float32).tobytes()
    ).hexdigest()
    handoff_checks = {
        "prefix_disabled": response.get("enabled") is False
        and response.get("calibration_ticks") == 0
        and response.get("home_return_ticks") == 0,
        "zero_context_bypass_enabled": response.get(
            "zero_context_bypass"
        )
        is True,
        "zero_context_exact": response.get("context_sha256")
        == zero_context_sha,
        "context_shape_and_finite": response.get("context_shape") == [1, 64]
        and response.get("context_finite") is True,
        "phase_reset_exact": response.get("locomotion_phase_reset")
        == [1.0, 0.0],
        "initial_hidden_zero": response.get(
            "locomotion_hidden_exact_zero"
        )
        is True
        and bool(rows)
        and np.count_nonzero(hidden_in[0]) == 0,
        "initial_previous_action_zero": response.get(
            "locomotion_previous_action_exact_zero"
        )
        is True
        and bool(rows)
        and np.count_nonzero(previous_in[0]) == 0,
        "applied_target_observer_exact": response.get(
            "applied_target_observation_matches_bridge"
        )
        is True,
        "actions_exact_zero": actions.shape == (len(rows), 14)
        and np.count_nonzero(actions) == 0,
        "recurrent_chains_exact": bool(rows)
        and np.array_equal(previous_in[1:], previous_out[:-1])
        and np.array_equal(hidden_in[1:], hidden_out[:-1]),
        "context_immutable": all(
            row.get("policy_calibration_context_sha256")
            == zero_context_sha
            for row in rows
        ),
        "graph_authoritative_no_host_delta": bool(rows)
        and all(
            row.get("policy_graph_authoritative_output") is True
            and row.get("policy_host_action_delta_max_abs") == 0.0
            for row in rows
        ),
        "full_observation_traced": observations.shape == (len(rows), 115),
        "applied_target_slot_continuity": observations.shape
        == (len(rows), 115)
        and applied.shape == (len(rows), 14)
        and np.array_equal(observations[1:, 83:97], applied[:-1]),
    }
    expected_ticks = prereg["matrix"]["duration_ticks"]
    behavior = prereg["behavior_contract"]
    core = behavior["x0_core"]
    quality = behavior["x0_replacement_quality"]
    mean_vx = float(np.mean(velocity))
    pitch_p95 = float(np.percentile(np.abs(pitch), 95))
    minimum_height = float(np.min(height))
    tracking_p95 = float(
        np.max(np.percentile(tracking[:, PITCH_INDICES], 95, axis=0))
    )
    maximum_rate = float(np.max(rate))
    saturated = int(np.count_nonzero(saturation))
    behavior_checks = {
        "ticks": len(rows) == expected_ticks
        and ticks == list(range(expected_ticks)),
        "finite": all(
            np.all(np.isfinite(value))
            for value in (
                actions,
                observations,
                velocity,
                pitch,
                height,
                tracking,
                force,
                rate,
            )
        ),
        "stationary": abs(mean_vx)
        <= core["maximum_absolute_mean_local_vx_m_s"],
        "pitch": pitch_p95 <= core["maximum_body_pitch_p95_rad"],
        "height": minimum_height >= core["minimum_base_height_m"],
        "tracking": tracking_p95
        <= quality["maximum_pitch_tracking_p95_rad"],
        "zero_rate": maximum_rate
        <= quality["maximum_rate_excess_rad_s"],
        "zero_saturation": saturated == 0,
    }
    protection = prereg["protection_contract"]
    current = force / protection["motor_constant_nm_per_a"]
    overcurrent = max(
        longest_run(
            current[:, index] > protection["overcurrent_threshold_a"]
        )
        for index in range(14)
    )
    overload = max(
        longest_run(force[:, index] > protection["overload_threshold_nm"])
        for index in range(14)
    )
    protection_pass = (
        overcurrent <= protection["pass_max_consecutive_ticks"]
        and overload <= protection["pass_max_consecutive_ticks"]
    )
    readback = exact_readback(run)
    passed = (
        all(handoff_checks.values())
        and all(behavior_checks.values())
        and protection_pass
        and readback
    )
    return {
        "passed": passed,
        "handoff_checks": handoff_checks,
        "behavior_checks": behavior_checks,
        "protection_pass": protection_pass,
        "readback_exact": readback,
        "metrics": {
            "mean_local_vx_m_s": mean_vx,
            "body_pitch_p95_rad": pitch_p95,
            "minimum_base_height_m": minimum_height,
            "pitch_tracking_p95_rad": tracking_p95,
            "maximum_rate_excess_rad_s": maximum_rate,
            "worst_strict_overcurrent_run_ticks": overcurrent,
            "worst_strict_overload_run_ticks": overload,
        },
    }


def main() -> int:
    if AUDIT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T9 audit")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit_correction = load_audit_correction(prereg)
    issues: list[str] = []
    prereg_basis = {
        key: prereg[key]
        for key in (
            "question",
            "causal_basis",
            "repository_inputs",
            "playground",
            "candidate",
            "matrix",
            "bypass_contract",
            "behavior_contract",
            "protection_contract",
            "reused_t8_evidence",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    append_if(
        issues,
        canonical_sha256(prereg_basis)
        == prereg["preregistered_contract_sha256"],
        "preregistration_canonical",
    )
    result_basis = {
        key: value
        for key, value in result.items()
        if key != "result_sha256"
    }
    append_if(
        issues,
        canonical_sha256(result_basis) == result["result_sha256"],
        "result_canonical",
    )
    for label, frozen in prereg["repository_inputs"].items():
        if label == "independent_auditor":
            corrected = audit_correction["corrected_auditor"]
            path = Path(corrected["path"])
            append_if(
                issues,
                audit_correction["original_audit"][
                    "preregistered_auditor"
                ]
                == frozen
                and path.is_file()
                and path.stat().st_size == corrected["bytes"]
                and sha256(path) == corrected["sha256"],
                "audit_corrected_repository_input",
            )
        else:
            path = Path(frozen["path"])
            append_if(
                issues,
                path.is_file()
                and path.stat().st_size == frozen["bytes"]
                and sha256(path) == frozen["sha256"],
                f"repository_input:{label}",
            )
    reused = prereg["reused_t8_evidence"]
    t8_result = json.loads(
        Path(reused["result"]["path"]).read_text(encoding="utf-8")
    )
    t8_audit = json.loads(
        Path(reused["independent_audit"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t8_failure = json.loads(
        Path(reused["failure_analysis"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    append_if(
        issues,
        sha256(Path(reused["result"]["path"]))
        == reused["result"]["sha256"]
        and t8_result["passing_cells"] == 12,
        "reused_t8_result",
    )
    append_if(
        issues,
        sha256(Path(reused["independent_audit"]["path"]))
        == reused["independent_audit"]["sha256"]
        and t8_audit["issues"] == []
        and t8_audit["passing_cells"] == 12,
        "reused_t8_audit",
    )
    append_if(
        issues,
        sha256(Path(reused["failure_analysis"]["path"]))
        == reused["failure_analysis"]["sha256"]
        and all(t8_failure["checks"].values())
        and len(t8_failure["moving_cells"]) == 12
        and all(item["green"] for item in t8_failure["moving_cells"]),
        "reused_t8_moving_cells",
    )

    checkpoint_ids = {
        item["checkpoint_id"]
        for item in prereg["candidate"]["checkpoints"]
    }
    expected_keys = {
        (checkpoint, fit)
        for checkpoint in checkpoint_ids
        for fit in prereg["matrix"]["fits"]
    }
    observed_keys = set()
    audited = []
    for block in result.get("blocks") or []:
        key = (block["checkpoint_id"], block["fit_id"])
        observed_keys.add(key)
        manifest_path = Path(block["manifest"]["path"])
        append_if(
            issues,
            manifest_path.is_file()
            and sha256(manifest_path) == block["manifest"]["sha256"],
            f"manifest:{key}",
        )
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        append_if(
            issues,
            canonical_sha256(manifest["block_contract"])
            == manifest["block_contract_sha256"],
            f"block_contract:{key}",
        )
        evaluation_path = Path(manifest["evaluation"]["path"])
        trace_path = Path(manifest["trace"]["path"])
        append_if(
            issues,
            evaluation_path.is_file()
            and sha256(evaluation_path)
            == manifest["evaluation"]["sha256"],
            f"evaluation:{key}",
        )
        append_if(
            issues,
            trace_path.is_file()
            and sha256(trace_path) == manifest["trace"]["sha256"],
            f"trace:{key}",
        )
        if not evaluation_path.is_file() or not trace_path.is_file():
            continue
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        rows = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
        ]
        recomputed = audit_cell(prereg, evaluation["run"], rows)
        append_if(
            issues,
            recomputed["passed"] == block["cell"]["cell_green"],
            f"cell_classification:{key}",
        )
        append_if(
            issues,
            recomputed["handoff_checks"]
            == block["cell"]["bypass_checks"],
            f"bypass_checks:{key}",
        )
        audited.append({"key": list(key), **recomputed})
    append_if(issues, observed_keys == expected_keys, "block_identity")
    new_green = sum(item["passed"] for item in audited)
    combined = new_green + 12
    passed = len(audited) == 4 and new_green == 4 and combined == 16
    expected_status = (
        "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
        if passed
        else "HOLD_T9_COMMAND_AWARE_PREFIX_BYPASS"
    )
    expected_decision = (
        "EARN_RESPONSE_CONDITIONED_V121_CONTINUATION_CPU_CONTRACT"
        if passed
        else "CLOSE_COMMAND_AWARE_PREFIX_BYPASS_WITHOUT_TRAINING"
    )
    append_if(
        issues,
        result.get("new_passing_cells") == new_green,
        "result_new_passing_cells",
    )
    append_if(
        issues,
        result.get("combined_passing_cells") == combined,
        "result_combined_passing_cells",
    )
    append_if(
        issues, result.get("status") == expected_status, "result_status"
    )
    append_if(
        issues,
        result.get("decision") == expected_decision,
        "result_decision",
    )
    audit_passed = not issues
    basis = {
        "schema_version": (
            "open_duck.t9_command_aware_prefix_bypass_audit.v1"
        ),
        "status": (
            "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS_INDEPENDENT_AUDIT"
            if audit_passed
            else "HOLD_T9_COMMAND_AWARE_PREFIX_BYPASS_INDEPENDENT_AUDIT"
        ),
        "result_file_sha256": sha256(RESULT),
        "result_canonical_sha256": result["result_sha256"],
        "audit_correction_contract_sha256": audit_correction[
            "correction_contract_sha256"
        ],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "audited_new_cells": len(audited),
        "new_passing_cells": new_green,
        "reused_t8_moving_cells": 12,
        "combined_passing_cells": combined,
        "classification": {
            "status": expected_status,
            "decision": expected_decision,
        },
        "issues": issues,
        "authority": {
            "training_or_hosted_compute": False,
            "robot_rdkx5_torque_motion": False,
            "gate5": False,
        },
    }
    payload = {**basis, "audit_sha256": canonical_sha256(basis)}
    AUDIT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T9 command-aware prefix-bypass independent audit",
        "",
        f"- Status: `{payload['status']}`",
        f"- New passing cells: `{payload['new_passing_cells']}/4`",
        f"- Reused T8 moving cells: `{payload['reused_t8_moving_cells']}/12`",
        f"- Combined cells: `{payload['combined_passing_cells']}/16`",
        f"- Issues: `{len(issues)}`",
        f"- Audit SHA-256: `{payload['audit_sha256']}`",
        "",
        "The auditor independently rehashed and recomputed the four new x=0 "
        "traces, context/state/action/applied-target chains, stationary and "
        "tracking gates, corrected servo-duration rules, and exact readbacks. "
        "It also revalidated the immutable audited T8 moving-cell evidence.",
        "",
        "This audit does not authorize hosted training, robot/RDK-X5 access, "
        "Gate 5, torque, motion, deployment, or grounded replay.",
    ]
    if issues:
        lines.extend(["", "## Issues", "", *[f"- {item}" for item in issues]])
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"issues={len(issues)}")
    print(f"audit_sha256={payload['audit_sha256']}")
    return 0 if audit_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
