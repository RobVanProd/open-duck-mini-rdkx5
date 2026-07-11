# Pre-Fall Trajectory Signature Preregistration

Date: 2026-07-11

Status: **FROZEN BEFORE RESULT COMPUTATION**

This analysis reads the existing seeds 8-71 full-observation baseline traces.
It performs no simulation, intervention, training, robot access, GPU use, or
Colab allocation.

## Question

Which physically interpretable changes during the first 10 control ticks
(0.20 seconds) consistently distinguish later one-second falls from completed
runs across all three independent seed blocks?

## Frozen blocks and outcome

- block A: seeds 8-23
- block B: seeds 24-39
- block C: seeds 40-71
- positive outcome: termination before the one-second horizon
- compute ROC AUC independently in each block; larger feature values always
  mean greater predicted risk

## Frozen features

All features use only ticks 0-9:

1. `base_height_drop_m`: first base height minus minimum base height.
2. `abs_pitch_growth_rad`: maximum absolute body pitch minus initial absolute
   body pitch.
3. `adverse_forward_velocity_m_s`: negative mean local x velocity.
4. `actuator_tracking_error_p95_rad`: 95th percentile across time of the
   per-tick maximum absolute applied-target minus actual-position error.
5. `joint_speed_p95_rad_s`: 95th percentile across time of the maximum absolute
   actuated-joint velocity, using the last 14 generalized velocities.
6. `contact_transition_count`: number of changes in the two-bit foot-contact
   state over the window.

No feature, direction, window, threshold, weighting, or subset will be changed
after results are computed.

## Decision rule

A feature becomes a candidate recovery variable only if its fall-ranking ROC
AUC is at least 0.70 in each of blocks A, B, and C. This is evidence of a
replicated early association, not causality and not an authorized intervention.
If no feature passes, these simple physical signatures do not provide an
outcome-aligned recovery target and this route closes without post-hoc tuning.
