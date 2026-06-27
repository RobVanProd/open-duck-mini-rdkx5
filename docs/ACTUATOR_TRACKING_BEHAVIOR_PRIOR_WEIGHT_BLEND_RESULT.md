# Actuator-Tracking Behavior-Prior Weight Blend Result

Status: `HOLD_WEIGHT_BLEND_DOES_NOT_FIX_TRACKING`

This diagnostic tested whether interpolating ONNX weights between the
behavior-prior PPO run's exported step-0 policy and the step-40960 policy could
recover useful forward motion while reducing the fitted-bridge tracking hold.

The blend artifacts were generated with:

```text
tools/blend_onnx_policy_weights.py
```

The tool blends ONNX initializers by order after checking shape compatibility.
It is an offline analysis tool only. The generated ONNX files are not robot
candidates.

## Inputs

```text
base:   A100 behavior-prior PPO export, step 0
target: A100 behavior-prior PPO export, step 40960
alphas: 0.05, 0.10, 0.20, 0.35, 0.50
```

The compact fitted-bridge CPU sweep evaluated each policy at `x=0.0` and
`x=0.08` for one second.

## Result

No endpoint or blended policy promoted.

```text
best blend: alpha 0.05
x=0.08 mean vx: 0.0253 m/s
x=0.08 track ratio: 0.3158
x=0.08 max pitch tracking p95: 0.2217 rad
x=0.08 max pitch sent velocity p95: 1.8523 rad/s
status: HOLD_CANDIDATE_TRACKING
```

The best blend improved forward progress slightly over the step-0 export, but
it did not materially improve the tracking hold:

```text
step 0 x=0.08 tracking p95:     0.2233 rad
alpha 0.05 x=0.08 tracking p95: 0.2217 rad
alpha 0.20 x=0.08 tracking p95: 0.2206 rad
alpha 0.50 x=0.08 tracking p95: 0.2160 rad
```

Larger blends inherited the step-40960 drift toward lower progress:

```text
step 40960 x=0.08 track ratio: 0.1043
alpha 0.35 x=0.08 track ratio: 0.2101
alpha 0.50 x=0.08 track ratio: 0.1016
```

All target velocities stayed below the measured fitted envelope, and action
saturation was zero. The blocker remained closed-loop tracking quality, not
target-rate or saturation.

## Interpretation

Linear weight interpolation between the prior-preserving step-0 export and the
higher-reward step-40960 export does not solve the deployability gap. Small
alphas preserve or slightly improve motion but leave the tracking hold
unchanged. Larger alphas continue the PPO drift toward low forward progress.

The next deployable-policy attempt should not rely on post-hoc interpolation.
It needs a training mechanism that preserves the working behavior directly while
optimizing tracking, such as a stronger teacher-action continuity loss,
rollout-correction from the working selector, or a gate-aware fine-tuning loop.

## Artifacts

```text
outputs/analysis/actuator_tracking_behavior_prior_weight_blends_manifest.json
outputs/analysis/ACTUATOR_TRACKING_BEHAVIOR_PRIOR_WEIGHT_BLEND_SWEEP.md
outputs/analysis/actuator_tracking_behavior_prior_weight_blend_sweep.json
```

No robot tests, SSH, deployment, runtime behavior changes, or policy-file
changes were performed.
