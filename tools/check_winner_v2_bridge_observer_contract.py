#!/usr/bin/env python3
"""Replay the frozen composite traces through the fitted bridge observer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from actuator_bridge_model import ActuatorBridgeModel, JOINT_NAMES, params_from_fit


ROOT = Path(__file__).resolve().parents[1]
TRACE_ROOT = ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_eval_traces"
FIT_PATHS = {
    "p30": ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
}
EXPECTED_STEPS = (512000, 1024000)
EXPECTED_COMMANDS = ("x0.000", "x0.074", "x0.077", "x0.080")
ACTION_SCALE_RAD = 0.25
DT_S = 0.02
TOLERANCE_RAD = 1.0e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    traces: list[dict] = []
    homes: list[np.ndarray] = []
    total_rows = 0
    max_error = 0.0
    failures: list[str] = []

    for fit_name, fit_path in FIT_PATHS.items():
        fit = json.loads(fit_path.read_text())
        params = params_from_fit(fit)
        for step in EXPECTED_STEPS:
            directory = TRACE_ROOT / fit_name / f"T2_EQUAL_{step}"
            for command in EXPECTED_COMMANDS:
                matches = sorted(directory.glob(f"{command}_seed*_T2_EQUAL_{step}.jsonl"))
                if len(matches) != 1:
                    failures.append(f"expected_one_trace:{fit_name}:{step}:{command}:{len(matches)}")
                    continue
                path = matches[0]
                rows = [json.loads(line) for line in path.read_text().splitlines() if line]
                if len(rows) != 600:
                    failures.append(f"expected_600_rows:{path.relative_to(ROOT)}:{len(rows)}")
                    continue
                first_sent = np.asarray(rows[0]["sent_target_rad"], dtype=float)
                first_action = np.asarray(rows[0]["action_w_delay"], dtype=float)
                home = first_sent - ACTION_SCALE_RAD * first_action
                homes.append(home)
                observer = ActuatorBridgeModel(params, initial_target=home)
                trace_error = 0.0
                for index, row in enumerate(rows):
                    sent = np.asarray(row["sent_target_rad"], dtype=float)
                    recorded = np.asarray(row["applied_target_rad"], dtype=float)
                    if sent.shape != (14,) or recorded.shape != (14,):
                        failures.append(f"shape:{path.relative_to(ROOT)}:{index}")
                        continue
                    if not np.all(np.isfinite(sent)) or not np.all(np.isfinite(recorded)):
                        failures.append(f"nonfinite:{path.relative_to(ROOT)}:{index}")
                        continue
                    predicted = observer.step(sent, DT_S)
                    error = float(np.max(np.abs(predicted - recorded)))
                    trace_error = max(trace_error, error)
                    max_error = max(max_error, error)
                total_rows += len(rows)
                traces.append(
                    {
                        "fit": fit_name,
                        "step": step,
                        "command": command,
                        "path": str(path.relative_to(ROOT)),
                        "sha256": sha256(path),
                        "rows": len(rows),
                        "max_abs_error_rad": trace_error,
                    }
                )

    home_error = 0.0
    if homes:
        reference_home = homes[0]
        home_error = max(float(np.max(np.abs(home - reference_home))) for home in homes)
    else:
        reference_home = np.zeros(14, dtype=float)
        failures.append("no_home_vectors")

    checks = {
        "all_16_traces_present": len(traces) == 16,
        "exactly_9600_rows": total_rows == 9600,
        "joint_order_is_14d": len(JOINT_NAMES) == 14,
        "home_vectors_exact": home_error <= TOLERANCE_RAD,
        "observer_reconstructs_every_target": max_error <= TOLERANCE_RAD,
        "no_row_failures": not failures,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V2_BRIDGE_OBSERVER_CONTRACT"
        if not failed_checks
        else "HOLD_WINNER_V2_BRIDGE_OBSERVER_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v2_bridge_observer_contract.v1",
        "status": status,
        "decision": (
            "PIN_EXTERNAL_FITTED_BRIDGE_OBSERVER_FOR_OBS83_97"
            if not failed_checks
            else "STOP_C1_OBSERVER_MISMATCH"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "failures": failures,
        "contract": {
            "observation_dim": 115,
            "applied_target_slice": [83, 97],
            "previous_action_state_dim": 14,
            "action_scale_rad": ACTION_SCALE_RAD,
            "dt_s": DT_S,
            "tolerance_rad": TOLERANCE_RAD,
            "joint_names": JOINT_NAMES,
            "home_target_rad": reference_home.tolist(),
            "fit_sha256": {name: sha256(path) for name, path in FIT_PATHS.items()},
        },
        "measurements": {
            "trace_count": len(traces),
            "row_count": total_rows,
            "max_home_vector_error_rad": home_error,
            "max_applied_target_reconstruction_error_rad": max_error,
        },
        "traces": traces,
        "authority": {
            "runtime_integration": False,
            "hardware_fit_selection": False,
            "gate5": False,
            "robot_or_rdk_x5": False,
        },
    }
    out_json = ROOT / "outputs/analysis/winner_v2_bridge_observer_contract.json"
    out_md = ROOT / "outputs/analysis/WINNER_V2_BRIDGE_OBSERVER_CONTRACT_20260716.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(
        "# Winner v2 Bridge-Observer Contract\n\n"
        f"Status: `{status}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- Frozen traces: {len(traces)}/16\n"
        f"- Frozen rows: {total_rows}/9600\n"
        f"- Maximum home-vector disagreement: {home_error:.12g} rad\n"
        f"- Maximum applied-target reconstruction error: {max_error:.12g} rad\n\n"
        "The winner ONNX interface carries only the 115-D observation and a 14-D "
        "bounded-action state. It does not carry the per-joint delay queues and lag "
        "state. Therefore obs[83:97] is an external host responsibility. On pass, "
        "the v2 contract pins the existing fitted bridge forward observer to that "
        "slot, initialized at home and advanced once after each sent target.\n\n"
        "This does not integrate the runtime, choose a hardware fit, authorize Gate "
        "5, or clear the robot.\n"
    )
    if failed_checks:
        raise SystemExit(f"contract failed: {failed_checks}")


if __name__ == "__main__":
    main()
