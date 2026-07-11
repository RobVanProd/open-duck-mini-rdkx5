# Stage A Direct Joint-Target Tracking Preregistration

Date: 2026-07-11

Status: **PRE-REGISTERED; NOT LAUNCHED**

## Evidence

Across the no-prior and command-progress experiments, 8/12 compact evaluations
passed the training bridge-tracking surrogate while failing the actual-joint
tracking gate. The gate error was 2.04-2.25 times the bridge-surrogate p95, with
an unmodeled gap of 0.0979-0.1190 rad. Source inspection confirms that the
existing `actuator_tracking` reward is the mean pseudo-Huber cost between sent
and bridge-applied targets across all 14 joints, while the compact gate uses
the worst pitch-chain p95 error between sent targets and actual joint position.

The new default-off reward contract directly measures sent-target versus
actual-position error on the six pitch-chain actuator indices
`2,3,4,11,12,13`. Its CPU-only wiring check passed with GPUs hidden, finite
reward and observations, unchanged 101/14 observation/action dimensions, and
matching diagnostic and scaled-cost metrics.

The scale is fixed before training. With pseudo-Huber delta `0.03`, frozen
step-163,840 `x=0` and `x=0.08` traces imply equal-contribution scales of
`-0.007874889679` and `-0.007954892799`; their registered mean is
`-0.007914891239136222`. This makes the new penalty's mean magnitude equal to
the existing `-0.04` bridge-tracking penalty rather than choosing a scale from
outcomes.

## One-Factor Experiment

Replay the authoritative prior-enabled Stage A recipe from the same rate175
step-0 checkpoint. Preserve the behavior prior, restore KL, PPO settings,
reward scales, reset distribution, actuator bridge, noise, domain
randomization, push-disabled setting, and 163,840 requested timesteps. Change
only:

- `joint_target_tracking_scale = -0.007914891239136222`;
- `joint_target_tracking_huber_delta = 0.03`;
- `joint_target_tracking_joint_indices = 2,3,4,11,12,13`.

Do not enable command-progress failure termination in this experiment.

## Gates

Run every emitted checkpoint through the same compact corrected-bridge `x=0`
and `x=0.08` gates. If none passes both, stop and close this exact surrogate.
If multiple pass, select highest `x=0.08` mean velocity, then lower tracking
p95, then earlier step.

Only the selected compact-pass checkpoint may run seeds 40-71. The expanded
pass rule remains: falls <=5/32, passes >=4/32, mean velocity >=-0.0185 m/s, no
pitch-chain velocity violation, and compact `x=0` pass.

Failure closes this exact pitch-chain mean-cost formulation and calibrated
scale without tuning the scale, delta, joint set, aggregation, KL, or training
length. Colab CUDA only for training; CPU-only evaluation is allowed. No local
GPU, robot, deployment, SSH, grounded replay, or moving hardware test.
