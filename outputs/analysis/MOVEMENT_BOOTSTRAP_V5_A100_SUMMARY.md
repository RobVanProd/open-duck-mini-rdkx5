# Movement Bootstrap V5 A100 Summary

status: `HOLD_NON_DEPLOYABLE`

This was an offline A100 training run. It did not SSH, deploy, touch the robot,
or change runtime behavior.

## Candidate

- recipe: `movement_bootstrap_v5`
- purpose: test whether an in-envelope forward gait exists
- final ONNX sha256: `622661f17a59b82dc9e920f694a9c849336f9bb7d580e52c5e04beeef62b9750`
- final ONNX source: `outputs/analysis/colab_cli/open-duck-a100-v5-staged-curriculum-20260623T181611Z/.../2026_06_23_184259_460800.onnx`

Training completed all three phases:

```text
phase 1: x=0.04-0.06, mild bridge
phase 2: x=0.04-0.06, fitted bridge, 2.5-3.75 rad/s
phase 3: x=0.04-0.08, fitted bridge, 2.5-3.75 rad/s
```

Phase 3 did not relax the actuator envelope back to the optimistic
`5.24 rad/s` limit.

## Candidate Gates

### x=0.0

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

Key metrics:

```text
samples before termination: 57-77 depending on bridge mode
max pitch tracking p95: 0.2333 rad
max sent target velocity p95: 5.2400 rad/s
body pitch p95: 1.2998 rad
min base height: 0.0198 m
action saturation: 0.0%
```

Interpretation: the candidate is not stable at zero command.

### x=0.08

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

Key metrics:

```text
samples: 750
termination: duration_complete
mean local vx, fitted mode: 0.0012 m/s
tracking ratio, fitted mode: 0.0146
max pitch tracking p95: 0.0745 rad
max sent target velocity p95: 0.5203 rad/s
body pitch p95: 0.1306 rad
min base height: 0.1536 m
action saturation: 0.0%
```

Interpretation: the policy is actuator-safe at `x=0.08`, but it essentially
stands still.

## Command Feasibility Curve

Evidence:

```text
outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/command_feasibility_curve.json
```

| command_x | status | termination | max pitch p95 target velocity | envelope | mean local vx |
|---:|---|---|---:|---|---:|
| 0.00 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `fall_or_nan` | 5.1573 | above | 0.2529 |
| 0.02 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `fall_or_nan` | 4.0802 | above | 0.1463 |
| 0.04 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `duration_complete` | 1.0697 | below | 0.0017 |
| 0.06 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `duration_complete` | 1.2235 | below | 0.0023 |
| 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `duration_complete` | 1.4159 | below | 0.0031 |
| 0.10 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `duration_complete` | 0.8798 | below | 0.0052 |
| 0.12 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `duration_complete` | 1.0454 | below | 0.0070 |

## Decision

V5 did not find an in-envelope forward gait.

It avoids the original `BEST_WALK_ONNX_2` target-rate failure at nonzero
commands, but the learned behavior is near-standstill. At `x=0.0` and `x=0.02`,
the candidate becomes aggressive enough to exceed the measured envelope and
falls.

This is not deployable and must not be tested on the robot.

Under `docs/CANDIDATE_FEASIBILITY_STOP_RULE.md`, this is:

```text
feasibility-targeted recipe attempts: 1 / 3
breakthrough: no
```

The next offline choice should be deliberate:

```text
either one more feasibility-targeted recipe with a clearly different mechanism
or stop escalating curricula if the next attempts repeat this shape
```
