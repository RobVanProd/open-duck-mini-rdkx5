#!/usr/bin/env python3
"""Independently audit the completed T6 robustness screen.

This module intentionally does not import the T6 runner.  It reconstructs the
gate from the preregistration, evaluation JSON, block manifests, and raw JSONL
traces so a runner-side aggregation defect cannot validate its own result.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
DEFAULT_PREREG = (
    ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
)
DEFAULT_RESULT = ANALYSIS / "t6_corrected_robustness_screen_result.json"
DEFAULT_AUDIT = (
    ANALYSIS / "t6_corrected_robustness_screen_independent_audit.json"
)
DEFAULT_MARKDOWN = (
    ANALYSIS / "T6_CORRECTED_ROBUSTNESS_SCREEN_INDEPENDENT_AUDIT_20260725.md"
)


def file_sha256(path: Path) -> str:
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


def finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def longest_true_run(values: list[bool]) -> int:
    best = 0
    current = 0
    for value in values:
        if value:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def same_number(left: Any, right: Any, tolerance: float = 1.0e-12) -> bool:
    return (
        finite(left)
        and finite(right)
        and math.isclose(
            float(left),
            float(right),
            rel_tol=tolerance,
            abs_tol=tolerance,
        )
    )


def same_value(left: Any, right: Any) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            same_value(left[key], right[key]) for key in left
        )
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            same_value(a, b) for a, b in zip(left, right, strict=True)
        )
    if finite(left) and finite(right):
        return same_number(left, right)
    return left == right


def require(
    condition: bool,
    issue: str,
    issues: list[str],
) -> bool:
    if not condition:
        issues.append(issue)
    return condition


def preregistration_contract_sha256(prereg: dict[str, Any]) -> str:
    keys = (
        "repository_inputs",
        "candidate_pairs",
        "playground",
        "condition",
        "matrix",
        "behavior_contract",
        "protection_contract",
        "decision_rule",
        "execution_contract",
    )
    return canonical_sha256({key: prereg[key] for key in keys})


def trace_metrics(
    path: Path,
    contract: dict[str, Any],
    issues: list[str],
) -> dict[str, Any]:
    ticks: list[int] = []
    torques: list[list[float]] = []
    excesses: list[list[float]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            row = json.loads(line)
            if row.get("mode") != "fitted":
                continue
            ticks.append(int(row["tick"]))
            torque = row.get("actuator_force_nm")
            excess = row.get("conservative_rate_excess_rad_s")
            require(
                isinstance(torque, list)
                and len(torque) == 14
                and all(finite(value) for value in torque),
                f"{path}:line{line_number}:invalid_torque_vector",
                issues,
            )
            require(
                isinstance(excess, list)
                and len(excess) == 14
                and all(finite(value) for value in excess),
                f"{path}:line{line_number}:invalid_rate_vector",
                issues,
            )
            torques.append([abs(float(value)) for value in torque])
            excesses.append([float(value) for value in excess])
    require(bool(torques), f"{path}:no_fitted_rows", issues)
    if not torques:
        return {}

    constant = float(contract["motor_constant_nm_per_a"])
    current = [
        [value / constant for value in one_tick]
        for one_tick in torques
    ]
    overcurrent = max(
        longest_true_run(
            [
                one_tick[joint]
                > float(contract["overcurrent_threshold_a"])
                for one_tick in current
            ]
        )
        for joint in range(14)
    )
    overload = max(
        longest_true_run(
            [
                one_tick[joint]
                > float(contract["overload_threshold_nm"])
                for one_tick in torques
            ]
        )
        for joint in range(14)
    )
    force_limit = float(contract["simulator_force_limit_abs_nm"])
    force_tolerance = float(contract["force_limit_tolerance_nm"])
    return {
        "sha256": file_sha256(path),
        "rows": len(ticks),
        "ticks_contiguous_from_zero": ticks == list(range(len(ticks))),
        "worst_peak_torque_nm_diagnostic": max(
            value for one_tick in torques for value in one_tick
        ),
        "worst_peak_current_a_diagnostic": max(
            value for one_tick in current for value in one_tick
        ),
        "worst_strict_overcurrent_run_ticks": overcurrent,
        "worst_strict_overload_run_ticks": overload,
        "simulator_force_limit_hit_ticks_diagnostic": sum(
            abs(value - force_limit) <= force_tolerance
            for one_tick in torques
            for value in one_tick
        ),
        "maximum_full_measured_vector_excess_rad_s": max(
            value for one_tick in excesses for value in one_tick
        ),
        "duration_protection_pass": (
            overcurrent <= int(contract["pass_max_consecutive_ticks"])
            and overload <= int(contract["pass_max_consecutive_ticks"])
        ),
    }


def evaluation_behavior(run: dict[str, Any]) -> dict[str, Any]:
    fitted = (run.get("modes") or {}).get("fitted") or {}
    emergence = run.get("emergence") or {}
    metrics = ((run.get("candidate_gate") or {}).get("metrics") or {})
    command = float(run["command_x"])
    mean_vx = emergence.get("mean_velocity_x_m_s")
    return {
        "command_x_m_s": command,
        "samples": int(fitted.get("samples") or 0),
        "termination_reason": emergence.get("termination_reason"),
        "evaluator_candidate_gate_status_diagnostic": (
            (run.get("candidate_gate") or {}).get("status")
        ),
        "emergence_pass": bool(emergence.get("pass")),
        "left_contact_transitions": int(
            emergence.get("left_contact_transition_count") or 0
        ),
        "right_contact_transitions": int(
            emergence.get("right_contact_transition_count") or 0
        ),
        "mean_local_vx_m_s": mean_vx,
        "track_ratio": (
            float(mean_vx) / command
            if command > 0.0 and finite(mean_vx)
            else None
        ),
        "body_pitch_p95_rad": metrics.get(
            "max_abs_body_pitch_p95_rad"
        ),
        "minimum_base_height_m": metrics.get("min_base_height_m"),
        "pitch_tracking_p95_rad": metrics.get(
            "max_pitch_tracking_p95_rad"
        ),
        "action_saturation_pct": metrics.get(
            "max_action_saturation_pct"
        ),
        "p95_rate_excess_rad_s": metrics.get(
            "max_sent_target_velocity_limit_excess_rad_s"
        ),
        "instant_rate_excess_rad_s": metrics.get(
            "max_sent_target_velocity_max_limit_excess_rad_s"
        ),
    }


def classify_behavior(
    row: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    zero = abs(float(row["command_x_m_s"])) <= 1.0e-12
    core = contract["x0_core"] if zero else contract["moving_core"]
    quality = (
        contract["x0_replacement_quality"]
        if zero
        else contract["moving_replacement_quality"]
    )
    core_checks = {
        "samples": row["samples"] == int(core["samples"]),
        "duration": row["termination_reason"] == "duration_complete",
        "finite_mean_vx": finite(row["mean_local_vx_m_s"]),
        "body_pitch": finite(row["body_pitch_p95_rad"])
        and float(row["body_pitch_p95_rad"])
        <= float(core["maximum_body_pitch_p95_rad"]),
        "height": finite(row["minimum_base_height_m"])
        and float(row["minimum_base_height_m"])
        >= float(core["minimum_base_height_m"]),
        "saturation": finite(row["action_saturation_pct"])
        and float(row["action_saturation_pct"])
        <= float(core["maximum_action_saturation_pct"]),
    }
    if zero:
        core_checks["zero_velocity"] = (
            finite(row["mean_local_vx_m_s"])
            and abs(float(row["mean_local_vx_m_s"]))
            <= float(core["maximum_absolute_mean_local_vx_m_s"])
        )
    else:
        core_checks.update(
            {
                "emergence": bool(row["emergence_pass"]),
                "bilateral_transitions": (
                    int(row["left_contact_transitions"]) > 0
                    and int(row["right_contact_transitions"]) > 0
                ),
                "positive_velocity": finite(row["mean_local_vx_m_s"])
                and float(row["mean_local_vx_m_s"]) > 0.0,
                "minimum_track_ratio": finite(row["track_ratio"])
                and float(row["track_ratio"])
                >= float(core["minimum_track_ratio"]),
            }
        )
    quality_checks = {
        "tracking": finite(row["pitch_tracking_p95_rad"])
        and float(row["pitch_tracking_p95_rad"])
        <= float(quality["maximum_pitch_tracking_p95_rad"]),
        "p95_rate": finite(row["p95_rate_excess_rad_s"])
        and float(row["p95_rate_excess_rad_s"])
        <= float(quality["maximum_rate_excess_rad_s"]),
        "instant_rate": finite(row["instant_rate_excess_rad_s"])
        and float(row["instant_rate_excess_rad_s"])
        <= float(quality["maximum_rate_excess_rad_s"]),
        "zero_saturation": finite(row["action_saturation_pct"])
        and float(row["action_saturation_pct"])
        <= float(quality["maximum_action_saturation_pct"]),
    }
    return {
        **row,
        "core_checks": core_checks,
        "replacement_quality_checks": quality_checks,
        "core_pass": all(core_checks.values()),
        "replacement_quality_pass": all(quality_checks.values()),
    }


def exact_override_readback(
    report: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    if report.get("enabled") is not True:
        return False
    key, value = next(iter(expected.items()))
    readback = report.get("readback")
    if (
        report.get("key") != key
        or report.get("value") != value
        or not isinstance(readback, dict)
    ):
        return False
    before = readback.get("before")
    after = readback.get("after")
    if (
        not isinstance(before, list)
        or not isinstance(after, list)
        or len(before) != len(value)
        or len(after) != len(value)
    ):
        return False
    return all(
        same_number(float(after_item) - float(before_item), expected_item)
        for before_item, after_item, expected_item in zip(
            before,
            after,
            value,
            strict=True,
        )
    )


def recompute_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    cells = [
        cell
        for block in candidate["blocks"]
        for cell in block["result"]["cells"]
    ]
    moving = [
        cell
        for cell in cells
        if float(cell["behavior"]["command_x_m_s"]) > 0.0
    ]
    return {
        "completed_cells": len(cells),
        "green_cells": sum(bool(cell["cell_green"]) for cell in cells),
        "all_blocks_green": (
            len(candidate["blocks"]) == 4
            and all(
                bool(block["result"]["block_green"])
                for block in candidate["blocks"]
            )
        ),
        "worst_tracking_p95_rad": max(
            float(cell["behavior"]["pitch_tracking_p95_rad"])
            for cell in cells
        ),
        "minimum_moving_vx_m_s": min(
            float(cell["behavior"]["mean_local_vx_m_s"])
            for cell in moving
        ),
        "minimum_moving_track_ratio": min(
            float(cell["behavior"]["track_ratio"]) for cell in moving
        ),
        "worst_strict_overcurrent_run_ticks": max(
            int(cell["trace"]["worst_strict_overcurrent_run_ticks"])
            for cell in cells
        ),
        "worst_strict_overload_run_ticks": max(
            int(cell["trace"]["worst_strict_overload_run_ticks"])
            for cell in cells
        ),
        "worst_peak_torque_nm_diagnostic": max(
            float(cell["trace"]["worst_peak_torque_nm_diagnostic"])
            for cell in cells
        ),
        "worst_peak_current_a_diagnostic": max(
            float(cell["trace"]["worst_peak_current_a_diagnostic"])
            for cell in cells
        ),
        "simulator_force_limit_hit_ticks_diagnostic": sum(
            int(
                cell["trace"][
                    "simulator_force_limit_hit_ticks_diagnostic"
                ]
            )
            for cell in cells
        ),
    }


def audit(
    result_path: Path = DEFAULT_RESULT,
    prereg_path: Path = DEFAULT_PREREG,
) -> dict[str, Any]:
    issues: list[str] = []
    result_path = result_path.resolve()
    prereg_path = prereg_path.resolve()
    result = json.loads(result_path.read_text(encoding="utf-8"))
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    cache_root = Path(result["cache_root"])

    computed_prereg_contract = preregistration_contract_sha256(prereg)
    require(
        computed_prereg_contract
        == prereg.get("preregistered_contract_sha256"),
        "preregistration_contract_sha256",
        issues,
    )
    require(
        result.get("preregistered_contract_sha256")
        == computed_prereg_contract,
        "result_preregistration_contract_sha256",
        issues,
    )
    result_basis = copy.deepcopy(result)
    recorded_result_sha = result_basis.pop("result_sha256", None)
    computed_result_sha = canonical_sha256(result_basis)
    require(
        recorded_result_sha == computed_result_sha,
        "result_canonical_sha256",
        issues,
    )

    expected_candidates = prereg["candidate_pairs"]
    result_candidates = result.get("candidates") or []
    require(
        [item["candidate_id"] for item in result_candidates]
        == [item["candidate_id"] for item in expected_candidates],
        "candidate_order",
        issues,
    )

    manifest_count = 0
    evaluation_count = 0
    trace_count = 0
    readback_count = 0
    cell_count = 0
    green_cell_count = 0
    manifest_file_hashes: list[dict[str, Any]] = []
    candidate_audits: list[dict[str, Any]] = []
    expected_commands = [
        float(value) for value in prereg["matrix"]["commands_x_m_s"]
    ]
    expected_fits = list(prereg["matrix"]["fits"])
    override = prereg["condition"]["override"]
    max_rate_excess = float(
        prereg["behavior_contract"]["moving_replacement_quality"][
            "maximum_rate_excess_rad_s"
        ]
    )

    for candidate_contract, candidate in zip(
        expected_candidates,
        result_candidates,
        strict=True,
    ):
        candidate_id = candidate_contract["candidate_id"]
        expected_checkpoint_ids = [
            checkpoint["checkpoint_id"]
            for checkpoint in candidate_contract["checkpoints"]
        ]
        require(
            candidate.get("checkpoint_ids") == expected_checkpoint_ids,
            f"{candidate_id}:checkpoint_ids",
            issues,
        )
        expected_block_order = [
            (checkpoint_id, fit_id)
            for checkpoint_id in expected_checkpoint_ids
            for fit_id in expected_fits
        ]
        blocks = candidate.get("blocks") or []
        require(
            [
                (block.get("checkpoint_id"), block.get("fit_id"))
                for block in blocks
            ]
            == expected_block_order,
            f"{candidate_id}:block_order",
            issues,
        )
        for block in blocks:
            checkpoint_id = block["checkpoint_id"]
            fit_id = block["fit_id"]
            manifest_path = (
                cache_root
                / candidate_id
                / checkpoint_id
                / fit_id
                / "t6_block_manifest.json"
            )
            require(
                manifest_path.is_file(),
                f"{candidate_id}:{checkpoint_id}:{fit_id}:manifest_missing",
                issues,
            )
            if not manifest_path.is_file():
                continue
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
            manifest_count += 1
            computed_manifest_canonical = canonical_sha256(manifest)
            require(
                block.get("manifest_sha256")
                == computed_manifest_canonical,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:manifest_canonical",
                issues,
            )
            manifest_file_hashes.append(
                {
                    "candidate_id": candidate_id,
                    "checkpoint_id": checkpoint_id,
                    "fit_id": fit_id,
                    "path": str(manifest_path),
                    "file_sha256": file_sha256(manifest_path),
                    "canonical_sha256": computed_manifest_canonical,
                }
            )
            block_contract = manifest.get("block_contract") or {}
            require(
                block_contract.get("candidate_id") == candidate_id,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:contract_candidate",
                issues,
            )
            require(
                (block_contract.get("checkpoint") or {}).get(
                    "checkpoint_id"
                )
                == checkpoint_id,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:contract_checkpoint",
                issues,
            )
            require(
                block_contract.get("fit_id") == fit_id,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:contract_fit",
                issues,
            )
            require(
                block_contract.get("preregistered_contract_sha256")
                == computed_prereg_contract,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:contract_prereg",
                issues,
            )
            require(
                (block_contract.get("condition") or {}).get("override")
                == override,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:contract_override",
                issues,
            )

            evaluation_path = Path(manifest["evaluation_path"])
            require(
                evaluation_path.is_file(),
                f"{candidate_id}:{checkpoint_id}:{fit_id}:evaluation_missing",
                issues,
            )
            if not evaluation_path.is_file():
                continue
            evaluation_count += 1
            evaluation_sha = file_sha256(evaluation_path)
            require(
                evaluation_sha == manifest.get("evaluation_sha256"),
                f"{candidate_id}:{checkpoint_id}:{fit_id}:evaluation_manifest_hash",
                issues,
            )
            require(
                evaluation_sha
                == block["result"].get("evaluation_sha256"),
                f"{candidate_id}:{checkpoint_id}:{fit_id}:evaluation_result_hash",
                issues,
            )
            require(
                str(evaluation_path)
                == block["result"].get("evaluation_path"),
                f"{candidate_id}:{checkpoint_id}:{fit_id}:evaluation_path",
                issues,
            )
            evaluation = json.loads(
                evaluation_path.read_text(encoding="utf-8")
            )
            require(
                (evaluation.get("execution") or {}).get("platform")
                == "cpu",
                f"{candidate_id}:{checkpoint_id}:{fit_id}:cpu_only",
                issues,
            )
            require(
                (evaluation.get("inputs") or {}).get(
                    "eval_dynamics_override"
                )
                == override,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:requested_override",
                issues,
            )
            runs = evaluation.get("runs") or []
            require(
                [float(run["command_x"]) for run in runs]
                == expected_commands,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:commands",
                issues,
            )
            manifest_traces = manifest.get("traces") or []
            result_cells = block["result"].get("cells") or []
            require(
                len(runs) == len(manifest_traces) == len(result_cells) == 4,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:cell_count",
                issues,
            )
            recomputed_cells: list[dict[str, Any]] = []
            for run, manifest_trace, stored_cell in zip(
                runs,
                manifest_traces,
                result_cells,
                strict=True,
            ):
                command = float(run["command_x"])
                trace_path = Path(manifest_trace["path"])
                require(
                    trace_path.is_file(),
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:trace_missing"
                    ),
                    issues,
                )
                if not trace_path.is_file():
                    continue
                trace_count += 1
                computed_trace = trace_metrics(
                    trace_path,
                    prereg["protection_contract"],
                    issues,
                )
                require(
                    computed_trace.get("sha256")
                    == manifest_trace.get("sha256"),
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:trace_manifest_hash"
                    ),
                    issues,
                )
                stored_trace = stored_cell["trace"]
                require(
                    str(trace_path) == stored_trace.get("path"),
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:trace_path"
                    ),
                    issues,
                )
                for key, value in computed_trace.items():
                    require(
                        same_value(stored_trace.get(key), value),
                        (
                            f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                            f"x{command}:trace_metric:{key}"
                        ),
                        issues,
                    )

                behavior = classify_behavior(
                    evaluation_behavior(run),
                    prereg["behavior_contract"],
                )
                require(
                    same_value(stored_cell.get("behavior"), behavior),
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:behavior"
                    ),
                    issues,
                )
                trace_valid = (
                    bool(computed_trace["ticks_contiguous_from_zero"])
                    and int(computed_trace["rows"])
                    == int(behavior["samples"])
                )
                cell_green = (
                    trace_valid
                    and bool(behavior["core_pass"])
                    and bool(behavior["replacement_quality_pass"])
                    and bool(computed_trace["duration_protection_pass"])
                    and float(
                        computed_trace[
                            "maximum_full_measured_vector_excess_rad_s"
                        ]
                    )
                    <= max_rate_excess
                )
                require(
                    stored_cell.get("trace_valid") is trace_valid,
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:trace_valid"
                    ),
                    issues,
                )
                require(
                    stored_cell.get("cell_green") is cell_green,
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:cell_green"
                    ),
                    issues,
                )
                readback_exact = exact_override_readback(
                    run.get("dynamics_override") or {},
                    override,
                )
                require(
                    readback_exact,
                    (
                        f"{candidate_id}:{checkpoint_id}:{fit_id}:"
                        f"x{command}:override_readback"
                    ),
                    issues,
                )
                readback_count += int(readback_exact)
                cell_count += 1
                green_cell_count += int(cell_green)
                recomputed_cells.append(
                    {
                        "behavior": behavior,
                        "trace": computed_trace,
                        "trace_valid": trace_valid,
                        "cell_green": cell_green,
                    }
                )

            block_green = (
                len(recomputed_cells) == 4
                and all(cell["cell_green"] for cell in recomputed_cells)
            )
            require(
                block["result"].get("all_readbacks_exact")
                is (len(recomputed_cells) == 4),
                f"{candidate_id}:{checkpoint_id}:{fit_id}:readback_aggregate",
                issues,
            )
            require(
                block["result"].get("requested_override_exact") is True,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:override_aggregate",
                issues,
            )
            require(
                block["result"].get("block_green") is block_green,
                f"{candidate_id}:{checkpoint_id}:{fit_id}:block_green",
                issues,
            )

        recomputed = recompute_candidate(candidate)
        for key, value in recomputed.items():
            require(
                same_value(candidate.get(key), value),
                f"{candidate_id}:aggregate:{key}",
                issues,
            )
        require(
            candidate.get("expected_cells") == 16,
            f"{candidate_id}:expected_cells",
            issues,
        )
        candidate_audits.append(
            {
                "candidate_id": candidate_id,
                "green_cells": recomputed["green_cells"],
                "all_blocks_green": recomputed["all_blocks_green"],
                "minimum_moving_vx_m_s": recomputed[
                    "minimum_moving_vx_m_s"
                ],
                "worst_tracking_p95_rad": recomputed[
                    "worst_tracking_p95_rad"
                ],
                "worst_strict_overcurrent_run_ticks": recomputed[
                    "worst_strict_overcurrent_run_ticks"
                ],
                "worst_strict_overload_run_ticks": recomputed[
                    "worst_strict_overload_run_ticks"
                ],
            }
        )

    expected_cells = int(prereg["matrix"]["total_cells"])
    survivors = [
        candidate["candidate_id"]
        for candidate in result_candidates
        if candidate.get("all_blocks_green") is True
    ]
    expected_status = (
        "PASS_T6_FROZEN_ROBUST_SURVIVOR_EXISTS"
        if survivors
        else "PASS_T6_NO_FROZEN_ROBUST_SURVIVOR"
    )
    expected_decision = (
        "ADVANCE_SELECTED_SURVIVOR_TO_SEQUENTIAL_R2_REVALIDATION"
        if survivors
        else "EARN_AUTOMATIC_CONFIGURATION_RESPONSE_MECHANISM_REVIEW"
    )
    require(
        manifest_count == int(prereg["matrix"]["total_blocks"]),
        "total_manifest_count",
        issues,
    )
    require(
        evaluation_count == int(prereg["matrix"]["total_blocks"]),
        "total_evaluation_count",
        issues,
    )
    require(trace_count == expected_cells, "total_trace_count", issues)
    require(cell_count == expected_cells, "total_cell_count", issues)
    require(
        readback_count == expected_cells,
        "total_exact_readback_count",
        issues,
    )
    require(
        result.get("expected_cells") == expected_cells,
        "result_expected_cells",
        issues,
    )
    require(
        result.get("completed_cells") == cell_count,
        "result_completed_cells",
        issues,
    )
    require(
        result.get("status") == expected_status,
        "result_status",
        issues,
    )
    require(
        result.get("decision") == expected_decision,
        "result_decision",
        issues,
    )
    require(
        result.get("selected_survivor")
        == (survivors[0] if len(survivors) == 1 else None),
        "result_selected_survivor",
        issues,
    )
    require(
        result.get("authority") == prereg.get("authority"),
        "result_authority",
        issues,
    )

    payload = {
        "schema_version": (
            "open_duck.t6_corrected_robustness_independent_audit.v1"
        ),
        "status": (
            "PASS_T6_INDEPENDENT_AUDIT"
            if not issues
            else "FAIL_T6_INDEPENDENT_AUDIT"
        ),
        "result": {
            "path": str(result_path),
            "file_sha256": file_sha256(result_path),
            "recorded_canonical_sha256": recorded_result_sha,
            "computed_canonical_sha256": computed_result_sha,
            "status": result.get("status"),
            "decision": result.get("decision"),
        },
        "preregistration": {
            "path": str(prereg_path),
            "file_sha256": file_sha256(prereg_path),
            "recorded_contract_sha256": prereg.get(
                "preregistered_contract_sha256"
            ),
            "computed_contract_sha256": computed_prereg_contract,
        },
        "counts": {
            "manifests": manifest_count,
            "evaluations": evaluation_count,
            "traces": trace_count,
            "cells": cell_count,
            "green_cells": green_cell_count,
            "exact_override_readbacks": readback_count,
            "candidates": len(candidate_audits),
            "survivors": len(survivors),
        },
        "candidate_audits": candidate_audits,
        "manifest_files": manifest_file_hashes,
        "issues": issues,
        "authority": prereg["authority"],
    }
    payload["audit_sha256"] = canonical_sha256(payload)
    return payload


def write_audit(
    payload: dict[str, Any],
    audit_path: Path = DEFAULT_AUDIT,
    markdown_path: Path = DEFAULT_MARKDOWN,
) -> None:
    audit_path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T6 corrected robustness screen — independent audit",
        "",
        f"- Status: `{payload['status']}`",
        f"- Audit SHA-256: `{payload['audit_sha256']}`",
        f"- Result file SHA-256: `{payload['result']['file_sha256']}`",
        (
            "- Result canonical SHA-256: "
            f"`{payload['result']['computed_canonical_sha256']}`"
        ),
        (
            "- Evidence: "
            f"`{payload['counts']['manifests']}` manifests, "
            f"`{payload['counts']['evaluations']}` evaluations, "
            f"`{payload['counts']['traces']}` traces, "
            f"`{payload['counts']['cells']}` cells, "
            f"`{payload['counts']['exact_override_readbacks']}` exact "
            "override readbacks"
        ),
        f"- Survivors: `{payload['counts']['survivors']}`",
        "",
        "| candidate | green cells | full pair | worst tracking | min vx | "
        "current run | overload run |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for candidate in payload["candidate_audits"]:
        lines.append(
            f"| `{candidate['candidate_id']}` | "
            f"{candidate['green_cells']}/16 | "
            f"`{candidate['all_blocks_green']}` | "
            f"{candidate['worst_tracking_p95_rad']} | "
            f"{candidate['minimum_moving_vx_m_s']} | "
            f"{candidate['worst_strict_overcurrent_run_ticks']} | "
            f"{candidate['worst_strict_overload_run_ticks']} |"
        )
    lines.extend(
        [
            "",
            "This auditor does not import the T6 runner. It independently "
            "recomputes the preregistration and result canonical hashes, every "
            "manifest/evaluation/trace hash, exact COM mutation readback, "
            "trace duration-protection metrics, behavior classifications, "
            "candidate aggregates, and the final decision.",
            "",
            "This CPU-only audit authorizes no hosted training, robot access, "
            "Gate 5, torque, or motion.",
        ]
    )
    markdown_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--prereg", type=Path, default=DEFAULT_PREREG)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_MARKDOWN,
    )
    args = parser.parse_args()
    payload = audit(args.result, args.prereg)
    if args.write:
        write_audit(
            payload,
            args.audit_output,
            args.markdown_output,
        )
    print(payload["status"])
    print(f"AUDIT_SHA256={payload['audit_sha256']}")
    print(f"ISSUES={len(payload['issues'])}")
    return 0 if payload["status"] == "PASS_T6_INDEPENDENT_AUDIT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
