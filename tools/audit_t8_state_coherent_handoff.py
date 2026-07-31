#!/usr/bin/env python3
"""Independently audit the completed T8 raw traces and decision."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
ABI_AMENDMENT = (
    ANALYSIS / "t8_state_coherent_handoff_abi_amendment.json"
)
RESULT = ANALYSIS / "t8_state_coherent_handoff_result.json"
ORIGINAL_AUDIT = (
    ANALYSIS / "t8_state_coherent_handoff_independent_audit.json"
)
AUDIT_CORRECTION = (
    ANALYSIS / "t8_state_coherent_handoff_audit_correction.json"
)
AUDIT = ANALYSIS / "t8_state_coherent_handoff_independent_audit_v2.json"
MARKDOWN = (
    ANALYSIS / "T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT_V2_20260726.md"
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


def load_abi_amendment(prereg: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(ABI_AMENDMENT.read_text(encoding="utf-8"))
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
    if (
        value.get("status")
        != "PREREGISTERED_T8_PREOUTCOME_ABI_ORDER_CORRECTION"
        or canonical_sha256(basis) != value["amendment_contract_sha256"]
        or value["original_preregistration"][
            "preregistered_contract_sha256"
        ]
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("invalid T8 pre-outcome ABI amendment")
    return value


def load_audit_correction(
    prereg: dict[str, Any], amendment: dict[str, Any]
) -> dict[str, Any]:
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
        value.get("status")
        != "T8_POSTOUTCOME_AUDIT_BODY_FRAME_CORRECTION"
        or canonical_sha256(basis) != value["correction_contract_sha256"]
        or value["original_audit"]["preregistered_contract_sha256"]
        != prereg["preregistered_contract_sha256"]
        or value["original_audit"]["abi_amendment_contract_sha256"]
        != amendment["amendment_contract_sha256"]
    ):
        raise RuntimeError("invalid T8 audit correction")
    corrected = value["corrected_auditor"]
    if (
        Path(corrected["path"]).resolve() != Path(__file__).resolve()
        or sha256(Path(__file__)) != corrected["sha256"]
    ):
        raise RuntimeError("T8 corrected auditor changed")
    return value


def finite_array(value: np.ndarray) -> bool:
    return bool(np.all(np.isfinite(value)))


def longest_run(mask: np.ndarray) -> int:
    longest = 0
    current = 0
    for value in mask:
        current = current + 1 if bool(value) else 0
        longest = max(longest, current)
    return longest


def trace_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"invalid T8 trace: {path}:{line_number}"
                ) from exc
            if value.get("mode") == "fitted":
                rows.append(value)
    return rows


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
        and before.shape == (3,)
        and after.shape == (3,)
        and np.array_equal(before, after)
    )


def transitions(values: np.ndarray) -> int:
    if len(values) < 2:
        return 0
    return int(np.count_nonzero(values[1:] != values[:-1]))


def audit_cell(
    prereg: dict[str, Any],
    run: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    command = float(run["command_x"])
    expected_ticks = prereg["matrix"]["duration_ticks"]
    ticks = [int(row["tick"]) for row in rows]
    actions = np.asarray([row["action"] for row in rows], dtype=np.float32)
    pitch = np.asarray([row["body_pitch_rad"] for row in rows], dtype=float)
    height = np.asarray([row["base_height_m"] for row in rows], dtype=float)
    velocity = np.asarray(
        [row["local_linvel_m_s"][0] for row in rows], dtype=float
    )
    tracking = np.abs(
        np.asarray([row["tracking_error_rad"] for row in rows], dtype=float)
    )
    force = np.abs(
        np.asarray([row["actuator_force_nm"] for row in rows], dtype=float)
    )
    sent_excess = np.asarray(
        [row["sent_target_rate_excess_rad_s"] for row in rows], dtype=float
    )
    conservative_excess = np.asarray(
        [row["conservative_rate_excess_rad_s"] for row in rows], dtype=float
    )
    saturation = np.asarray(
        [row["action_saturated"] for row in rows], dtype=np.int64
    )
    contacts = np.asarray(
        [row["foot_contacts"] for row in rows], dtype=np.int64
    )
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
    audit = (
        ((run.get("modes") or {}).get("fitted") or {}).get(
            "response_calibration"
        )
        or {}
    )
    calibration_action = np.asarray(
        audit.get("calibration_final_action"), dtype=np.float32
    )
    observer = np.asarray(
        audit.get("observer_bridge_applied_target_rad"), dtype=np.float32
    )
    handoff_observation = np.asarray(
        audit.get("locomotion_applied_target_observation_rad"),
        dtype=np.float32,
    )
    context_sha = audit.get("context_sha256")
    handoff_checks = {
        "response_enabled": audit.get("enabled") is True,
        "calibration_ticks_exact": audit.get("calibration_ticks") == 250,
        "zero_home_return_ticks": audit.get("home_return_ticks") == 0,
        "calibrator_sha_exact": audit.get("calibrator_sha256")
        == prereg["calibrator"]["sha256"],
        "context_shape": audit.get("context_shape") == [1, 64],
        "context_finite": audit.get("context_finite") is True,
        "phase_reset_exact": audit.get("locomotion_phase_reset")
        == [1.0, 0.0],
        "policy_hidden_zero": audit.get("locomotion_hidden_exact_zero")
        is True,
        "previous_action_preserved": (
            audit.get("locomotion_previous_action_matches_calibration")
            is True
        ),
        "handoff_state_preserved": audit.get("handoff_state_preserved")
        is True,
        "applied_target_observer_preserved": (
            audit.get("applied_target_observation_matches_bridge") is True
            and observer.shape == (14,)
            and handoff_observation.shape == (14,)
            and np.array_equal(observer, handoff_observation)
        ),
        "full_observation_traced": observations.shape
        == (len(rows), 115),
        "first_previous_action_matches_calibration": (
            bool(rows)
            and calibration_action.shape == (14,)
            and previous_in.shape == (len(rows), 14)
            and np.array_equal(previous_in[0], calibration_action)
        ),
        "first_hidden_zero": (
            bool(rows)
            and hidden_in.shape == (len(rows), 64)
            and np.count_nonzero(hidden_in[0]) == 0
        ),
        "recurrent_state_chains_exact": (
            bool(rows)
            and np.array_equal(previous_in[1:], previous_out[:-1])
            and np.array_equal(hidden_in[1:], hidden_out[:-1])
        ),
        "context_immutable": (
            isinstance(context_sha, str)
            and all(
                row.get("policy_calibration_context_sha256") == context_sha
                for row in rows
            )
        ),
        "graph_authoritative_no_host_delta": (
            bool(rows)
            and all(
                row.get("policy_graph_authoritative_output") is True
                and row.get("policy_host_action_delta_max_abs") == 0.0
                for row in rows
            )
        ),
        "applied_target_slot_continuity": (
            observations.shape == (len(rows), 115)
            and applied.shape == (len(rows), 14)
            and (
                len(rows) <= 1
                or np.array_equal(observations[1:, 83:97], applied[:-1])
            )
        ),
    }
    complete = len(rows) == expected_ticks and ticks == list(
        range(expected_ticks)
    )
    finite = all(
        finite_array(value)
        for value in (
            actions,
            pitch,
            height,
            velocity,
            tracking,
            force,
            sent_excess,
            conservative_excess,
            observations,
        )
    )
    mean_vx = float(np.mean(velocity)) if len(velocity) else math.nan
    pitch_p95 = (
        float(np.percentile(np.abs(pitch), 95)) if len(pitch) else math.nan
    )
    minimum_height = float(np.min(height)) if len(height) else math.nan
    tracking_p95 = (
        float(np.max(np.percentile(tracking[:, PITCH_INDICES], 95, axis=0)))
        if tracking.ndim == 2 and tracking.shape[1] == 14 and len(tracking)
        else math.nan
    )
    saturation_pct = (
        float(np.mean(np.any(saturation != 0, axis=1)) * 100.0)
        if saturation.ndim == 2 and len(saturation)
        else math.nan
    )
    max_rate = (
        float(max(np.max(sent_excess), np.max(conservative_excess)))
        if sent_excess.size and conservative_excess.size
        else math.nan
    )
    contact_counts = (
        [transitions(contacts[:, index]) for index in range(2)]
        if contacts.ndim == 2 and contacts.shape[1] >= 2
        else [0, 0]
    )
    progress = (
        float(np.sum(velocity) * 0.02) if len(velocity) else math.nan
    )
    zero = abs(command) <= 1.0e-12
    core = (
        prereg["behavior_contract"]["x0_core"]
        if zero
        else prereg["behavior_contract"]["moving_core"]
    )
    quality = (
        prereg["behavior_contract"]["x0_replacement_quality"]
        if zero
        else prereg["behavior_contract"]["moving_replacement_quality"]
    )
    behavior_checks = {
        "complete": complete,
        "finite": finite,
        "pitch": math.isfinite(pitch_p95)
        and pitch_p95 <= core["maximum_body_pitch_p95_rad"],
        "height": math.isfinite(minimum_height)
        and minimum_height >= core["minimum_base_height_m"],
        "core_saturation": math.isfinite(saturation_pct)
        and saturation_pct <= core["maximum_action_saturation_pct"],
        "tracking": math.isfinite(tracking_p95)
        and tracking_p95 <= quality["maximum_pitch_tracking_p95_rad"],
        "zero_rate_excess": max_rate
        <= quality["maximum_rate_excess_rad_s"],
        "quality_zero_saturation": saturation_pct
        <= quality["maximum_action_saturation_pct"],
    }
    if zero:
        behavior_checks["stationary"] = (
            math.isfinite(mean_vx)
            and abs(mean_vx) <= core["maximum_absolute_mean_local_vx_m_s"]
        )
    else:
        behavior_checks.update(
            {
                "positive_progress": math.isfinite(progress)
                and progress > 0.0,
                "positive_velocity": math.isfinite(mean_vx)
                and mean_vx > 0.0,
                "minimum_track_ratio": math.isfinite(mean_vx)
                and mean_vx / command >= core["minimum_track_ratio"],
                "bilateral_transitions": min(contact_counts) > 0,
            }
        )
    protection = prereg["protection_contract"]
    current = force / protection["motor_constant_nm_per_a"]
    current_runs = [
        longest_run(
            current[:, index] > protection["overcurrent_threshold_a"]
        )
        for index in range(14)
    ]
    overload_runs = [
        longest_run(force[:, index] > protection["overload_threshold_nm"])
        for index in range(14)
    ]
    protection_pass = (
        max(current_runs, default=0)
        <= protection["pass_max_consecutive_ticks"]
        and max(overload_runs, default=0)
        <= protection["pass_max_consecutive_ticks"]
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
            "rows": len(rows),
            "mean_local_vx_m_s": mean_vx,
            "body_pitch_p95_rad": pitch_p95,
            "minimum_base_height_m": minimum_height,
            "pitch_tracking_p95_rad": tracking_p95,
            "action_saturation_pct": saturation_pct,
            "maximum_rate_excess_rad_s": max_rate,
            "progress_x_m": progress,
            "contact_transitions": contact_counts,
            "worst_strict_overcurrent_run_ticks": max(
                current_runs, default=0
            ),
            "worst_strict_overload_run_ticks": max(
                overload_runs, default=0
            ),
        },
    }


def main() -> int:
    if AUDIT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T8 audit")
    issues: list[str] = []
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    amendment = load_abi_amendment(prereg)
    audit_correction = load_audit_correction(prereg, amendment)
    prereg_basis = {
        key: prereg[key]
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
    append_if(
        issues,
        canonical_sha256(prereg_basis)
        == prereg["preregistered_contract_sha256"],
        "preregistration_canonical_sha256",
    )
    result_basis = {
        key: value
        for key, value in result.items()
        if key != "result_sha256"
    }
    append_if(
        issues,
        canonical_sha256(result_basis) == result["result_sha256"],
        "result_canonical_sha256",
    )
    corrected_labels = {"runner", "worker"}
    for label, value in prereg["repository_inputs"].items():
        if label in corrected_labels:
            corrected = amendment["corrected_files"][label]
            path = Path(corrected["path"])
            append_if(
                issues,
                amendment["original_preregistration"][
                    "repository_inputs"
                ][label]
                == value
                and path.is_file()
                and path.stat().st_size == corrected["bytes"]
                and sha256(path) == corrected["sha256"],
                f"corrected_repository_input:{label}",
            )
        elif label == "independent_auditor":
            corrected = audit_correction["corrected_auditor"]
            path = Path(corrected["path"])
            append_if(
                issues,
                amendment["original_preregistration"][
                    "repository_inputs"
                ][label]
                == value
                and path.is_file()
                and path.stat().st_size == corrected["bytes"]
                and sha256(path) == corrected["sha256"],
                "audit_corrected_repository_input",
            )
        else:
            path = Path(value["path"])
            append_if(
                issues,
                path.is_file()
                and path.stat().st_size == value["bytes"]
                and sha256(path) == value["sha256"],
                f"repository_input:{label}",
            )
    append_if(
        issues,
        result.get("abi_amendment", {}).get(
            "amendment_contract_sha256"
        )
        == amendment["amendment_contract_sha256"],
        "result_abi_amendment",
    )

    checkpoint_by_id = {
        item["checkpoint_id"]: item
        for item in prereg["candidate"]["checkpoints"]
    }
    expected_keys = {
        (checkpoint_id, fit_id)
        for checkpoint_id in checkpoint_by_id
        for fit_id in prereg["matrix"]["fits"]
    }
    observed_keys: set[tuple[str, str]] = set()
    audited_cells = []
    for block in result.get("blocks") or []:
        key = (block["checkpoint_id"], block["fit_id"])
        observed_keys.add(key)
        manifest_receipt = block["manifest"]
        manifest_path = Path(manifest_receipt["path"])
        append_if(
            issues,
            manifest_path.is_file()
            and manifest_path.stat().st_size == manifest_receipt["bytes"]
            and sha256(manifest_path) == manifest_receipt["sha256"],
            f"manifest_receipt:{key}",
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
        append_if(
            issues,
            manifest["block_contract"].get("abi_amendment", {}).get(
                "amendment_contract_sha256"
            )
            == amendment["amendment_contract_sha256"],
            f"block_abi_amendment:{key}",
        )
        checkpoint = checkpoint_by_id.get(block["checkpoint_id"])
        append_if(
            issues,
            checkpoint is not None
            and manifest["block_contract"]["checkpoint"] == checkpoint,
            f"checkpoint_contract:{key}",
        )
        evaluation_path = Path(manifest["evaluation"]["path"])
        append_if(
            issues,
            evaluation_path.is_file()
            and sha256(evaluation_path)
            == manifest["evaluation"]["sha256"],
            f"evaluation_receipt:{key}",
        )
        if not evaluation_path.is_file():
            continue
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        runs = evaluation.get("runs") or []
        append_if(
            issues,
            [float(run["command_x"]) for run in runs]
            == prereg["matrix"]["commands_x_m_s"],
            f"command_order:{key}",
        )
        stored_cells = block["result"]["cells"]
        append_if(
            issues,
            len(runs) == len(stored_cells) == len(manifest["traces"]) == 4,
            f"cell_count:{key}",
        )
        for index, (run, trace_receipt, stored) in enumerate(
            zip(
                runs,
                manifest["traces"],
                stored_cells,
                strict=True,
            )
        ):
            trace_path = Path(trace_receipt["path"])
            append_if(
                issues,
                trace_path.is_file()
                and sha256(trace_path) == trace_receipt["sha256"],
                f"trace_receipt:{key}:{index}",
            )
            if not trace_path.is_file():
                continue
            recomputed = audit_cell(
                prereg, run, trace_rows(trace_path)
            )
            append_if(
                issues,
                recomputed["passed"] == stored["cell_green"],
                f"cell_classification:{key}:{index}",
            )
            append_if(
                issues,
                recomputed["handoff_checks"]
                == stored["handoff"]["checks"],
                f"handoff_checks:{key}:{index}",
            )
            audited_cells.append(
                {
                    "checkpoint_id": key[0],
                    "fit_id": key[1],
                    "command_x_m_s": float(run["command_x"]),
                    **recomputed,
                }
            )

    append_if(
        issues,
        observed_keys == expected_keys,
        "exact_block_identity",
    )
    passing_cells = sum(item["passed"] for item in audited_cells)
    all_green = (
        len(audited_cells) == prereg["matrix"]["total_cells"]
        and passing_cells == prereg["matrix"]["total_cells"]
    )
    expected_status = (
        "PASS_T8_STATE_COHERENT_HANDOFF"
        if all_green
        else "HOLD_T8_STATE_COHERENT_HANDOFF"
    )
    expected_decision = (
        "EARN_RESPONSE_CONDITIONED_V121_CONTINUATION_CPU_CONTRACT"
        if all_green
        else "CLOSE_DIRECT_STATE_COHERENT_V121_HANDOFF_WITHOUT_TRAINING"
    )
    append_if(
        issues,
        result.get("completed_cells") == len(audited_cells),
        "result_completed_cells",
    )
    append_if(
        issues,
        result.get("passing_cells") == passing_cells,
        "result_passing_cells",
    )
    append_if(
        issues,
        result.get("status") == expected_status,
        "result_status",
    )
    append_if(
        issues,
        result.get("decision") == expected_decision,
        "result_decision",
    )
    passed = not issues
    basis = {
        "schema_version": (
            "open_duck.t8_state_coherent_handoff_independent_audit.v1"
        ),
        "status": (
            "PASS_T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT"
            if passed
            else "HOLD_T8_STATE_COHERENT_HANDOFF_INDEPENDENT_AUDIT"
        ),
        "result_file_sha256": sha256(RESULT),
        "result_canonical_sha256": result["result_sha256"],
        "audit_correction_contract_sha256": audit_correction[
            "correction_contract_sha256"
        ],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "audited_blocks": len(observed_keys),
        "audited_cells": len(audited_cells),
        "passing_cells": passing_cells,
        "independent_classification": {
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
        "# T8 state-coherent handoff independent audit",
        "",
        f"- Status: `{payload['status']}`",
        f"- Audited blocks: `{payload['audited_blocks']}`",
        f"- Audited cells: `{payload['audited_cells']}`",
        f"- Passing cells: `{payload['passing_cells']}`",
        f"- Issues: `{len(issues)}`",
        f"- Audit SHA-256: `{payload['audit_sha256']}`",
        "",
        "The auditor independently rehashed the preregistration, result, "
        "manifests, evaluations, and all JSONL traces; rebuilt the behavior, "
        "servo-duration, recurrent-chain, context, applied-target-slot, and "
        "nominal-readback checks; and reclassified the final decision.",
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
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
