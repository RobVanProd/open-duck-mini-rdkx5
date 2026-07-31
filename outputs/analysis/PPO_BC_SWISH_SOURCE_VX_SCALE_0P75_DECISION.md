# PPO BC Swish Source-VX Scale 0.75 Decision

status: `HOLD_X008_FORWARD_PROGRESS_REGRESSION`

This diagnostic scaled the deployable-shape source-VX recovery policy outputs
before closed-loop replay. It was run offline only. No robot tests, SSH,
deployment, runtime behavior changes, or training were performed.

## Inputs

- base policy: `outputs/analysis/ppo_bc_swish_seed5_source_vx_recovery_step0.onnx`
- scaled policy: `outputs/analysis/ppo_bc_swish_seed5_source_vx_recovery_step0_scale_0p75.onnx`
- task: `flat_terrain_backlash`
- bridge: `fitted`
- duration: `10 s`

## Hard-Seed Screen

Artifact: `outputs/analysis/SOURCE_VX_SCALE_X0_HARD_SEED_SCREEN.md`

At `command_x=0.0`, seeds `3` and `5` were screened for action scales
`0.25`, `0.50`, and `0.75`:

| scale | falls | duration complete | mean vx |
|---:|---:|---:|---:|
| 0.25 | 1 / 2 | 1 / 2 | -0.1598 m/s |
| 0.50 | 1 / 2 | 1 / 2 | -0.1535 m/s |
| 0.75 | 0 / 2 | 2 / 2 | -0.0002 m/s |

Only `scale_0p75` cleared both hard standstill seeds.

## Full x=0.0 Gate

Artifact: `outputs/analysis/SOURCE_VX_SCALE_0P75_X0_FULL_GATE.md`

```text
command_x: 0.0
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0003 m/s
mean body_pitch_p95: 0.0232 rad
mean base_height_min: 0.1527 m
mean max pitch target velocity p95: 0.4107 rad/s
mean max pitch tracking p95: 0.0710 rad
```

This fixes the hard-seed x=0.0 standstill failure seen in the first
command-conditioned BC attempt.

## Full x=0.08 Gate

Artifact: `outputs/analysis/SOURCE_VX_SCALE_0P75_X008_FULL_GATE.md`

```text
command_x: 0.08
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0004 m/s
mean track ratio: 0.0046
mean body_pitch_p95: 0.0230 rad
mean base_height_min: 0.1527 m
mean max pitch target velocity p95: 0.4296 rad/s
mean max pitch tracking p95: 0.0715 rad
```

The same policy is stable at x=0.08 but does not walk. Every seed holds with
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.

## Interpretation

The 0.75 action scale is useful as a standstill-stabilizing diagnostic, but it
is not a walking candidate. It shows that hard-seed zero-command stability can
be recovered by retaining enough of the source-VX feedback policy, but a global
scale factor collapses command sensitivity and removes the x=0.08 gait.

Do not deploy this policy. Do not start PPO from this as a final candidate.
The next deployable-policy step should preserve the full source-VX x=0.08
walking behavior while adding a command-conditioned zero-command branch or
teacher, rather than using one global action scale for all commands.
