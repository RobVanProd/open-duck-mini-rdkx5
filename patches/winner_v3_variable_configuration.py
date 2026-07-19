"""Frozen winner-v3 variable-configuration training primitives.

This module contains only deterministic CPU/JAX plumbing for the preregistered
``R64_ZERO_INIT_RECURRENT_ADAPTER`` curriculum.  It does not select a policy,
change the reward, or expose any simulator configuration parameter to the
actor.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import jax
import jax.numpy as jnp
from mujoco import mjx
from mujoco.mjx._src import math as mjx_math


TORSO_BODY_NAME = "trunk_assembly"
TORSO_BODY_ID = 2
FLOOR_GEOM_ID = 0

JOINT_NAMES = (
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
)

CONSERVATIVE_VELOCITY_LIMITS_RAD_S = jnp.asarray(
    [1.0, 0.75, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 1.25, 1.0, 1.25],
    dtype=jnp.float32,
)

P30_DELAY_TICKS = jnp.asarray(
    [3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 2, 3, 2, 3], dtype=jnp.int32
)
P31_34_DELAY_TICKS = P30_DELAY_TICKS
P30_TAU_S = jnp.asarray(
    [0.015, 0.015, 0.005, 0.010, 0.010, 0.120, 0.120,
     0.120, 0.120, 0.020, 0.035, 0.010, 0.030, 0.005],
    dtype=jnp.float32,
)
P31_34_TAU_S = jnp.asarray(
    [0.015, 0.015, 0.005, 0.005, 0.010, 0.120, 0.120,
     0.120, 0.120, 0.020, 0.035, 0.005, 0.030, 0.005],
    dtype=jnp.float32,
)
P30_GAIN_RATIO = jnp.asarray(
    [0.7469437079656184, 0.8596445465043524, 1.03426574193671,
     0.8490159786673369, 0.9162182282603282, 0.3158492371182989,
     0.7727338223615077, 0.3866450431266670, 0.5261726355532654,
     0.8584811176689752, 0.7534558442567720, 0.9176126028700832,
     0.8875449429540980, 1.0452016907968515],
    dtype=jnp.float32,
)
P31_34_GAIN_RATIO = jnp.asarray(
    [0.7469437079656184, 0.8596445465043524, 1.0290421775834944,
     0.8975311774483291, 0.9021225632101694, 0.3158492371182989,
     0.7727338223615077, 0.3866450431266670, 0.5261726355532654,
     0.8584811176689752, 0.7534558442567720, 0.9176126028700832,
     0.8875449429540980, 1.0452016907968515],
    dtype=jnp.float32,
)

NOMINAL_TORSO_INERTIA = jnp.asarray(
    [0.0034448951258009347, 0.0029271882823563265, 0.001676066591842733],
    dtype=jnp.float32,
)
TORSO_INERTIA_DIAGONAL_BOUNDS = jnp.asarray(
    [
        [0.0026004056132208414, 0.0042893846383810290],
        [0.0021344694541206940, 0.0037199071105919594],
        [0.0010084599326584598, 0.0023436732510270066],
    ],
    dtype=jnp.float32,
)
TORSO_INERTIA_PRODUCT_LIMIT = jnp.float32(0.00025000000000000006)

SENSOR_NOISE_MAXIMUM_SCALES = jnp.asarray(
    [0.03, 0.05, 0.08, 2.5, 0.1, 0.1, 0.1, 0.05], dtype=jnp.float32
)
SENSOR_NOISE_NAMES = (
    "hip_pos_rad",
    "knee_pos_rad",
    "ankle_pos_rad",
    "joint_vel_rad_s",
    "gravity",
    "linvel_m_s",
    "gyro_rad_s",
    "accelerometer",
)

# Exact winner-v2 native representation constants already frozen by the
# representation-selection contract.
SOFT_OFFSETS_RAD = jnp.asarray(
    [0.0844, 0.0721, -0.0890, 0.0371, -0.0767, 0.0245, 0.0,
     -0.0890, -0.0399, 0.0951, -0.0476, 0.0660, 0.0798, 0.1887],
    dtype=jnp.float32,
)
GYRO_LSB_RAD_S = jnp.float32(jnp.pi / (180.0 * 16.0))
ACCEL_LSB_M_S2 = jnp.float32(0.01)
POSITION_LSB_RAD = jnp.float32(2.0 * jnp.pi / 4096.0)
VELOCITY_OBS_LSB = jnp.float32((2.0 * jnp.pi / 4095.0) * 0.05)


def _scaled_interval(nominal, low, high, scale):
    """Scale an interval's deviations from a frozen nominal value."""
    return nominal + scale * (low - nominal), nominal + scale * (high - nominal)


def _uniform(key, low, high, shape=()):
    low = jnp.asarray(low)
    high = jnp.asarray(high)
    return low + jax.random.uniform(key, shape=shape, dtype=low.dtype) * (high - low)


def _valid_inertia(tensor: jax.Array) -> jax.Array:
    values = jnp.linalg.eigvalsh(tensor)
    return jnp.all(values > 0.0) & (values[2] < values[0] + values[1])


def _contract_inertia(diagonal: jax.Array, products: jax.Array):
    """Apply the preregistered nominal-directed validity contraction."""
    contraction_count = jnp.asarray(0, dtype=jnp.int32)
    current_diagonal = diagonal
    current_products = products
    for _ in range(17):
        tensor = jnp.asarray(
            [
                [current_diagonal[0], current_products[0], current_products[1]],
                [current_products[0], current_diagonal[1], current_products[2]],
                [current_products[1], current_products[2], current_diagonal[2]],
            ]
        )
        invalid = ~_valid_inertia(tensor)
        current_diagonal = jnp.where(
            invalid,
            NOMINAL_TORSO_INERTIA + 0.5 * (current_diagonal - NOMINAL_TORSO_INERTIA),
            current_diagonal,
        )
        current_products = jnp.where(invalid, current_products * 0.5, current_products)
        contraction_count = contraction_count + invalid.astype(jnp.int32)
    tensor = jnp.asarray(
        [
            [current_diagonal[0], current_products[0], current_products[1]],
            [current_products[0], current_diagonal[1], current_products[2]],
            [current_products[1], current_products[2], current_diagonal[2]],
        ]
    )
    return tensor, contraction_count


def rotation_matrix_to_quaternion(matrix: jax.Array) -> jax.Array:
    """Convert a proper rotation matrix to scalar-first quaternion."""
    m = matrix
    q_abs = jnp.sqrt(
        jnp.maximum(
            jnp.asarray(
                [
                    1.0 + m[0, 0] + m[1, 1] + m[2, 2],
                    1.0 + m[0, 0] - m[1, 1] - m[2, 2],
                    1.0 - m[0, 0] + m[1, 1] - m[2, 2],
                    1.0 - m[0, 0] - m[1, 1] + m[2, 2],
                ]
            ),
            0.0,
        )
    )
    candidates = jnp.asarray(
        [
            [q_abs[0] * q_abs[0], m[2, 1] - m[1, 2], m[0, 2] - m[2, 0], m[1, 0] - m[0, 1]],
            [m[2, 1] - m[1, 2], q_abs[1] * q_abs[1], m[1, 0] + m[0, 1], m[0, 2] + m[2, 0]],
            [m[0, 2] - m[2, 0], m[1, 0] + m[0, 1], q_abs[2] * q_abs[2], m[2, 1] + m[1, 2]],
            [m[1, 0] - m[0, 1], m[0, 2] + m[2, 0], m[2, 1] + m[1, 2], q_abs[3] * q_abs[3]],
        ]
    )
    candidates = candidates / (2.0 * jnp.maximum(q_abs[:, None], 0.1))
    quaternion = candidates[jnp.argmax(q_abs)]
    quaternion = quaternion / jnp.linalg.norm(quaternion)
    return jnp.where(quaternion[0] < 0.0, -quaternion, quaternion)


def reconstruct_relative_inertia_tensor(
    nominal_iquat: jax.Array, body_iquat: jax.Array, principal_inertia: jax.Array
) -> jax.Array:
    """Read a sampled full tensor back in the nominal inertial frame."""
    nominal_rotation = mjx_math.quat_to_mat(nominal_iquat)
    sampled_rotation = mjx_math.quat_to_mat(body_iquat)
    relative_rotation = nominal_rotation.T @ sampled_rotation
    return relative_rotation @ jnp.diag(principal_inertia) @ relative_rotation.T


def make_winner_v3_configuration_randomizer(
    *, torso_body_id: int, deviation_scale: float
):
    """Build the frozen coupled model randomizer for one curriculum stage."""
    torso_body_id = int(torso_body_id)
    scale = jnp.float32(deviation_scale)
    if torso_body_id != TORSO_BODY_ID:
        raise ValueError(f"winner-v3 torso id must be {TORSO_BODY_ID}, got {torso_body_id}")
    if float(deviation_scale) not in (0.0, 0.25, 0.5, 1.0):
        raise ValueError("winner-v3 deviation scale must be 0/.25/.5/1")

    def randomizer(model: mjx.Model, rng: jax.Array):
        nominal_iquat = model.body_iquat[torso_body_id]
        nominal_body_inertia = model.body_inertia[torso_body_id]
        nominal_body_ipos = model.body_ipos[torso_body_id]

        dof_ids = jnp.asarray(
            [idx for idx, has_loss in enumerate(model.dof_hasfrictionloss) if has_loss]
        )
        dof_addresses = jnp.asarray(
            [address for address in model.jnt_dofadr if address in dof_ids]
        )

        @jax.vmap
        def sample_one(key):
            keys = jax.random.split(key, 11)
            floor_low, floor_high = _scaled_interval(jnp.float32(1.0), 0.5, 1.0, scale)
            floor = _uniform(keys[0], floor_low, floor_high)
            geom_friction = model.geom_friction.at[FLOOR_GEOM_ID, 0].set(floor)

            friction_low, friction_high = _scaled_interval(jnp.float32(1.0), 0.9, 1.1, scale)
            friction_scale = _uniform(
                keys[1], friction_low, friction_high, shape=(model.nu,)
            )
            dof_frictionloss = model.dof_frictionloss.at[dof_addresses].set(
                model.dof_frictionloss[dof_addresses] * friction_scale
            )

            armature_low, armature_high = _scaled_interval(jnp.float32(1.0), 1.0, 1.05, scale)
            armature_scale = _uniform(
                keys[2], armature_low, armature_high, shape=(model.nu,)
            )
            dof_armature = model.dof_armature.at[dof_addresses].set(
                model.dof_armature[dof_addresses] * armature_scale
            )

            link_scale = _uniform(keys[3], 1.0 - 0.1 * scale, 1.0 + 0.1 * scale)
            body_mass = model.body_mass * link_scale
            torso_add = _uniform(keys[4], -0.1 * scale, 0.1 * scale)
            body_mass = body_mass.at[torso_body_id].add(torso_add)

            com_offset = _uniform(
                keys[5], -0.05 * scale, 0.05 * scale, shape=(3,)
            )
            body_ipos = model.body_ipos.at[torso_body_id].set(
                nominal_body_ipos + com_offset
            )

            diagonal_low = NOMINAL_TORSO_INERTIA + scale * (
                TORSO_INERTIA_DIAGONAL_BOUNDS[:, 0] - NOMINAL_TORSO_INERTIA
            )
            diagonal_high = NOMINAL_TORSO_INERTIA + scale * (
                TORSO_INERTIA_DIAGONAL_BOUNDS[:, 1] - NOMINAL_TORSO_INERTIA
            )
            diagonal = _uniform(keys[6], diagonal_low, diagonal_high, shape=(3,))
            products = _uniform(
                keys[7],
                -TORSO_INERTIA_PRODUCT_LIMIT * scale,
                TORSO_INERTIA_PRODUCT_LIMIT * scale,
                shape=(3,),
            )
            tensor, contraction_count = _contract_inertia(diagonal, products)
            principal, eigenvectors = jnp.linalg.eigh(tensor)
            eigenvectors = eigenvectors.at[:, 2].multiply(
                jnp.where(jnp.linalg.det(eigenvectors) < 0.0, -1.0, 1.0)
            )
            delta_quat = rotation_matrix_to_quaternion(eigenvectors)
            sampled_iquat = mjx_math.quat_mul(nominal_iquat, delta_quat)
            sampled_iquat = sampled_iquat / jnp.linalg.norm(sampled_iquat)
            body_inertia = model.body_inertia.at[torso_body_id].set(principal)
            body_iquat = model.body_iquat.at[torso_body_id].set(sampled_iquat)

            # Scale zero is the formal default-off path and must preserve the
            # original representation, not merely an equivalent eigensystem.
            body_inertia = jnp.where(scale == 0.0, model.body_inertia, body_inertia)
            body_iquat = jnp.where(scale == 0.0, model.body_iquat, body_iquat)
            body_ipos = jnp.where(scale == 0.0, model.body_ipos, body_ipos)
            body_mass = jnp.where(scale == 0.0, model.body_mass, body_mass)
            geom_friction = jnp.where(scale == 0.0, model.geom_friction, geom_friction)
            dof_frictionloss = jnp.where(
                scale == 0.0, model.dof_frictionloss, dof_frictionloss
            )
            dof_armature = jnp.where(scale == 0.0, model.dof_armature, dof_armature)
            return (
                geom_friction,
                dof_frictionloss,
                dof_armature,
                body_mass,
                body_ipos,
                body_inertia,
                body_iquat,
                contraction_count,
            )

        (
            geom_friction,
            dof_frictionloss,
            dof_armature,
            body_mass,
            body_ipos,
            body_inertia,
            body_iquat,
            _contraction_count,
        ) = sample_one(rng)
        in_axes = jax.tree_util.tree_map(lambda _: None, model)
        in_axes = in_axes.tree_replace(
            {
                "geom_friction": 0,
                "dof_frictionloss": 0,
                "dof_armature": 0,
                "body_mass": 0,
                "body_ipos": 0,
                "body_inertia": 0,
                "body_iquat": 0,
            }
        )
        return model.tree_replace(
            {
                "geom_friction": geom_friction,
                "dof_frictionloss": dof_frictionloss,
                "dof_armature": dof_armature,
                "body_mass": body_mass,
                "body_ipos": body_ipos,
                "body_inertia": body_inertia,
                "body_iquat": body_iquat,
            }
        ), in_axes

    return randomizer


def sample_episode_contract(rng: jax.Array, deviation_scale: float) -> dict[str, jax.Array]:
    """Sample per-episode actuator and sensor/transport contract values."""
    scale = jnp.float32(deviation_scale)
    keys = jax.random.split(rng, 7)
    gain_low, gain_high = _scaled_interval(
        P30_GAIN_RATIO,
        jnp.minimum(P30_GAIN_RATIO, P31_34_GAIN_RATIO),
        jnp.maximum(P30_GAIN_RATIO, P31_34_GAIN_RATIO),
        scale,
    )
    tau_low, tau_high = _scaled_interval(
        P30_TAU_S,
        jnp.minimum(P30_TAU_S, P31_34_TAU_S),
        jnp.maximum(P30_TAU_S, P31_34_TAU_S),
        scale,
    )
    gain_ratio = _uniform(keys[0], gain_low, gain_high, shape=(len(JOINT_NAMES),))
    tau_s = _uniform(keys[1], tau_low, tau_high, shape=(len(JOINT_NAMES),))
    delay_low = jnp.minimum(P30_DELAY_TICKS, P31_34_DELAY_TICKS)
    delay_high = jnp.maximum(P30_DELAY_TICKS, P31_34_DELAY_TICKS)
    delay_ticks = jax.random.randint(
        keys[2], delay_low.shape, delay_low, delay_high + 1, dtype=jnp.int32
    )
    max_extra_delay = jnp.floor(2.0 * scale + 1.0e-6).astype(jnp.int32)
    additional_action_delay = jax.random.randint(
        keys[3], (), 0, max_extra_delay + 1, dtype=jnp.int32
    )
    imu_delay = jax.random.randint(
        keys[4], (), 0, max_extra_delay + 1, dtype=jnp.int32
    )
    native_probability = jnp.float32(0.5) * scale
    native_quantization = jax.random.bernoulli(keys[5], native_probability)
    return {
        "actuator_gain_ratio": gain_ratio,
        "actuator_tau_s": tau_s,
        "actuator_delay_ticks": delay_ticks,
        "additional_action_delay_ticks": additional_action_delay,
        "imu_delay_ticks": imu_delay,
        "native_quantization": native_quantization,
        "native_quantization_probability": native_probability,
        "sensor_noise_scales": SENSOR_NOISE_MAXIMUM_SCALES * scale,
        "deviation_scale": scale,
    }


def native_quantize_observation(
    observation: jax.Array,
    *, home_rad: jax.Array,
) -> jax.Array:
    """Apply the frozen BNO055/STS3215 native input representation."""
    values = jnp.asarray(observation, dtype=jnp.float32)
    if values.shape[-1] != 115:
        raise ValueError("winner-v3 observation must contain exactly 115 elements")
    origin = jnp.asarray(home_rad, dtype=jnp.float32) + SOFT_OFFSETS_RAD + jnp.pi
    result = values
    result = result.at[0:3].set(jnp.round(values[0:3] / GYRO_LSB_RAD_S) * GYRO_LSB_RAD_S)
    result = result.at[3:6].set(jnp.round(values[3:6] / ACCEL_LSB_M_S2) * ACCEL_LSB_M_S2)
    result = result.at[13:27].set(
        jnp.round((values[13:27] + origin) / POSITION_LSB_RAD)
        * POSITION_LSB_RAD
        - origin
    )
    result = result.at[27:41].set(
        jnp.round(values[27:41] / VELOCITY_OBS_LSB) * VELOCITY_OBS_LSB
    )
    return result


def validate_episode_readback(readback: Mapping[str, jax.Array]) -> None:
    """Fail closed on malformed host-side readback before a formal run."""
    required: dict[str, Sequence[int] | tuple[()]] = {
        "actuator_gain_ratio": (14,),
        "actuator_tau_s": (14,),
        "actuator_delay_ticks": (14,),
        "additional_action_delay_ticks": (),
        "imu_delay_ticks": (),
        "native_quantization": (),
        "native_quantization_probability": (),
        "sensor_noise_scales": (8,),
        "deviation_scale": (),
    }
    for name, shape in required.items():
        if name not in readback or tuple(readback[name].shape) != tuple(shape):
            raise ValueError(f"invalid winner-v3 episode readback: {name}")
