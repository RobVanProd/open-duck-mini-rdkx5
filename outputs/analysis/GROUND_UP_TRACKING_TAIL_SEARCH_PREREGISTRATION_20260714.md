# Ground-Up Tracking-Tail Search Preregistration

status: `PREREGISTERED_CPU_SMOKE_FIRST`

## Causal question

Can a gate-aligned upper-tail cost remove the remaining full-horizon
pitch-chain tracking violation without sacrificing the ground-up policy's gait,
forward motion, or zero measured rate excess?

This is not a generic tracking-penalty retry. The earlier closed branch used a
mean pseudo-Huber tracking cost. Here the diagnostic is exactly zero at or
below .20 rad and penalizes only squared excess above the unchanged gate on
indices `2,3,4,11,12,13`:

`mean(square(max(abs(sent_target - actual_position) - 0.20, 0)))`

The CPU contract passes on 3,600 frozen trace rows with JAX/NumPy error below
`1e-10`, exact zero/monotonic synthetic checks, zero default scale, zero
transition/observation difference, and an exact scaled-reward delta.

## Protected source and control

- source: applied-target 1M checkpoint `1,003,520`;
- source ONNX SHA-256:
  `bae176ffd2d7af4cfb85169c817a9b43bcbe4ac1e5d721dd16959e71aaaf51be`;
- existing matched no-tail continuation: applied-target 2M checkpoint
  `2,007,040`;
- patch SHA-256:
  `9f716243e0c4ef487ef4227ef0cb9f389ed43c0456435987ac0846e1b629811e`.

The existing 2M result is the control. The new patch has scale zero by default
and the CPU transition contract proves it does not change state, observation,
or reward when disabled, so another control job would duplicate spent compute.

## Frozen scale screen

On the source checkpoint's three 600-tick traces:

- mean raw tail cost: `0.000012092883729440577`;
- mean already-scaled action-rate cost: `0.07947751512026621`;
- equal-contribution magnitude: `6572.254964031055`.

The screen is fixed before outcomes at one quarter, one, and four times that
measured anchor:

| arm | scale |
|---|---:|
| `T1_QUARTER` | `-1643.0637410077638` |
| `T2_EQUAL` | `-6572.254964031055` |
| `T3_FOUR` | `-26289.01985612422` |

No midpoint, threshold, joint-set, loss-shape, seed, LR, entropy, imitation,
horizon, bridge, observation, architecture, or checkpoint tuning is allowed.

## Shared training recipe

Every arm restores the same protected 1M checkpoint and changes only the tail
scale. Preserve PPO seed 100, 256 environments, episode length 600, unroll 20,
batch 256, four minibatches, four updates, LR .0003, discount .97, entropy
.005, reference-residual actor, imitation 1.0, signed progress, command support
x=[.074,.080), measured hard vector, fitted delay/tau bridge, applied-target
observation, reference phase 0, and privileged critic.

Each arm requests exactly 1,000,000 additional steps with three evaluations,
producing source/half/final checkpoints. Jobs run sequentially on Colab only.
The combined hosted ceiling is 6 compute units, counted even for failed setup.

## Required CPU gate before hosted compute

1. Remap the protected source checkpoint to CPU with exact save/restore.
2. Run a 1,024-step continuation using `T2_EQUAL`.
3. Require exact source-to-step-zero parameters, finite metrics and parameters,
   a nonzero finite tail metric, all actor leaves updated, and valid stateful
   hard-bounded ONNX at step zero and step 1,024.
4. Any failure blocks all hosted arms.

## Frozen 600-tick behavior gate

Every half and final checkpoint is evaluated at x=.074/.077/.080, seeds
100/101, deterministic home reset, fitted bridge, and 600 ticks. A checkpoint
passes only if every cell passes the unchanged candidate gate, walks for the
complete duration, retains bilateral support, has zero saturation/rate excess,
and worst pitch-chain tracking p95 is <=.20 rad.

An arm advances only if both its half and final checkpoints pass every cell.
This is temporal and checkpoint persistence; a single passing checkpoint or a
54-tick startup pass cannot advance.

If multiple arms pass, choose lower worst tracking p95, then higher minimum
forward velocity, then the smaller absolute tail scale. Training reward is
never used. If no arm passes, close this exact tail-exceedance formulation.

## Boundary

This preregistration authorizes the CPU smoke only now. Hosted jobs become
authorized only if that smoke passes and is repository-logged. It never
authorizes local GPU/iGPU, RDK-X5, robot, deployment, torque, or motor access.
