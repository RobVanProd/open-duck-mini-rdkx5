# Ground-Up Hard-Vector Command-Support Continuation Preregistration

status: `PREREGISTERED_BEFORE_ANY_CONTINUATION_UPDATE`

## Evidence selection

Correct deterministic-home evaluation superseded the earlier randomized-reset
classification: A1 reference residual at 4,014,080 steps passes x=`0.074` gait
emergence on seeds 100/101 and reaches `0.06398 m/s` mean body-forward speed.
The unchanged A1 policy also survives exact measured hard-vector projection on
both seeds with `0.05345 m/s`, bilateral transitions, zero saturation, and zero
target-rate excess. It narrowly misses the broader fitted-bridge gate at pitch-
chain tracking p95 `0.20246 rad` versus the frozen `0.20 rad` limit.

The x=`0.08` failure has a digital cause: A1 was trained at one exact command,
so its learned command standard deviation is `1e-6`; the `.006` command shift
normalizes near 6000 and saturates every action. These results select one
structural continuation, not a scalar search: train the already-emergent A1
policy inside the exact hard transition while sampling the closed nominal
command interval x=`[0.074, 0.080)`.

The CPU software contract passed before this preregistration:

- runner patch SHA-256
  `900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875`;
- enhanced reference-residual source SHA-256
  `546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630`;
- 4,096 sampled commands had standard deviation `0.00174425`;
- the environment transition, returned observation, reward history, and all 14
  first-tick rate bounds agreed;
- the stateful ONNX eight-tick chain had zero bound excess and JAX/ONNX first-
  action error `1.49e-8`.

## Protected source

- A1 archive:
  `outputs/analysis/A1_REFERENCE_ANCHORED_RESIDUAL_ground_up_recipe_artifacts.tar.gz`;
- archive SHA-256:
  `7cccf38d1bea2596d0fd44c8e9eeabc3248f0321e39adaa4707a5a9e59788564`;
- restore checkpoint:
  `A1_REFERENCE_ANCHORED_RESIDUAL/2026_07_14_141621_4014080`;
- source policy architecture: reference-anchored residual;
- Playground base commit: `b9be205ac64488c23504ca42e5ec790337adeec3`;
- projected reference table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`.

`BEST_WALK_ONNX_2` remains a frozen comparator only. It is not a teacher, warm
start, reward target, or source checkpoint.

## Frozen CPU update/export smoke

Run exactly one local CPU smoke from the protected A1 checkpoint:

- `CUDA_VISIBLE_DEVICES=''`, `JAX_PLATFORMS=cpu`;
- seed `100`, 32 environments, 1,024 requested steps, two evaluation callbacks
  (restored step zero and final);
- episode length `100`, unroll `8`, batch size `32`, four minibatches, one
  update per batch;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`;
- signed-progress objective, deterministic home reset, phase `0`, flat backlash;
- noise, action/IMU delay, pushes, and domain randomization off;
- uniform x=`[0.074,0.080)`, other command axes zero;
- exact 14-joint hard target-rate vector
  `[5.24,5.24,1.5,1.5,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.0,1.25]`.

The smoke passes only if the restored step-zero parameter tree exactly matches
the protected checkpoint, all training/evaluation values and final parameter
leaves are finite, at least one trainable policy leaf changes after the update,
both step-zero and final ONNX graphs expose exactly `obs, previous_action` to
`continuous_actions, previous_action_out`, and an eight-tick chained inference
has per-joint bound excess `<=1e-6`. This is a compatibility test; its reward or
behavior cannot select a policy.

## Frozen hosted continuation

Only a passing CPU smoke authorizes one T4 continuation job. The hosted job
restores the same A1 checkpoint and changes only the evidence-selected hard
transition and command support. Freeze:

- seed `100`, 256 environments, 2,000,000 requested new steps, three exports
  (restored step zero and the runner's expected rounded steps 1,003,520 and
  2,007,040);
- episode length `1,000`, unroll `20`, batch size `256`, 32 minibatches, four
  updates per batch;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`;
- every environment, reset, phase, objective, table, command range, and hard
  vector item from the CPU smoke unchanged.

Training reward is excluded from selection. No learning-rate, entropy, reward,
phase, vector, command-range, seed, horizon, or checkpoint search is permitted.
Recover and hash every checkpoint, ONNX, log, and manifest before stopping the
session. A vanished hosted filesystem may be retried only with this identical
recipe; it does not authorize a changed arm.

## Frozen nominal decision

Evaluate the 1,003,520 and 2,007,040 continuation checkpoints locally on CPU,
using deterministic home reset, phase 0, the fitted bridge, duration `1.08 s`,
commands x=`0.074/0.077/0.080`, and seeds `100/101`. Stateful inference starts
`previous_action` at home action zero and feeds each applied output back exactly
once per control tick.

A checkpoint passes only if all six runs complete, pass the existing body-frame
moving-emergence rule, retain bilateral contact transitions, contain finite and
nonconstant actions, have no constant saturation, have measured target-rate
excess `<=1e-5 rad/s`, and pass the unchanged fitted-bridge candidate gates,
including pitch-chain tracking p95 `<=0.20 rad`. The route advances only if both
post-update checkpoints pass, establishing persistence rather than selecting a
single transient export. Otherwise it holds without post-hoc tuning.

A pass authorizes only a separately preregistered x=`0` preservation test. It
does not authorize randomization, delays, pushes, terrain, comparison against
`BEST_WALK_ONNX_2`, RDK-X5 work, deployment, robot validation, torque, or motor
access.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, torque, or motor access is
authorized. Colab remains unauthorized until the frozen CPU smoke passes.
