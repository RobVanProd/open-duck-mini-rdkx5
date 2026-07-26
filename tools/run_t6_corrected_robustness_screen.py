#!/usr/bin/env python3
"""Run the preregistered corrected-gate torso-COM robustness screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
ABI_AMENDMENT = (
    ANALYSIS / "t6_corrected_robustness_screen_abi_amendment.json"
)
RESULT = ANALYSIS / "t6_corrected_robustness_screen_result.json"
MARKDOWN = ANALYSIS / "T6_CORRECTED_ROBUSTNESS_SCREEN_RESULT_20260725.md"


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


def longest_true_run(values: np.ndarray) -> int:
    best = current = 0
    for value in values:
        if bool(value):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def verify_preregistration(prereg: dict[str, Any]) -> None:
    if prereg.get("status") != "PREREGISTERED_T6_CORRECTED_ROBUSTNESS_SCREEN":
        raise RuntimeError(f"invalid T6 preregistration: {prereg.get('status')}")
    basis = {
        key: prereg[key]
        for key in (
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
    }
    if canonical_sha256(basis) != prereg["preregistered_contract_sha256"]:
        raise RuntimeError("T6 preregistered contract hash mismatch")
    for name, item in prereg["repository_inputs"].items():
        path = Path(item["path"])
        if not path.is_file():
            raise RuntimeError(f"T6 repository input changed: {path}")
        if name != "runner" and sha256(path) != item["sha256"]:
            raise RuntimeError(f"T6 repository input changed: {path}")
    amendment = load_abi_amendment(prereg)
    if sha256(Path(__file__)) != amendment["corrected_runner_sha256"]:
        raise RuntimeError("T6 runner does not match the ABI amendment")
    for candidate in prereg["candidate_pairs"]:
        for checkpoint in candidate["checkpoints"]:
            path = Path(checkpoint["path"])
            if not path.is_file() or sha256(path) != checkpoint["sha256"]:
                raise RuntimeError(f"T6 policy changed: {path}")
    playground = Path(prereg["playground"]["path"])
    for relative, expected in prereg["playground"]["required_file_sha256"].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T6 Playground file changed: {relative}")
    for item in prereg["playground"]["composition_manifests"].values():
        path = Path(item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise RuntimeError(f"T6 composition manifest changed: {path}")


def load_abi_amendment(prereg: dict[str, Any]) -> dict[str, Any]:
    if not ABI_AMENDMENT.is_file():
        raise RuntimeError("T6 recurrent ABI amendment is missing")
    amendment = json.loads(ABI_AMENDMENT.read_text(encoding="utf-8"))
    basis = {
        key: amendment[key]
        for key in (
            "original_preregistration",
            "preoutcome_evidence",
            "onnx_abi",
            "authorized_change",
            "corrected_runner_sha256",
            "unchanged_contract",
        )
    }
    if (
        amendment.get("status")
        != "PREREGISTERED_T6_PREOUTCOME_RECURRENT_ABI_CORRECTION"
        or canonical_sha256(basis) != amendment["amendment_contract_sha256"]
        or amendment["original_preregistration"][
            "preregistered_contract_sha256"
        ]
        != prereg["preregistered_contract_sha256"]
        or amendment["original_preregistration"]["runner_sha256"]
        != prereg["repository_inputs"]["runner"]["sha256"]
    ):
        raise RuntimeError("invalid T6 recurrent ABI amendment")
    return amendment


def block_contract(
    prereg: dict[str, Any],
    candidate: dict[str, Any],
    checkpoint: dict[str, Any],
    fit_id: str,
) -> dict[str, Any]:
    amendment = load_abi_amendment(prereg)
    return {
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": prereg["condition"],
        "matrix": prereg["matrix"],
        "candidate_id": candidate["candidate_id"],
        "checkpoint": checkpoint,
        "fit_id": fit_id,
        "fit_sha256": prereg["repository_inputs"][f"fit_{fit_id}"]["sha256"],
        "repository_inputs": prereg["repository_inputs"],
        "playground": prereg["playground"],
        "execution_amendment": {
            "path": str(ABI_AMENDMENT.resolve()),
            "sha256": sha256(ABI_AMENDMENT),
            "amendment_contract_sha256": amendment[
                "amendment_contract_sha256"
            ],
        },
    }


def block_dir(
    cache_root: Path,
    candidate_id: str,
    checkpoint_id: str,
    fit_id: str,
) -> Path:
    return cache_root / candidate_id / checkpoint_id / fit_id


def trace_paths(
    directory: Path,
    policy: Path,
    matrix: dict[str, Any],
) -> list[Path]:
    return [
        directory
        / "traces"
        / f"x{float(command):.3f}_seed{matrix['seed']}_{policy.stem}.jsonl"
        for command in matrix["commands_x_m_s"]
    ]


def load_cached_block(
    manifest_path: Path,
    expected_contract: dict[str, Any],
) -> dict[str, Any] | None:
    if not manifest_path.is_file():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("block_contract") != expected_contract:
        return None
    if manifest.get("block_contract_sha256") != canonical_sha256(
        expected_contract
    ):
        return None
    eval_path = Path(manifest["evaluation_path"])
    if not eval_path.is_file() or sha256(eval_path) != manifest["evaluation_sha256"]:
        return None
    for item in manifest["traces"]:
        path = Path(item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            return None
    return manifest


def run_or_load_block(
    prereg: dict[str, Any],
    candidate: dict[str, Any],
    checkpoint: dict[str, Any],
    fit_id: str,
    cache_root: Path,
) -> tuple[dict[str, Any], bool]:
    directory = block_dir(
        cache_root,
        candidate["candidate_id"],
        checkpoint["checkpoint_id"],
        fit_id,
    )
    manifest_path = directory / "t6_block_manifest.json"
    contract = block_contract(prereg, candidate, checkpoint, fit_id)
    cached = load_cached_block(manifest_path, contract)
    if cached is not None:
        return cached, True

    if directory.exists():
        raise RuntimeError(
            f"T6 block exists but does not match its frozen contract: {directory}"
        )
    trace_dir = directory / "traces"
    trace_dir.mkdir(parents=True)
    evaluation_path = directory / "evaluation.json"
    stdout_path = directory / "stdout.log"
    policy = Path(checkpoint["path"])
    matrix = prereg["matrix"]
    fit = Path(prereg["repository_inputs"][f"fit_{fit_id}"]["path"])
    command = [
        sys.executable,
        str(Path(prereg["repository_inputs"]["evaluator"]["path"])),
        "--policy",
        str(policy),
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        str(fit),
        "--reference-feature-table",
        prereg["repository_inputs"]["reference_features"]["path"],
        "--reference-start-phase",
        "0",
        "--expected-observation-dim",
        "115",
        "--policy-state-input-names",
        "previous_action,h_in",
        "--policy-state-output-names",
        "previous_action_out,h_out",
        "--policy-applied-target-observation",
        "--trace-dir",
        str(trace_dir),
        "--commands",
        ",".join(str(value) for value in matrix["commands_x_m_s"]),
        "--seeds",
        str(matrix["seed"]),
        "--duration-s",
        str(matrix["duration_ticks"] / matrix["frequency_hz"]),
        "--minimum-emergence-duration-s",
        "1.08",
        "--task",
        "flat_terrain_backlash",
        "--eval-dynamics-override-json",
        json.dumps(
            prereg["condition"]["override"],
            separators=(",", ":"),
            sort_keys=True,
        ),
        "--reset-mode",
        "home-support",
        "--policy-action-rate-limit-joint-indices",
        "2,3,4,11,12,13",
        "--output-json",
        str(evaluation_path),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_COMPILATION_CACHE_DIR": str(
                cache_root.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    with stdout_path.open("w", encoding="utf-8") as stream:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2400,
            check=False,
        )
    if completed.returncode != 0 or not evaluation_path.is_file():
        raise RuntimeError(
            f"T6 evaluator failed for {directory}; "
            f"returncode={completed.returncode}; log={stdout_path}"
        )
    traces = trace_paths(directory, policy, matrix)
    missing = [path for path in traces if not path.is_file()]
    if missing:
        raise RuntimeError(f"T6 evaluator omitted traces: {missing}")
    manifest = {
        "schema_version": "open_duck.t6_corrected_robustness_block.v1",
        "block_contract": contract,
        "block_contract_sha256": canonical_sha256(contract),
        "command": command,
        "evaluation_path": str(evaluation_path),
        "evaluation_sha256": sha256(evaluation_path),
        "stdout_path": str(stdout_path),
        "traces": [
            {"path": str(path), "sha256": sha256(path)} for path in traces
        ],
    }
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, manifest_path)
    return manifest, False


def exact_override_readback(
    report: dict[str, Any] | None,
    expected: dict[str, Any],
) -> bool:
    report = report or {}
    if report.get("enabled") is not True:
        return False
    key, value = next(iter(expected.items()))
    readback = report.get("readback")
    return (
        report.get("key") == key
        and report.get("value") == value
        and isinstance(readback, dict)
        and bool(readback)
    )


def trace_summary(path: Path, contract: dict[str, Any]) -> dict[str, Any]:
    ticks: list[int] = []
    forces: list[list[float]] = []
    rate_excess: list[list[float]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("mode") != "fitted":
                continue
            ticks.append(int(row["tick"]))
            forces.append(row["actuator_force_nm"])
            rate_excess.append(row["conservative_rate_excess_rad_s"])
    torque = np.abs(np.asarray(forces, dtype=np.float64))
    excess = np.asarray(rate_excess, dtype=np.float64)
    if torque.ndim != 2 or torque.shape[1] != 14 or excess.shape != torque.shape:
        raise RuntimeError(f"invalid T6 trace shape: {path}")
    current = torque / float(contract["motor_constant_nm_per_a"])
    overcurrent_runs = [
        longest_true_run(current[:, index] > contract["overcurrent_threshold_a"])
        for index in range(14)
    ]
    overload_runs = [
        longest_true_run(torque[:, index] > contract["overload_threshold_nm"])
        for index in range(14)
    ]
    max_overcurrent = max(overcurrent_runs, default=0)
    max_overload = max(overload_runs, default=0)
    return {
        "path": str(path),
        "sha256": sha256(path),
        "rows": len(ticks),
        "ticks_contiguous_from_zero": ticks == list(range(len(ticks))),
        "worst_peak_torque_nm_diagnostic": float(np.max(torque)),
        "worst_peak_current_a_diagnostic": float(np.max(current)),
        "worst_strict_overcurrent_run_ticks": int(max_overcurrent),
        "worst_strict_overload_run_ticks": int(max_overload),
        "simulator_force_limit_hit_ticks_diagnostic": int(
            np.sum(
                np.abs(
                    torque - float(contract["simulator_force_limit_abs_nm"])
                )
                <= float(contract["force_limit_tolerance_nm"])
            )
        ),
        "maximum_full_measured_vector_excess_rad_s": float(np.max(excess)),
        "duration_protection_pass": (
            max_overcurrent <= contract["pass_max_consecutive_ticks"]
            and max_overload <= contract["pass_max_consecutive_ticks"]
        ),
    }


def behavior_row(run: dict[str, Any]) -> dict[str, Any]:
    fitted = (run.get("modes") or {}).get("fitted") or {}
    emergence = run.get("emergence") or {}
    gate = run.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    command = float(run["command_x"])
    mean_vx = emergence.get("mean_velocity_x_m_s")
    return {
        "command_x_m_s": command,
        "samples": int(fitted.get("samples") or 0),
        "termination_reason": emergence.get("termination_reason"),
        "evaluator_candidate_gate_status_diagnostic": gate.get("status"),
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
            if command > 0 and finite(mean_vx)
            else None
        ),
        "body_pitch_p95_rad": metrics.get("max_abs_body_pitch_p95_rad"),
        "minimum_base_height_m": metrics.get("min_base_height_m"),
        "pitch_tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
        "action_saturation_pct": metrics.get("max_action_saturation_pct"),
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
    zero = abs(row["command_x_m_s"]) <= 1.0e-12
    core = contract["x0_core"] if zero else contract["moving_core"]
    quality = contract["x0_replacement_quality"] if zero else contract[
        "moving_replacement_quality"
    ]
    core_checks = {
        "samples": row["samples"] == core["samples"],
        "duration": row["termination_reason"] == "duration_complete",
        "finite_mean_vx": finite(row["mean_local_vx_m_s"]),
        "body_pitch": finite(row["body_pitch_p95_rad"])
        and row["body_pitch_p95_rad"] <= core["maximum_body_pitch_p95_rad"],
        "height": finite(row["minimum_base_height_m"])
        and row["minimum_base_height_m"] >= core["minimum_base_height_m"],
        "saturation": finite(row["action_saturation_pct"])
        and row["action_saturation_pct"]
        <= core["maximum_action_saturation_pct"],
    }
    if zero:
        core_checks["zero_velocity"] = (
            finite(row["mean_local_vx_m_s"])
            and abs(row["mean_local_vx_m_s"])
            <= core["maximum_absolute_mean_local_vx_m_s"]
        )
    else:
        core_checks.update(
            {
                "emergence": row["emergence_pass"],
                "bilateral_transitions": (
                    row["left_contact_transitions"] > 0
                    and row["right_contact_transitions"] > 0
                ),
                "positive_velocity": finite(row["mean_local_vx_m_s"])
                and row["mean_local_vx_m_s"] > 0.0,
                "minimum_track_ratio": finite(row["track_ratio"])
                and row["track_ratio"] >= core["minimum_track_ratio"],
            }
        )
    quality_checks = {
        "tracking": finite(row["pitch_tracking_p95_rad"])
        and row["pitch_tracking_p95_rad"]
        <= quality["maximum_pitch_tracking_p95_rad"],
        "p95_rate": finite(row["p95_rate_excess_rad_s"])
        and row["p95_rate_excess_rad_s"]
        <= quality["maximum_rate_excess_rad_s"],
        "instant_rate": finite(row["instant_rate_excess_rad_s"])
        and row["instant_rate_excess_rad_s"]
        <= quality["maximum_rate_excess_rad_s"],
        "zero_saturation": finite(row["action_saturation_pct"])
        and row["action_saturation_pct"]
        <= quality["maximum_action_saturation_pct"],
    }
    return {
        **row,
        "core_checks": core_checks,
        "replacement_quality_checks": quality_checks,
        "core_pass": all(core_checks.values()),
        "replacement_quality_pass": all(quality_checks.values()),
    }


def extract_block(
    manifest: dict[str, Any],
    prereg: dict[str, Any],
) -> dict[str, Any]:
    evaluation = json.loads(
        Path(manifest["evaluation_path"]).read_text(encoding="utf-8")
    )
    runs = evaluation.get("runs") or []
    matrix = prereg["matrix"]
    expected_commands = [float(item) for item in matrix["commands_x_m_s"]]
    if [float(run["command_x"]) for run in runs] != expected_commands:
        raise RuntimeError("T6 evaluation returned the wrong command order")
    expected_trace_paths = {
        float(command): Path(item["path"])
        for command, item in zip(expected_commands, manifest["traces"], strict=True)
    }
    rows = []
    for run in runs:
        command = float(run["command_x"])
        behavior = classify_behavior(
            behavior_row(run),
            prereg["behavior_contract"],
        )
        trace = trace_summary(
            expected_trace_paths[command],
            prereg["protection_contract"],
        )
        trace_valid = (
            trace["ticks_contiguous_from_zero"]
            and trace["rows"] == behavior["samples"]
        )
        rows.append(
            {
                "behavior": behavior,
                "trace": trace,
                "trace_valid": trace_valid,
                "cell_green": (
                    trace_valid
                    and behavior["core_pass"]
                    and behavior["replacement_quality_pass"]
                    and trace["duration_protection_pass"]
                    and trace["maximum_full_measured_vector_excess_rad_s"]
                    <= prereg["behavior_contract"][
                        "moving_replacement_quality"
                    ]["maximum_rate_excess_rad_s"]
                ),
            }
        )
    override = prereg["condition"]["override"]
    readbacks = [
        exact_override_readback(run.get("dynamics_override"), override)
        for run in runs
    ]
    return {
        "evaluation_path": manifest["evaluation_path"],
        "evaluation_sha256": manifest["evaluation_sha256"],
        "execution_platform": (evaluation.get("execution") or {}).get("platform"),
        "requested_override_exact": (
            (evaluation.get("inputs") or {}).get("eval_dynamics_override")
            == override
        ),
        "all_readbacks_exact": len(readbacks) == 4 and all(readbacks),
        "cells": rows,
        "block_green": (
            len(rows) == 4
            and all(item["cell_green"] for item in rows)
            and len(readbacks) == 4
            and all(readbacks)
        ),
    }


def candidate_summary(
    candidate: dict[str, Any],
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    cells = [
        cell
        for block in blocks
        for cell in block["result"]["cells"]
    ]
    moving = [
        cell
        for cell in cells
        if cell["behavior"]["command_x_m_s"] > 0.0
    ]
    return {
        "candidate_id": candidate["candidate_id"],
        "checkpoint_ids": [
            item["checkpoint_id"] for item in candidate["checkpoints"]
        ],
        "expected_cells": 16,
        "completed_cells": len(cells),
        "green_cells": sum(item["cell_green"] for item in cells),
        "all_blocks_green": len(blocks) == 4
        and all(item["result"]["block_green"] for item in blocks),
        "worst_tracking_p95_rad": max(
            item["behavior"]["pitch_tracking_p95_rad"] for item in cells
        ),
        "minimum_moving_vx_m_s": min(
            item["behavior"]["mean_local_vx_m_s"] for item in moving
        ),
        "minimum_moving_track_ratio": min(
            item["behavior"]["track_ratio"] for item in moving
        ),
        "worst_strict_overcurrent_run_ticks": max(
            item["trace"]["worst_strict_overcurrent_run_ticks"]
            for item in cells
        ),
        "worst_strict_overload_run_ticks": max(
            item["trace"]["worst_strict_overload_run_ticks"] for item in cells
        ),
        "worst_peak_torque_nm_diagnostic": max(
            item["trace"]["worst_peak_torque_nm_diagnostic"] for item in cells
        ),
        "worst_peak_current_a_diagnostic": max(
            item["trace"]["worst_peak_current_a_diagnostic"] for item in cells
        ),
        "simulator_force_limit_hit_ticks_diagnostic": sum(
            item["trace"]["simulator_force_limit_hit_ticks_diagnostic"]
            for item in cells
        ),
        "blocks": blocks,
    }


def selection_key(
    summary: dict[str, Any],
    fixed_order: list[str],
) -> tuple[Any, ...]:
    return (
        summary["worst_strict_overload_run_ticks"],
        summary["worst_strict_overcurrent_run_ticks"],
        summary["worst_tracking_p95_rad"],
        -summary["minimum_moving_vx_m_s"],
        fixed_order.index(summary["candidate_id"]),
    )


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# T6 corrected-gate torso-COM robustness screen",
        "",
        f"- Status: `{payload['status']}`",
        f"- Decision: `{payload['decision']}`",
        f"- Cells: `{payload['completed_cells']}/{payload['expected_cells']}`",
        f"- Selected survivor: `{payload['selected_survivor']}`",
        f"- Result SHA-256: `{payload['result_sha256']}`",
        "",
        "| candidate | green cells | green pair | tracking p95 | min vx | "
        "min ratio | current run | overload run | peak torque | peak current |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["candidates"]:
        lines.append(
            f"| `{item['candidate_id']}` | {item['green_cells']}/16 | "
            f"`{item['all_blocks_green']}` | "
            f"{item['worst_tracking_p95_rad']} | "
            f"{item['minimum_moving_vx_m_s']} | "
            f"{item['minimum_moving_track_ratio']} | "
            f"{item['worst_strict_overcurrent_run_ticks']} | "
            f"{item['worst_strict_overload_run_ticks']} | "
            f"{item['worst_peak_torque_nm_diagnostic']} | "
            f"{item['worst_peak_current_a_diagnostic']} |"
        )
    lines.extend(
        [
            "",
            "The condition is the pre-existing R2 `TORSO_COM_X_NEG` endpoint "
            "(`-0.05 m`), selected before this screen because it was the first "
            "failure of the prior winner after six R2 passes.",
            "",
            "Tracking, zero saturation, and zero measured-rate excess are "
            "explicit replacement-quality goals where T4 showed the old "
            "baseline can fail; they are not relabeled as generic feasibility "
            "claims. Servo protection uses the manufacturer-derived 100-tick "
            "duration rules from T5.",
            "",
            "This CPU-only result does not authorize training, robot access, "
            "Gate 5, torque, or motion.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t6_corrected_robustness_screen_v1"
        ),
    )
    parser.add_argument("--max-new-blocks", type=int, default=None)
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T6 requires --execute after preregistration review")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T6 result")
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    summaries = []
    new_blocks = 0
    cache_hits = 0
    for candidate in prereg["candidate_pairs"]:
        candidate_blocks = []
        for checkpoint in candidate["checkpoints"]:
            for fit_id in prereg["matrix"]["fits"]:
                if (
                    args.max_new_blocks is not None
                    and new_blocks >= args.max_new_blocks
                ):
                    break
                manifest, cached = run_or_load_block(
                    prereg,
                    candidate,
                    checkpoint,
                    fit_id,
                    cache_root,
                )
                cache_hits += int(cached)
                new_blocks += int(not cached)
                result = extract_block(manifest, prereg)
                candidate_blocks.append(
                    {
                        "checkpoint_id": checkpoint["checkpoint_id"],
                        "fit_id": fit_id,
                        "manifest_sha256": canonical_sha256(manifest),
                        "result": result,
                    }
                )
                print(
                    f"{candidate['candidate_id']} "
                    f"{checkpoint['checkpoint_id']} {fit_id} "
                    f"{'cache' if cached else 'run'} "
                    f"green={result['block_green']}",
                    flush=True,
                )
            if (
                args.max_new_blocks is not None
                and new_blocks >= args.max_new_blocks
            ):
                break
        if len(candidate_blocks) == 4:
            summaries.append(candidate_summary(candidate, candidate_blocks))
        if (
            args.max_new_blocks is not None
            and new_blocks >= args.max_new_blocks
        ):
            break

    complete = len(summaries) == len(prereg["candidate_pairs"])
    expected_cells = len(prereg["candidate_pairs"]) * 16
    completed_cells = sum(item["completed_cells"] for item in summaries)
    survivors = [item for item in summaries if item["all_blocks_green"]]
    if complete and survivors:
        selected = min(
            survivors,
            key=lambda item: selection_key(
                item,
                prereg["decision_rule"]["fixed_tiebreak_order"],
            ),
        )["candidate_id"]
        status = "PASS_T6_FROZEN_ROBUST_SURVIVOR_EXISTS"
        decision = "ADVANCE_SELECTED_SURVIVOR_TO_SEQUENTIAL_R2_REVALIDATION"
    elif complete:
        selected = None
        status = "PASS_T6_NO_FROZEN_ROBUST_SURVIVOR"
        decision = "EARN_AUTOMATIC_CONFIGURATION_RESPONSE_MECHANISM_REVIEW"
    else:
        selected = None
        status = "PARTIAL_T6_NO_DECISION"
        decision = "RESUME_EXACT_FROZEN_BLOCKS"
    payload = {
        "schema_version": "open_duck.t6_corrected_robustness_screen_result.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": prereg["condition"],
        "expected_cells": expected_cells,
        "completed_cells": completed_cells,
        "cache_hits": cache_hits,
        "new_blocks": new_blocks,
        "cache_root": str(cache_root),
        "selected_survivor": selected,
        "candidates": summaries,
        "authority": prereg["authority"],
    }
    payload["result_sha256"] = canonical_sha256(payload)
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if complete:
        write_markdown(payload)
    print(status)
    print(f"RESULT_FILE_SHA256={sha256(RESULT)}")
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
