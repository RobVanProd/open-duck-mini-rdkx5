#!/usr/bin/env python3
"""Run the frozen 144-cell reporting-only full-observation replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from check_ground_up_torso_com_full_obs_contract import (
    EVALUATOR,
    MATRIX_ROOT,
    ORIGINAL_REPO,
    REPO,
    canonical_manifest,
    matrix_identity,
    normalize_behavior,
    sha256,
    validate_matrix,
)


def command_for(source: dict[str, Any], output: Path, trace_dir: Path) -> list[str]:
    inputs = source["inputs"]
    command = [
        sys.executable, str(EVALUATOR),
        "--policy", inputs["policy"],
        "--playground-root", inputs["playground_root"],
        "--fit", inputs["fit"],
        "--reference-feature-table", inputs["reference_feature_table"],
        "--reference-start-phase", str(inputs["reference_start_phase"]),
        "--expected-observation-dim", str(inputs["expected_observation_dim"]),
        "--policy-state-input-names", ",".join(inputs["policy_state_input_names"]),
        "--policy-state-output-names", ",".join(inputs["policy_state_output_names"]),
        "--trace-dir", str(trace_dir),
        "--trace-full-obs",
        "--commands", ",".join(str(value) for value in inputs["commands"]),
        "--seeds", ",".join(str(value) for value in inputs["seeds"]),
        "--duration-s", str(inputs["duration_s"]),
        "--minimum-emergence-duration-s", str(inputs["minimum_emergence_duration_s"]),
        "--task", inputs["task"],
        "--reset-mode", inputs["reset_mode"],
        "--policy-action-rate-limit-joint-indices", ",".join(
            str(value) for value in inputs["policy_action_rate_limit_joint_indices"]
        ),
        "--output-json", str(output),
    ]
    if inputs["policy_applied_target_observation"]:
        command.append("--policy-applied-target-observation")
    if inputs["eval_dynamics_override"] is not None:
        command.extend([
            "--eval-dynamics-override-json",
            json.dumps(inputs["eval_dynamics_override"], sort_keys=True, separators=(",", ":")),
        ])
    if inputs["policy_action_rate_limit_rad_s"] is not None:
        command.extend([
            "--policy-action-rate-limit-rad-s",
            str(inputs["policy_action_rate_limit_rad_s"]),
        ])
    if inputs["policy_action_rate_limit_values"]:
        command.extend([
            "--policy-action-rate-limit-values",
            ",".join(str(value) for value in inputs["policy_action_rate_limit_values"]),
        ])
    return command


def validate_full_traces(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for run in payload["runs"]:
        path = Path(run["trace_jsonl"])
        records = [json.loads(line) for line in path.read_text().splitlines()]
        if not records or [record.get("tick") for record in records] != list(range(len(records))):
            raise ValueError(f"noncontiguous or empty trace: {path}")
        for record in records:
            obs = record.get("obs_state")
            if not isinstance(obs, list) or len(obs) != 115:
                raise ValueError(f"missing obs_state[115]: {path} tick {record.get('tick')}")
            if not all(isinstance(value, (int, float)) and value == value and abs(value) != float("inf") for value in obs):
                raise ValueError(f"nonfinite observation: {path} tick {record.get('tick')}")
        rows.append({
            "path": str(path),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "rows": len(records),
            "command_x": run["command_x"],
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ORIGINAL_REPO / "outputs/analysis/ground_up_torso_com_full_obs_replay",
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("exact CPU environment required")
    contract = json.loads(args.contract.read_text())
    if contract.get("status") != "PASS_TORSO_COM_FULL_OBS_STUDY_CONTRACT":
        raise RuntimeError("passing committed contract required")
    expected_tool_hash = contract["details"]["study_tool_hashes"]["replay"]
    if sha256(Path(__file__)) != expected_tool_hash:
        raise RuntimeError("replay tool changed after contract")

    output_root = args.output_root.resolve()
    matrix_out = output_root / "matrices"
    trace_root = output_root / "traces"
    matrix_out.mkdir(parents=True, exist_ok=True)
    trace_rows: list[dict[str, Any]] = []
    matrix_rows: list[dict[str, Any]] = []
    env = dict(os.environ)
    env.update({"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu"})

    source_paths = sorted(MATRIX_ROOT.glob("*.json"))
    if len(source_paths) != 36:
        raise RuntimeError("source matrix count changed")
    for index, source_path in enumerate(source_paths, start=1):
        identity = validate_matrix(source_path)
        source = json.loads(source_path.read_text())
        condition, arm, step, fit = matrix_identity(source_path)
        trace_dir = trace_root / condition / arm / str(step) / fit
        output = matrix_out / source_path.name
        temporary = output.with_suffix(".tmp.json")
        if output.exists():
            if not args.resume:
                raise RuntimeError(f"existing output requires --resume: {output}")
            replay = json.loads(output.read_text())
        else:
            if temporary.exists():
                raise RuntimeError(f"partial matrix requires deliberate inspection: {temporary}")
            print(f"[{index}/36] {source_path.name}", flush=True)
            subprocess.run(command_for(source, temporary, trace_dir), cwd=REPO, env=env, check=True)
            replay = json.loads(temporary.read_text())
            if normalize_behavior(source) != normalize_behavior(replay):
                raise RuntimeError(f"behavior reproduction mismatch: {source_path.name}")
            temporary.replace(output)
        if normalize_behavior(source) != normalize_behavior(replay):
            raise RuntimeError(f"saved behavior reproduction mismatch: {source_path.name}")
        rows = validate_full_traces(replay)
        for row in rows:
            row.update(identity)
        trace_rows.extend(rows)
        matrix_rows.append({
            **identity,
            "path": str(output),
            "sha256": sha256(output),
            "bytes": output.stat().st_size,
            "exact_behavior_reproduction": True,
        })

    if len(matrix_rows) != 36 or len(trace_rows) != 144:
        raise RuntimeError("campaign cardinality mismatch")
    canonical_lines = "".join(
        f"{Path(row['path']).relative_to(output_root).as_posix()}\t{row['sha256']}\n"
        for row in sorted(trace_rows, key=lambda item: item["path"])
    )
    payload = {
        "schema_version": "ground_up_torso_com_full_obs_replay.v1",
        "status": "PASS_EXACT_FULL_OBSERVATION_REPLAY",
        "source_contract_sha256": sha256(args.contract),
        "source_matrix_manifest_sha256": canonical_manifest(MATRIX_ROOT, "*.json")[0],
        "matrices": matrix_rows,
        "traces": trace_rows,
        "trace_manifest_sha256": hashlib.sha256(canonical_lines.encode()).hexdigest(),
        "counts": {
            "matrices": len(matrix_rows),
            "cells": len(trace_rows),
            "trace_bytes": sum(row["bytes"] for row in trace_rows),
            "trace_rows": sum(row["rows"] for row in trace_rows),
        },
        "execution": {
            "cpu_only": True,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "jax_platforms": os.environ.get("JAX_PLATFORMS"),
            "training": False,
            "robot_or_rdk": False,
        },
    }
    result = output_root / "replay_manifest.json"
    result.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], **payload["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
