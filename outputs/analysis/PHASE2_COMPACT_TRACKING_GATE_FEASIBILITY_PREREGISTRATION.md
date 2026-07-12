# Compact Tracking Gate Feasibility Preregistration

Date: 2026-07-11

Status: **COMPLETED; MIXED RESULT; GATE IS RESET-SENSITIVE**

## Question

Can the strongest known stable, rate-bounded teacher satisfy the frozen
one-second `x=0.08` compact gate across the original eight reset seeds?

The teacher completes 15 seconds on seeds 0-7 with mean velocity 0.0340 m/s,
mean ratio 0.4254, and no falls. Its 15-second tracking p95 is below 0.20 rad on
all seeds, but seed 0 fails the one-second gate at 0.2478 rad. A fixed-window
trace audit shows the startup window is worst, while two later windows are also
marginally above 0.20. This does not yet prove either gate infeasibility or a
startup-only artifact.

## Frozen Audit

Run the existing rate-bounded teacher without modification:

- policy: `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate.onnx`;
- command: `x=0.08`;
- task: `flat_terrain_backlash`;
- fitted actuator bridge;
- pitch-chain policy-action rate limit: `2.0 rad/s` on indices
  `2,3,4,11,12,13`;
- duration: `1.0 s`;
- seeds: `0-7`;
- no push, reward override, reset settle, policy change, training, or gate
  change.

Use the unchanged candidate gate, including tracking p95 <=0.20 rad, progress
ratio >=0.25, mean velocity >=0.02 m/s, duration completion, posture, velocity,
and saturation constraints.

## Decision Rule

- `8/8` pass: the compact gate is feasible for the frozen controller on this
  block; retain it and treat learned-policy failures as a training problem.
- `0/8` pass: the compact gate is not demonstrated feasible by the strongest
  stable controller; suspend further policy training and audit the gate/reset
  contract independently before changing thresholds.
- Mixed result: classify the gate as reset-sensitive. Do not change it and do
  not resume training. Pre-register an independent seed block to measure the
  reset sensitivity before any acceptance-contract decision.

CPU-only execution with JAX and both GPU visibility variables forced off. No
robot, deployment, SSH, grounded replay, or moving hardware test.
