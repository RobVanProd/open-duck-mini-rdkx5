#!/usr/bin/env python3
"""Build the hash-bound winner-v2 policy-to-runtime handoff package.

This tool does not run simulation, train, access hardware, or select a deployment
checkpoint.  It consumes four already generated CPU full-observation traces and
packages both persistent policy checkpoints required by the evidence contract.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any
import zipfile

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper, shape_inference
import onnxruntime as ort


SCHEMA_VERSION = "winner_v2_rdkx5_native_handoff.v1.1"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
POLICY_DIR = (
    REPO_ROOT
    / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies"
)
FIT_PATH = REPO_ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
REFERENCE_PATH = (
    REPO_ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
)
WINNER_MODULE = (
    REPO_ROOT / "runtime/mini_bdx_runtime/mini_bdx_runtime/winner_v2.py"
)
POLICY_HASHES = {
    512000: "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de",
    1024000: "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece",
}
SELECTED_STEP = 512000
SELECTED_ONNX_SHA256 = POLICY_HASHES[SELECTED_STEP]
FIT_HASH = "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b"
REFERENCE_HASH = "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]
HOME_RAD = np.asarray(
    [
        0.002,
        0.053,
        -0.630,
        1.368,
        -0.784,
        0.0,
        0.0,
        0.0,
        0.0,
        -0.003,
        -0.065,
        0.635,
        1.379,
        -0.796,
    ],
    dtype=np.float32,
)
RESET_QPOS = np.asarray(
    [
        0.0, 0.0, 0.15000000596046448, 1.0, 0.0, 0.0, 0.0,
        0.0020000000949949026, 0.0, 0.05299999937415123, 0.0,
        -0.6299999952316284, 0.0, 1.3680000305175781, 0.0,
        -0.7839999794960022, 0.0, 0.0, 0.0, 0.0, 0.0,
        -0.003000000026077032, 0.0, -0.06499999761581421, 0.0,
        0.6349999904632568, 0.0, 1.378999948501587, 0.0,
        -0.7960000038146973, 0.0,
    ],
    dtype=np.float32,
)
TRACE_TEMPLATE = "winner_v2_{step}_x{command:.3f}_full.jsonl"
GOLDEN_TOLERANCE = 1.0e-6
JAX_EQUIVALENCE_TOLERANCE = 1.0e-6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    if len(rows) != 600 or [row["tick"] for row in rows] != list(range(600)):
        raise ValueError(f"{path}: expected exact ticks 0..599")
    return rows


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: numpy_helper.to_array(item) for item in model.graph.initializer}


def tensor_contract(value_info: Any) -> dict[str, Any]:
    tensor = value_info.type.tensor_type
    dimensions = []
    for dim in tensor.shape.dim:
        if dim.HasField("dim_value"):
            dimensions.append(int(dim.dim_value))
        elif dim.HasField("dim_param"):
            dimensions.append(str(dim.dim_param))
        else:
            dimensions.append(None)
    return {
        "name": value_info.name,
        "dtype": TensorProto.DataType.Name(tensor.elem_type).lower(),
        "rank": len(dimensions),
        "dimensions": dimensions,
    }


def make_intermediate_session(policy: Path) -> ort.InferenceSession:
    model = shape_inference.infer_shapes(onnx.load(str(policy)))
    known = {item.name: item for item in [*model.graph.value_info, *model.graph.output]}
    for name in [
        "raw_continuous_actions",
        "velocity_bounded_actions",
        "deadband_source_actions",
    ]:
        if name in {item.name for item in model.graph.output}:
            continue
        if name in known:
            model.graph.output.append(known[name])
        else:
            model.graph.output.append(
                helper.make_tensor_value_info(name, TensorProto.FLOAT, [1, 14])
            )
    handle = tempfile.NamedTemporaryFile(suffix=".onnx", delete=False)
    handle.close()
    try:
        onnx.save(model, handle.name)
        session = ort.InferenceSession(
            handle.name,
            providers=["CPUExecutionProvider"],
        )
    finally:
        os.unlink(handle.name)
    return session


def gzip_lossless(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as incoming, destination.open("wb") as raw_out:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            compresslevel=9,
            fileobj=raw_out,
            mtime=0,
        ) as outgoing:
            shutil.copyfileobj(incoming, outgoing)


def write_npz_deterministic(path: Path, arrays: dict[str, np.ndarray]) -> None:
    """Write an NPZ with stable member order, timestamps, and permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(
                buffer,
                np.asarray(arrays[name]),
                allow_pickle=False,
            )
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def independent_jax_forward(
    weights: dict[str, np.ndarray], obs: Any, previous_action: Any
) -> Any:
    """Independent JAX replay of the final graph from frozen initializers."""
    import jax
    import jax.numpy as jnp

    z = (obs - jnp.asarray(weights["obs_mean"])) / jnp.asarray(weights["obs_std"])
    reference = obs[jnp.asarray(weights["reference_indices"], dtype=jnp.int32)]
    reference = jnp.clip(reference, weights["clip_min"], weights["clip_max"])
    location = jnp.arctanh(reference)
    for index in range(3):
        pre = (
            z @ jnp.asarray(weights[f"trunk_{index}_weight"])
            + jnp.asarray(weights[f"trunk_{index}_bias"])
        )
        z = pre * jax.nn.sigmoid(pre)
    residual = (
        z @ jnp.asarray(weights["residual_weight"])
        + jnp.asarray(weights["residual_bias"])
    )
    raw = jnp.tanh(location + residual)
    delta = jnp.asarray(weights["max_action_delta"])[0]
    bounded = jnp.maximum(
        jnp.minimum(raw, previous_action + delta), previous_action - delta
    )
    home = jnp.asarray(weights["guard_home"])[0]
    indices = jnp.asarray(weights["guard_joint_obs_indices"], dtype=jnp.int32)
    actual = home + obs[indices]
    scale = jnp.asarray(weights["guard_action_scale"])[0]
    desired = home + bounded * scale
    margin = jnp.asarray(weights["guard_margin"])[0]
    target = jnp.minimum(jnp.maximum(desired, actual - margin), actual + margin)
    pitch_action = jnp.clip(
        (target - home) / scale,
        jnp.asarray(weights["guard_action_min"])[0],
        jnp.asarray(weights["guard_action_max"])[0],
    )
    guarded = jnp.where(
        jnp.asarray(weights["guard_pitch_mask"])[0], pitch_action, bounded
    )
    command_index = int(weights["deadband_command_index"][0])
    return jnp.where(
        jnp.abs(obs[command_index]) <= weights["deadband_abs_limit"][0],
        jnp.asarray(weights["deadband_zero_action"])[0],
        guarded,
    )


def observation_slices(
    normalizers: dict[str, dict[str, list[float]]]
) -> dict[str, Any]:
    return {
        "schema_version": "winner_v2_observation_map.v1",
        "dimension": 115,
        "dtype": "float32",
        "normalization": {
            "location": "inside_each_ONNX_graph",
            "equation": "obs_normalized=(obs-obs_mean)/obs_std",
            "per_checkpoint_initializers": normalizers,
        },
        "joint_order": JOINT_NAMES,
        "slices": [
            {
                "start": 0, "end_exclusive": 3, "name": "gyro_local_xyz",
                "units": "rad/s", "scale": 1.0, "clipping": None,
                "frame": "torso IMU site local xyz", "sign": "MuJoCo sensor axes",
                "source_timing": "current pre-inference state at tick t",
                "training_noise": "uniform +/-0.1 rad/s at noise level 1; formal eval level 0",
                "delay_filter": "no actor-path delay or filter",
                "privileged": False, "reset": [0.0, 0.0, 0.0],
                "first_tick": "golden pack obs[0:3]",
            },
            {
                "start": 3, "end_exclusive": 6, "name": "accelerometer_local_xyz",
                "units": "m/s^2", "scale": 1.0, "clipping": None,
                "frame": "torso IMU site local xyz", "sign": "MuJoCo sensor axes",
                "source_timing": "current pre-inference state at tick t",
                "training_noise": "uniform +/-0.05 m/s^2 at noise level 1; formal eval level 0",
                "delay_filter": "no actor-path delay or filter; MuJoCo specific-force sensor includes gravity response",
                "privileged": False,
                "reset": "deterministic simulator forward value; not assumed to be zero",
                "first_tick": "golden pack obs[3:6] (reset settling transient)",
            },
            {
                "start": 6, "end_exclusive": 13, "name": "command",
                "elements": ["vx", "vy", "yaw_rate", "neck_pitch", "head_pitch", "head_yaw", "head_roll"],
                "units": ["m/s", "m/s", "rad/s", "rad", "rad", "rad", "rad"],
                "scale": 1.0, "clipping": "host rejects unsupported command",
                "frame": "base-local commanded velocity; logical head angles",
                "sign": "positive forward/left/CCW and positive logical joint convention",
                "source_timing": "command pinned before observation at tick t",
                "training_noise": "none", "delay_filter": "none", "privileged": False,
                "reset": "requested command", "first_tick": "requested command",
            },
            {
                "start": 13, "end_exclusive": 27, "name": "joint_position_error",
                "units": "rad", "scale": 1.0, "clipping": None,
                "frame": "logical joint coordinates", "sign": "joint_order logical sign",
                "joint_order": JOINT_NAMES,
                "source_timing": "current measured/simulated position at tick t minus home",
                "training_noise": "hips +/-0.03, knees +/-0.05, ankles +/-0.08 rad at noise level 1; eval 0",
                "delay_filter": "no explicit actor-path delay/filter", "privileged": False,
                "reset": [0.0] * 14, "first_tick": [0.0] * 14,
            },
            {
                "start": 27, "end_exclusive": 41, "name": "joint_velocity_scaled",
                "units": "rad (rad/s multiplied by 0.05 s)", "scale": 0.05,
                "clipping": None, "frame": "logical joint coordinates",
                "sign": "joint_order logical sign", "joint_order": JOINT_NAMES,
                "source_timing": "current measured/simulated joint velocity at tick t",
                "training_noise": "raw velocity +/-2.5 rad/s at noise level 1 before x0.05; eval 0",
                "delay_filter": "no explicit actor-path delay/filter", "privileged": False,
                "reset": [0.0] * 14, "first_tick": [0.0] * 14,
            },
            {
                "start": 41, "end_exclusive": 55, "name": "final_action_t_minus_2",
                "units": "normalized action", "scale": 1.0, "clipping": "already final bounded",
                "frame": "joint_order", "sign": "joint logical sign", "joint_order": JOINT_NAMES,
                "source_timing": "final graph/environment action from control tick t-2",
                "training_noise": "none", "delay_filter": "two-tick history", "privileged": False,
                "reset": [0.0] * 14, "first_tick": [0.0] * 14,
            },
            {
                "start": 55, "end_exclusive": 69, "name": "final_action_t_minus_3",
                "units": "normalized action", "scale": 1.0, "clipping": "already final bounded",
                "frame": "joint_order", "sign": "joint logical sign", "joint_order": JOINT_NAMES,
                "source_timing": "control tick t-3", "training_noise": "none",
                "delay_filter": "three-tick history", "privileged": False,
                "reset": [0.0] * 14, "first_tick": [0.0] * 14,
            },
            {
                "start": 69, "end_exclusive": 83, "name": "final_action_t_minus_4",
                "units": "normalized action", "scale": 1.0, "clipping": "already final bounded",
                "frame": "joint_order", "sign": "joint logical sign", "joint_order": JOINT_NAMES,
                "source_timing": "control tick t-4", "training_noise": "none",
                "delay_filter": "four-tick history", "privileged": False,
                "reset": [0.0] * 14, "first_tick": [0.0] * 14,
            },
            {
                "start": 83, "end_exclusive": 97, "name": "bridge_realized_applied_target_previous_transition",
                "units": "absolute logical rad", "scale": 1.0, "clipping": "P30 delay/tau/velocity transition",
                "frame": "logical joint coordinates", "sign": "joint logical sign", "joint_order": JOINT_NAMES,
                "source_timing": "value realized by the preceding transition and visible at observation tick t",
                "training_noise": "none", "delay_filter": "per-joint P30 delay/tau/velocity bridge",
                "privileged": False,
                "source_variable": "info['ground_up_actuator_bridge_applied_targets']",
                "source_update": "Joystick._apply_ground_up_measured_actuator_bridge; updated before physics, then read by _get_obs",
                "hardware_source": "host P30 forward observer from previously confirmed sent targets; not measured joint position",
                "reset": HOME_RAD.astype(float).tolist(), "first_tick": HOME_RAD.astype(float).tolist(),
            },
            {
                "start": 97, "end_exclusive": 99, "name": "foot_contacts_left_right",
                "units": "boolean encoded float32", "scale": 1.0, "clipping": "0 or 1",
                "frame": "left, right", "sign": "1=contact, 0=no contact",
                "source_timing": "current contact state at tick t",
                "training_noise": "none", "delay_filter": "none", "privileged": False,
                "reset": [1.0, 1.0], "first_tick": [1.0, 1.0],
            },
            {
                "start": 99, "end_exclusive": 101, "name": "gait_phase_cos_sin",
                "units": "unitless", "scale": 1.0, "clipping": None,
                "frame": "[cos,sin]", "sign": "positive mathematical convention",
                "source_timing": "current phase index before inference; advance after observation for next tick",
                "training_noise": "none", "delay_filter": "27-tick deterministic phase", "privileged": False,
                "reset": [1.0, 0.0], "first_tick": [1.0, 0.0],
            },
            {
                "start": 101, "end_exclusive": 115, "name": "projected_reference_action",
                "units": "normalized action", "scale": 1.0, "clipping": "source table already projected",
                "frame": "joint_order", "sign": "joint logical sign", "joint_order": JOINT_NAMES,
                "source_timing": "lookup at current command3 and current phase index used by obs[99:101]",
                "training_noise": "none", "delay_filter": "nearest L1 command-table row; no temporal filter",
                "privileged": False,
                "hardware_source": "deterministic host lookup, not an X5 sensor",
                "reset": [0.0] * 14,
                "first_tick": "zero for x=0; reference table phase 0 for supported moving command",
            },
        ],
        "hardware_availability": {
            "direct_X5_or_servo_inputs": ["gyro", "accelerometer", "joint position", "joint velocity", "foot GPIO contact"],
            "host_internal_inputs": ["command", "three action histories", "phase", "projected reference", "P30 observer state"],
            "not_directly_measured": ["bridge realized target obs[83:97]"],
            "privileged_actor_inputs": [],
        },
    }


def build_policy_pack(
    *, step: int, command: float, rows: list[dict[str, Any]], policy: Path
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    model = onnx.load(str(policy))
    weights = initializers(model)
    session = make_intermediate_session(policy)
    output_names = [
        "continuous_actions",
        "previous_action_out",
        "raw_continuous_actions",
        "velocity_bounded_actions",
        "deadband_source_actions",
    ]
    arrays: dict[str, list[Any]] = {
        key: []
        for key in [
            "tick", "obs", "obs_normalized", "command_raw", "command_normalized",
            "phase_index_before", "phase_index_after", "phase_before", "phase_after",
            "previous_action_in", "previous_action_out", "raw_action",
            "velocity_bounded_action", "guard_bounded_action", "final_action",
            "target_pre_runtime_rate_limit_rad", "sent_target_rad",
            "applied_target_rad", "observer_estimate_next_tick_rad",
            "actual_position_rad", "foot_contacts", "action_saturated",
            "sent_target_rate_excess_rad_s", "external_5p24_limiter_changed",
            "tracking_error_rad", "done",
        ]
    }
    previous = np.zeros((1, 14), dtype=np.float32)
    jax_max_error = 0.0
    onnx_trace_max_error = 0.0
    state_output_max_error = 0.0
    external_limiter_max_error = 0.0
    commanded_substitution_first_divergence = None
    advanced_phase_first_divergence = None
    commanded_previous = previous.copy()
    advanced_previous = previous.copy()
    reference_table = np.load(REFERENCE_PATH)
    try:
        import jax
        import jax.numpy as jnp

        jax_forward = jax.jit(
            lambda one_obs, one_state: independent_jax_forward(
                weights, one_obs, one_state
            )
        )
    except ImportError:
        jax_forward = None

    for row in rows:
        tick = int(row["tick"])
        obs = np.asarray(row["obs_state"], dtype=np.float32)
        values = session.run(
            output_names,
            {"obs": obs[None], "previous_action": previous},
        )
        final, state, raw, velocity, guarded = [
            np.asarray(value, dtype=np.float32) for value in values
        ]
        recorded_action = np.asarray(row["action"], dtype=np.float32)[None]
        onnx_trace_max_error = max(
            onnx_trace_max_error,
            float(np.max(np.abs(final - recorded_action))),
        )
        state_output_max_error = max(
            state_output_max_error, float(np.max(np.abs(final - state)))
        )

        if jax_forward is not None:
            jax_action = jax_forward(jnp.asarray(obs), jnp.asarray(previous[0]))
            jax_max_error = max(
                jax_max_error,
                float(np.max(np.abs(np.asarray(jax_action) - final[0]))),
            )
        else:
            jax_max_error = float("nan")

        target_pre = np.asarray(row["target_pre_rate_limit_rad"], dtype=np.float32)
        sent = np.asarray(row["sent_target_rad"], dtype=np.float32)
        external_limiter_max_error = max(
            external_limiter_max_error, float(np.max(np.abs(target_pre - sent)))
        )
        phase_index = int(row["oracle_state"]["phase_index"])
        next_index = (phase_index + 1) % 27
        next_phase = np.asarray(
            [
                np.cos(next_index / 27.0 * 2.0 * np.pi),
                np.sin(next_index / 27.0 * 2.0 * np.pi),
            ],
            dtype=np.float32,
        )
        normalized = (obs - weights["obs_mean"]) / weights["obs_std"]

        # Measure the earliest semantic divergence from the legacy commanded-
        # target slice.  Tick zero shares the home initialization by contract.
        commanded_obs = obs.copy()
        if tick > 0:
            commanded_obs[83:97] = np.asarray(
                rows[tick - 1]["sent_target_rad"], dtype=np.float32
            )
        commanded_action, commanded_state = session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": commanded_obs[None], "previous_action": commanded_previous},
        )
        if (
            commanded_substitution_first_divergence is None
            and np.max(np.abs(commanded_action - final)) > GOLDEN_TOLERANCE
        ):
            commanded_substitution_first_divergence = {
                "tick": tick,
                "max_action_error": float(np.max(np.abs(commanded_action - final))),
                "obs83_97_max_error_rad": float(
                    np.max(np.abs(commanded_obs[83:97] - obs[83:97]))
                ),
            }
        commanded_previous = np.asarray(commanded_state, dtype=np.float32)

        # Wrong advanced-first semantics must advance both phase and reference.
        advanced_obs = obs.copy()
        advanced_obs[99:101] = next_phase
        if np.linalg.norm(advanced_obs[6:9]) <= 0.01:
            advanced_obs[101:115] = 0.0
        else:
            command_index = int(
                np.argmin(
                    np.sum(
                        np.abs(
                            np.asarray(reference_table["commands"], dtype=np.float32)
                            - advanced_obs[6:9]
                        ),
                        axis=1,
                    )
                )
            )
            advanced_obs[101:115] = reference_table["actions"][command_index, next_index]
        advanced_action, advanced_state = session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": advanced_obs[None], "previous_action": advanced_previous},
        )
        if (
            advanced_phase_first_divergence is None
            and np.max(np.abs(advanced_action - final)) > GOLDEN_TOLERANCE
        ):
            advanced_phase_first_divergence = {
                "tick": tick,
                "max_action_error": float(np.max(np.abs(advanced_action - final))),
            }
        advanced_previous = np.asarray(advanced_state, dtype=np.float32)

        items = {
            "tick": tick,
            "obs": obs,
            "obs_normalized": normalized.astype(np.float32),
            "command_raw": obs[6:13],
            "command_normalized": normalized[6:13].astype(np.float32),
            "phase_index_before": phase_index,
            "phase_index_after": next_index,
            "phase_before": obs[99:101],
            "phase_after": next_phase,
            "previous_action_in": previous[0],
            "previous_action_out": state[0],
            "raw_action": raw[0],
            "velocity_bounded_action": velocity[0],
            "guard_bounded_action": guarded[0],
            "final_action": final[0],
            "target_pre_runtime_rate_limit_rad": target_pre,
            "sent_target_rad": sent,
            "applied_target_rad": np.asarray(row["applied_target_rad"], dtype=np.float32),
            "observer_estimate_next_tick_rad": np.asarray(
                row["policy_observer_applied_target_rad"], dtype=np.float32
            ),
            "actual_position_rad": np.asarray(row["actual_position_rad"], dtype=np.float32),
            "foot_contacts": np.asarray(row["foot_contacts"], dtype=np.int8),
            "action_saturated": np.asarray(row["action_saturated"], dtype=np.int8),
            "sent_target_rate_excess_rad_s": np.asarray(
                row["sent_target_rate_excess_rad_s"], dtype=np.float32
            ),
            "external_5p24_limiter_changed": bool(np.max(np.abs(target_pre - sent)) > 0.0),
            "tracking_error_rad": np.asarray(row["tracking_error_rad"], dtype=np.float32),
            "done": bool(row["done"]),
        }
        for key, value in items.items():
            arrays[key].append(value)
        previous = state.copy()

    packed = {key: np.asarray(value) for key, value in arrays.items()}
    evidence = {
        "step": step,
        "command_x": command,
        "rows": len(rows),
        "onnx_to_frozen_trace_max_abs_error": onnx_trace_max_error,
        "onnx_action_to_state_output_max_abs_error": state_output_max_error,
        "independent_jax_from_onnx_initializers_max_abs_error": jax_max_error,
        "jax_comparison_scope": (
            "independent CPU JAX replay of the final graph using frozen ONNX "
            "initializers; not an Orbax-checkpoint restore comparison"
        ),
        "external_5p24_limiter_max_abs_change_rad": external_limiter_max_error,
        "legacy_commanded_target_substitution_first_divergence": (
            commanded_substitution_first_divergence
        ),
        "advanced_first_phase_substitution_first_divergence": (
            advanced_phase_first_divergence
        ),
    }
    return packed, evidence


def compact_rows(pack: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    result = []
    for tick in range(5):
        row = {}
        for key, value in pack.items():
            item = value[tick]
            row[key] = item.tolist() if isinstance(item, np.ndarray) else item.item()
        result.append(row)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, default=Path("/tmp"))
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    trace_root = args.trace_root.resolve()
    output = args.output_root.resolve()

    for step, expected in POLICY_HASHES.items():
        path = POLICY_DIR / f"T2_EQUAL_{step}.onnx"
        if sha256(path) != expected:
            raise SystemExit(f"policy hash mismatch: {path}")
    if sha256(FIT_PATH) != FIT_HASH or sha256(REFERENCE_PATH) != REFERENCE_HASH:
        raise SystemExit("fit/reference hash mismatch")

    output.mkdir(parents=True, exist_ok=True)
    for relative in ["policies", "observer", "reference", "golden/full_traces"]:
        (output / relative).mkdir(parents=True, exist_ok=True)
    for step in POLICY_HASHES:
        shutil.copy2(
            POLICY_DIR / f"T2_EQUAL_{step}.onnx",
            output / "policies" / f"T2_EQUAL_{step}.onnx",
        )
    shutil.copy2(FIT_PATH, output / "observer/p30_actuator_fit.json")
    shutil.copy2(WINNER_MODULE, output / "observer/winner_v2_contract.py")
    shutil.copy2(
        REFERENCE_PATH,
        output / "reference/ground_up_projected_reference_feature_table.npz",
    )

    candidates = []
    normalizers: dict[str, dict[str, list[float]]] = {}
    compact: dict[str, Any] = {
        "schema_version": "winner_v2_compact_golden.v1",
        "description": "ticks 0..4; complete 600-tick tensors are in adjacent NPZ packs",
        "joint_order": JOINT_NAMES,
        "cells": [],
    }
    evidence_cells = []

    for step, expected_hash in POLICY_HASHES.items():
        policy = POLICY_DIR / f"T2_EQUAL_{step}.onnx"
        model = onnx.load(str(policy))
        weights = initializers(model)
        normalizers[str(step)] = {
            "obs_mean": weights["obs_mean"].astype(float).tolist(),
            "obs_std": weights["obs_std"].astype(float).tolist(),
        }
        candidates.append(
            {
                "checkpoint_step": step,
                "role": (
                    "selected_runtime_v2_review_checkpoint"
                    if step == SELECTED_STEP
                    else "persistent_audit_sibling_not_selected_for_runtime"
                ),
                "path": f"policies/T2_EQUAL_{step}.onnx",
                "bytes": policy.stat().st_size,
                "sha256": expected_hash,
                "onnx_ir_version": int(model.ir_version),
                "producer_name": model.producer_name,
                "producer_version": model.producer_version,
                "opsets": [
                    {"domain": item.domain, "version": int(item.version)}
                    for item in model.opset_import
                ],
                "inputs": [tensor_contract(item) for item in model.graph.input],
                "outputs": [tensor_contract(item) for item in model.graph.output],
                "nodes": len(model.graph.node),
                "initializers": len(model.graph.initializer),
            }
        )
        for command in [0.0, 0.08]:
            trace = trace_root / TRACE_TEMPLATE.format(step=step, command=command)
            if not trace.is_file():
                raise SystemExit(f"missing full-observation trace: {trace}")
            rows = load_rows(trace)
            pack, evidence = build_policy_pack(
                step=step, command=command, rows=rows, policy=policy
            )
            stem = f"T2_EQUAL_{step}_x{command:.3f}"
            npz_path = output / "golden" / f"{stem}.npz"
            write_npz_deterministic(npz_path, pack)
            gzip_path = output / "golden/full_traces" / f"{stem}.jsonl.gz"
            gzip_lossless(trace, gzip_path)
            evidence.update(
                {
                    "golden_npz": str(npz_path.relative_to(output)),
                    "golden_npz_sha256": sha256(npz_path),
                    "full_trace_gzip": str(gzip_path.relative_to(output)),
                    "full_trace_gzip_sha256": sha256(gzip_path),
                    "source_jsonl_sha256": sha256(trace),
                }
            )
            evidence_cells.append(evidence)
            compact["cells"].append(
                {
                    "step": step,
                    "command_x": command,
                    "policy_sha256": expected_hash,
                    "ticks": compact_rows(pack),
                }
            )

    write_json(output / "compact_golden_vectors.json", compact)
    write_json(output / "observation_map.json", observation_slices(normalizers))

    graph_contract = {
        "schema_version": SCHEMA_VERSION,
        "disposition": "REQUIRES_REVIEWED_115_RUNTIME_V2",
        "policy_handoff_status": "BLOCKED",
        "single_selected_deployment_checkpoint": SELECTED_STEP,
        "selected_onnx_sha256": SELECTED_ONNX_SHA256,
        "selection_reason": (
            "Both persistence checkpoints passed the prospectively frozen native-"
            "representation matrix. The first ranking criterion selected 512000 "
            "on lower worst tracking p95; training and simulator reward had no weight."
        ),
        "policy_candidates": candidates,
        "state_contract": {
            "input": "previous_action",
            "output": "previous_action_out",
            "shape": [1, 14],
            "dtype": "float32",
            "initial_value": [0.0] * 14,
            "units": "normalized final action",
            "joint_order": JOINT_NAMES,
            "update_order": [
                "compose obs[t] with current phase and preceding P30 observer value",
                "infer(obs[t], previous_action[t])",
                "use continuous_actions[t] as final normalized action",
                "store previous_action_out[t] as previous_action[t+1]",
                "send home + action*0.25 after proving host 5.24 limiter is identity",
                "advance P30 observer exactly once from the confirmed sent target",
                "advance phase exactly once for obs[t+1]",
            ],
        },
        "graph_internal_transforms": {
            "normalization": True,
            "reference_residual_composition": True,
            "measured_hard_vector_projection": True,
            "actual_centered_pitch_guard": True,
            "zero_command_deadband": True,
            "conservative_left_ankle_repair": True,
            "P30_delay_tau_observer": False,
        },
        "transform_artifacts": {
            "actual_centered_guard": {
                "contract_sha256": "fccc6fa0127ab11f7044b9623709a5b0efda9447c972bc3b0ed699d3ec07a882",
                "composer_sha256": "078ed5a0396fda357083e5a90d7237f39d8f1c889e0cc2db71d119c6e5ab0259",
            },
            "zero_command_deadband": {
                "contract_sha256": "e91a775c213d16d0fbe48ee218ea55ea06f099021e89d382cea7479799c6720d",
                "composer_sha256": "37264573cc86fc31df4caf97b65ac7ba503049bd1d89979ed437957a52274451",
            },
            "conservative_left_ankle_envelope": {
                "contract_sha256": "b52f98d2810678b3b7cc4fa47352432991eb180c9326133af05b0647434d716d",
                "composer_sha256": "e61bb0d5484251b0b29cbe099743e8c236b8ffb00539480c2b1bb4f954648455",
            },
            "P30_fit_sha256": FIT_HASH,
            "reference_composer_sha256": "5c90994a24aa223c94f3a51927228e97000f6118c927561a87a3f2684dcf4889",
        },
        "action_contract": {
            "output_semantics": "final normalized absolute home-offset action",
            "target_equation": "logical_target_rad=home_rad+continuous_actions*0.25",
            "home_rad": HOME_RAD.astype(float).tolist(),
            "action_scale_rad": 0.25,
            "joint_order": JOINT_NAMES,
            "max_action_delta_normalized_per_tick": candidates and initializers(
                onnx.load(str(POLICY_DIR / "T2_EQUAL_512000.onnx"))
            )["max_action_delta"][0].astype(float).tolist(),
            "measured_rate_limits_rad_s": [
                5.24, 5.24, 1.50, 1.50, 1.50, 5.24, 5.24,
                5.24, 5.24, 5.24, 5.24, 1.25, 1.00, 1.25,
            ],
            "authoritative_layer": "final ONNX output",
            "host_5p24_limiter": (
                "permitted only as an asserted identity/no-op; any changed target is a contract failure"
            ),
            "head_overlay": "disabled and forbidden; head commands must be zero",
            "extra_filter": "forbidden",
            "deadband": {"obs_index": 6, "absolute_threshold": float(initializers(
                onnx.load(str(POLICY_DIR / "T2_EQUAL_512000.onnx"))
            )["deadband_abs_limit"][0]), "zeroes_action_and_state": True},
            "left_ankle_repair": {
                "joint_index": 4,
                "joint_name": "left_ankle",
                "initializer": "max_action_delta[0,4]",
                "value_normalized_per_tick": 0.11999999731779099,
                "rate_rad_s": 1.50,
                "prior_rate_rad_s": 1.75,
            },
        },
        "phase_command_reset": {
            "period_ticks": 27,
            "representation": "[cos(2*pi*index/27), sin(2*pi*index/27)]",
            "initial_index": 0,
            "tick0_phase": [1.0, 0.0],
            "ordering": "observe current phase, infer, advance once for next tick",
            "commands": [0.0, 0.074, 0.077, 0.080],
            "moving_support_m_s": [0.074, 0.080],
            "zero_command_behavior": "deadband emits exact zero action and state for 600 ticks",
            "other_command_axes": "must be exactly zero",
            "reset_qpos": RESET_QPOS.astype(float).tolist(),
            "reset_qvel": [0.0] * 30,
            "reset_ctrl_rad": HOME_RAD.astype(float).tolist(),
            "contacts": [1.0, 1.0],
            "physics_dt_s": 0.002,
            "control_dt_s": 0.02,
            "physics_substeps": 10,
        },
        "authority": {
            "robot_clearance": False,
            "gate5": False,
            "runtime_deployment": False,
            "robot_or_rdk_x5": False,
            "gpu_or_igpu": False,
            "training_or_hosted_compute": False,
        },
        "unresolved_blockers": [
            "No single deployment checkpoint is selected; both graphs are persistence evidence.",
            "The reviewed native runtime is the frozen 101-D v1 contract; a reviewed 115-D v2 implementation is absent.",
            "The real-build torso COM/inertia audit is incomplete (46 required inputs missing), so robot clearance remains NO.",
        ],
    }
    write_json(output / "policy_contract.json", graph_contract)

    fit = json.loads(FIT_PATH.read_text())
    joint_fit = {}
    for name in JOINT_NAMES:
        combined = fit.get("primary", {}).get("joints", {}).get(name, {}).get("combined")
        if combined is None:
            joint_fit[name] = {
                "delay_ticks": 0,
                "tau_s": 0.0,
                "velocity_limit_rad_s": "infinity",
                "fit_error_statistics": None,
                "semantics": "pass-through; no measured P30 fit for this non-pitch joint",
            }
        else:
            joint_fit[name] = {
                key: combined[key]
                for key in [
                    "delay_ticks", "tau_s", "velocity_limit_rad_s", "rmse",
                    "mae", "p95_abs_error", "p99_abs_error", "max_abs_error",
                ]
            }
    observer_contract = {
        "schema_version": "winner_v2_p30_observer_handoff.v1",
        "host_code": "observer/winner_v2_contract.py:FittedBridgeObserver",
        "inside_ONNX": False,
        "fit_path": "observer/p30_actuator_fit.json",
        "fit_sha256": FIT_HASH,
        "dt_s": 0.02,
        "joint_order": JOINT_NAMES,
        "initial_value_rad": HOME_RAD.astype(float).tolist(),
        "initial_queue": "home repeated delay_ticks+1 per joint",
        "input": "confirmed logical sent target in rad; no hardware sensor input",
        "output": "estimated realized/applied absolute logical target in rad for next observation obs[83:97]",
        "equations": [
            "queue_i.append(sent_i); retain delay_i+1 values; delayed_i=queue_i[0]",
            "alpha_i=1-exp(-0.02/tau_i) when tau_i>0, otherwise desired_i=delayed_i",
            "desired_i=previous_i+alpha_i*(delayed_i-previous_i)",
            "step_i=clip(desired_i-previous_i, +/-velocity_limit_i*0.02)",
            "value_i=previous_i+step_i",
        ],
        "timing": (
            "obs[t] receives the observer value from the preceding confirmed transition; "
            "after action[t] is converted and sent, advance exactly once for obs[t+1]"
        ),
        "staleness_failure": (
            "If any required sensor sample is stale, the target send is unconfirmed, the "
            "20 ms tick is missed, or update count is ambiguous, invalidate the controller "
            "and stop inference; never silently reuse or double-step observer state."
        ),
        "fit_provenance": {
            "telemetry_jsonl": fit["primary"]["telemetry_jsonl"],
            "startup_ticks_excluded": fit["primary"]["startup_ticks"],
            "selection_metric": fit["primary"]["selection_metric"],
            "fit_population": "P30 fixed-target hardware telemetry",
            "cross_fit_test": (
                "P30 observer evaluated as a fixed artifact on both P30 and independently "
                "measured P31/34 plant matrices; both checkpoints, x=0/.074/.077/.080"
            ),
            "cross_fit_result_sha256": "804165bd1fdf45fdb1ab8369617e460d65de60a9f6f0ced90337429b56162231",
            "cross_fit_cells": "32/32 pass",
            "maximum_P30_vs_P31_34_observer_separation_rad": 0.004135804,
        },
        "per_joint_parameters_and_fit_errors": joint_fit,
        "golden_agreement": "all 2400 packaged rows: observer estimate equals P30 simulated applied target exactly",
    }
    write_json(output / "observer_contract.json", observer_contract)

    evidence = {
        "schema_version": "winner_v2_handoff_golden_evidence.v1",
        "execution": {
            "cpu_only": True,
            "robot_or_rdk": False,
            "gpu_or_igpu": False,
            "training": False,
            "playground_control_commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
            "patch_hashes": {
                "ground_up_search_runner.patch": "6a176589b766de65ac2746c66f3387bfca5384d6ce4adf3703c752d8103a5e55",
                "ground_up_reference_conditioned.patch": "4138ecddb9ffc0df468a2780522c1732bc4b0e1a0865d181da1112d1c16902fb",
                "ground_up_recipe_search.patch": "3f5d892f5ce531207de6c86b18c9f5dbea83bc131a3fc2e5085851c2e4e3e5f8",
                "ground_up_stage1_mechanism_stack.patch": "cf5155dfd54a4699865b9823e8bf090f9f54b0e53df5583eb448e315d60053dc",
                "ground_up_nominal_reference_bootstrap.patch": "0d89b85815eb570115ec5f35d677aba68299f977b3e36c60b10dfa869533ebba",
                "ground_up_signed_progress_objective.patch": "13ddc699d3a005416a5790152b4a9d4f442216cfec4a991f93be65bde85ffa5b",
                "ground_up_reference_residual_actor.patch": "57bcf2394fa47745e9c26c6933e58a06c3799aba35e7000762befc5fac2f7d3b",
                "ground_up_hard_vector_command_support.patch": "900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875",
                "ground_up_measured_actuator_bridge.patch": "133531963abea46cd0394526a2fa88b018fc21ca68c365863304e3e96d6ca0df",
                "ground_up_applied_target_observation.patch": "bdcac27115fcbe855079f5365ac046e863a9b302ff16f560d12a26cd492f2821",
                "ground_up_tracking_tail_exceedance.patch": "9f716243e0c4ef487ef4227ef0cb9f389ed43c0456435987ac0846e1b629811e",
            },
            "reference_residual_network_sha256": "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
            "seed": 167931544,
            "ticks_per_trace": 600,
            "commands": [0.0, 0.08],
            "fit": "P30",
            "policy_phase_advance_before_observation": False,
            "reset_mode": "home-support",
            "noise": 0.0,
            "action_delay_ticks": 0,
        },
        "tolerances": {
            "runtime_ONNX_golden_max_abs": GOLDEN_TOLERANCE,
            "independent_JAX_replay_max_abs": JAX_EQUIVALENCE_TOLERANCE,
            "zero_deadband_action_and_state": "bit-exact zero",
        },
        "cells": evidence_cells,
        "formal_trace_reproduction": (
            "Fresh full-observation rows reproduce the pre-existing frozen P30 traces "
            "at zero error for action, sent target, applied target, actual position, and obs[0:6]."
        ),
        "trace_generator_command": (
            "python tools/generate_winner_v2_runtime_handoff_traces.py "
            "--recreate --output-root /tmp"
        ),
        "package_generator_command": (
            "CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu "
            "python tools/build_winner_v2_runtime_handoff.py --trace-root /tmp"
        ),
    }
    write_json(output / "golden_evidence.json", evidence)

    environment = {
        "schema_version": "winner_v2_handoff_environment.v1",
        "generation": {
            "python": "3.12.13",
            "numpy": "2.5.1",
            "onnx": "1.22.0",
            "onnxruntime": "1.27.0",
            "jax": "0.8.2",
            "jaxlib": "0.8.2",
            "mujoco": "3.9.0",
            "backend": "cpu",
        },
        "runtime_minimum": {
            "python": ">=3.10",
            "numpy": ">=1.26",
            "onnx": ">=1.16",
            "onnxruntime": ">=1.20.1",
            "providers": ["CPUExecutionProvider"],
        },
    }
    write_json(output / "environment_lock.json", environment)

    # README.md and inspect_and_smoke.py are maintained text-first files.  Hash
    # every package member except the manifest itself to avoid self-reference.
    required = [
        path
        for path in output.rglob("*")
        if (
            path.is_file()
            and path.name != "manifest.json"
            and path.suffix != ".pyc"
            and "__pycache__" not in path.parts
        )
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_self_hash": "not_included_to_avoid_self_reference",
        "policy_repository": "RobVanProd/open-duck-mini-rdkx5",
        "policy_branch": "codex/torso-com-decode-probe",
        "policy_evidence_base_commit": "e0badd7aa79ff791212b8d3822f9eefdc4c162e0",
        "handoff_metadata_correction_preidentity_commit": (
            "aa6a4466d15ccd1bdcc02a50ec3267c5a9bc67f0"
        ),
        "handoff_commit": "reported externally after commit; cannot be self-embedded",
        "dirty_state_at_generation": "package files intentionally uncommitted",
        "disposition": "REQUIRES_REVIEWED_115_RUNTIME_V2",
        "policy_handoff_status": "BLOCKED",
        "selected_checkpoint_step": SELECTED_STEP,
        "selected_onnx_sha256": SELECTED_ONNX_SHA256,
        "robot_clearance": False,
        "files": [
            {
                "path": str(path.relative_to(output)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(required)
        ],
        "external_source_artifacts": [
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in [
                REPO_ROOT / "outputs/analysis/winner_v2_runtime_contract.json",
                REPO_ROOT / "outputs/analysis/winner_v2_observer_cross_fit_result.json",
                REPO_ROOT / "outputs/analysis/winner_v2_p30_observer_pin.json",
                REPO_ROOT / "outputs/analysis/policy_robot_readiness_reaudit_20260719.json",
                REPO_ROOT / "outputs/analysis/ground_up_actual_centered_guard_transform_contract.json",
                REPO_ROOT / "outputs/analysis/ground_up_command_deadband_repair_transform_contract.json",
                REPO_ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_transform_contract.json",
                REPO_ROOT / "tools/build_ground_up_actual_centered_guard_screen.py",
                REPO_ROOT / "tools/build_ground_up_command_deadband_repair.py",
                REPO_ROOT / "tools/build_ground_up_dual_fit_conservative_envelope_repair.py",
                REPO_ROOT / "tools/closed_loop_sim_eval.py",
                REPO_ROOT / "tools/generate_winner_v2_runtime_handoff_traces.py",
                REPO_ROOT / "tools/build_winner_v2_runtime_handoff.py",
            ]
        ],
    }
    write_json(output / "manifest.json", manifest)

    print(
        json.dumps(
            {
                "status": "PASS_HANDOFF_PACKAGE_BUILT_BLOCKED_FOR_REVIEW",
                "output": str(output),
                "manifest_sha256": sha256(output / "manifest.json"),
                "files": len(manifest["files"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
