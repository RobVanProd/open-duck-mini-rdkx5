#!/usr/bin/env python3
"""Contract and run the preregistered torso-COM signed causal-response study."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_torso_com_package_contract_20260714")
MANIFEST = REPO / "outputs/analysis/ground_up_torso_com_full_obs_replay_manifest.json"
FULL_RESULT = REPO / "outputs/analysis/ground_up_torso_com_full_obs_study_result.json"
POLICY_ROOT = REPO / "outputs/analysis/ground_up_torso_com_eval_policies"
P30 = REPO / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
P31 = REPO / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json"
REFERENCE = REPO / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
JOYSTICK = PLAYGROUND / "playground/open_duck_mini_v2/joystick.py"
SCENE = PLAYGROUND / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
BRIDGE_SOURCE = REPO / "tools/actuator_bridge_model.py"

EXPECTED_HASHES = {
    "manifest": "ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07",
    "full_result": "e55462259ab5c850f7226e0a9e107a985ee6007a1ceaf1b8fa5eec025f83ede7",
    "p30": "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b",
    "p31": "a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276",
    "reference": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "joystick": "3f7c63918ec811259eaa1c0020abd504e25336d1a7d9fbfefe2cc08baaa5521b",
    "scene": "33af97247d6a876cf47c9e37185cb71bd09f6793bc0f62d90cbe2a91caa3ba63",
    "bridge": "3c9f2714f394d6f9f0c7e7baa693311eb7cf562617cabc4cd03d063db09dadce",
}
POLICIES = {
    "A05_DIRECT_1003520": "e50a121bf0c2d9a2715d65b8356e4e1af68a16c1ecb264975c1c1d33acea32a7",
    "A05_DIRECT_2007040": "eaa01f1d1c29f7bb6e7c9cf77093229e708ad317bb8d2a175617f4e9955b11c5",
    "U05_DIRECT_1003520": "6aa4364ec3291d5f42b5adf725a79c3c18f0062f0f4741e09f814ea1af7db9af",
    "U05_DIRECT_2007040": "c16be9b15549343073a24e3844da54d648415dbd5979e321db10e45fc6167a11",
    "U_CURRICULUM_512000": "1653f55429867c63248175c7f3be2b8b550f57dd29f03321da312495ba6528b5",
    "U_CURRICULUM_1024000": "2665ac124d59ddeb93777cf1d82ca1bc0d0506bb26bd1c06645356c66fce3001",
}
FORK_TICKS = (0, 24, 32, 40)
COMMANDS = (0.074, 0.077, 0.08)
DIRECTION = np.asarray(
    [1.1654748916625977, 0.11948448419570923, 1.0919904708862305],
    dtype=np.float32,
)
HORIZON = 8

sys.path.insert(0, str(REPO / "tools"))
from actuator_bridge_model import (  # noqa: E402
    ActuatorBridgeModel,
    load_fit_json,
    params_from_fit,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clone_bridge(bridge: ActuatorBridgeModel) -> ActuatorBridgeModel:
    output = ActuatorBridgeModel(bridge.params, initial_target=bridge.value)
    output._queues = [queue.copy() for queue in bridge._queues]  # noqa: SLF001
    return output


def pitch_from_quat(quat: np.ndarray) -> float:
    w, x, y, z = [float(value) for value in quat]
    return math.asin(float(np.clip(2.0 * (w * y - z * x), -1.0, 1.0)))


def yaw_from_quat(quat: np.ndarray) -> float:
    w, x, y, z = [float(value) for value in quat]
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def policy_path(key: str) -> Path:
    arm, _step = key.rsplit("_", 1)
    return POLICY_ROOT / arm / f"{key}.onnx"


def initialize_environment() -> tuple[Any, Any, Any]:
    import jax
    import mujoco

    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("exact CPU environment required")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")
    sys.path.insert(0, str(PLAYGROUND))
    previous = Path.cwd()
    os.chdir(PLAYGROUND)
    try:
        from playground.open_duck_mini_v2 import joystick

        config = joystick.default_config()
        config.reference_feature_table_path = str(REFERENCE.resolve())
        overrides = {
            "push_config.enable": False,
            "lin_vel_x": [0.074, 0.074],
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
        env = joystick.Joystick(
            task="flat_terrain_backlash", config=config, config_overrides=overrides
        )
    finally:
        os.chdir(previous)
    return jax, mujoco, env


def load_sources() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    paths = {
        "manifest": MANIFEST, "full_result": FULL_RESULT, "p30": P30,
        "p31": P31, "reference": REFERENCE, "joystick": JOYSTICK,
        "scene": SCENE, "bridge": BRIDGE_SOURCE,
    }
    actual = {name: sha256(path) for name, path in paths.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"frozen source hash mismatch: {actual}")
    for key, expected in POLICIES.items():
        if sha256(policy_path(key)) != expected:
            raise ValueError(f"policy hash mismatch: {key}")
    manifest = json.loads(MANIFEST.read_text())
    full_result = json.loads(FULL_RESULT.read_text())
    if manifest.get("status") != "PASS_EXACT_FULL_OBSERVATION_REPLAY":
        raise ValueError("source replay did not pass")
    if manifest.get("trace_manifest_sha256") != "7d7ccbe3b06e3a58546be5da02bdb138a218c08c11a0f10dea74a29d891c9f01":
        raise ValueError("source trace manifest mismatch")
    if full_result.get("decision") != "SUPPORT_PREREGISTERED_SIGNED_CAUSAL_RESPONSE_STUDY":
        raise ValueError("source decision mismatch")
    selected = [
        item for item in manifest["traces"]
        if item["condition"] == "NOMINAL"
        and round(float(item["command_x"]), 3) in {round(value, 3) for value in COMMANDS}
    ]
    if len(selected) != 36:
        raise ValueError(f"expected 36 nominal moving traces, got {len(selected)}")
    return manifest, full_result, sorted(selected, key=lambda item: item["path"])


def load_trace(item: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(item["path"])
    if sha256(path) != item["sha256"]:
        raise ValueError(f"trace hash mismatch: {path}")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len(rows) != 600 or [row.get("tick") for row in rows] != list(range(600)):
        raise ValueError(f"trace row/tick contract mismatch: {path}")
    for row in rows:
        if len(row.get("obs_state") or []) != 115:
            raise ValueError(f"trace observation contract mismatch: {path}")
        if len(row.get("qpos") or []) != 31 or len(row.get("qvel") or []) != 30:
            raise ValueError(f"trace physical-state contract mismatch: {path}")
    return rows


def reconstruct_policy(session: Any, rows: list[dict[str, Any]]) -> dict[int, dict[str, np.ndarray]]:
    wanted: dict[int, dict[str, np.ndarray]] = {}
    previous = np.zeros((1, 14), dtype=np.float32)
    for tick, row in enumerate(rows[: max(FORK_TICKS) + 1]):
        obs = np.asarray(row["obs_state"], dtype=np.float32)
        state_input = previous.copy()
        action, previous = session.run(
            None, {"obs": obs[None], "previous_action": state_input}
        )
        expected = np.asarray(row["policy_raw_action"], dtype=np.float32)
        if float(np.max(np.abs(action[0] - expected))) > 1e-6:
            raise ValueError(f"baseline ONNX mismatch at tick {tick}")
        if tick in FORK_TICKS:
            minus, plus = obs.copy(), obs.copy()
            minus[3:6] -= DIRECTION
            plus[3:6] += DIRECTION
            action_minus = session.run(
                None, {"obs": minus[None], "previous_action": state_input}
            )[0][0]
            action_plus = session.run(
                None, {"obs": plus[None], "previous_action": state_input}
            )[0][0]
            wanted[tick] = {
                "state_input": state_input,
                "baseline": action[0].astype(np.float64),
                "minus": action_minus.astype(np.float64),
                "plus": action_plus.astype(np.float64),
                "obs": obs,
            }
    return wanted


def reconstruct_bridge(
    rows: list[dict[str, Any]], fit_path: Path, home: np.ndarray, tick: int
) -> tuple[ActuatorBridgeModel, np.ndarray, float]:
    bridge = ActuatorBridgeModel(
        params_from_fit(load_fit_json(fit_path)), initial_target=home
    )
    maximum_error = 0.0
    for row in rows[:tick]:
        applied = bridge.step(row["sent_target_rad"], 0.02)
        maximum_error = max(
            maximum_error,
            float(np.max(np.abs(applied - np.asarray(row["applied_target_rad"])))),
        )
    previous_sent = (
        home.copy() if tick == 0 else np.asarray(rows[tick - 1]["sent_target_rad"], dtype=float)
    )
    return bridge, previous_sent, maximum_error


def source_state(
    rows: list[dict[str, Any]], tick: int, init_q: np.ndarray, home: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if tick == 0:
        return init_q.copy(), np.zeros(30, dtype=float), home.copy()
    prior = rows[tick - 1]
    return (
        np.asarray(prior["qpos"], dtype=float),
        np.asarray(prior["qvel"], dtype=float),
        np.asarray(prior["ctrl"], dtype=float),
    )


def model_with_com(mujoco: Any, source: Any, offset_x: float) -> Any:
    model = copy.copy(source)
    body_id = int(model.body("trunk_assembly").id)
    before = np.asarray(model.body_ipos).copy()
    model.body_ipos[body_id, 0] += float(offset_x)
    changed = np.argwhere(np.asarray(model.body_ipos) != before).tolist()
    if body_id != 2 or changed != [[2, 0]]:
        raise ValueError(f"COM mutation contract failed: body={body_id}, changed={changed}")
    return model


def simulate(
    *, mujoco: Any, model: Any, qpos: np.ndarray, qvel: np.ndarray,
    ctrl: np.ndarray, bridge: ActuatorBridgeModel, previous_sent: np.ndarray,
    actions: np.ndarray, home: np.ndarray, action_scale: float,
    max_motor_velocity: float, dt: float, n_substeps: int,
) -> dict[str, Any]:
    data = mujoco.MjData(model)
    mujoco.mj_setConst(model, data)
    data.qpos[:] = qpos
    data.qvel[:] = qvel
    data.ctrl[:] = ctrl
    mujoco.mj_forward(model, data)
    sent = previous_sent.copy()
    pitch, pitch_rate, height, local_vx, sent_rows, applied_rows = [], [], [], [], [], []
    for raw in actions:
        action = np.clip(np.asarray(raw, dtype=float), -1.0, 1.0)
        target = home + action * action_scale
        sent = np.clip(
            target,
            sent - max_motor_velocity * dt,
            sent + max_motor_velocity * dt,
        )
        applied = bridge.step(sent, dt)
        data.ctrl[:] = applied
        for _ in range(n_substeps):
            mujoco.mj_step(model, data)
        quat = np.asarray(data.qpos[3:7], dtype=float)
        yaw = yaw_from_quat(quat)
        pitch.append(pitch_from_quat(quat))
        pitch_rate.append(float(data.qvel[4]))
        height.append(float(data.qpos[2]))
        local_vx.append(
            math.cos(yaw) * float(data.qvel[0])
            + math.sin(yaw) * float(data.qvel[1])
        )
        sent_rows.append(sent.copy())
        applied_rows.append(applied.copy())
    return {
        "pitch": np.asarray(pitch), "pitch_rate": np.asarray(pitch_rate),
        "height": np.asarray(height), "local_vx": np.asarray(local_vx),
        "sent": np.asarray(sent_rows), "applied": np.asarray(applied_rows),
        "qpos_final": np.asarray(data.qpos).copy(),
        "qvel_final": np.asarray(data.qvel).copy(),
    }


def difference(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {
        key: np.asarray(right[key]) - np.asarray(left[key])
        for key in ("pitch", "pitch_rate", "height", "local_vx", "sent", "applied")
    }


def run_cell(
    *, mujoco: Any, env: Any, item: dict[str, Any], rows: list[dict[str, Any]],
    policy_state: dict[str, np.ndarray], tick: int, fit_path: Path,
) -> dict[str, Any]:
    home = np.asarray(env._default_actuator, dtype=float)
    init_q = np.asarray(env._init_q, dtype=float)
    qpos, qvel, ctrl = source_state(rows, tick, init_q, home)
    bridge, previous_sent, bridge_error = reconstruct_bridge(rows, fit_path, home, tick)
    if bridge_error > 1e-6:
        raise ValueError(f"bridge reconstruction error {bridge_error}")
    baseline = np.asarray(rows[tick]["policy_raw_action"], dtype=float)
    baseline_target = home + baseline * float(env._config.action_scale)
    baseline_sent = np.clip(
        baseline_target,
        previous_sent - float(env._config.max_motor_velocity) * float(env.dt),
        previous_sent + float(env._config.max_motor_velocity) * float(env.dt),
    )
    saved_sent = np.asarray(rows[tick]["sent_target_rad"], dtype=float)
    sent_error = float(np.max(np.abs(baseline_sent - saved_sent)))
    saved_applied = np.asarray(rows[tick]["applied_target_rad"], dtype=float)
    baseline_applied = clone_bridge(bridge).step(baseline_sent, float(env.dt))
    applied_error = float(np.max(np.abs(baseline_applied - saved_applied)))
    if sent_error > 1e-6 or applied_error > 1e-6:
        raise ValueError(f"fork boundary target mismatch: sent={sent_error}, applied={applied_error}")

    future = np.asarray(
        [rows[index]["policy_raw_action"] for index in range(tick, tick + HORIZON)],
        dtype=float,
    )
    action_minus = future.copy()
    action_plus = future.copy()
    action_minus[0] = policy_state["minus"]
    action_plus[0] = policy_state["plus"]

    common = {
        "mujoco": mujoco, "qpos": qpos, "qvel": qvel, "ctrl": ctrl,
        "previous_sent": previous_sent, "home": home,
        "action_scale": float(env._config.action_scale),
        "max_motor_velocity": float(env._config.max_motor_velocity),
        "dt": float(env.dt), "n_substeps": int(env.n_substeps),
    }
    model_neg = model_with_com(mujoco, env.mj_model, -0.05)
    model_pos = model_with_com(mujoco, env.mj_model, 0.05)
    physical_neg = simulate(
        **common, model=model_neg, bridge=clone_bridge(bridge), actions=future
    )
    physical_pos = simulate(
        **common, model=model_pos, bridge=clone_bridge(bridge), actions=future
    )
    actor_neg = simulate(
        **common, model=env.mj_model, bridge=clone_bridge(bridge), actions=action_minus
    )
    actor_pos = simulate(
        **common, model=env.mj_model, bridge=clone_bridge(bridge), actions=action_plus
    )
    disturbance = difference(physical_neg, physical_pos)
    actor = difference(actor_neg, actor_pos)
    d_pitch = disturbance["pitch"]
    a_pitch = actor["pitch"]
    d_norm = float(np.linalg.norm(d_pitch))
    a_norm = float(np.linalg.norm(a_pitch))
    alignment = (
        float(np.dot(d_pitch, a_pitch) / (d_norm * a_norm))
        if d_norm >= 1e-6 and a_norm >= 1e-6 else None
    )
    if alignment is None:
        classification = "PHYSICALLY_NEGLIGIBLE"
    elif alignment <= -0.25:
        classification = "CORRECTIVE"
    elif alignment >= 0.25:
        classification = "AMPLIFYING"
    else:
        classification = "ORTHOGONAL_OR_MIXED"
    return {
        "policy": f"{item['arm']}_{item['step']}", "arm": item["arm"],
        "step": int(item["step"]), "fit": item["fit"],
        "command_x": float(item["command_x"]), "tick": tick,
        "classification": classification, "alignment_cosine": alignment,
        "disturbance_pitch_norm_rad": d_norm, "actor_pitch_norm_rad": a_norm,
        "disturbance_pitch_rad": d_pitch.tolist(),
        "actor_pitch_rad": a_pitch.tolist(),
        "disturbance_pitch_rate": disturbance["pitch_rate"].tolist(),
        "actor_pitch_rate": actor["pitch_rate"].tolist(),
        "disturbance_height_m": disturbance["height"].tolist(),
        "actor_height_m": actor["height"].tolist(),
        "disturbance_local_vx_m_s": disturbance["local_vx"].tolist(),
        "actor_local_vx_m_s": actor["local_vx"].tolist(),
        "actor_sent_target_difference_rad": actor["sent"].tolist(),
        "actor_applied_target_difference_rad": actor["applied"].tolist(),
        "fork_action_difference": (
            np.asarray(policy_state["plus"]) - np.asarray(policy_state["minus"])
        ).tolist(),
        "reconstruction": {
            "bridge_max_error_rad": bridge_error,
            "sent_target_error_rad": sent_error,
            "applied_target_error_rad": applied_error,
        },
    }


def counts(cells: list[dict[str, Any]]) -> dict[str, int]:
    names = ("CORRECTIVE", "AMPLIFYING", "ORTHOGONAL_OR_MIXED", "PHYSICALLY_NEGLIGIBLE")
    return {name: sum(cell["classification"] == name for cell in cells) for name in names}


def classify_policy(cells: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    total = counts(cells)
    by_fit = {fit: counts([cell for cell in cells if cell["fit"] == fit]) for fit in ("p30", "p31_34")}
    by_tick = {str(tick): counts([cell for cell in cells if cell["tick"] == tick]) for tick in FORK_TICKS}
    systematic_corrective = (
        total["CORRECTIVE"] >= 18 and total["AMPLIFYING"] <= 2
        and all(row["CORRECTIVE"] >= 8 for row in by_fit.values())
        and all(row["CORRECTIVE"] >= 4 for row in by_tick.values())
    )
    systematic_amplifying = (
        total["AMPLIFYING"] >= 18 and total["CORRECTIVE"] <= 2
        and all(row["AMPLIFYING"] >= 8 for row in by_fit.values())
        and all(row["AMPLIFYING"] >= 4 for row in by_tick.values())
    )
    if systematic_corrective:
        classification = "SYSTEMATIC_CORRECTIVE"
    elif systematic_amplifying:
        classification = "SYSTEMATIC_AMPLIFYING"
    elif total["PHYSICALLY_NEGLIGIBLE"] >= 18:
        classification = "PHYSICALLY_NEGLIGIBLE_POLICY"
    else:
        classification = "MIXED_POLICY_RESPONSE"
    return classification, {"total": total, "by_fit": by_fit, "by_tick": by_tick}


def contract(output: Path) -> int:
    manifest, full_result, selected = load_sources()
    jax, mujoco, env = initialize_environment()
    import onnxruntime as ort

    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}
    checks["cpu_only"] = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    checks["environment_constants_exact"] = (
        float(env.dt) == 0.02 and int(env.n_substeps) == 10
        and float(env._config.action_scale) == 0.25
        and float(env._config.max_motor_velocity) == 5.24
        and int(env.mj_model.body("trunk_assembly").id) == 2
        and abs(float(env.mj_model.body_mass[2]) - 0.698526) <= 1e-12
    )
    checks["selected_trace_count_exact"] = len(selected) == 36
    sessions = {}
    for key in POLICIES:
        session = ort.InferenceSession(str(policy_path(key)), providers=["CPUExecutionProvider"])
        if session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError(f"non-CPU provider for {key}")
        sessions[key] = session
    fork_index = {
        (row["policy"], row["condition"], row["fit"], round(float(row["command_x"]), 3), int(row["tick"])): row
        for row in full_result["sensitivity"]["forks"]
    }
    max_baseline_error = 0.0
    max_bridge_error = 0.0
    max_sent_error = 0.0
    max_applied_error = 0.0
    max_fork_delta_error = 0.0
    prepared = []
    home = np.asarray(env._default_actuator, dtype=float)
    for item in selected:
        rows = load_trace(item)
        key = f"{item['arm']}_{item['step']}"
        states = reconstruct_policy(sessions[key], rows)
        fit_path = P30 if item["fit"] == "p30" else P31
        for tick in FORK_TICKS:
            state = states[tick]
            max_baseline_error = max(
                max_baseline_error,
                float(np.max(np.abs(state["baseline"] - np.asarray(rows[tick]["policy_raw_action"])))),
            )
            bridge, previous_sent, bridge_error = reconstruct_bridge(rows, fit_path, home, tick)
            max_bridge_error = max(max_bridge_error, bridge_error)
            baseline_target = home + state["baseline"] * float(env._config.action_scale)
            sent = np.clip(
                baseline_target,
                previous_sent - float(env._config.max_motor_velocity) * float(env.dt),
                previous_sent + float(env._config.max_motor_velocity) * float(env.dt),
            )
            max_sent_error = max(max_sent_error, float(np.max(np.abs(sent - np.asarray(rows[tick]["sent_target_rad"])))))
            applied = clone_bridge(bridge).step(sent, float(env.dt))
            max_applied_error = max(max_applied_error, float(np.max(np.abs(applied - np.asarray(rows[tick]["applied_target_rad"])))))
            frozen = fork_index[(key, "NOMINAL", item["fit"], round(float(item["command_x"]), 3), tick)]
            delta = state["plus"] - state["minus"]
            max_fork_delta_error = max(
                max_fork_delta_error,
                float(np.max(np.abs(delta - np.asarray(frozen["action_difference"])))),
            )
        prepared.append((item, rows, states, fit_path))
    checks["all_trace_state_schemas_exact"] = len(prepared) == 36
    checks["onnx_recurrent_reconstruction_exact"] = max_baseline_error <= 1e-6
    checks["saved_fork_action_differences_exact"] = max_fork_delta_error <= 1e-6
    checks["bridge_queue_reconstruction_exact"] = max_bridge_error <= 1e-6
    checks["sent_target_reconstruction_exact"] = max_sent_error <= 1e-6
    checks["applied_target_reconstruction_exact"] = max_applied_error <= 1e-6

    smoke_item, smoke_rows, smoke_states, smoke_fit = next(
        row for row in prepared
        if row[0]["arm"] == "A05_DIRECT" and int(row[0]["step"]) == 1003520
        and row[0]["fit"] == "p30" and round(float(row[0]["command_x"]), 3) == 0.074
    )
    smoke = run_cell(
        mujoco=mujoco, env=env, item=smoke_item, rows=smoke_rows,
        policy_state=smoke_states[32], tick=32, fit_path=smoke_fit,
    )
    # Identity branches use an identical action sequence and nominal model.
    bridge, previous_sent, _ = reconstruct_bridge(smoke_rows, smoke_fit, home, 32)
    qpos, qvel, ctrl = source_state(smoke_rows, 32, np.asarray(env._init_q), home)
    future = np.asarray([smoke_rows[i]["policy_raw_action"] for i in range(32, 40)])
    common = {
        "mujoco": mujoco, "model": env.mj_model, "qpos": qpos, "qvel": qvel,
        "ctrl": ctrl, "previous_sent": previous_sent, "home": home,
        "action_scale": float(env._config.action_scale),
        "max_motor_velocity": float(env._config.max_motor_velocity),
        "dt": float(env.dt), "n_substeps": int(env.n_substeps), "actions": future,
    }
    identity_a = simulate(**common, bridge=clone_bridge(bridge))
    identity_b = simulate(**common, bridge=clone_bridge(bridge))
    identity_error = max(
        float(np.max(np.abs(identity_a[key] - identity_b[key])))
        for key in ("pitch", "pitch_rate", "height", "local_vx", "sent", "applied")
    )
    checks["identical_branch_isolation_exact"] = identity_error == 0.0
    checks["physical_com_intervention_nonzero"] = smoke["disturbance_pitch_norm_rad"] >= 1e-6
    checks["actor_intervention_nonzero"] = (
        float(np.max(np.abs(smoke["fork_action_difference"]))) > 0.0
        and float(np.max(np.abs(smoke["actor_sent_target_difference_rad"]))) > 0.0
    )
    negative_model = model_with_com(mujoco, env.mj_model, -0.05)
    positive_model = model_with_com(mujoco, env.mj_model, 0.05)
    base_ipos = np.asarray(env.mj_model.body_ipos)
    checks["body2_x_only_mutation_exact"] = (
        abs(float(negative_model.body_ipos[2, 0] - base_ipos[2, 0]) + 0.05) <= 1e-12
        and abs(float(positive_model.body_ipos[2, 0] - base_ipos[2, 0]) - 0.05) <= 1e-12
        and np.array_equal(negative_model.body_ipos[:, 1:], base_ipos[:, 1:])
        and np.array_equal(positive_model.body_ipos[:, 1:], base_ipos[:, 1:])
    )
    checks["formal_cells_not_executed"] = True
    details.update({
        "tool_sha256": sha256(Path(__file__)),
        "playground_commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
        "selected_traces": len(selected), "formal_cells": 144,
        "maximum_baseline_action_error": max_baseline_error,
        "maximum_saved_fork_delta_error": max_fork_delta_error,
        "maximum_bridge_error_rad": max_bridge_error,
        "maximum_sent_target_error_rad": max_sent_error,
        "maximum_applied_target_error_rad": max_applied_error,
        "identity_branch_max_error": identity_error,
        "smoke_intervention": {
            "disturbance_pitch_norm_rad": smoke["disturbance_pitch_norm_rad"],
            "actor_pitch_norm_rad": smoke["actor_pitch_norm_rad"],
            "fork_action_max_abs": float(np.max(np.abs(smoke["fork_action_difference"]))),
        },
        "devices": [str(device) for device in jax.devices()],
    })
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_TORSO_COM_SIGNED_RESPONSE_CONTRACT" if not failed else "FAIL_TORSO_COM_SIGNED_RESPONSE_CONTRACT"
    payload = {
        "schema_version": "ground_up_torso_com_signed_response_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": details,
        "execution": {"cpu_only": True, "formal_cells_executed": 0, "training": False, "robot_or_rdk": False},
        "authority": {"formal_144_cell_study_if_pass": True, "training": False, "gpu_or_igpu": False, "robot_or_rdk": False},
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


def study(contract_path: Path, output: Path, markdown: Path) -> int:
    contract_payload = json.loads(contract_path.read_text())
    if contract_payload.get("status") != "PASS_TORSO_COM_SIGNED_RESPONSE_CONTRACT":
        raise ValueError("passing signed-response contract required")
    if contract_payload["details"]["tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("study tool changed after contract")
    _manifest, full_result, selected = load_sources()
    _jax, mujoco, env = initialize_environment()
    import onnxruntime as ort

    sessions = {
        key: ort.InferenceSession(str(policy_path(key)), providers=["CPUExecutionProvider"])
        for key in POLICIES
    }
    cells = []
    for trace_index, item in enumerate(selected, start=1):
        rows = load_trace(item)
        key = f"{item['arm']}_{item['step']}"
        states = reconstruct_policy(sessions[key], rows)
        fit_path = P30 if item["fit"] == "p30" else P31
        print(f"[{trace_index}/36] {key} {item['fit']} x={item['command_x']}", flush=True)
        for tick in FORK_TICKS:
            cells.append(run_cell(
                mujoco=mujoco, env=env, item=item, rows=rows,
                policy_state=states[tick], tick=tick, fit_path=fit_path,
            ))
    if len(cells) != 144:
        raise ValueError(f"formal cell count mismatch: {len(cells)}")
    policies = {}
    for key in sorted(POLICIES):
        subset = [cell for cell in cells if cell["policy"] == key]
        classification, localization = classify_policy(subset)
        policies[key] = {"classification": classification, "cells": len(subset), **localization}
    classifications = [row["classification"] for row in policies.values()]
    if all(value == "SYSTEMATIC_CORRECTIVE" for value in classifications):
        decision = "SUPPORT_MEMORY_OR_ESTIMATOR_PREREGISTRATION"
    elif all(value == "SYSTEMATIC_AMPLIFYING" for value in classifications):
        decision = "SUPPORT_OBJECTIVE_SIGN_PREREGISTRATION"
    elif all(value == "PHYSICALLY_NEGLIGIBLE_POLICY" for value in classifications):
        decision = "SUPPORT_ACTUATOR_EFFECT_FORMULATION_PREREGISTRATION"
    else:
        decision = "MIXED_SIGN_NO_POLICY_FAMILY_SELECTED"
    arms = {}
    for arm in ("U_CURRICULUM", "A05_DIRECT", "U05_DIRECT"):
        siblings = {key: row["classification"] for key, row in policies.items() if key.startswith(arm + "_")}
        arms[arm] = {
            "checkpoints": siblings,
            "persistent_same_classification": len(set(siblings.values())) == 1,
            "classification": next(iter(set(siblings.values()))) if len(set(siblings.values())) == 1 else "MIXED_SIBLING_RESPONSE",
        }
    payload = {
        "schema_version": "ground_up_torso_com_signed_response.v1",
        "status": "PASS_TORSO_COM_SIGNED_RESPONSE_COMPLETE",
        "decision": decision, "policies": policies, "arms": arms,
        "aggregate": counts(cells), "cells": cells,
        "sources": {
            "contract_sha256": sha256(contract_path),
            "manifest_sha256": sha256(MANIFEST),
            "full_observation_result_sha256": sha256(FULL_RESULT),
        },
        "thresholds": {"alignment_corrective_max": -0.25, "alignment_amplifying_min": 0.25, "minimum_pitch_vector_norm_rad": 1e-6},
        "execution": {"cpu_only": True, "formal_cells": len(cells), "training": False, "robot_or_rdk": False, "p_value": None},
        "authority": {"next_preregistration_only": True, "training": False, "gpu_or_igpu": False, "robot_or_rdk": False},
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Signed Causal-Response Result", "",
        f"status: `{payload['status']}`", f"decision: `{decision}`", "",
        "| policy | classification | corrective | amplifying | mixed | negligible |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for key, row in policies.items():
        total = row["total"]
        lines.append(
            f"| {key} | `{row['classification']}` | {total['CORRECTIVE']} | {total['AMPLIFYING']} | "
            f"{total['ORTHOGONAL_OR_MIXED']} | {total['PHYSICALLY_NEGLIGIBLE']} |"
        )
    lines.extend(["", "No p-value or training reward is used. The result authorizes only the next preregistration named by the frozen decision.", ""])
    markdown.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "decision": decision, "aggregate": payload["aggregate"]}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("contract", "study"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "contract":
        return contract(args.output)
    if args.contract is None or args.markdown is None:
        parser.error("study mode requires --contract and --markdown")
    return study(args.contract, args.output, args.markdown)


if __name__ == "__main__":
    raise SystemExit(main())
