#!/usr/bin/env python3
"""Run T23's frozen sequential 20-condition R2 robustness matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

from run_t6_corrected_robustness_screen import (
    behavior_row,
    classify_behavior,
    exact_override_readback,
    trace_summary,
)
from run_t8_state_coherent_handoff import (
    read_trace,
    state_handoff_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
RESULT = ANALYSIS / "t27_t23_robustness_matrix_result.json"
MARKDOWN = ANALYSIS / "T27_T23_ROBUSTNESS_MATRIX_RESULT_20260726.md"
DEFAULT_CACHE_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t27_t23_robustness_matrix_v1"
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
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T27 frozen receipt changed: {label}={path}")


def matrix_plan(
    conditions: list[dict[str, Any]],
    policies: list[dict[str, Any]],
    fits: list[dict[str, Any]],
    commands: list[float],
    seed: int,
) -> list[dict[str, Any]]:
    return [
        {
            "condition_index": condition_index,
            "condition_id": condition["id"],
            "override": condition["override"],
            "checkpoint_id": policy["checkpoint_id"],
            "step": int(policy["step"]),
            "policy_sha256": policy["sha256"],
            "fit_id": fit["fit_id"],
            "fit_sha256": fit["sha256"],
            "command_x_m_s": float(command),
            "seed": int(seed),
            "duration_ticks": 600,
        }
        for condition_index, condition in enumerate(conditions, start=1)
        for policy in policies
        for fit in fits
        for command in commands
    ]


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T27 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for policy in value["policies"]:
        verify_receipt(policy, f"policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        verify_receipt(fit, f"fit:{fit['fit_id']}")
    verify_receipt(value["calibrator"], "calibrator")
    verify_receipt(value["reference_feature_table"], "reference")
    verify_receipt(value["playground"]["manifest"], "playground_manifest")
    plan = matrix_plan(
        value["conditions"],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != int(value["matrix"]["maximum_cells"])
        or canonical_sha256(plan) != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T27 matrix plan changed")
    return value


def block_contract(
    prereg: Mapping[str, Any],
    condition: Mapping[str, Any],
    policy: Mapping[str, Any],
    fit: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": condition,
        "policy": {
            "checkpoint_id": policy["checkpoint_id"],
            "step": policy["step"],
            "sha256": policy["sha256"],
        },
        "fit": {"fit_id": fit["fit_id"], "sha256": fit["sha256"]},
        "commands_x_m_s": prereg["commands_x_m_s"],
        "seed": prereg["seed"],
        "duration_ticks": 600,
        "support_handoff": prereg["support_handoff"],
        "behavior_contract": prereg["behavior_contract"],
        "protection_contract": prereg["protection_contract"],
    }


def block_directory(
    cache_root: Path,
    condition_index: int,
    condition_id: str,
    checkpoint_id: str,
    fit_id: str,
) -> Path:
    return (
        cache_root
        / f"{condition_index:02d}_{condition_id}"
        / checkpoint_id
        / fit_id
    )


def load_cached_manifest(
    path: Path, expected_contract: Mapping[str, Any]
) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("block_contract") != expected_contract
        or value.get("block_contract_sha256")
        != canonical_sha256(expected_contract)
    ):
        return None
    verify_receipt(value["evaluation"], "cached:evaluation")
    verify_receipt(value["stdout"], "cached:stdout")
    for index, item in enumerate(value["traces"]):
        verify_receipt(item, f"cached:trace:{index}")
    return value


def run_or_load_block(
    prereg: Mapping[str, Any],
    condition: Mapping[str, Any],
    policy: Mapping[str, Any],
    fit: Mapping[str, Any],
    cache_root: Path,
) -> tuple[dict[str, Any], bool]:
    condition_index = int(condition["condition_index"])
    directory = block_directory(
        cache_root,
        condition_index,
        str(condition["id"]),
        str(policy["checkpoint_id"]),
        str(fit["fit_id"]),
    )
    manifest_path = directory / "manifest.json"
    contract = block_contract(prereg, condition, policy, fit)
    cached = load_cached_manifest(manifest_path, contract)
    if cached is not None:
        return cached, True
    if directory.exists():
        raise RuntimeError(
            f"T27 block exists without a valid manifest: {directory}"
        )
    trace_dir = directory / "traces"
    trace_dir.mkdir(parents=True)
    evaluation = directory / "evaluation.json"
    stdout = directory / "stdout.log"
    command = [
        sys.executable,
        prereg["repository_inputs"]["worker"]["path"],
        "--formal",
        "--policy",
        policy["path"],
        "--policy-sha256",
        policy["sha256"],
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        fit["path"],
        "--reference-feature-table",
        prereg["reference_feature_table"]["path"],
        "--calibrator",
        prereg["calibrator"]["path"],
        "--calibrator-sha256",
        prereg["calibrator"]["sha256"],
        "--override-json",
        json.dumps(
            condition["override"], separators=(",", ":"), sort_keys=True
        ),
        "--commands",
        ",".join(str(item) for item in prereg["commands_x_m_s"]),
        "--seed",
        str(prereg["seed"]),
        "--duration-s",
        "12.0",
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
            "JAX_COMPILATION_CACHE_DIR": str(
                cache_root.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    with stdout.open("w", encoding="utf-8") as stream:
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
    expected_traces = [
        trace_dir
        / (
            f"x{float(command_x):.3f}_seed{prereg['seed']}_"
            f"{Path(policy['path']).stem}.jsonl"
        )
        for command_x in prereg["commands_x_m_s"]
    ]
    if (
        completed.returncode != 0
        or not evaluation.is_file()
        or any(not path.is_file() for path in expected_traces)
    ):
        raise RuntimeError(
            f"T27 worker failed: returncode={completed.returncode}; "
            f"log={stdout}"
        )
    manifest = {
        "schema_version": "open_duck.t27_t23_robustness_block.v1",
        "block_contract": contract,
        "block_contract_sha256": canonical_sha256(contract),
        "command": command,
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "traces": [receipt(path) for path in expected_traces],
    }
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, manifest_path)
    return manifest, False


def extract_block(
    prereg: Mapping[str, Any],
    condition: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    evaluation = json.loads(
        Path(manifest["evaluation"]["path"]).read_text(encoding="utf-8")
    )
    inputs = evaluation.get("inputs") or {}
    expected_inputs = {
        "calibration_ticks": 250,
        "home_return_ticks": 0,
        "preserve_handoff_state": True,
        "expected_observation_dim": 115,
        "expected_action_dim": 14,
        "policy_state_input_names": ["h_in", "previous_action"],
        "policy_state_output_names": ["h_out", "previous_action_out"],
        "policy_context_input_name": "calibration_context",
        "policy_graph_authoritative_output": True,
        "policy_applied_target_observation": True,
        "reference_start_phase": 0,
        "eval_dynamics_override": condition["override"],
        "commands_x_m_s": prereg["commands_x_m_s"],
        "seed": prereg["seed"],
        "duration_s": 12.0,
    }
    worker_inputs_exact = all(
        inputs.get(key) == expected for key, expected in expected_inputs.items()
    )
    runs = evaluation.get("runs") or []
    if [float(run["command_x"]) for run in runs] != [
        float(item) for item in prereg["commands_x_m_s"]
    ]:
        raise RuntimeError("T27 worker returned the wrong command order")
    rows = []
    for run, trace_receipt in zip(
        runs, manifest["traces"], strict=True
    ):
        path = Path(trace_receipt["path"])
        records = read_trace(path)
        behavior = classify_behavior(
            behavior_row(run), prereg["behavior_contract"]
        )
        protection = trace_summary(path, prereg["protection_contract"])
        handoff = state_handoff_summary(run, records)
        trace_valid = (
            protection["ticks_contiguous_from_zero"]
            and protection["rows"] == behavior["samples"]
            and protection["rows"] == 600
            and sha256(path) == trace_receipt["sha256"]
        )
        readback_exact = exact_override_readback(
            run.get("dynamics_override"), condition["override"]
        )
        cell_green = (
            trace_valid
            and behavior["core_pass"]
            and behavior["replacement_quality_pass"]
            and protection["duration_protection_pass"]
            and protection["maximum_full_measured_vector_excess_rad_s"]
            == 0.0
            and handoff["all_checks_pass"]
            and readback_exact
        )
        rows.append(
            {
                "command_x_m_s": float(run["command_x"]),
                "behavior": behavior,
                "protection": protection,
                "handoff": handoff,
                "trace_valid": trace_valid,
                "override_readback_exact": readback_exact,
                "cell_green": cell_green,
            }
        )
    return {
        "worker_inputs_exact": worker_inputs_exact,
        "execution_platform": (evaluation.get("execution") or {}).get(
            "platform"
        ),
        "cells": rows,
        "block_green": (
            worker_inputs_exact
            and evaluation.get("formal") is True
            and len(rows) == 4
            and all(item["cell_green"] for item in rows)
        ),
    }


def condition_summary(
    condition: Mapping[str, Any],
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    cells = [
        cell
        for block in blocks
        for cell in block["result"]["cells"]
    ]
    moving = [
        cell for cell in cells if cell["command_x_m_s"] > 0.0
    ]
    return {
        "condition_index": condition["condition_index"],
        "condition_id": condition["id"],
        "override": condition["override"],
        "cells": len(cells),
        "green_cells": sum(cell["cell_green"] for cell in cells),
        "condition_green": (
            len(blocks) == 4
            and all(block["result"]["block_green"] for block in blocks)
            and len(cells) == 16
            and all(cell["cell_green"] for cell in cells)
        ),
        "worst_tracking_p95_rad": max(
            cell["behavior"]["pitch_tracking_p95_rad"] for cell in cells
        ),
        "minimum_moving_vx_m_s": min(
            cell["behavior"]["mean_local_vx_m_s"] for cell in moving
        ),
        "worst_strict_overcurrent_run_ticks": max(
            cell["protection"]["worst_strict_overcurrent_run_ticks"]
            for cell in cells
        ),
        "worst_strict_overload_run_ticks": max(
            cell["protection"]["worst_strict_overload_run_ticks"]
            for cell in cells
        ),
        "worst_peak_current_a_diagnostic": max(
            cell["protection"]["worst_peak_current_a_diagnostic"]
            for cell in cells
        ),
        "worst_peak_torque_nm_diagnostic": max(
            cell["protection"]["worst_peak_torque_nm_diagnostic"]
            for cell in cells
        ),
    }


def write_markdown(result: Mapping[str, Any]) -> None:
    lines = [
        "# T27 T23 sequential R2 robustness result",
        "",
        f"- Status: `{result['status']}`",
        f"- Decision: `{result['decision']}`",
        f"- Completed conditions: "
        f"`{result['summary']['completed_conditions']}/20`",
        f"- Green cells: `{result['summary']['green_cells']}/"
        f"{result['summary']['completed_cells']}`",
        f"- First failed condition: "
        f"`{result['summary']['first_failed_condition']}`",
        "",
        "| # | condition | green | tracking p95 | min vx | current run | "
        "overload run |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for condition in result["conditions"]:
        lines.append(
            f"| {condition['condition_index']} | "
            f"`{condition['condition_id']}` | "
            f"{condition['green_cells']}/{condition['cells']} | "
            f"{condition['worst_tracking_p95_rad']:.9f} | "
            f"{condition['minimum_moving_vx_m_s']:.9f} | "
            f"{condition['worst_strict_overcurrent_run_ticks']} | "
            f"{condition['worst_strict_overload_run_ticks']} |"
        )
    lines.extend(
        [
            "",
            "Conditions run in the frozen order and stop after the first "
            "complete failed 16-cell condition. Raw traces remain in the "
            "D: evidence cache and are not committed.",
            "",
            "This CPU-only result does not authorize Gate 5, RDK-X5 access, "
            "robot access, torque, motion, or deployment.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T27 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T27 formal execution requires a clean worktree")

    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    all_blocks: list[dict[str, Any]] = []
    condition_results: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    first_failed: str | None = None

    for condition in prereg["conditions"]:
        blocks = []
        for policy in prereg["policies"]:
            for fit in prereg["fits"]:
                manifest, cached = run_or_load_block(
                    prereg,
                    condition,
                    policy,
                    fit,
                    cache_root,
                )
                result = extract_block(prereg, condition, manifest)
                block = {
                    "condition_index": condition["condition_index"],
                    "condition_id": condition["id"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "step": policy["step"],
                    "fit_id": fit["fit_id"],
                    "cached": cached,
                    "manifest": receipt(
                        Path(manifest["evaluation"]["path"]).parent
                        / "manifest.json"
                    ),
                    "result": result,
                }
                blocks.append(block)
                all_blocks.append(block)
                cache_hits += int(cached)
                new_blocks += int(not cached)
                print(
                    json.dumps(
                        {
                            "condition": condition["id"],
                            "block": (
                                f"{policy['checkpoint_id']}:{fit['fit_id']}"
                            ),
                            "block_green": result["block_green"],
                            "elapsed_s": time.time() - started,
                        }
                    ),
                    flush=True,
                )
        summary = condition_summary(condition, blocks)
        condition_results.append(summary)
        print(
            json.dumps(
                {
                    "completed_conditions": len(condition_results),
                    "condition": condition["id"],
                    "green_cells": summary["green_cells"],
                    "condition_green": summary["condition_green"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
        if not summary["condition_green"]:
            first_failed = str(condition["id"])
            break

    complete = len(condition_results) == len(prereg["conditions"])
    all_green = complete and all(
        item["condition_green"] for item in condition_results
    )
    completed_cells = sum(item["cells"] for item in condition_results)
    green_cells = sum(item["green_cells"] for item in condition_results)
    result = {
        "schema_version": "open_duck.t27_t23_robustness_matrix_result.v1",
        "status": (
            "PASS_T27_T23_FULL_R2_ROBUSTNESS"
            if all_green
            else "HOLD_T27_T23_R2_ROBUSTNESS"
        ),
        "decision": (
            "EARN_T23_GATE5_PACKAGE_PREREGISTRATION"
            if all_green
            else "STOP_T23_AT_FIRST_FAILED_R2_CONDITION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "summary": {
            "expected_conditions": len(prereg["conditions"]),
            "completed_conditions": len(condition_results),
            "matrix_complete": complete,
            "completed_cells": completed_cells,
            "green_cells": green_cells,
            "all_completed_cells_green": green_cells == completed_cells,
            "all_twenty_conditions_green": all_green,
            "first_failed_condition": first_failed,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds": time.time() - started,
        },
        "conditions": condition_results,
        "blocks": all_blocks,
        "cache_root": str(cache_root),
        "authority": {
            "gate5_package_preregistration_authorized": all_green,
            "gate5_hardware_authorized": False,
            "checkpoint_selection_authorized": False,
            "additional_training_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(result)
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(RESULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
