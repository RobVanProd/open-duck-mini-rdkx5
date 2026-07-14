# Ground-Up Measured-Bridge-Only Continuation Preregistration

status: `PREREGISTERED_BEFORE_IMPLEMENTATION_OR_UPDATE`

## Evidence selection

The hard-vector command-support continuation solved command normalization and
target-rate compliance, and every post-update run walked with bilateral contact
transitions. It failed only the unchanged fitted actuator-tracking gate. The
1,003,520-step checkpoint is the protected source because it Pareto-dominates
the 2,007,040-step checkpoint for this next causal question: its tracking p95 is
`.21235-.22243 rad` across x=`.074/.077/.080`, it has zero saturation at all
three commands, and the later checkpoint worsens tracking to `.21897-.23868`
and reaches `1.8519%` saturation at x=`.080`.

The measured-bridge integration audit then proved that the exact train-time JAX
transition and independent NumPy evaluator agree within `1.4305115e-7 rad`
over five 256-tick sequences. It also proved the required ordering:

`hard-bounded sent target -> fitted actuator bridge -> physics`

This selects one bridge-only structural continuation. The old constrained PPO
route is not a valid control: its target-rate, actuator-tracking, behavior-prior,
restore-KL, and related penalties collapsed to double-support standing and are
closed. None of those terms may be added here.

## Protected source

- archive:
  `outputs/analysis/A1_HARD_VECTOR_COMMAND_SUPPORT_artifacts.tar.gz`;
- archive SHA-256:
  `cfc895aca4ddf4ffb0eabf0ca338cd7dd03b19cc7d32125c53ad7ce36bb9ab83`;
- restore checkpoint:
  `A1_HARD_VECTOR_COMMAND_SUPPORT/2026_07_14_155545_1003520`;
- checkpoint directory SHA-256:
  `96cd5e6f15bb45f589be45c8c568098d0a2cafcfc317c1ce8f818247e080fd14`;
- source ONNX SHA-256:
  `f583377fef75e90f93380b9f4bf971f664f484629193a0e58ae6f466c3bad2be`;
- Playground base commit:
  `b9be205ac64488c23504ca42e5ec790337adeec3`;
- hard-vector patch SHA-256:
  `900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875`;
- bridge audit JSON SHA-256:
  `6aa4c24b37932fe287ac7ba57233f99fa308521afe24ac2ceb609d94a534d75d`.

`BEST_WALK_ONNX_2` remains a frozen comparator only. It is not a teacher, warm
start, behavior prior, reward target, or source checkpoint.

## Frozen causal factor

Keep the protected source's architecture, reference table, phase, hard target
vector, uniform x=`[.074,.080)`, signed-progress objective, reward scales,
optimizer, reset, and nominal environment unchanged. Add only the deterministic
plant transition below after the hard sent-target limit and before physics:

- joint order: canonical 14-joint policy order;
- delay ticks: `3,3,3,3,3,3,2,3,3,3,2,3,2,3`;
- tau seconds:
  `.015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005`;
- velocity limits:
  `5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25`;
- first-order coefficient: `1-exp(-dt/max(tau,1e-4))`;
- history and applied target initialize exactly at the home motor target;
- sent target remains in policy/observation history;
- bridged applied target alone drives physics;
- no bridge randomization and no bridge-derived reward or cost.

The delay/tau vectors match the 14-joint combined fixed-target fit. Only the six
pitch-chain velocity entries are claimed as measured fits; all other `5.24`
entries are deliberately neutral.

## Frozen CPU implementation and update contract

Implementation is authorized locally on CPU only. The composed patch must apply
cleanly after the existing ground-up patch stack and pass all of these checks
before hosted training is authorized:

1. CPU is the only visible JAX backend (`CUDA_VISIBLE_DEVICES=''`,
   `JAX_PLATFORMS=cpu`).
2. Reset delay history and applied target equal the home target exactly.
3. Five deterministic bridge sequences match the independent NumPy model within
   `1e-6 rad`; every source-order and provenance check remains true.
4. An environment transition proves sent target is hard bounded, applied target
   equals the bridge output, physics receives applied rather than sent target,
   and returned observation retains sent history plus actual joint state.
5. A 1,024-requested-step smoke restores the protected 1,003,520 checkpoint
   exactly, changes at least one policy leaf, and leaves every parameter and
   scalar metric finite.
6. Step-zero and final ONNX graphs retain exactly `obs, previous_action` inputs
   and `continuous_actions, previous_action_out` outputs, and eight chained
   ticks have per-joint hard-bound excess `<=1e-6`.

Freeze the CPU smoke at seed `100`, 32 environments, two evaluation callbacks,
episode length `100`, unroll `8`, batch size `32`, four minibatches, one update
per batch, LR `3e-4`, discount `0.97`, entropy `0.005`, and imitation `1.0`.
Its reward and short behavior are compatibility diagnostics only.

## Conditionally authorized hosted continuation

Only a fully passing CPU contract authorizes one self-cleaning Colab T4 job:

- source: exact protected 1,003,520 checkpoint above;
- seed `100`, 256 environments, 2,000,000 requested new steps;
- three exports: restored step zero and expected rounded steps `1,003,520` and
  `2,007,040`;
- episode length `600`, unroll `20`, batch size `256`, four minibatches, four
  updates per batch;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`;
- every protected-source setting unchanged except enabling the frozen bridge.

No hyperparameter, reward, vector, source, seed, horizon, or checkpoint search
is authorized. Recover and hash every checkpoint, ONNX, log, and manifest before
stopping the hosted session. Training reward cannot select a policy.

## Frozen nominal decision gate

Evaluate both post-update ONNX checkpoints locally on CPU with deterministic
home reset, phase 0, the same fitted bridge, x=`.074/.077/.080`, seeds `100/101`,
and the unchanged `1.08 s` emergence window. Stateful inference starts at home
action zero and feeds each `previous_action_out` back exactly once.

Both checkpoints must pass all six runs: complete duration, body-frame moving
emergence, bilateral contact transitions, finite nonconstant actions, no
constant saturation, target-rate excess `<=1e-5 rad/s`, saturation fraction
`<=1%`, and pitch-chain tracking p95 `<=.20 rad`. Requiring both checkpoints
prevents transient checkpoint selection. Any failure closes this exact arm
without post-hoc tuning.

A pass authorizes only a separately preregistered x=`0` preservation gate. It
does not authorize robustness training, RDK-X5 software, deployment, robot
validation, torque, or motor access.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, torque, or motor access is
authorized. Colab remains unauthorized until the CPU contract passes.

