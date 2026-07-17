#!/usr/bin/env python3
"""CPU contract for the default-off independent policy-observer bridge."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

from actuator_bridge_model import ActuatorBridgeModel, params_from_fit


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/home/lsd/robots/envs/ground-up-control/bin/python")
EVALUATOR = ROOT / "tools/evaluate_ground_up_policy.py"
CLOSED_LOOP = ROOT / "tools/closed_loop_sim_eval.py"
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
POLICY = ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx"
P30 = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
P31 = ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json"
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
BASELINE = ROOT / "outputs/analysis/winner_v2_observer_cross_fit_prechange_baseline.json"
HOME = np.asarray(
    [0.002, 0.053, -0.630, 1.368, -0.784, 0, 0, 0, 0, -0.003, -0.065, 0.635, 1.379, -0.796],
    dtype=float,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_result(path: Path) -> bytes:
    payload = json.loads(path.read_text())

    def clean(value):
        if isinstance(value, dict):
            return {
                key: clean(item)
                for key, item in value.items()
                if key not in {"wall_clock_s", "trace_jsonl"}
            }
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    selected = clean(
        {
            "status": payload["status"],
            "aggregate": payload["aggregate"],
            "runs": payload["runs"],
        }
    )
    return (json.dumps(selected, sort_keys=True, separators=(",", ":")) + "\n").encode()


def run_eval(directory: Path, *, observer: Path | None, duration_s: float, full_obs: bool) -> tuple[dict, Path]:
    trace_dir = directory / "traces"
    trace_dir.mkdir(parents=True)
    result_path = directory / "eval.json"
    command = [
        str(PYTHON), str(EVALUATOR),
        "--policy", str(POLICY),
        "--playground-root", str(PLAYGROUND),
        "--fit", str(P30),
        "--reference-feature-table", str(REFERENCE),
        "--reference-start-phase", "0",
        "--expected-observation-dim", "115",
        "--policy-state-input-names", "previous_action",
        "--policy-state-output-names", "previous_action_out",
        "--policy-applied-target-observation",
        "--trace-dir", str(trace_dir),
        "--commands", "0.077",
        "--seeds", "167931544",
        "--duration-s", str(duration_s),
        "--minimum-emergence-duration-s", "1.08",
        "--task", "flat_terrain_backlash",
        "--reset-mode", "home-support",
        "--output-json", str(result_path),
    ]
    if observer is not None:
        command.extend(["--policy-observer-fit", str(observer)])
    if full_obs:
        command.append("--trace-full-obs")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu"},
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + "\n" + completed.stderr)
    traces = list(trace_dir.glob("*.jsonl"))
    if len(traces) != 1:
        raise RuntimeError(f"expected one trace, got {len(traces)}")
    return json.loads(result_path.read_text()), traces[0]


def main() -> int:
    baseline = json.loads(BASELINE.read_text())
    with tempfile.TemporaryDirectory(prefix="winner_v2_observer_contract_") as temp:
        temp = Path(temp)
        default_result, default_trace = run_eval(
            temp / "default_off", observer=None, duration_s=12.0, full_obs=False
        )
        enabled_result, enabled_trace = run_eval(
            temp / "enabled", observer=P31, duration_s=0.16, full_obs=True
        )
        default_canonical_hash = hashlib.sha256(
            canonical_result(temp / "default_off/eval.json")
        ).hexdigest()
        rows = [json.loads(line) for line in enabled_trace.read_text().splitlines() if line]

    plant = ActuatorBridgeModel(
        params_from_fit(json.loads(P30.read_text())), initial_target=HOME
    )
    observer = ActuatorBridgeModel(
        params_from_fit(json.loads(P31.read_text())), initial_target=HOME
    )
    max_plant_reconstruction = 0.0
    max_observer_reconstruction = 0.0
    max_observation_timing = 0.0
    max_plant_observer_separation = 0.0
    previous_observer = HOME.copy()
    for row in rows:
        obs = np.asarray(row["obs_state"], dtype=float)
        sent = np.asarray(row["sent_target_rad"], dtype=float)
        recorded_plant = np.asarray(row["applied_target_rad"], dtype=float)
        recorded_observer = np.asarray(
            row["policy_observer_applied_target_rad"], dtype=float
        )
        max_observation_timing = max(
            max_observation_timing,
            float(np.max(np.abs(obs[83:97] - previous_observer))),
        )
        expected_plant = plant.step(sent, 0.02)
        expected_observer = observer.step(sent, 0.02)
        max_plant_reconstruction = max(
            max_plant_reconstruction,
            float(np.max(np.abs(recorded_plant - expected_plant))),
        )
        max_observer_reconstruction = max(
            max_observer_reconstruction,
            float(np.max(np.abs(recorded_observer - expected_observer))),
        )
        max_plant_observer_separation = max(
            max_plant_observer_separation,
            float(np.max(np.abs(recorded_plant - recorded_observer))),
        )
        previous_observer = recorded_observer

    source = CLOSED_LOOP.read_text()
    checks = {
        "prechange_evaluator_hash_frozen": baseline["evaluator_sha256"]
        == "f35d35789d50baf557d3b2427dfe326ccc60c7607e79069e5a9dd51f2f01f8d6",
        "default_off_trace_byte_identical": sha256(default_trace)
        == baseline["raw_trace_sha256"],
        "default_off_canonical_result_exact": default_canonical_hash
        == baseline["canonical_result_sha256"],
        "default_off_status_preserved": default_result["status"]
        == "PASS_GAIT_EMERGENCE_CHECKPOINT",
        "enabled_eight_rows_recorded": len(rows) == 8,
        "enabled_result_reports_separate_observer": enabled_result["runs"][0][
            "policy_observer_fit_enabled"
        ]
        is True,
        "plant_bridge_reconstructed_exactly": max_plant_reconstruction <= 1e-12,
        "observer_bridge_reconstructed_exactly": max_observer_reconstruction <= 1e-12,
        "observation_uses_previous_observer_state": max_observation_timing <= 1e-7,
        "contract_exercises_distinct_bridge_states": max_plant_observer_separation
        >= 1e-5,
        "feature_is_default_off": "policy_observer_fit: Mapping[str, Any] | None = None"
        in source,
        "physics_and_observation_targets_are_separate_arguments": (
            "policy_observer_applied_target" in source
            and "mjx_env.step(env.mjx_model, state.data, applied_target" in source
        ),
        "cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu",
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V2_OBSERVER_CROSS_FIT_DEFAULT_OFF_CONTRACT"
        if not failed
        else "HOLD_WINNER_V2_OBSERVER_CROSS_FIT_DEFAULT_OFF_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v2_observer_cross_fit_default_off_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "measurements": {
            "default_off_trace_sha256": sha256(default_trace),
            "default_off_canonical_result_sha256": default_canonical_hash,
            "enabled_rows": len(rows),
            "max_plant_reconstruction_error_rad": max_plant_reconstruction,
            "max_observer_reconstruction_error_rad": max_observer_reconstruction,
            "max_observation_timing_error_rad": max_observation_timing,
            "max_plant_observer_separation_rad": max_plant_observer_separation,
        },
        "hashes": {
            "evaluator_postchange": sha256(CLOSED_LOOP),
            "policy": sha256(POLICY),
            "plant_fit": sha256(P30),
            "observer_fit": sha256(P31),
            "reference": sha256(REFERENCE),
        },
        "authority": {
            "run_32_formal_cpu_cells": not failed,
            "training_gpu_hosted_robot_rdk_gate5": False,
        },
    }
    out_json = ROOT / "outputs/analysis/winner_v2_observer_cross_fit_default_off_contract.json"
    out_md = ROOT / "outputs/analysis/WINNER_V2_OBSERVER_CROSS_FIT_DEFAULT_OFF_CONTRACT_20260717.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(
        "# Winner-v2 Observer Cross-Fit Default-Off Contract\n\n"
        f"Status: `{status}`\n\n"
        f"- Default-off trace SHA-256: `{sha256(default_trace)}`\n"
        f"- Default-off canonical result SHA-256: `{default_canonical_hash}`\n"
        f"- Enabled implementation rows: {len(rows)}\n"
        f"- Plant reconstruction maximum error: {max_plant_reconstruction:.12g} rad\n"
        f"- Observer reconstruction maximum error: {max_observer_reconstruction:.12g} rad\n"
        f"- Observation timing maximum error: {max_observation_timing:.12g} rad\n"
        f"- Exercised plant/observer separation: {max_plant_observer_separation:.12g} rad\n"
        f"- Failed checks: `{failed}`\n\n"
        "Passing authorizes only the preregistered 32-cell CPU cross-fit matrix. "
        "It does not authorize hardware, deployment, Gate 5, training or accelerators.\n"
    )
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
