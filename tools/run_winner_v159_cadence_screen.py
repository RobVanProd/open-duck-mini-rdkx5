#!/usr/bin/env python3
"""Run V159's single preregistered CPU-only cadence falsifier."""

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
PREREG = ANALYSIS / "winner_v159_cadence_screen_preregistration.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
OUTPUT = ANALYSIS / "winner_v159_cadence_screen_result.json"
MARKDOWN = ANALYSIS / "WINNER_V159_CADENCE_SCREEN_RESULT_20260725.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def phase_audit(path: Path, factor: float) -> dict[str, object]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    phases = np.asarray(
        [row["obs_state"][99:101] for row in rows], dtype=np.float64
    )
    angles = np.unwrap(np.arctan2(phases[:, 1], phases[:, 0]))
    increments = np.diff(angles)
    expected = factor * 2.0 * np.pi / 27.0
    errors = np.abs(increments - expected)
    return {
        "rows": len(rows),
        "first_phase": phases[0].tolist(),
        "expected_increment_rad": float(expected),
        "median_increment_rad": float(np.median(increments)),
        "maximum_increment_error_rad": float(np.max(errors)),
        "checks": {
            "rows_exact_600": len(rows) == 600,
            "first_phase_exact": bool(
                np.array_equal(phases[0], np.asarray([1.0, 0.0]))
            ),
            "all_increments_match_factor": bool(
                np.max(errors) <= 2.0e-6
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V159: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    paths = {
        "builder": TOOLS
        / "build_winner_v159_cadence_screen_preregistration.py",
        "composer": TOOLS / "compose_winner_v159_cadence_evaluator.py",
        "source_evaluator_manifest": Path(
            manifest["source"]["manifest_path"]
        ),
        "source_evaluator": Path(manifest["source"]["path"]),
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "v140_result": V140_RESULT,
        "v141_runner": TOOLS
        / "run_winner_v141_projected_final_behavior.py",
        "v158_reporting_correction": ANALYSIS
        / "winner_v158_x077_shadow_census_reporting_correction.json",
        "phase_advance_result": ROOT
        / "docs/PHASE2_RIGHT_SWING_PHASE_ADVANCE_RESULT.md",
        "runtime": ROOT / "runtime/scripts/v2_rl_walk_mujoco.py",
        "selected_policy": policy,
    }
    observed_hashes = {
        name: sha256(path) for name, path in paths.items()
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V159_CADENCE_SCREEN"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V159 preregistration changed")
    row = prereg["matrix"]["row"]
    factor = float(row["phase_frequency_factor"])
    evaluator = load_evaluator(evaluator_path)
    original_run = evaluator.run_closed_loop_sim

    def run_at_fixed_cadence(config):
        return original_run(
            dataclasses.replace(
                config, phase_frequency_factor=factor
            )
        )

    evaluator.run_closed_loop_sim = run_at_fixed_cadence
    run_root.mkdir(parents=True)
    traces_root = run_root / "traces"
    cells_root = run_root / "cells"
    traces_root.mkdir()
    cells_root.mkdir()
    trace_path = traces_root / "v159_v140_p30_x0.077_seed167931544.jsonl"
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cell = run_cell(
        evaluator=evaluator,
        row=row,
        policy=policy,
        playground=Path(v126["external_inputs"]["playground"]),
        base_prereg=base_prereg,
        trace_path=trace_path,
        cpu_only=cpu_only,
    )
    cell_path = cells_root / "v159_v140_p30_x0.077_seed167931544.json"
    cell_path.write_text(
        json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    phase = phase_audit(trace_path, factor)
    checks = {
        "cpu_only": cpu_only,
        "cell_pass": bool(cell["pass"]),
        "phase_contract": all(phase["checks"].values()),
        "one_cell_only": True,
        "no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v159.cadence_screen_result.v1",
        "status": (
            "PASS_WINNER_V159_CADENCE_SCREEN"
            if not failed
            else "HOLD_WINNER_V159_CADENCE_SCREEN"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
            "runner": sha256(Path(__file__).resolve()),
        },
        "cadence": {
            "factor": factor,
            "offset": float(row["phase_frequency_factor_offset"]),
            "audit": phase,
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
            "EARN_V160_FIXED_CADENCE_DUAL_CHECKPOINT_NOMINAL"
            if not failed
            else "CLOSE_POSTEXPORT_CADENCE_MECHANISM_NO_FACTOR_SWEEP"
        ),
        "authority": {
            "cpu_behavior_screen": True,
            "training": False,
            "hosted_training": False,
            "runtime_config_change": False,
            "candidate_selection": False,
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
        "# Winner V159 cadence screen result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Cadence factor: `{factor}` (offset "
        f"`{row['phase_frequency_factor_offset']}`).\n"
        f"- Cell pass: `{cell['pass']}`; peak torque: "
        f"`{cell.get('torque_gate', {}).get('worst_peak_torque_nm')}` "
        "N·m.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- One CPU-only cell; no sweep, training, Colab, runtime edit, "
        "deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
