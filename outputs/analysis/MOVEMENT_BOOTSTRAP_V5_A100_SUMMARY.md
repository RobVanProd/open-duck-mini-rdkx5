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

Final v5 did not find a stable in-envelope forward gait.

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

## Phase Checkpoint Audit

After the final v5 hold, the phase checkpoints were swept at low commands.

Evidence:

```text
outputs/analysis/movement_bootstrap_v5_a100_phase1_command_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
outputs/analysis/movement_bootstrap_v5_a100_phase1_x0_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
outputs/analysis/movement_bootstrap_v5_a100_phase2_command_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
```

Phase 1 is the useful lead:

```text
x=0.0:  duration_complete, pitch p95 target velocity 0.3714 rad/s,
        max tracking p95 0.0830 rad
x=0.04: duration_complete, pitch p95 target velocity 0.2780 rad/s,
        mean local vx 0.0018 m/s
x=0.06: duration_complete, pitch p95 target velocity 0.3107 rad/s,
        mean local vx 0.0028 m/s
x=0.08: fall_or_nan after 80 samples, pitch p95 target velocity 1.9529 rad/s,
        mean local vx 0.1892 m/s
```

Interpretation: phase 1 briefly produced meaningful forward motion at `x=0.08`
while staying below the measured actuator envelope, but it was unstable. That is
not deployable, but it is different from the final standstill. It suggests the
next recipe should preserve and stabilize the phase-1 motion pattern instead of
continuing to optimize the final v5 standstill.

Phase 2 regressed:

```text
x=0.04: duration_complete, mean local vx 0.0026 m/s
x=0.06: duration_complete, mean local vx 0.0030 m/s
x=0.08: fall_or_nan after 61 samples, pitch p95 target velocity 4.1595 rad/s
```

Interpretation: the fitted-bridge phase did not preserve the phase-1 motion. At
`x=0.08`, it both fell and moved back above the measured actuator envelope.

The next offline choice should be deliberate:

```text
preserve/stabilize the phase-1 in-envelope motion, or stop escalating curricula
if later attempts repeat standstill/fall without stable in-envelope progress
```

## Phase-1 Failure Trace

The phase-1 `x=0.08` lead was rerun with opt-in closed-loop trace logging.

Evidence:

```text
outputs/analysis/PHASE1_X008_FAILURE_TRACE.md
outputs/analysis/phase1_x008_failure_trace.json
policy/candidates/movement_bootstrap_v5_phase1_in_envelope_unstable_20260623/
```

Trace summary:

```text
samples: 80
done tick/time: 79 / 1.58 s
mean local vx: 0.1892 m/s
max pitch-chain p95 target velocity: 1.9529 rad/s
body pitch abs p95/max: 1.1841 / 1.4642 rad
base height min: 0.0434 m
contact events: 13
action saturation: 0%
```

The fall is not caused by action saturation or above-envelope target velocity.
It is an unstable in-envelope forward-motion rollout that pitches over quickly.
That makes the next training target a continuity/stabilization problem, not a
generic "try more progress reward" problem.
