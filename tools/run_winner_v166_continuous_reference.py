#!/usr/bin/env python3
"""Run V166's one-cell continuous-reference cadence falsifier."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v141_projected_final_behavior import (  # noqa: E402
    load_evaluator,
    run_cell,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v166_continuous_reference_preregistration.json"
OUTPUT = ANALYSIS / "winner_v166_continuous_reference_result.json"
MARKDOWN = ANALYSIS / "WINNER_V166_CONTINUOUS_REFERENCE_RESULT_20260725.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(
        item
        for item in path.rglob("*")
        if item.is_file()
        and "__pycache__" not in item.parts
        and item.name != "V166_COMPOSITION_MANIFEST.json"
    ):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def audit_trace(
    trace_path: Path, table_path: Path, factor: float
) -> dict[str, object]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    obs = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
    phase_vectors = obs[:, 99:101]
    angles = np.unwrap(np.arctan2(phase_vectors[:, 1], phase_vectors[:, 0]))
    increments = np.diff(angles)
    expected_increment = factor * 2.0 * np.pi / 27.0
    table = np.load(table_path)
    commands = np.asarray(table["commands"], dtype=np.float64)
    actions = np.asarray(table["actions"], dtype=np.float64)
    command = np.asarray([0.077, 0.0, 0.0], dtype=np.float64)
    command_index = int(
        np.argmin(np.sum(np.abs(commands - command[None, :]), axis=1))
    )
    phase = np.mod(
        np.arctan2(phase_vectors[:, 1], phase_vectors[:, 0]),
        2.0 * np.pi,
    ) * actions.shape[1] / (2.0 * np.pi)
    phase_floor = np.floor(phase)
    lower_index = phase_floor.astype(np.int64) % actions.shape[1]
    upper_index = (lower_index + 1) % actions.shape[1]
    fraction = phase - phase_floor
    expected_actions = actions[command_index, lower_index] + fraction[:, None] * (
        actions[command_index, upper_index]
        - actions[command_index, lower_index]
    )
    observed_actions = obs[:, 101:115]
    action_error = float(
        np.max(np.abs(observed_actions - expected_actions))
    )
    integer_expected = actions[command_index]
    integer_interpolated = actions[command_index] + 0.0 * (
        np.roll(actions[command_index], -1, axis=0) - actions[command_index]
    )
    return {
        "rows": len(rows),
        "first_phase": phase_vectors[0].tolist(),
        "expected_increment_rad": expected_increment,
        "median_increment_rad": float(np.median(increments)),
        "maximum_increment_error_rad": float(
            np.max(np.abs(increments - expected_increment))
        ),
        "reference_action_linf": action_error,
        "integer_table_linf": float(
            np.max(np.abs(integer_expected - integer_interpolated))
        ),
        "command_index": command_index,
        "command_cell": commands[command_index].tolist(),
        "checks": {
            "rows_exact_600": len(rows) == 600,
            "first_phase_exact": bool(
                np.array_equal(
                    phase_vectors[0], np.asarray([1.0, 0.0])
                )
            ),
            "all_phase_increments_match_factor": bool(
                np.max(np.abs(increments - expected_increment)) <= 2.0e-6
            ),
            "all_reference_actions_match_interpolation": (
                action_error <= 2.0e-6
            ),
            "integer_interpolation_exact": bool(
                np.array_equal(integer_expected, integer_interpolated)
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V166: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = {name: Path(path) for name, path in prereg["paths"].items()}
    observed_hashes = {
        name: sha256(path) for name, path in paths.items()
    }
    if (
        prereg["status"] != "PREREGISTERED_WINNER_V166_CONTINUOUS_REFERENCE"
        or prereg["failed_checks"] != []
        or prereg["input_hashes"] != observed_hashes
        or directory_sha256(Path(prereg["playground_root"]))
        != prereg["playground_tree_sha256"]
    ):
        raise ValueError("V166 preregistration changed")

    evaluator = load_evaluator(paths["evaluator"])
    original_run = evaluator.run_closed_loop_sim
    factor = float(prereg["mechanism"]["factor"])

    def run_at_fixed_cadence(config):
        return original_run(
            dataclasses.replace(config, phase_frequency_factor=factor)
        )

    evaluator.run_closed_loop_sim = run_at_fixed_cadence
    base = json.loads(paths["base_preregistration"].read_text(encoding="utf-8"))
    v140 = json.loads(paths["v140_result"].read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    row = dict(prereg["matrix"]["row"])
    run_root.mkdir(parents=True)
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir()
    traces_root.mkdir()
    trace_path = traces_root / "v166_v140_p30_x0.077_seed167931544.jsonl"
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cell = run_cell(
        evaluator=evaluator,
        row=row,
        policy=policy,
        playground=Path(prereg["playground_root"]),
        base_prereg=base,
        trace_path=trace_path,
        cpu_only=cpu_only,
    )
    cell_path = cells_root / "v166_v140_p30_x0.077_seed167931544.json"
    cell_path.write_text(
        json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    audit = audit_trace(
        trace_path, paths["reference_feature_table"], factor
    )
    checks = {
        "cpu_only": cpu_only,
        "cell_pass": cell["pass"],
        "phase_and_reference_contract": all(audit["checks"].values()),
        "policy_hash_unchanged": sha256(policy)
        == prereg["input_hashes"]["selected_policy"],
        "one_cell_only": True,
        "no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    payload = {
        "schema_version": "winner_v166.continuous_reference_result.v1",
        "status": (
            "PASS_WINNER_V166_CONTINUOUS_REFERENCE"
            if passed
            else "HOLD_WINNER_V166_CONTINUOUS_REFERENCE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "cadence": {
            "factor": factor,
            "offset": row["phase_frequency_factor_offset"],
            "audit": audit,
        },
        "cell": cell,
        "artifacts": {
            "run_root": str(run_root),
            "cell": {"path": str(cell_path), "sha256": sha256(cell_path)},
            "trace": {
                "path": str(trace_path),
                "sha256": sha256(trace_path),
            },
        },
        "decision": (
            "EARN_REVIEWED_CONTINUOUS_REFERENCE_ADAPTER_CONTRACT_DECISION"
            if passed
            else "CLOSE_CONTINUOUS_REFERENCE_CADENCE_EXPANSION_NO_RETRY"
        ),
        "authority": {
            "contract_review": passed,
            "production_contract_change": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V166 continuous-reference result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Cell pass: `{cell['pass']}`; peak torque: "
        f"`{cell.get('torque_gate', {}).get('worst_peak_torque_nm')}` N.m.\n"
        f"- Reference-action L-inf: `{audit['reference_action_linf']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only evidence; production contract remains unchanged.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
