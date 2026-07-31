#!/usr/bin/env python3
"""Independently audit T7 preregistration, raw traces, and published result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t7_universal_response_support_preregistration.json"
RESULT = ANALYSIS / "t7_universal_response_support_result.json"
AUDIT = ANALYSIS / "t7_universal_response_support_independent_audit.json"
MARKDOWN = (
    ANALYSIS / "T7_UNIVERSAL_RESPONSE_SUPPORT_INDEPENDENT_AUDIT_20260725.md"
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


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float32).tobytes()
    ).hexdigest()


def longest_per_joint(mask: np.ndarray) -> list[int]:
    current = np.zeros(14, dtype=np.int64)
    longest = np.zeros(14, dtype=np.int64)
    for row in mask:
        current = np.where(row, current + 1, 0)
        longest = np.maximum(longest, current)
    return longest.astype(int).tolist()


def trace_records(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def close(left: Any, right: Any, tolerance: float = 1.0e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def append_if(issues: list[str], condition: bool, message: str) -> None:
    if not condition:
        issues.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T7 audit requires --execute")
    if AUDIT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T7 independent audit")

    issues: list[str] = []
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg_basis = {
        key: prereg[key]
        for key in (
            "repository_inputs",
            "playground",
            "frozen_policy",
            "causal_audit",
            "matrix",
            "behavior_contract",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    append_if(
        issues,
        canonical_sha256(prereg_basis) == prereg["preregistered_contract_sha256"],
        "preregistration canonical hash mismatch",
    )
    result_basis = {
        key: value for key, value in result.items() if key != "result_sha256"
    }
    append_if(
        issues,
        canonical_sha256(result_basis) == result["result_sha256"],
        "result canonical hash mismatch",
    )
    append_if(
        issues,
        result["preregistered_contract_sha256"]
        == prereg["preregistered_contract_sha256"],
        "result points to a different preregistration",
    )
    for name, receipt in prereg["repository_inputs"].items():
        path = Path(receipt["path"])
        append_if(
            issues,
            path.is_file()
            and path.stat().st_size == receipt["bytes"]
            and sha256(path) == receipt["sha256"],
            f"repository input mismatch: {name}",
        )
    policy = Path(prereg["frozen_policy"]["path"])
    append_if(
        issues,
        policy.is_file()
        and policy.stat().st_size == prereg["frozen_policy"]["bytes"]
        and sha256(policy) == prereg["frozen_policy"]["sha256"],
        "frozen policy mismatch",
    )
    playground = Path(prereg["playground"]["path"])
    for relative, expected in prereg["playground"]["required_file_sha256"].items():
        path = playground / relative
        append_if(
            issues,
            path.is_file() and sha256(path) == expected,
            f"Playground file mismatch: {relative}",
        )
    for name, receipt in prereg["playground"]["composition_manifests"].items():
        path = Path(receipt["path"])
        append_if(
            issues,
            path.is_file() and sha256(path) == receipt["sha256"],
            f"composition manifest mismatch: {name}",
        )

    import onnx
    import onnxruntime as ort

    session = ort.InferenceSession(str(policy), providers=["CPUExecutionProvider"])
    observed_inputs = {item.name: item.shape for item in session.get_inputs()}
    observed_outputs = {item.name: item.shape for item in session.get_outputs()}
    append_if(
        issues,
        observed_inputs == prereg["frozen_policy"]["abi"]["inputs"],
        "policy input ABI mismatch",
    )
    append_if(
        issues,
        observed_outputs == prereg["frozen_policy"]["abi"]["outputs"],
        "policy output ABI mismatch",
    )
    model = onnx.load(policy)
    initializer = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item), dtype=np.float32)
        for item in model.graph.initializer
    }
    delta = initializer.get("cal_max_action_delta")
    append_if(
        issues,
        delta is not None and delta.shape == (1, 14),
        "cal_max_action_delta missing or wrong shape",
    )
    if delta is None or delta.shape != (1, 14):
        raise RuntimeError("cannot independently audit the action chain")
    delta = delta[0]
    target = np.asarray(
        prereg["frozen_policy"]["universal_raw_action"], dtype=np.float32
    )

    manifests = result["block_manifests"]
    append_if(
        issues,
        len(manifests) == prereg["matrix"]["cells"],
        "block manifest count mismatch",
    )
    manifest_by_key: dict[tuple[str, str, int], dict[str, Any]] = {}
    for manifest in manifests:
        contract = manifest["block_contract"]
        key = (
            contract["configuration"]["id"],
            contract["fit_id"],
            contract["repeat"],
        )
        manifest_by_key[key] = manifest
        append_if(
            issues,
            canonical_sha256(contract) == manifest["block_contract_sha256"],
            f"block contract hash mismatch: {key}",
        )
        for kind in ("evaluation", "trace", "stdout"):
            receipt = manifest[kind]
            path = Path(receipt["path"])
            append_if(
                issues,
                path.is_file() and sha256(path) == receipt["sha256"],
                f"{kind} receipt mismatch: {key}",
            )

    cell_by_key = {
        (cell["configuration_id"], cell["fit_id"], cell["repeat"]): cell
        for cell in result["cells"]
    }
    append_if(
        issues,
        len(cell_by_key) == prereg["matrix"]["cells"],
        "result cell identity count mismatch",
    )
    recomputed: dict[tuple[str, str, int], dict[str, Any]] = {}
    thresholds = prereg["behavior_contract"]["all_cells"]
    protection = prereg["behavior_contract"]["servo_protection"]
    for configuration in prereg["matrix"]["configurations"]:
        for fit_id in prereg["matrix"]["fits"]:
            for repeat in prereg["matrix"]["repeats"]:
                key = (configuration["id"], fit_id, repeat)
                append_if(issues, key in manifest_by_key, f"missing manifest: {key}")
                append_if(issues, key in cell_by_key, f"missing result cell: {key}")
                if key not in manifest_by_key or key not in cell_by_key:
                    continue
                manifest = manifest_by_key[key]
                stored = cell_by_key[key]
                records = trace_records(Path(manifest["trace"]["path"]))
                evaluation = json.loads(
                    Path(manifest["evaluation"]["path"]).read_text(encoding="utf-8")
                )
                ticks_exact = len(records) == prereg["matrix"]["duration_ticks"] and all(
                    row["tick"] == tick for tick, row in enumerate(records)
                )
                actions = np.asarray(
                    [row["action"] for row in records], dtype=np.float32
                )
                previous_in = np.asarray(
                    [
                        row["policy_state_input"]["previous_action"][0]
                        for row in records
                    ],
                    dtype=np.float32,
                )
                previous_out = np.asarray(
                    [
                        row["policy_state_output"]["previous_action_out"][0]
                        for row in records
                    ],
                    dtype=np.float32,
                )
                hidden_in = np.asarray(
                    [row["policy_state_input"]["h_in"][0] for row in records],
                    dtype=np.float32,
                )
                hidden_out = np.asarray(
                    [row["policy_state_output"]["h_out"][0] for row in records],
                    dtype=np.float32,
                )
                expected_actions = []
                previous = np.zeros(14, dtype=np.float32)
                for _ in records:
                    lower = np.maximum(previous - delta, -1.0)
                    upper = np.minimum(previous + delta, 1.0)
                    expected = np.maximum(np.minimum(target, upper), lower)
                    expected_actions.append(expected.copy())
                    previous = expected
                exact_chain = bool(
                    np.array_equal(
                        actions, np.asarray(expected_actions, dtype=np.float32)
                    )
                    and np.array_equal(previous_out, actions)
                    and np.array_equal(previous_in[0], np.zeros(14, np.float32))
                    and np.array_equal(previous_in[1:], previous_out[:-1])
                    and np.array_equal(hidden_in[0], np.zeros(64, np.float32))
                    and np.array_equal(hidden_in[1:], hidden_out[:-1])
                )
                height = np.asarray(
                    [row["base_height_m"] for row in records], dtype=float
                )
                vx = np.asarray(
                    [row["local_linvel_m_s"][0] for row in records], dtype=float
                )
                pitch = np.asarray(
                    [row["body_pitch_rad"] for row in records], dtype=float
                )
                saturation = np.asarray(
                    [row["action_saturated"] for row in records], dtype=np.int64
                )
                sent_excess = np.asarray(
                    [row["sent_target_rate_excess_rad_s"] for row in records],
                    dtype=float,
                )
                conservative_excess = np.asarray(
                    [row["conservative_rate_excess_rad_s"] for row in records],
                    dtype=float,
                )
                force = np.abs(
                    np.asarray(
                        [row["actuator_force_nm"] for row in records], dtype=float
                    )
                )
                current = force / protection["motor_constant_nm_per_a"]
                current_run = longest_per_joint(
                    current > protection["strict_overcurrent_threshold_a"]
                )
                overload_run = longest_per_joint(
                    force > protection["strict_overload_threshold_nm"]
                )
                runs = evaluation.get("runs") or []
                termination = (
                    None
                    if len(runs) != 1
                    else (runs[0].get("emergence") or {}).get(
                        "termination_reason"
                    )
                )
                dynamics = None if len(runs) != 1 else runs[0].get(
                    "dynamics_override"
                )
                readback = {} if dynamics is None else dynamics.get("readback") or {}
                before = np.asarray(readback.get("before"), dtype=float)
                after = np.asarray(readback.get("after"), dtype=float)
                offset = np.asarray(
                    configuration["override"]["torso_com_offset_m"], dtype=float
                )
                readback_exact = bool(
                    dynamics is not None
                    and dynamics.get("value")
                    == configuration["override"]["torso_com_offset_m"]
                    and readback.get("body_id") == 2
                    and readback.get("body_name") == "trunk_assembly"
                    and before.shape == (3,)
                    and after.shape == (3,)
                    and np.array_equal(after - before, offset)
                )
                context = hidden_out[prereg["matrix"]["response_context_tick"]]
                checks = {
                    "ticks_exact": ticks_exact,
                    "duration_complete": termination == "duration_complete",
                    "all_values_finite": bool(
                        np.all(np.isfinite(actions))
                        and np.all(np.isfinite(hidden_out))
                        and np.all(np.isfinite(height))
                        and np.all(np.isfinite(vx))
                        and np.all(np.isfinite(pitch))
                        and np.all(np.isfinite(force))
                    ),
                    "action_and_state_chains_exact": exact_chain,
                    "host_action_delta_zero": all(
                        row["policy_host_action_delta_max_abs"] == 0.0
                        for row in records
                    ),
                    "model_com_readback_exact": readback_exact,
                    "minimum_base_height": float(np.min(height))
                    >= thresholds["minimum_base_height_m"],
                    "absolute_mean_local_vx": abs(float(np.mean(vx)))
                    <= thresholds["maximum_absolute_mean_local_vx_m_s"],
                    "body_pitch_p95": float(np.percentile(np.abs(pitch), 95))
                    <= thresholds["maximum_body_pitch_p95_rad"],
                    "zero_saturation": int(np.count_nonzero(saturation)) == 0,
                    "zero_sent_rate_excess": float(np.max(sent_excess)) == 0.0,
                    "zero_conservative_rate_excess": float(
                        np.max(conservative_excess)
                    )
                    == 0.0,
                    "corrected_overcurrent_duration": max(current_run)
                    <= protection["maximum_consecutive_ticks"],
                    "corrected_overload_duration": max(overload_run)
                    <= protection["maximum_consecutive_ticks"],
                    "context_finite": bool(np.all(np.isfinite(context))),
                }
                metrics = {
                    "minimum_base_height_m": float(np.min(height)),
                    "mean_local_vx_m_s": float(np.mean(vx)),
                    "body_pitch_p95_rad": float(
                        np.percentile(np.abs(pitch), 95)
                    ),
                    "maximum_abs_body_pitch_rad": float(np.max(np.abs(pitch))),
                    "action_saturation_pct": float(np.mean(saturation) * 100.0),
                    "maximum_sent_rate_excess_rad_s": float(np.max(sent_excess)),
                    "maximum_conservative_rate_excess_rad_s": float(
                        np.max(conservative_excess)
                    ),
                    "maximum_torque_nm_diagnostic": float(np.max(force)),
                    "maximum_current_a_diagnostic": float(np.max(current)),
                    "maximum_overcurrent_run_ticks": max(current_run),
                    "maximum_overload_run_ticks": max(overload_run),
                    "per_joint_overcurrent_run_ticks": current_run,
                    "per_joint_overload_run_ticks": overload_run,
                }
                append_if(
                    issues,
                    stored["checks"] == checks,
                    f"stored checks differ from raw trace: {key}",
                )
                for name, observed in metrics.items():
                    expected = stored["metrics"][name]
                    if isinstance(observed, list):
                        equal = observed == expected
                    elif isinstance(observed, int):
                        equal = observed == expected
                    else:
                        equal = close(observed, expected)
                    append_if(
                        issues,
                        equal,
                        f"stored metric differs: {key} {name}",
                    )
                append_if(
                    issues,
                    stored["response_context_sha256"] == array_sha256(context),
                    f"context hash differs: {key}",
                )
                append_if(
                    issues,
                    stored["hidden_trace_sha256"] == array_sha256(hidden_out),
                    f"hidden trace hash differs: {key}",
                )
                append_if(
                    issues,
                    stored["action_trace_sha256"] == array_sha256(actions),
                    f"action trace hash differs: {key}",
                )
                append_if(
                    issues,
                    stored["pass"] == all(checks.values()),
                    f"cell classification differs: {key}",
                )
                recomputed[key] = {
                    "context": context,
                    "context_sha256": array_sha256(context),
                    "hidden_sha256": array_sha256(hidden_out),
                    "trace_sha256": sha256(Path(manifest["trace"]["path"])),
                    "pass": all(checks.values()),
                }

    repeatability = []
    separation = []
    signal = prereg["behavior_contract"]["response_signal"]
    for configuration in prereg["matrix"]["configurations"]:
        for fit_id in prereg["matrix"]["fits"]:
            first = recomputed[(configuration["id"], fit_id, 0)]
            second = recomputed[(configuration["id"], fit_id, 1)]
            item = {
                "configuration_id": configuration["id"],
                "fit_id": fit_id,
                "trace_sha256_equal": (
                    first["trace_sha256"] == second["trace_sha256"]
                ),
                "context_sha256_equal": (
                    first["context_sha256"] == second["context_sha256"]
                ),
                "hidden_trace_sha256_equal": (
                    first["hidden_sha256"] == second["hidden_sha256"]
                ),
            }
            repeatability.append(item)
    for fit_id in prereg["matrix"]["fits"]:
        # The result contract serializes float32 contexts, then promotes those
        # saved values to float64 before computing separation. Reproduce that
        # representation boundary independently instead of subtracting in
        # float32 and comparing different last-bit rounding.
        nominal = recomputed[("NOMINAL", fit_id, 0)]["context"].astype(np.float64)
        negative = recomputed[("TORSO_COM_X_NEG", fit_id, 0)]["context"].astype(
            np.float64
        )
        positive = recomputed[("TORSO_COM_X_POS", fit_id, 0)]["context"].astype(
            np.float64
        )
        signed = float(np.max(np.abs(negative - positive)))
        nominal_negative = float(np.max(np.abs(nominal - negative)))
        nominal_positive = float(np.max(np.abs(nominal - positive)))
        separation.append(
            {
                "fit_id": fit_id,
                "signed_endpoint_linf": signed,
                "nominal_to_negative_linf": nominal_negative,
                "nominal_to_positive_linf": nominal_positive,
                "signed_endpoint_pass": (
                    signed
                    >= signal[
                        "minimum_signed_com_endpoint_linf_separation_per_fit"
                    ]
                ),
                "nominal_to_negative_pass": (
                    nominal_negative >= signal["nominal_difference_floor_linf"]
                ),
                "nominal_to_positive_pass": (
                    nominal_positive >= signal["nominal_difference_floor_linf"]
                ),
            }
        )
    response_evidence = {
        "repeatability": repeatability,
        "separation": separation,
    }
    response_checks = {
        "all_repeat_traces_bit_exact": all(
            item["trace_sha256_equal"] for item in repeatability
        ),
        "all_repeat_contexts_bit_exact": all(
            item["context_sha256_equal"] for item in repeatability
        ),
        "all_repeat_hidden_traces_bit_exact": all(
            item["hidden_trace_sha256_equal"] for item in repeatability
        ),
        "all_signed_endpoint_separations_pass": all(
            item["signed_endpoint_pass"] for item in separation
        ),
        "all_nominal_endpoint_separations_pass": all(
            item["nominal_to_negative_pass"] and item["nominal_to_positive_pass"]
            for item in separation
        ),
    }
    global_checks = {
        "exact_cell_count": len(recomputed) == prereg["matrix"]["cells"],
        "all_cells_pass": all(item["pass"] for item in recomputed.values()),
        **response_checks,
    }
    append_if(
        issues,
        result["response_evidence"] == response_evidence,
        "stored response evidence differs from raw traces",
    )
    append_if(
        issues,
        result["global_checks"] == global_checks,
        "stored global checks differ from independent audit",
    )
    passed = not issues
    expected_status = (
        "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
        if all(global_checks.values())
        else "HOLD_T7_UNIVERSAL_RESPONSE_SUPPORT"
    )
    expected_decision = (
        "EARN_STATE_COHERENT_SUPPORT_TO_LOCOMOTION_CPU_SCREEN"
        if all(global_checks.values())
        else "CLOSE_V91_V96_CURRENT_STACK_TRANSFER"
    )
    append_if(
        issues,
        result["status"] == expected_status,
        "stored status differs from independent classification",
    )
    append_if(
        issues,
        result["decision"] == expected_decision,
        "stored decision differs from independent classification",
    )
    passed = not issues
    audit_basis = {
        "schema_version": "open_duck.t7_universal_response_support_audit.v1",
        "status": (
            "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT_INDEPENDENT_AUDIT"
            if passed
            else "HOLD_T7_UNIVERSAL_RESPONSE_SUPPORT_INDEPENDENT_AUDIT"
        ),
        "result_sha256": sha256(RESULT),
        "result_canonical_sha256": result["result_sha256"],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "audited_cells": len(recomputed),
        "global_checks": global_checks,
        "response_evidence": response_evidence,
        "issues": issues,
        "authority": {
            "training_or_hosted_compute": False,
            "robot_rdkx5_torque_motion": False,
            "gate5": False,
        },
    }
    audit = {**audit_basis, "audit_sha256": canonical_sha256(audit_basis)}
    AUDIT.write_text(
        json.dumps(audit, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T7 universal response-support independent audit",
        "",
        f"- Status: `{audit['status']}`",
        f"- Audited cells: `{audit['audited_cells']}`",
        f"- Issues: `{len(issues)}`",
        f"- Audit SHA-256: `{audit['audit_sha256']}`",
        f"- Result file SHA-256: `{audit['result_sha256']}`",
        "",
        "The auditor independently rehashed every frozen input, manifest, "
        "evaluation, stdout file, and JSONL trace; rebuilt all action/state "
        "chains and support/protection metrics; and recomputed repeatability, "
        "context separation, cell classifications, and the final decision.",
        "",
        "This audit does not authorize hosted training, robot/RDK-X5 access, "
        "Gate 5, torque, motion, or deployment.",
    ]
    if issues:
        lines.extend(["", "## Issues", "", *[f"- {issue}" for issue in issues]])
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(audit["status"])
    print(f"issues={len(issues)}")
    print(f"audit_sha256={audit['audit_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
