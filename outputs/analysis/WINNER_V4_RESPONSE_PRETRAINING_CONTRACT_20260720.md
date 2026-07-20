# Winner-v4 Response Pretraining Contract — 2026-07-20

status: `PREREGISTERED_CPU_FALSIFICATION_NOT_RUN`

decision: `AUTHORIZE_ONE_ZERO_PPO_CPU_RESPONSE_IDENTIFIABILITY_RUN`

JSON SHA-256: `948e1323a2c0b0a2078602f3151b745d174f6355ab0cd4ff3eb3b65c55be7a7c`

## What this resolves

The runtime-exact 73-value automatic response context remains observable after physical sensor quantization and distinguishes the frozen -0.05 m and +0.05 m torso-X endpoints while the robot is feet-supported and otherwise unconstrained.

The runtime accepted the exact 73-field ABI but held training on two points: signed-X
identifiability and an underspecified calibration support boundary. This contract freezes
both before running any PPO step.

## Frozen support mode

ID: `feet_supported_flat_floor_free_body_passive_fall_catch_v1`

- a rigid, level, stationary surface supports both feet
- both frozen binary foot contacts remain true during the complete accepted home-settle and excitation population
- the floating body is not suspended, clamped, or intentionally loaded at the torso, head, limbs, or external stand
- a passive fall catch may surround the robot but must remain mechanically clear throughout accepted evidence
- loss of either foot contact or contact with the passive catch aborts and discards the calibration

This requires no scale, caliper, entered COM, component inventory, or other manual
per-build measurement. The simulator uses the same flat-floor, free-body boundary:
gravity and physical foot contact are active, and there is no torso support, equality
constraint, or external force.

## Frozen CPU falsification

For torso X = `-0.05 m` and `+0.05 m`, under both measured actuator fits, run the
runtime's exact 2,814-tick one-joint-at-a-time excitation after a 250-tick home
settle. Quantize targets, positions, current, gyro, and acceleration to the physical
interfaces before calling the runtime profile-v4 extractor. Repeat every cell twice.

Pass requires bit-exact repeats and a non-identical signed endpoint context under
each actuator fit. Either signed pair collapsing closes response73 before training.

## Authority

This authorizes one CPU-only, zero-PPO falsification run, locally or on hosted CPU.
It authorizes no policy implementation, training, GPU/iGPU, runtime implementation,
robot/X5 access, serial/GPIO/I2C, torque, motion, Gate 5, deployment, or clearance.
A pass authorizes only a separate policy implementation contract.
