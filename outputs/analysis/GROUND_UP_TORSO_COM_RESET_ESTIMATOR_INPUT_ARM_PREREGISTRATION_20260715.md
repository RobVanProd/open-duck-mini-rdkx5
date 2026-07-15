# Ground-Up Torso-COM Reset-Estimator Input Arm Preregistration

status: `PREREGISTERED_CPU_PACKAGE_CONTRACT_REQUIRED`

## Evidence and causal target

The corrected three-arm torso-COM remediation closed with no winner. Uniform,
anchored, and curriculum exposure to the corrected `trunk_assembly` X-COM axis
all preserved nominal gait but reproduced the signed endpoint failures at
essentially the pre-remediation magnitude. Axis exposure alone is therefore
not a sufficient repair.

The subsequent read-only chain establishes two narrower facts. First, the
deterministic reset accelerometer contains an exact COM-dependent signal in the
actor's existing input space, while the physical mid-gait map is predominantly
weak or nonlinear and the six feedforward actors' signed responses are mixed.
Second, the frozen three-anchor piecewise-linear reset estimator passes its
11-point feasibility curve: all eight held-out signs and ordering pass,
maximum X-COM error is `0.00121397629 m`, and minimum adjacent sensor
separation is `0.279735532 m/s^2`.

This selects one smallest formulation arm: provide the frozen reset estimate
explicitly to the existing feedforward reference-residual actor and latch it
for the episode. It does not select recurrence, a changed objective, a new
optimizer, or a different training recipe.

## Frozen evidence and source

- reset-estimator result SHA-256:
  `1fbae0325295cb5efd03d6140816f69fb73e590b72e34f1848ed93ebb24de951`;
- reset-estimator tool SHA-256:
  `bd38e5a2644655c76a7d0021b2bc10c46fe7475dceb16226f18b6affd98807d9`;
- protected raw `T2_EQUAL` checkpoint member:
  `ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000`;
- protected source archive SHA-256:
  `ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f`;
- verified CPU-remapped step-zero checkpoint:
  `outputs/ground_up_torso_com_cpu_smoke/2026_07_14_180720_0`, directory
  SHA-256
  `b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a`;
- the remap has 27 leaves and zero maximum error from the protected source;
- reference-residual actor source SHA-256:
  `546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630`.

The protected checkpoint's running-stat count is exactly `8,048,640`, its
`std_eps` is exactly zero, its policy observation is 115-D, its privileged
observation is 226-D, and the actor's raw reference action occupies the final
14 policy-observation coordinates.

## Frozen estimator-input definition

The arm name is `RESET_EST_LATCH_U05`. At each deterministic home reset:

1. read the same name-resolved three-axis `accelerometer` on site `imu` from
   the freshly initialized per-environment MJX data;
2. apply the exact frozen estimator from the feasibility study, using only the
   three frozen reset anchors at X-COM `{-0.05,0,+0.05} m`, clipped segment
   projections, Euclidean residual selection, and negative-segment tie rule;
3. compute `z = clip(x_hat / 0.05, -1, +1)`;
4. store `z` in environment info and hold it bit-identically for every step of
   that episode.

No later sensor value may update the latch. No true model COM, privileged body
field, gait-phase estimator, filter, noise model, learned estimator, or label
leakage may enter the policy observation. The critic receives the same latched
`z` only because its existing privileged observation begins with the complete
policy observation; it receives no additional exact COM field.

Insert `z` at policy-observation index 101, immediately before the 14-D raw
reference action. The new policy observation is 116-D and the reference action
remains exactly the final 14 coordinates. Because `privileged_state` begins
with `state`, the same insertion is at privileged index 101 and its size
becomes 227-D. All pre-existing coordinates retain order and value.

## Frozen checkpoint expansion

Construct one expanded step-zero checkpoint from the verified CPU remap:

- insert mean `0`, standard deviation `1`, and summed variance `8,048,640` at
  index 101 in both `state` and `privileged_state` normalizer arrays;
- preserve the shared count `{hi: 0, lo: 8048640}` and `std_eps=0` exactly;
- insert one all-zero row at actor kernel
  `params/residual_trunk/hidden_0/kernel` index 101, changing `(115,512)` to
  `(116,512)`;
- insert one all-zero row at critic kernel `params/hidden_0/kernel` index 101,
  changing `(226,512)` to `(227,512)`;
- preserve every other normalizer, actor, and critic value bit-for-bit.

The new normalizer coordinate is therefore an internally consistent identity
coordinate at the protected count. The zero kernel rows require step-zero
actor distribution outputs and critic values to equal the protected source for
the same original observation, for `z` at `-1`, `0`, and `+1`, within maximum
absolute error `1e-7`. This is checkpoint surgery, not training and not a new
random initialization.

## Frozen eventual training recipe

This document does **not** authorize training. If a later artifact explicitly
authorizes hosted training, it may authorize only this single arm with:

- seed 100 and the expanded protected T2 checkpoint;
- uniform targeted `trunk_assembly` X-COM offset `[-.05,+.05]` throughout;
- 2,000,000 requested continuation steps and exports at actual steps 0,
  1,003,520, and 2,007,040;
- reference-residual actor, privileged critic, reference phase 0,
  deterministic home reset, command support x=`[.074,.080)`, fitted measured
  bridge, applied-target observation, signed progress, tail scale
  `-6572.254964031055`, LR `.0003`, discount `.97`, entropy `.005`, 256
  environments, episode length 600, unroll 20, batch 256, four minibatches,
  and four updates;
- noise, unrelated dynamics axes, pushes, and terrain disabled;
- conservative `1.50 rad/s` left-ankle training limit and every other velocity
  limit unchanged.

The only formulation change from the failed `U05_DIRECT` control is the
frozen latched estimator coordinate and the exact zero-row checkpoint
expansion required to receive it. No reward, seed, LR, schedule, command,
reset, bridge, horizon, architecture width/depth, or randomizer change is
allowed after outcomes. Training reward is never used for selection.

## Frozen eventual behavior evaluation

This document does **not** authorize behavior evaluation. If training and
evaluation are later authorized, both full-range checkpoints must pass every
cell of the same frozen evaluation used to close the preceding remediation:

- complete R1 at x=0/.074/.077/.080 under P30 and P31/34 fits;
- corrected `TORSO_COM_X_NEG` and symmetric `TORSO_COM_X_POS` matrices;
- 600 ticks, deterministic home reset, exact per-run model readback, bilateral
  gait, zero saturation, zero measured rate excess, tracking p95 `<=.20 rad`,
  and all prior x=0 and nominal thresholds.

The evaluated graph must contain the same actual-position guard, x=0 deadband,
and conservative left-ankle envelope transforms. The arm advances only if both
checkpoints pass every cell. Otherwise close it without midpoint, retry,
closest-checkpoint promotion, or reward-based selection. A pass would authorize
only a separate next preregistration; it would not clear R2 condition 8+, R3,
runtime, RDK-X5, or robot use.

## Required CPU package contract

Before any continuation or hosted session, a committed CPU-only contract must:

1. verify every frozen evidence, archive, checkpoint, patch, helper, and feature
   table hash;
2. prove estimator source identity, body/sensor name resolution, three anchor
   constants, clipping, residual selection, tie rule, scale, latch-at-reset,
   and no post-reset latch writes;
3. prove exact 115->116 and 226->227 coordinate maps, with the raw reference
   action still occupying the last 14 actor inputs;
4. expand and save/restore the checkpoint, verify all new running statistics
   and zero rows exactly, and prove all other values unchanged;
5. prove protected actor and critic step-zero equality at `z={-1,0,+1}`;
6. run reset-only CPU checks at X-COM `{-0.05,0,+0.05}` proving the latch equals
   the frozen estimator, stays finite and in `[-1,+1]`, and changes only with
   reset COM;
7. prove the feature is default-off and the prior 115/226-D environment and
   checkpoint path remain unchanged when disabled;
8. prove CPU-only execution with zero training steps, zero dynamic behavior
   cells, and no accelerator, Colab, RDK-X5, or robot access.

Any failure closes the package attempt until a new preregistration; tolerances,
indices, initialization values, estimator constants, or latch timing may not
be changed post hoc.

## Authority boundary

This document authorizes only implementation of the default-off estimator-input
feature, deterministic checkpoint-expansion tool, and the CPU package contract
above. It authorizes no PPO step or other training, no Colab session, no local
GPU/iGPU, no formal behavior matrix, no retry/tuning, no R2/R3 continuation,
no runtime design, no RDK-X5 or robot access, no deployment, torque, or motors.
A passing package contract may support a separate hosted-training authorization;
it does not itself authorize one.
