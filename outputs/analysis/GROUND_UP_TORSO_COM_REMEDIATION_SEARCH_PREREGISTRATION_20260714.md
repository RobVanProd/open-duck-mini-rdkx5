# Ground-Up Torso-COM Remediation Search Preregistration

status: `PREREGISTERED_CPU_PACKAGE_CONTRACT_REQUIRED`

## Evidence and causal target

The corrected R2 evaluator proves that the current nominal winner fails the
`trunk_assembly` X COM endpoint at `-0.05 m` in every checkpoint/actuator-fit
matrix. X=0 falls after 47 ticks and moving commands fall after 41–42 ticks.
The same audit found the training randomizer's `TORSO_BODY_ID = 1` targeted the
massless outer `base`, while the compiled inertial torso is body 2 at
`0.698526 kg`. The policy therefore has no training exposure to the uncertainty
that stopped R2.

The corrected targeted-randomizer contract passes. It name-resolves and checks
`trunk_assembly`, changes only `body_ipos[2,0]`, preserves the nominal
reset/command/noise/push controls, and proves both uniform and exact-anchor
sampling on CPU.

## Protected source and unchanged recipe

- Restore the raw `T2_EQUAL` final checkpoint member
  `ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000`
  from archive SHA-256
  `ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f`.
- Preserve seed 100, reference-residual actor, privileged critic, reference
  phase 0, deterministic home reset, command support x=[.074,.080), fitted
  measured bridge, applied-target observation, signed progress, tail scale
  `-6572.254964031055`, LR `.0003`, discount `.97`, entropy `.005`, 256
  environments, episode length 600, unroll 20, batch 256, four minibatches,
  and four updates.
- Keep noise, unrelated dynamics axes, pushes, and terrain disabled.
- Use the conservative `1.50 rad/s` left-ankle training limit required by the
  independently measured P31/34 fit. Every other velocity limit is unchanged.
- The only arm variable is the targeted X-COM sampling schedule/distribution.

## Frozen three-arm search

| arm | schedule | total requested continuation |
|---|---|---:|
| `U05_DIRECT` | uniform X offset `[-.05,+.05]` throughout | 2,000,000 steps |
| `A05_DIRECT` | equal categorical anchors `[-.05,0,+.05]` throughout | 2,000,000 steps |
| `U_CURRICULUM` | uniform `±.01` for .5M, `±.03` for .5M, then `±.05` for 1M | 2,000,000 steps |

All arms begin from the same protected source. No retry, midpoint, LR, reward,
seed, architecture, bridge, command, reset, or horizon tuning is allowed after
outcomes. The maximum hosted budget is 8 Colab compute units; setup failures
count. Jobs run sequentially and all artifacts/checkpoints must be recovered
and hashed before the session is stopped.

## Required package and CPU smoke before Colab

1. Verify every source archive, patch, helper, and feature-table hash.
2. Compose the exact checkout and require the torso randomizer contract to pass.
3. Restore the source checkpoint on CPU with exact step-zero parameters.
4. Run a 1,024-step `U05_DIRECT` continuation and require finite parameters and
   metrics, nonzero sampled COM spread, actor updates, and valid stateful ONNX.
5. Prove default-off continuation remains exact and no local accelerator is
   visible.

Only a passing, committed package/smoke contract authorizes the hosted search.

## Frozen evaluation and selection

Apply the same actual-position guard, x=0 deadband, and conservative
left-ankle envelope transforms to every evaluated export. Each arm must have
two temporally distinct checkpoints after exposure to the full `±.05 m` range.
Both checkpoints must pass:

- the complete R1 matrix at x=0/.074/.077/.080 under both P30 and P31/34 fits;
- the corrected `TORSO_COM_X_NEG` matrix;
- the symmetric `TORSO_COM_X_POS` matrix;
- 600 ticks, deterministic home reset, exact model readback, bilateral gait,
  zero saturation/rate excess, tracking p95 `<=.20 rad`, and all prior x=0 and
  nominal thresholds.

An arm advances only if both full-range checkpoints pass every cell. If more
than one advances, rank by: (1) lower worst endpoint tracking p95, (2) higher
minimum endpoint mean vx, (3) lower worst nominal tracking p95, then (4)
`U_CURRICULUM`, `A05_DIRECT`, `U05_DIRECT` as the preregistered simplicity and
endpoint-coverage tiebreak. Training reward is never used. If none pass, close
this exact targeted-COM formulation without promoting the closest arm.

## Boundary

This document authorizes only construction and CPU validation of the package.
It does not yet authorize Colab, local GPU/iGPU, condition 8+, R3+, RDK-X5,
robot access, deployment, torque, or motors.
