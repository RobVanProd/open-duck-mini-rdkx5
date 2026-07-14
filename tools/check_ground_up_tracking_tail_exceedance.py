#!/usr/bin/env python3
"""CPU contract for the default-off ground-up tracking-tail diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys

import jax
import jax.numpy as jp
import numpy as np


EXPECTED_INDICES = (2, 3, 4, 11, 12, 13)
THRESHOLD_RAD = 0.20


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace_arrays(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    sent, actual, manifest = [], [], []
    for root in paths:
        for path in sorted(root.glob("*.jsonl")):
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            rows = [row for row in rows if row.get("mode") == "fitted"]
            sent.extend(row["sent_target_rad"] for row in rows)
            actual.extend(row["actual_position_rad"] for row in rows)
            manifest.append(
                {
                    "path": str(path.resolve()),
                    "sha256": sha256_file(path),
                    "rows": len(rows),
                }
            )
    return np.asarray(sent), np.asarray(actual), manifest


def trace_group_stats(path: Path) -> dict:
    sent, actual, manifest = load_trace_arrays([path])
    values = numpy_cost(sent.astype(np.float64), actual.astype(np.float64))
    action_rate = []
    for item in sorted(path.glob("*.jsonl")):
        for line in item.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            value = (row.get("reward_terms") or {}).get("cost/action_rate")
            if value is not None:
                action_rate.append(float(value))
    return {
        "path": str(path.resolve()),
        "rows": len(values),
        "nonzero_fraction": float(np.mean(values > 0.0)),
        "mean_raw_tail_cost": float(np.mean(values)),
        "p95_raw_tail_cost": float(np.percentile(values, 95)),
        "max_raw_tail_cost": float(np.max(values)),
        "mean_scaled_action_rate_cost": float(np.mean(action_rate)),
        "files": manifest,
    }


def numpy_cost(sent: np.ndarray, actual: np.ndarray) -> np.ndarray:
    error = np.abs(sent[:, EXPECTED_INDICES] - actual[:, EXPECTED_INDICES])
    return np.mean(np.square(np.maximum(error - THRESHOLD_RAD, 0.0)), axis=1)


def transition_contract(
    joystick, checkout: Path, reference_table: Path, ticks: int
) -> dict:
    def config(scale: float):
        cfg = joystick.default_config()
        cfg.reference_feature_table_path = str(reference_table.resolve())
        cfg.nominal_reference_bootstrap = True
        cfg.ground_up_hard_vector_command_support = True
        cfg.ground_up_command_support_range = [0.074, 0.080]
        cfg.ground_up_measured_actuator_bridge = True
        cfg.ground_up_applied_target_observation = True
        cfg.ground_up_signed_progress_objective = True
        cfg.reference_start_phase = 0
        cfg.noise_config.level = 0.0
        cfg.noise_config.action_min_delay = 0
        cfg.noise_config.action_max_delay = 1
        cfg.noise_config.imu_min_delay = 0
        cfg.noise_config.imu_max_delay = 1
        cfg.push_config.enable = False
        cfg.reward_config.scales.tracking_tail_exceedance = scale
        return cfg

    previous_cwd = Path.cwd()
    os.chdir(checkout.resolve())
    try:
        control = joystick.Joystick(
            task="flat_terrain_backlash", config=config(0.0)
        )
        enabled = joystick.Joystick(
            task="flat_terrain_backlash", config=config(-1.0)
        )
    finally:
        os.chdir(previous_cwd)
    reset_control = jax.jit(control.reset)
    reset_enabled = jax.jit(enabled.reset)
    step_control = jax.jit(control.step)
    step_enabled = jax.jit(enabled.step)
    key = jax.random.PRNGKey(20260714)
    state_control = reset_control(key)
    state_enabled = reset_enabled(key)
    maximum_state_error = 0.0
    maximum_reward_contract_error = 0.0
    nonzero_cost_steps = 0
    for tick in range(ticks):
        sign = 1.0 if (tick // 8) % 2 == 0 else -1.0
        action = jp.zeros(14).at[jp.asarray(EXPECTED_INDICES)].set(sign)
        state_control = step_control(state_control, action)
        state_enabled = step_enabled(state_enabled, action)
        maximum_state_error = max(
            maximum_state_error,
            float(jp.max(jp.abs(state_control.data.qpos - state_enabled.data.qpos))),
            float(jp.max(jp.abs(state_control.data.qvel - state_enabled.data.qvel))),
            float(jp.max(jp.abs(state_control.obs["state"] - state_enabled.obs["state"]))),
        )
        raw_cost = float(
            joystick.ground_up_tracking_tail_exceedance_cost(
                state_enabled.info["motor_targets"],
                enabled.get_actuator_joints_qpos(state_enabled.data.qpos),
                THRESHOLD_RAD,
            )
        )
        nonzero_cost_steps += int(raw_cost > 0.0)
        expected_difference = raw_cost * enabled.dt
        observed_difference = float(state_control.reward - state_enabled.reward)
        maximum_reward_contract_error = max(
            maximum_reward_contract_error,
            abs(observed_difference - expected_difference),
        )
    return {
        "ticks": ticks,
        "maximum_state_or_observation_error": maximum_state_error,
        "maximum_reward_contract_error": maximum_reward_contract_error,
        "nonzero_cost_steps": nonzero_cost_steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--reference-table", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, action="append", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--dynamics-ticks", type=int, default=64)
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("set CUDA_VISIBLE_DEVICES='' for this CPU-only check")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu for this CPU-only check")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")

    sys.path.insert(0, str(args.checkout.resolve()))
    joystick = importlib.import_module("playground.open_duck_mini_v2.joystick")
    function = joystick.ground_up_tracking_tail_exceedance_cost

    zero = np.zeros(14, dtype=np.float32)
    synthetic = {}
    for name, error in (
        ("below", 0.19),
        ("at", 0.20),
        ("above_0p21", 0.21),
        ("above_0p25", 0.25),
    ):
        actual = zero.copy()
        actual[2] = error
        synthetic[name] = float(function(jp.asarray(zero), jp.asarray(actual), THRESHOLD_RAD))

    sent, actual, trace_manifest = load_trace_arrays(args.trace_dir)
    group_stats = {
        path.name: trace_group_stats(path) for path in args.trace_dir
    }
    jax_values = np.asarray(
        jax.vmap(lambda s, a: function(s, a, THRESHOLD_RAD))(
            jp.asarray(sent, dtype=jp.float32), jp.asarray(actual, dtype=jp.float32)
        )
    )
    numpy_values = numpy_cost(sent.astype(np.float64), actual.astype(np.float64))

    cfg = joystick.default_config()
    default_scale = float(cfg.reward_config.scales.tracking_tail_exceedance)
    default_threshold = float(cfg.ground_up_tracking_tail_threshold_rad)
    expected_0p21 = (0.01**2) / len(EXPECTED_INDICES)
    expected_0p25 = (0.05**2) / len(EXPECTED_INDICES)
    transition = transition_contract(
        joystick, args.checkout, args.reference_table.resolve(), args.dynamics_ticks
    )
    checks = {
        "jax_backend_is_cpu": jax.default_backend() == "cpu",
        "pitch_chain_indices_match_gate": tuple(joystick.GROUND_UP_PITCH_CHAIN_INDICES)
        == EXPECTED_INDICES,
        "default_scale_is_zero": default_scale == 0.0,
        "default_threshold_is_0p20": default_threshold == THRESHOLD_RAD,
        "below_threshold_is_zero": synthetic["below"] == 0.0,
        "at_threshold_is_zero": synthetic["at"] == 0.0,
        "above_threshold_matches_analytic_0p21": abs(
            synthetic["above_0p21"] - expected_0p21
        )
        <= 1e-9,
        "above_threshold_matches_analytic_0p25": abs(
            synthetic["above_0p25"] - expected_0p25
        )
        <= 1e-9,
        "monotonic_above_threshold": synthetic["above_0p25"]
        > synthetic["above_0p21"]
        > 0.0,
        "trace_jax_matches_independent_numpy": float(
            np.max(np.abs(jax_values - numpy_values))
        )
        <= 1e-9,
        "trace_values_are_finite": bool(np.isfinite(jax_values).all()),
        "trace_corpus_has_3600_rows": len(jax_values) == 3600,
        "tail_scale_does_not_change_dynamics_or_observation": transition[
            "maximum_state_or_observation_error"
        ]
        == 0.0,
        "enabled_reward_delta_equals_negative_scaled_cost": transition[
            "maximum_reward_contract_error"
        ]
        <= 1e-7,
        "transition_probe_reaches_nonzero_tail_cost": transition[
            "nonzero_cost_steps"
        ]
        > 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_TRACKING_TAIL_CPU_CONTRACT" if not failed else "FAIL_TRACKING_TAIL_CPU_CONTRACT"
    payload = {
        "schema_version": "ground_up_tracking_tail_cpu_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "definition": {
            "pitch_chain_indices": list(EXPECTED_INDICES),
            "threshold_rad": THRESHOLD_RAD,
            "cost": "mean(square(max(abs(sent_target-actual_position)-threshold,0)))",
            "default_scale": default_scale,
        },
        "synthetic": synthetic,
        "trace_contract": {
            "rows": len(jax_values),
            "nonzero_rows": int(np.count_nonzero(jax_values > 0.0)),
            "nonzero_fraction": float(np.mean(jax_values > 0.0)),
            "mean_raw_cost": float(np.mean(jax_values)),
            "p95_raw_cost": float(np.percentile(jax_values, 95)),
            "max_raw_cost": float(np.max(jax_values)),
            "jax_numpy_max_abs_error": float(np.max(np.abs(jax_values - numpy_values))),
            "groups": group_stats,
        },
        "transition_contract": transition,
        "inputs": {
            "checkout": str(args.checkout.resolve()),
            "patch": {"path": str(args.patch.resolve()), "sha256": sha256_file(args.patch)},
            "reference_table": {
                "path": str(args.reference_table.resolve()),
                "sha256": sha256_file(args.reference_table),
            },
            "traces": trace_manifest,
        },
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "gpu_access": False,
            "colab_access": False,
        },
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Tracking-Tail CPU Contract",
        "",
        f"status: `{status}`",
        "",
        f"- frozen threshold: `{THRESHOLD_RAD} rad`",
        f"- pitch-chain indices: `{list(EXPECTED_INDICES)}`",
        f"- default scale: `{default_scale}`",
        f"- frozen trace rows: `{len(jax_values)}`",
        f"- nonzero trace fraction: `{float(np.mean(jax_values > 0.0)):.8f}`",
        f"- mean raw tail cost: `{float(np.mean(jax_values)):.12f}`",
        f"- JAX/NumPy maximum error: `{float(np.max(np.abs(jax_values - numpy_values))):.12g}`",
        f"- transition state/observation error: `{transition['maximum_state_or_observation_error']:.12g}`",
        f"- transition reward-contract error: `{transition['maximum_reward_contract_error']:.12g}`",
        f"- transition nonzero-cost steps: `{transition['nonzero_cost_steps']}/{transition['ticks']}`",
        "",
        "Every contract check passes only if the diagnostic is exactly zero below",
        "and at .20 rad, monotonic above it, uses the same six gate joints, remains",
        "default-off, and reproduces an independent NumPy implementation.",
        "",
        "This is a diagnostic wiring pass only. It does not select a scale or",
        "authorize PPO, Colab, deployment, RDK-X5, or robot use.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
