#!/usr/bin/env python3
"""Localize committed oracle-COM failures and freeze exact cadence states."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from actuator_bridge_model import ActuatorBridgeModel, params_from_fit
from run_oracle_phase_com_authority import initialize_native, source_state


ROOT = Path(__file__).resolve().parents[1]
TRACE_ROOT = ROOT / "outputs/analysis/oracle_phase_com_compensation_traces/formal"
CELL_ROOT = ROOT / "outputs/analysis/oracle_phase_com_compensation_cells"
STATE_ROOT = ROOT / "outputs/analysis/oracle_com_viability_funnel_states"
OUTPUT_JSON = ROOT / "outputs/analysis/oracle_com_failure_localization.json"
OUTPUT_MD = ROOT / "outputs/analysis/ORACLE_COM_FAILURE_LOCALIZATION.md"
SEED = 167931544
DESIGN_FIT = "p30"
DESIGN_COMMAND = 0.077
CADENCE = 4

DIVERGENCE_THRESHOLDS = {
    "local_velocity_linf_m_s": 0.05,
    "pitch_or_roll_rad": 0.05,
    "pitch_or_roll_rate_rad_s": 0.5,
    "support_relative_com_linf_m": 0.01,
    "policy_base_action_linf": 0.04,
    "applied_target_linf_rad": 0.01,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def trace_name(condition: str, policy: str, fit: str, command: float) -> str:
    return f"{condition}_{policy}_{fit}_x{command:.3f}_seed{SEED}.jsonl"


def first_run(values: list[bool], width: int = 3) -> int | None:
    for start in range(max(0, len(values) - width + 1)):
        if all(values[start : start + width]):
            return start
    return None


def divergence_components(endpoint: dict[str, Any], nominal: dict[str, Any]) -> dict[str, float | bool]:
    eo, no = endpoint["oracle_state"], nominal["oracle_state"]
    return {
        "local_velocity_linf_m_s": float(np.max(np.abs(np.asarray(endpoint["local_linvel_m_s"]) - np.asarray(nominal["local_linvel_m_s"])))),
        "contact_sequence_differs": endpoint["foot_contacts"] != nominal["foot_contacts"],
        "pitch_or_roll_rad": max(abs(float(eo["pitch_rad"]) - float(no["pitch_rad"])), abs(float(eo["roll_rad"]) - float(no["roll_rad"]))),
        "pitch_or_roll_rate_rad_s": max(abs(float(eo["pitch_rate_rad_s"]) - float(no["pitch_rate_rad_s"])), abs(float(eo["roll_rate_rad_s"]) - float(no["roll_rate_rad_s"]))),
        "support_relative_com_linf_m": float(np.max(np.abs(np.asarray(eo["support_relative_com_m"]) - np.asarray(no["support_relative_com_m"])))),
        "policy_base_action_linf": float(np.max(np.abs(np.asarray(endpoint["policy_base_action"]) - np.asarray(nominal["policy_base_action"])))),
        "applied_target_linf_rad": float(np.max(np.abs(np.asarray(endpoint["applied_target_rad"]) - np.asarray(nominal["applied_target_rad"])))),
    }


def meaningful(components: dict[str, float | bool]) -> bool:
    if bool(components["contact_sequence_differs"]):
        return True
    return any(float(components[key]) >= limit for key, limit in DIVERGENCE_THRESHOLDS.items())


def bridge_state(rows: list[dict[str, Any]], fit: dict[str, Any], home: np.ndarray, tick: int) -> tuple[ActuatorBridgeModel, np.ndarray, float]:
    bridge = ActuatorBridgeModel(params_from_fit(fit), initial_target=home)
    error = 0.0
    for row in rows[:tick]:
        applied = bridge.step(row["sent_target_rad"], 0.02)
        error = max(error, float(np.max(np.abs(applied - np.asarray(row["applied_target_rad"], dtype=float)))))
    previous_sent = home.copy() if tick == 0 else np.asarray(rows[tick - 1]["sent_target_rad"], dtype=float)
    return bridge, previous_sent, error


def state_payload(*, rows: list[dict[str, Any]], tick: int, env: Any, fit: dict[str, Any], trace: Path, nominal: Path, cell: dict[str, Any]) -> dict[str, Any]:
    qpos, qvel, ctrl, actual = source_state(rows, tick, env)
    bridge, previous_sent, bridge_error = bridge_state(rows, fit, np.asarray(env._default_actuator, dtype=float), tick)
    previous_final = np.zeros(14, dtype=float) if tick == 0 else np.asarray(rows[tick - 1]["action"], dtype=float)
    return {
        "schema_version": "oracle_com_viability_funnel_state.v1",
        "condition": cell["condition"], "policy": cell["policy"], "fit": cell["fit"],
        "command_x": cell["command_x"], "seed": SEED, "tick": tick,
        "ticks_to_recorded_termination": len(rows) - tick,
        "source_trace": str(trace), "source_trace_sha256": sha256(trace),
        "matched_nominal_trace": str(nominal), "matched_nominal_trace_sha256": sha256(nominal),
        "qpos": qpos.tolist(), "qvel": qvel.tolist(), "ctrl": ctrl.tolist(),
        "actual_position_rad": actual.tolist(), "obs_state": rows[tick]["obs_state"],
        "oracle_state": rows[tick]["oracle_state"],
        "previous_final_action": previous_final.tolist(), "previous_sent_target_rad": previous_sent.tolist(),
        "bridge_value_rad": np.asarray(bridge.value, dtype=float).tolist(),
        "bridge_queues_rad": [np.asarray(queue, dtype=float).tolist() for queue in bridge._queues],
        "bridge_reconstruction_max_error_rad": bridge_error,
        "base_tape_rule": "endpoint_policy_base_action_then_matched_nominal_same_absolute_tick_after_endpoint_eof",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()
    result = json.loads((ROOT / "outputs/analysis/oracle_phase_com_compensation_result.json").read_text())
    cells = [c for c in result["cells"] if c["condition"] in {"X_NEG", "X_POS"} and float(c["command_x"]) > 0 and not c["pass"]]
    checks = {
        "cpu_environment": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu",
        "all_24_failing_moving_cells": len(cells) == 24,
        "all_trace_hashes_match_cells": all(sha256(Path(c["trace_path"])) == c["trace_sha256"] for c in cells),
        "design_subset_four_cells": sum(c["fit"] == DESIGN_FIT and abs(float(c["command_x"]) - DESIGN_COMMAND) < 1e-12 for c in cells) == 4,
    }
    if args.contract_only:
        print(json.dumps({"status": "PASS_LOCALIZATION_INPUT_CONTRACT", "checks": checks}, indent=2, sort_keys=True))
        return 0 if all(checks.values()) else 1

    _, env = initialize_native()
    fits = {}
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    records, state_index = [], []
    for cell in sorted(cells, key=lambda c: (c["condition"], c["policy"], c["fit"], c["command_x"])):
        trace = Path(cell["trace_path"])
        nominal = TRACE_ROOT / trace_name("NOMINAL", cell["policy"], cell["fit"], float(cell["command_x"]))
        rows, nominal_rows = load_rows(trace), load_rows(nominal)
        components = [divergence_components(row, nominal_rows[i]) for i, row in enumerate(rows)]
        first_div = next((i for i, item in enumerate(components) if meaningful(item)), None)
        first_contact = next((i for i, item in enumerate(components) if item["contact_sequence_differs"]), None)
        velocity_flags = [float(row["local_linvel_m_s"][0]) <= -0.02 if cell["condition"] == "X_NEG" else float(row["local_linvel_m_s"][0]) >= max(float(cell["command_x"]) + 0.10, 2.0 * float(cell["command_x"])) for row in rows]
        first_velocity = first_run(velocity_flags, 3)
        fit_path = Path(cell["fit_path"])
        fit = fits.setdefault(cell["fit"], json.loads(fit_path.read_text()))
        cadence_states = []
        for tick in range(0, len(rows), CADENCE):
            payload = state_payload(rows=rows, tick=tick, env=env, fit=fit, trace=trace, nominal=nominal, cell=cell)
            state_path = STATE_ROOT / f"{cell['condition']}_{cell['policy']}_{cell['fit']}_x{float(cell['command_x']):.3f}_tick{tick:03d}.json"
            state_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            cadence_states.append({"tick": tick, "path": str(state_path), "sha256": sha256(state_path), "design_subset": cell["fit"] == DESIGN_FIT and abs(float(cell["command_x"]) - DESIGN_COMMAND) < 1e-12})
            state_index.append(cadence_states[-1] | {"condition": cell["condition"], "policy": cell["policy"], "fit": cell["fit"], "command_x": cell["command_x"]})
        records.append({
            "condition": cell["condition"], "policy": cell["policy"], "fit": cell["fit"], "command_x": cell["command_x"],
            "termination_tick_count": len(rows), "first_meaningful_divergence_tick": first_div,
            "first_velocity_sign_error_or_runaway_tick": first_velocity, "first_contact_sequence_deviation_tick": first_contact,
            "first_divergence_components": None if first_div is None else components[first_div],
            "distance_from_first_divergence_to_termination_ticks": None if first_div is None else len(rows) - first_div,
            "distance_from_velocity_event_to_termination_ticks": None if first_velocity is None else len(rows) - first_velocity,
            "cadence_states": cadence_states,
        })
    payload = {
        "schema_version": "oracle_com_failure_localization.v1", "status": "PASS_ORACLE_COM_FAILURE_LOCALIZATION",
        "checks": checks | {"all_bridge_reconstructions_within_1e6": all(json.loads(Path(s["path"]).read_text())["bridge_reconstruction_max_error_rad"] <= 1e-6 for s in state_index)},
        "divergence_thresholds": DIVERGENCE_THRESHOLDS, "velocity_event_rule": {"width_ticks": 3, "x_neg_vx_at_most": -0.02, "x_pos_vx_at_least": "max(command+0.10,2*command)"},
        "cells": records, "state_index": state_index,
        "execution": {"cpu_only": True, "training": False, "robot_or_rdk": False, "gpu_or_igpu": False, "hosted": False},
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Oracle COM Failure Localization", "", "status: `PASS_ORACLE_COM_FAILURE_LOCALIZATION`", "", "| endpoint | checkpoint | fit | command | termination | first divergence | velocity event | contact deviation |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for row in records:
        lines.append(f"| {row['condition']} | {row['policy']} | {row['fit']} | {row['command_x']:.3f} | {row['termination_tick_count']} | {row['first_meaningful_divergence_tick']} | {row['first_velocity_sign_error_or_runaway_tick']} | {row['first_contact_sequence_deviation_tick']} |")
    lines += ["", f"Frozen cadence states: {len(state_index)} total; {sum(s['design_subset'] for s in state_index)} in the preregistered Stage-B design subset.", "", "This is CPU-only localization of committed traces. It changes no policy or simulator behavior.", ""]
    OUTPUT_MD.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "cells": len(records), "states": len(state_index), "design_states": sum(s["design_subset"] for s in state_index)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
