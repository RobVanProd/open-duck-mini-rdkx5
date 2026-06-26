# PPO BC Swish Command-Scale Decision

status: `HOLD_COMMAND_SCALE_TRACKING_LIMIT`

This diagnostic wrapped the source-VX recovery ONNX with command-x-dependent
action scaling:

```text
scale = low_scale + (high_scale - low_scale) * clip(abs(obs[6]) / 0.08, 0, 1)
action = source_vx_recovery_action * scale
```

It was run offline only. No robot tests, SSH, deployment, runtime behavior
changes, or training were performed.

## Tool

```text
tools/wrap_policy_command_scale.py
```

The wrapper preserves the source policy graph and appends an ONNX-only scale
branch using `obs[6]` (`command_x`).

## Primary Command-Scale Wrapper

```text
policy: outputs/analysis/ppo_bc_swish_seed5_source_vx_recovery_step0_cmdscale_0p75_to_1p0_x008.onnx
low_scale: 0.75
high_scale: 1.00
ramp_command_x: 0.08
```

At `x=0.0`, this exactly matches the stabilizing `scale_0p75` policy:

```text
artifact: outputs/analysis/SOURCE_VX_CMDSCALE_0P75_TO_1P0_X008_X0_GATE.md
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0003 m/s
mean body_pitch_p95: 0.0232 rad
mean max pitch target velocity p95: 0.4107 rad/s
mean max pitch tracking p95: 0.0710 rad
```

At `x=0.08`, this exactly restores the full source-VX recovery behavior:

```text
artifact: outputs/analysis/SOURCE_VX_CMDSCALE_0P75_TO_1P0_X008_X008_GATE.md
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0416 m/s
mean track ratio: 0.5201
mean max pitch target velocity p95: 3.8218 rad/s
mean max pitch tracking p95: 0.2662 rad
status: HOLD_CANDIDATE_TRACKING
```

This is a semantic improvement over the global scale: it combines stable
zero-command behavior with meaningful x=0.08 forward motion. It still fails the
candidate gate because the x=0.08 tracking error remains too high.

## High-Scale Boundary Screen

Additional wrappers kept `low_scale=0.75` and changed only the x=0.08
high-scale. Seeds `0` and `5` were screened:

| high scale | falls | duration complete | mean vx | mean track ratio | mean max tracking p95 | result |
|---:|---:|---:|---:|---:|---:|---|
| 0.90 | 1 / 2 | 1 / 2 | -0.1011 m/s | -1.2634 | 0.2405 rad | seed 5 falls |
| 0.93 | 0 / 2 | 2 / 2 | 0.0313 m/s | 0.3909 | 0.2508 rad | tracking hold |
| 0.935 | 0 / 2 | 2 / 2 | 0.0322 m/s | 0.4022 | 0.2504 rad | tracking hold |
| 0.94 | 0 / 2 | 2 / 2 | 0.0336 m/s | 0.4195 | 0.2498 rad | tracking hold |
| 0.95 | 0 / 2 | 2 / 2 | 0.0329 m/s | 0.4116 | 0.2534 rad | tracking hold |
| 0.975 | 0 / 2 | 2 / 2 | 0.0407 m/s | 0.5092 | 0.2587 rad | tracking hold |

The boundary is narrow and not monotonic enough to treat as solved by scalar
attenuation. Lowering the high-scale reduces tracking slightly, but it either
destabilizes seed 5 or remains at the tracking gate boundary.

## Previous-Target Smoothing Screen

The wrapper was extended to optionally smooth the desired motor target toward
`obs[83:97]`, the previous sent motor target:

```text
target = previous_target + alpha * (desired_target - previous_target)
action = clip((target - home) / action_scale, -1, 1)
```

Artifact: `outputs/analysis/SOURCE_VX_CMDSCALE_TARGET_SMOOTH_X008_SCREEN.md`

Seeds `0` and `5` were screened at `x=0.08`:

| alpha | falls | duration complete | mean vx | mean track ratio | mean max target vel p95 | mean max tracking p95 | result |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.90 | 0 / 2 | 2 / 2 | 0.0388 m/s | 0.4851 | 3.6584 rad/s | 0.2653 rad | tracking hold |
| 0.80 | 0 / 2 | 2 / 2 | 0.0318 m/s | 0.3970 | 3.4291 rad/s | 0.2592 rad | tracking hold |

This simple one-tick target smoothing does not solve the tracking gate. It
reduces target velocity and forward progress, but the fitted bridge still sees
tracking p95 well above the candidate threshold.

## Interpretation

Command-conditioned scaling is useful evidence, but not the final policy. It
proves that:

```text
1. zero-command stabilization and x=0.08 forward motion can coexist in one ONNX
2. the previous global scale failure was a command-conditioning problem
3. the remaining blocker is x=0.08 target/actual tracking, not falls or low progress
```

Do not deploy these policies and do not start PPO from them as final candidates.
The next deployable-policy step should change the shape/timing of the x=0.08
actions, not only their scalar amplitude or a one-tick target blend. A learned
command-conditioned policy or teacher should preserve the x=0 standstill branch
while reducing x=0.08 tracking p95 below the gate without losing forward
progress.
