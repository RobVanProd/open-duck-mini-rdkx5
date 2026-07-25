#!/usr/bin/env python3
"""Run and reconcile the preregistered T4 baseline gate matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t4_baseline_all_gates_preregistration.json"
OUTPUT = ANALYSIS / "t4_baseline_all_gates_result.json"
MARKDOWN = ANALYSIS / "T4_BASELINE_ALL_GATES_RESULT_20260725.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def verify_inputs(prereg: dict[str, Any]) -> None:
    if prereg.get("status") != "PREREGISTERED_T4_BASELINE_ALL_GATES":
        raise RuntimeError(f"invalid T4 preregistration: {prereg.get('status')}")
    for name, expected in prereg["input_sha256"].items():
        path = Path(prereg["input_paths"][name])
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"T4 input changed or missing: {name}: {path}")


def cell_contract(prereg: dict[str, Any], cell: dict[str, Any]) -> dict[str, Any]:
    return {
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "input_sha256": prereg["input_sha256"],
        "playground_commit": prereg["playground"]["commit"],
        "frozen_configuration": prereg["frozen_configuration"],
        "cell": cell,
    }


def cell_dir(cache_root: Path, cell: dict[str, Any]) -> Path:
    return (
        cache_root
        / cell["condition"]
        / f"seed_{int(cell['seed']):03d}"
    )


def run_or_load_cell(
    prereg: dict[str, Any],
    cell: dict[str, Any],
    cache_root: Path,
) -> tuple[dict[str, Any], bool]:
    directory = cell_dir(cache_root, cell)
    manifest_path = directory / "t4_cell_manifest.json"
    contract = cell_contract(prereg, cell)
    contract_hash = canonical_sha256(contract)
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result_path = Path(manifest["seed_sweep_result_path"])
        if (
            manifest.get("cell_contract_sha256") == contract_hash
            and result_path.is_file()
            and sha256(result_path) == manifest["seed_sweep_result_sha256"]
        ):
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            return {"manifest": manifest, "payload": payload}, True

    directory.mkdir(parents=True, exist_ok=True)
    result_path = directory / "candidate_seed_sweep.json"
    report_path = directory / "CANDIDATE_SEED_SWEEP.md"
    log_path = directory / "stdout.log"
    policy = Path(prereg["input_paths"]["policy"])
    command = [
        sys.executable,
        str(Path(prereg["input_paths"]["seed_sweep"])),
        "--policies",
        f"BEST_WALK_ONNX_2={policy}",
        "--seeds",
        str(int(cell["seed"])),
        "--fit-json",
        prereg["input_paths"]["fit"],
        "--playground-path",
        prereg["playground"]["path"],
        "--env-python",
        sys.executable,
        "--command-x",
        str(float(cell["command_x_m_s"])),
        "--task",
        "flat_terrain_backlash",
        "--duration",
        "15.0",
        "--bridge-mode",
        cell["bridge_mode"],
        "--mode-name",
        cell["mode_name"],
        "--jax-platform",
        "cpu",
        "--sim-preflight-timeout-s",
        "600",
        "--closed-loop-timeout-s",
        "1800",
        "--output-dir",
        str(directory / "raw"),
        "--output-json",
        str(result_path),
        "--output-md",
        str(report_path),
        "--run",
    ]
    with log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2100,
            check=False,
        )
    if completed.returncode != 0 or not result_path.is_file():
        raise RuntimeError(
            f"T4 cell failed: {cell}; returncode={completed.returncode}; "
            f"log={log_path}"
        )
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    results = payload.get("results") or []
    if len(results) != 1 or int(results[0].get("seed")) != int(cell["seed"]):
        raise RuntimeError(f"T4 cell produced wrong result set: {cell}")
    manifest = {
        "schema_version": "open_duck.t4_baseline_gate_cell.v1",
        "cell_contract_sha256": contract_hash,
        "cell_contract": contract,
        "command": command,
        "seed_sweep_result_path": str(result_path),
        "seed_sweep_result_sha256": sha256(result_path),
        "stdout_log_path": str(log_path),
    }
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, manifest_path)
    return {"manifest": manifest, "payload": payload}, False


def extract_cell(cell: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    row = (result["payload"].get("results") or [])[0]
    summary = row.get("summary") or {}
    raw_eval_path = Path(row["result_json"])
    raw_eval = json.loads(raw_eval_path.read_text(encoding="utf-8"))
    closed = raw_eval.get("closed_loop_sim") or {}
    gate = closed.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    mode = (closed.get("modes") or {}).get(cell["mode_name"]) or {}
    reward = mode.get("reward") or {}
    return {
        "condition": cell["condition"],
        "command_x_m_s": float(cell["command_x_m_s"]),
        "bridge_mode": cell["bridge_mode"],
        "seed": int(cell["seed"]),
        "status": row.get("status"),
        "candidate_gate_status": summary.get("candidate_gate_status"),
        "termination_reason": summary.get("termination_reason"),
        "mean_local_vx_m_s": summary.get("mean_local_vx_m_s"),
        "track_ratio": summary.get("track_ratio"),
        "max_pitch_tracking_p95_rad": metrics.get(
            "max_pitch_tracking_p95_rad"
        ),
        "max_p95_velocity_limit_excess_rad_s": metrics.get(
            "max_sent_target_velocity_limit_excess_rad_s"
        ),
        "max_instant_velocity_limit_excess_rad_s": metrics.get(
            "max_sent_target_velocity_max_limit_excess_rad_s"
        ),
        "max_action_saturation_pct": metrics.get(
            "max_action_saturation_pct"
        ),
        "max_abs_body_pitch_p95_rad": metrics.get(
            "max_abs_body_pitch_p95_rad"
        ),
        "min_base_height_m": metrics.get("min_base_height_m"),
        "min_reward_mean": metrics.get("min_reward_mean", reward.get("mean")),
        "per_joint_sent_target_velocity_p95_rad_s": metrics.get(
            "per_joint_sent_target_velocity_p95_rad_s"
        ),
        "pitch_chain_velocity_limits_rad_s": (
            gate.get("thresholds") or {}
        ).get("pitch_chain_velocity_limits_rad_s"),
        "raw_eval_path": str(raw_eval_path),
        "raw_eval_sha256": sha256(raw_eval_path),
    }


def max_finite(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if finite(row.get(key))]
    return max(values) if values else None


def min_finite(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if finite(row.get(key))]
    return min(values) if values else None


def mean_finite(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if finite(row.get(key))]
    return mean(values) if values else None


def aggregate_condition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    joint_values: dict[str, float] = {}
    velocity_limits = None
    for row in rows:
        velocity_limits = velocity_limits or row.get(
            "pitch_chain_velocity_limits_rad_s"
        )
        for joint, value in (
            row.get("per_joint_sent_target_velocity_p95_rad_s") or {}
        ).items():
            if finite(value):
                joint_values[joint] = max(
                    joint_values.get(joint, -math.inf), float(value)
                )
    return {
        "cell_count": len(rows),
        "duration_complete_count": sum(
            row["termination_reason"] == "duration_complete" for row in rows
        ),
        "fall_count": sum(
            row["termination_reason"] != "duration_complete" for row in rows
        ),
        "mean_vx_m_s": mean_finite(rows, "mean_local_vx_m_s"),
        "mean_abs_vx_m_s": (
            mean(
                abs(float(row["mean_local_vx_m_s"]))
                for row in rows
                if finite(row.get("mean_local_vx_m_s"))
            )
            if all(finite(row.get("mean_local_vx_m_s")) for row in rows)
            else None
        ),
        "mean_track_ratio": mean_finite(rows, "track_ratio"),
        "min_seed_track_ratio": min_finite(rows, "track_ratio"),
        "max_pitch_tracking_p95_rad": max_finite(
            rows, "max_pitch_tracking_p95_rad"
        ),
        "max_p95_velocity_limit_excess_rad_s": max_finite(
            rows, "max_p95_velocity_limit_excess_rad_s"
        ),
        "max_instant_velocity_limit_excess_rad_s": max_finite(
            rows, "max_instant_velocity_limit_excess_rad_s"
        ),
        "max_action_saturation_pct": max_finite(
            rows, "max_action_saturation_pct"
        ),
        "max_abs_body_pitch_p95_rad": max_finite(
            rows, "max_abs_body_pitch_p95_rad"
        ),
        "min_base_height_m": min_finite(rows, "min_base_height_m"),
        "min_reward_mean": min_finite(rows, "min_reward_mean"),
        "per_joint_sent_target_velocity_p95_rad_s": joint_values,
        "pitch_chain_velocity_limits_rad_s": velocity_limits,
        "candidate_gate_status_counts": dict(
            Counter(row["candidate_gate_status"] for row in rows)
        ),
    }


def compare(value: Any, operator: str, threshold: float) -> bool:
    if not finite(value):
        return False
    if operator == "eq":
        return float(value) == float(threshold)
    if operator == "gte":
        return float(value) >= float(threshold)
    if operator == "lte":
        return float(value) <= float(threshold)
    raise ValueError(f"unsupported gate operator: {operator}")


def gate_rows(
    prereg: dict[str, Any],
    condition: dict[str, Any],
    aggregate: dict[str, Any],
) -> list[dict[str, Any]]:
    command = float(condition["command_x_m_s"])
    sections = ["coded_candidate_gate"]
    sections.append(
        "documented_semantic_x000"
        if command == 0.0
        else "documented_promotion_x008"
    )
    rows = []
    for section in sections:
        for gate in prereg["gate_contract"][section]:
            applies = gate.get("applies_if_abs_command_gte")
            if applies is not None and abs(command) < float(applies):
                continue
            observed = aggregate.get(gate["metric"])
            passed = compare(observed, gate["operator"], gate["threshold"])
            rows.append(
                {
                    "condition": condition["condition"],
                    "gate_source": section,
                    "metric": gate["metric"],
                    "operator": gate["operator"],
                    "threshold": gate["threshold"],
                    "observed": observed,
                    "passed": passed,
                    "required_action_if_failed": (
                        None
                        if passed
                        else "RELAX_TO_BASELINE_OR_RELABEL_STRETCH"
                    ),
                }
            )
    return rows


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# T4 BEST_WALK baseline versus all current gates",
        "",
        f"- Status: `{payload['status']}`",
        f"- Cells: `{payload['completed_cells']}/{payload['expected_cells']}`",
        f"- Failed gate rows: `{payload['failed_gate_row_count']}`",
        f"- Result SHA-256: `{payload['result_sha256']}`",
        "",
        "## Condition summary",
        "",
        "| condition | complete | falls | mean vx | mean |vx| | mean track | "
        "min track | tracking p95 | p95 vel excess | max vel excess | "
        "action sat % | pitch p95 | height min | reward min |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for condition in payload["conditions"]:
        item = condition["aggregate"]
        lines.append(
            f"| `{condition['condition']}` | "
            f"{item['duration_complete_count']}/8 | {item['fall_count']} | "
            f"{item['mean_vx_m_s']} | {item['mean_abs_vx_m_s']} | "
            f"{item['mean_track_ratio']} | {item['min_seed_track_ratio']} | "
            f"{item['max_pitch_tracking_p95_rad']} | "
            f"{item['max_p95_velocity_limit_excess_rad_s']} | "
            f"{item['max_instant_velocity_limit_excess_rad_s']} | "
            f"{item['max_action_saturation_pct']} | "
            f"{item['max_abs_body_pitch_p95_rad']} | "
            f"{item['min_base_height_m']} | {item['min_reward_mean']} |"
        )
    lines.extend(
        [
            "",
            "## Gate reconciliation",
            "",
            "| condition | source | metric | gate | observed | pass | required action |",
            "|---|---|---|---|---:|---|---|",
        ]
    )
    for row in payload["gate_rows"]:
        lines.append(
            f"| `{row['condition']}` | `{row['gate_source']}` | "
            f"`{row['metric']}` | {row['operator']} {row['threshold']} | "
            f"{row['observed']} | `{row['passed']}` | "
            f"`{row['required_action_if_failed']}` |"
        )
    lines.extend(
        [
            "",
            "## Required context",
            "",
            "- `docs/DUCK_STATUS.md` records that a step-0 random-init export "
            "passed x=0.0 while every trained checkpoint from step 153600 "
            "onward failed it. This is an objective diagnostic, not a numeric "
            "gate modification.",
            "- This offline table does not deploy a policy or authorize robot "
            "testing.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy\t4_baseline_all_gates_v1"
        ),
    )
    parser.add_argument("--max-new-cells", type=int, default=None)
    args = parser.parse_args()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_inputs(prereg)
    cache_root = args.cache_root.resolve()
    cells = []
    cache_hits = 0
    new_cells = 0
    for index, cell in enumerate(prereg["matrix"], start=1):
        if args.max_new_cells is not None and new_cells >= args.max_new_cells:
            break
        result, cached = run_or_load_cell(prereg, cell, cache_root)
        cache_hits += int(cached)
        new_cells += int(not cached)
        extracted = extract_cell(cell, result)
        cells.append(extracted)
        print(
            f"[{index}/{len(prereg['matrix'])}] {cell['condition']} "
            f"seed={cell['seed']} {'cache' if cached else 'run'} "
            f"status={extracted['candidate_gate_status']}",
            flush=True,
        )
    complete = len(cells) == len(prereg["matrix"])
    condition_results = []
    reconciled_rows = []
    if complete:
        for condition in prereg["conditions"]:
            selected = [
                row
                for row in cells
                if row["condition"] == condition["condition"]
            ]
            aggregate = aggregate_condition(selected)
            condition_results.append(
                {**condition, "aggregate": aggregate}
            )
            reconciled_rows.extend(
                gate_rows(prereg, condition, aggregate)
            )
        failed = [row for row in reconciled_rows if not row["passed"]]
        status = (
            "BASELINE_PASSES_ALL_CURRENT_FEASIBILITY_GATES"
            if not failed
            else "BASELINE_FAILS_CURRENT_FEASIBILITY_GATES"
        )
    else:
        failed = []
        status = "PARTIAL_T4_MATRIX_NO_DECISION"
    payload = {
        "schema_version": "open_duck.t4_baseline_all_gates_result.v1",
        "status": status,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "matrix_sha256": prereg["matrix_sha256"],
        "expected_cells": len(prereg["matrix"]),
        "completed_cells": len(cells),
        "cache_hits": cache_hits,
        "new_cells": new_cells,
        "cache_root": str(cache_root),
        "conditions": condition_results,
        "gate_rows": reconciled_rows,
        "failed_gate_row_count": len(failed),
        "failed_gate_rows": failed,
        "decision_rule": prereg["decision_rule"],
        "required_context_note": prereg["required_context_note"],
        "authority": prereg["authority"],
    }
    payload["result_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if complete:
        write_markdown(payload)
    print(status)
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
