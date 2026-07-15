#!/usr/bin/env python3
"""Validate reset-estimator evaluator plumbing without executing a policy step."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax
import numpy as np
import onnxruntime as ort


REPO = Path(__file__).resolve().parents[1]
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_PREREGISTRATION_20260715.md"
CORRECTION = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EVALUATOR_NOMINAL_RESET_CORRECTION_PREREGISTRATION_20260715.md"
TRANSFORM = REPO / "outputs/analysis/ground_up_reset_com_estimator_eval_policy_transform_contract.json"
FEATURE_TABLE = REPO / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
CLOSED_LOOP = REPO / "tools/closed_loop_sim_eval.py"
CLI = REPO / "tools/evaluate_ground_up_policy.py"
EXPECTED_HASHES = {
    "preregistration": "a462f6ecf5a5ca7260ceb31361d7f3cb0360216fd024d94aab67e17bb7d9506f",
    "correction_preregistration": "2f04f677c6265b2a97bbbe4d31fa4c29b7ab1f481de405d1c7c3e3020b9a9770",
    "transform_contract": "391952c95cdcb1e2b1bcb460e46ca788be6fd5cc1d1a9d0a19ba294858c42149",
    "joystick": "4ddcfbda6f06f9d04acf4ee82deb364993da750adfb8487d032c16be38db3186",
    "runner": "e5ed1bac7ed181f02014487827f05f35fd421ff97ae50614de1b2ce8089f87a2",
}
ANCHORS = {
    -0.05: np.asarray([-13.04679012298584, 0.7727481126785278, 28.672449111938477]),
    0.0: np.asarray([-11.879271507263184, 0.8971166610717773, 29.650177001953125]),
    0.05: np.asarray([-10.715840339660645, 1.0117170810699463, 30.856430053710938]),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_estimate(sensor: np.ndarray) -> float:
    negative, nominal, positive = ANCHORS[-0.05], ANCHORS[0.0], ANCHORS[0.05]
    delta = sensor - nominal
    un, up = negative - nominal, positive - nominal
    tn = float(np.clip(np.dot(delta, un) / np.dot(un, un), 0.0, 1.0))
    tp = float(np.clip(np.dot(delta, up) / np.dot(up, up), 0.0, 1.0))
    rn = float(np.linalg.norm(sensor - (nominal + tn * un)))
    rp = float(np.linalg.norm(sensor - (nominal + tp * up)))
    return float(np.clip((-0.05 * tn if rn <= rp else 0.05 * tp) / 0.05, -1.0, 1.0))


def make_env(joystick: Any, enabled: bool) -> Any:
    config = joystick.default_config()
    config.reference_feature_table_path = str(FEATURE_TABLE)
    config.ground_up_reset_com_estimator_input = enabled
    if enabled:
        config.nominal_reference_bootstrap = True
    overrides = {
        "push_config.enable": False,
        "lin_vel_x": [0.0, 0.0],
        "lin_vel_y": [0.0, 0.0],
        "ang_vel_yaw": [0.0, 0.0],
        "neck_pitch_range": [0.0, 0.0],
        "head_pitch_range": [0.0, 0.0],
        "head_yaw_range": [0.0, 0.0],
        "head_roll_range": [0.0, 0.0],
        "noise_config.level": 0.0,
        "noise_config.action_min_delay": 0,
        "noise_config.action_max_delay": 1,
        "noise_config.imu_min_delay": 0,
        "noise_config.imu_max_delay": 1,
    }
    return joystick.Joystick(task="flat_terrain_backlash", config=config, config_overrides=overrides)


def reset_contract(joystick: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    env = make_env(joystick, True)
    nominal = env.mjx_model
    base_ipos = np.asarray(nominal.body_ipos)
    cells = []
    for offset in (-0.05, 0.0, 0.05):
        model = nominal.replace(body_ipos=nominal.body_ipos.at[2, 0].add(offset))
        env._mjx_model = model
        state = jax.jit(env.reset)(jax.random.PRNGKey(167931544))
        obs = np.asarray(state.obs["state"])
        latch = float(np.asarray(state.info["ground_up_reset_com_estimate_latched"]))
        sensor = np.asarray(env.get_accelerometer(state.data), dtype=float)
        delta = np.asarray(model.body_ipos) - base_ipos
        cells.append({
            "offset_m": offset,
            "body_name": env.mj_model.body(2).name,
            "body_id": 2,
            "body_ipos_x_readback_m": float(np.asarray(model.body_ipos)[2, 0]),
            "body2_x_only_mutation": bool(
                np.count_nonzero(delta) == (0 if offset == 0.0 else 1)
                and np.asarray(model.body_ipos)[2, 0]
                == np.asarray(base_ipos[2, 0] + np.asarray(offset, dtype=base_ipos.dtype), dtype=base_ipos.dtype)
            ),
            "observation_shape": list(obs.shape),
            "latch": latch,
            "observation_index_101": float(obs[101]),
            "independent_latch": independent_estimate(sensor),
            "sensor_m_s2": sensor.tolist(),
            "final_reference_action_size": int(obs[-14:].size),
        })
    disabled = make_env(joystick, False)
    state = jax.jit(disabled.reset)(jax.random.PRNGKey(167931544))
    return cells, {
        "observation_shape": list(np.asarray(state.obs["state"]).shape),
        "latch_key_absent": "ground_up_reset_com_estimate_latched" not in state.info,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--composed-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    composed = args.composed_root.resolve()
    transform = json.loads(TRANSFORM.read_text())
    policy_rows = []
    for row in transform["policies"]:
        path = Path(row["output_path"])
        session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        policy_rows.append({
            "step": row["step"],
            "path": str(path),
            "sha256": sha256(path),
            "expected_sha256": row["output_sha256"],
            "providers": session.get_providers(),
            "obs_shape": session.get_inputs()[0].shape,
        })

    sys.path.insert(0, str(composed))
    old_cwd = Path.cwd()
    os.chdir(composed)
    try:
        from playground.open_duck_mini_v2 import joystick
        cells, disabled = reset_contract(joystick)
    finally:
        os.chdir(old_cwd)

    composed_hashes = {
        "joystick": sha256(composed / "playground/open_duck_mini_v2/joystick.py"),
        "runner": sha256(composed / "playground/open_duck_mini_v2/runner.py"),
    }
    source = CLOSED_LOOP.read_text()
    cli_source = CLI.read_text()
    latches = [cell["latch"] for cell in cells]
    checks = {
        "preregistration_hash_exact": sha256(PREREG) == EXPECTED_HASHES["preregistration"],
        "correction_preregistration_hash_exact": sha256(CORRECTION) == EXPECTED_HASHES["correction_preregistration"],
        "transform_contract_hash_and_status_exact": sha256(TRANSFORM) == EXPECTED_HASHES["transform_contract"] and transform["status"] == "PASS_RESET_ESTIMATOR_EVAL_POLICY_TRANSFORM_CONTRACT",
        "composed_sources_exact": composed_hashes == {key: EXPECTED_HASHES[key] for key in composed_hashes},
        "evaluator_default_false_and_opt_in_exact": "policy_reset_com_estimator_input: bool = False" in source and "if config.policy_reset_com_estimator_input:" in source and "env_config.ground_up_reset_com_estimator_input = True" in source and "env_config.nominal_reference_bootstrap = True" in source and '"--policy-reset-com-estimator-input"' in cli_source and "args.policy_reset_com_estimator_input" in cli_source,
        "dynamics_override_precedes_reset": source.index("apply_eval_dynamics_override(") < source.index("env.reset") and "env.mj_model.body(\"trunk_assembly\").id" in source,
        "default_off_115d_no_latch": disabled == {"observation_shape": [115], "latch_key_absent": True},
        "enabled_116d_latch_and_reference_contract": all(cell["observation_shape"] == [116] and cell["final_reference_action_size"] == 14 and abs(cell["observation_index_101"] - cell["latch"]) <= 1e-6 for cell in cells),
        "independent_estimator_exact": all(abs(cell["latch"] - cell["independent_latch"]) <= 1e-6 for cell in cells),
        "body2_trunk_x_only_readback": all(cell["body_id"] == 2 and cell["body_name"] == "trunk_assembly" and cell["body2_x_only_mutation"] for cell in cells),
        "latches_finite_bounded_strict_order": all(np.isfinite(value) and -1.0 <= value <= 1.0 for value in latches) and latches[0] < latches[1] < latches[2],
        "contracted_graph_identity_and_cpu": len(policy_rows) == 2 and all(row["sha256"] == row["expected_sha256"] and row["obs_shape"] == [1, 116] and row["providers"] == ["CPUExecutionProvider"] for row in policy_rows),
        "execution_cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu" and jax.default_backend() == "cpu" and all(device.platform == "cpu" for device in jax.devices()),
        "zero_policy_steps_and_behavior_cells": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "ground_up_reset_com_estimator_behavior_evaluator_contract.v1",
        "status": "PASS_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_CONTRACT" if not failed else "FAIL_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_CONTRACT",
        "checks": checks,
        "failed_checks": failed,
        "execution": {"platform": "cpu", "policy_steps": 0, "formal_behavior_cells": 0},
        "source_hashes": {"preregistration": sha256(PREREG), "correction_preregistration": sha256(CORRECTION), "closed_loop": sha256(CLOSED_LOOP), "cli": sha256(CLI), "transform_contract": sha256(TRANSFORM), **composed_hashes},
        "policies": policy_rows,
        "reset_cells": cells,
        "default_off": disabled,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
