# Right-Knee Bridge Reset-Alignment Causal Preregistration

Date: 2026-07-11

Status: **PRE-REGISTERED; IMPLEMENTATION NOT YET RUN**

## Evidence basis

Across three independent seed blocks, first-0.20-second right-knee tracking
error predicts later falls. Target demand, limiter clipping, and rate saturation
do not explain it. Absolute error at tick 0 replicates (AUC
0.709/0.893/0.753), while later error growth does not. The bridge currently
initializes its right-knee applied target at the fixed nominal 1.379 rad despite
the randomized reset knee position.

## Single intervention

At bridge construction only, replace right-knee actuator index 12 in the bridge
initial applied-target vector with the measured reset right-knee position. Keep
every other target, state variable, policy input, action, limiter, gain, bridge
parameter, reset distribution, and gate unchanged. This must be a default-off,
eval-only option.

## Frozen screen

- seeds: 40-71, compared with the already saved exact-seed baseline
- original rate175 step-163,840 policy
- x=0.08, one-second horizon, canonical playground reset
- corrected fitted bridge and existing 2.0 rad/s pitch-chain policy limiter
- CPU only, full traces
- no training, robot, GPU, Colab, deployment, gain, or rate change

## Pass rule

All conditions are required:

1. falls decrease from 11/32 baseline to at most 5/32;
2. none of the 21 baseline duration-complete seeds becomes a fall;
3. candidate passes do not decrease from 4/32;
4. mean velocity does not regress by more than 0.01 m/s from baseline -0.0285;
5. first-10-tick right-knee p95 tracking error decreases on at least 9 of the
   11 baseline fall seeds.

Failure closes this exact initialization route without tuning another joint,
blend duration, target offset, or scale. Passing authorizes only a subsequent
reviewed validation step, not robot deployment.
