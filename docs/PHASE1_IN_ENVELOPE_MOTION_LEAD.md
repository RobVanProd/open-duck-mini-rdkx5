# Phase-1 In-Envelope Motion Lead

This note records the current strongest training lead.

## Finding

`movement_bootstrap_v5` did not produce a deployable final policy, but its
phase-1 checkpoint produced meaningful forward motion at `command_x=0.08` while
remaining inside the measured actuator target-velocity envelope.

Preserved candidate:

```text
policy/candidates/movement_bootstrap_v5_phase1_in_envelope_unstable_20260623/candidate.onnx
sha256: dcaa47993f65f4eedf980a78255d723409873b9b65e6a7d3d1002beeea7a3b48
```

Key evidence:

```text
outputs/analysis/PHASE1_X008_FAILURE_TRACE.md
outputs/analysis/phase1_x008_failure_trace.json
outputs/analysis/movement_bootstrap_v5_a100_phase1_command_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
```

## Metrics

At `command_x=0.08` with the fitted actuator bridge:

```text
samples: 80
termination: fall_or_nan at tick 79 / 1.58 s
mean local forward velocity: 0.1892 m/s
pitch-chain p95 target velocity max: 1.9529 rad/s
velocity envelope: 2.25-3.75 rad/s
action saturation: 0%
body pitch abs p95: 1.1841 rad
body pitch abs max: 1.4642 rad
base height min: 0.0434 m
contact events: 13
```

Interpretation:

The failure is not an above-envelope actuator-rate failure and not action
saturation. It is an unstable forward-motion rollout that pitches over within
about 1.6 seconds. That makes this a stabilization/contact-timing problem, not
proof that in-envelope forward motion is impossible.

## Why Later V5 Phases Failed

The phase checkpoint audit showed:

```text
phase 1 x=0.08: below envelope, moving, unstable
phase 2 x=0.08: above envelope, moving, unstable
final x=0.08: below envelope, stable standstill
```

So the phase transition destroyed the useful behavior in two different ways:

- first by drifting back above the actuator envelope,
- then by consolidating into standstill.

## V6 Design Target

`movement_bootstrap_v6` should recover and stabilize the phase-1 behavior.

Design constraints:

- keep the `2.5-3.75 rad/s` fitted envelope active in every phase,
- do not expand the command range after phase 1,
- add stability pressure gradually,
- use lower PPO learning rate / clip during consolidation,
- do not count a stable standstill as success,
- do not request robot validation until `x=0.0` and `x=0.08` sim gates pass.

Open mechanism gap:

A true action-level trust-region or behavior-cloning anchor against the phase-1
policy is not implemented yet. V6 approximates continuity with checkpoint
continuation, small PPO update sizes, and conservative stability rewards. If V6
again loses phase-1 motion, the next offline task should implement a real
teacher-policy/action-anchor mechanism rather than another generic curriculum.

## V6 Result

`movement_bootstrap_v6` completed offline A100 training, but it did not recover
the phase-1 moving gait.

Final candidate gates:

```text
x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION, 78 samples, mean local vx 0.1935 m/s
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, duration complete, mean local vx 0.0009 m/s
```

Phase checkpoint curves also stayed in standstill:

```text
phase 1 x=0.06: mean local vx 0.0004 m/s, max pitch p95 target velocity 0.1254 rad/s
phase 1 x=0.08: mean local vx 0.0009 m/s, max pitch p95 target velocity 0.1077 rad/s
phase 2 x=0.06: mean local vx 0.0005 m/s, max pitch p95 target velocity 0.1741 rad/s
phase 2 x=0.08: mean local vx 0.0010 m/s, max pitch p95 target velocity 0.1390 rad/s
```

Interpretation:

V6 kept the measured actuator envelope active, but the stricter envelope from
phase 1 over-constrained the search and collapsed directly into standstill. The
next useful offline task is to preserve a training checkpoint for the moving
phase-1 behavior and add a real teacher-policy/action-anchor or trust-region
continuity mechanism. Another generic stability/reward recipe is unlikely to
answer the actual continuity problem.

## Trainable Recovery Checkpoint

A one-phase A100 rerun of `movement_bootstrap_v5` recovered a trainable phase-1
checkpoint:

```text
policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/
candidate sha256: 0b7d9c3b24ac047a0a7d5e2e2c15f8e03280a2e30389d4c102dd44a733ce03e5
checkpoint: checkpoint_2026_06_23_205634_368640/
```

This recovered candidate is still not deployable:

```text
x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION
x=0.08: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

But at `x=0.08` with the fitted bridge it again shows in-envelope forward
motion:

```text
samples: 52
mean local vx: 0.2989 m/s
track ratio: 3.7362
max pitch-chain p95 target velocity: 1.7912 rad/s
action saturation: 0%
```

Use this checkpoint as the continuation anchor for the next stabilization
experiment. Do not use it for robot validation.

## V7 Checkpoint-Anchored Result

`movement_bootstrap_v7` used the trainable recovery checkpoint as its initial
restore point. It did not produce a deployable policy, but it did improve the
failure shape:

```text
x=0.0:  duration complete, HOLD_CANDIDATE_TRACKING, max pitch tracking p95 0.0860 rad
x=0.08: fitted bridge fall after 60 samples, mean local vx 0.2640 m/s
```

The `x=0.08` fitted rollout was still inside the measured target-velocity
envelope:

```text
max pitch-chain p95 target velocity: 2.2663 rad/s
action saturation: 0%
```

Preserved candidate:

```text
policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/
```

The next question is no longer whether in-envelope forward motion exists. It is
why the in-envelope gait falls under fitted actuator dynamics, especially around
pitch/body stability and contact timing.

The `x=0.08` fitted-rollout onset analysis is preserved in:

```text
outputs/analysis/V7_X008_ONSET_ANALYSIS.md
```

The forward-speed overshoot begins before the large pitch collapse:

```text
local_vx > 0.08 m/s: tick 3 / 0.06s
body_pitch_abs > 0.25 rad: tick 15 / 0.30s
terminal local_vx: 1.3183 m/s
```

Use v7 as the next continuation anchor only with explicit pressure against
velocity overshoot and pitch/pitch-rate growth under forward command. Do not
spend the next recipe on more actuator-envelope tightening.

## V8 Overshoot-Stabilized Result

`movement_bootstrap_v8` started from the v7 anchored checkpoint and added
forward-overshoot, pitch, and pitch-rate costs under the fitted actuator bridge.
It is preserved here:

```text
policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/
outputs/analysis/MOVEMENT_BOOTSTRAP_V8_A100_SUMMARY.md
```

V8 confirms that the v7 lunge is controllable: the `x=0.08` rollout completed
the full duration without falling, with `0%` action saturation and pitch/base
height inside the candidate limits. It also shows the current stabilizers were
too strong:

```text
x=0.08 fitted mean local vx: 0.0015 m/s
x=0.08 fitted command tracking ratio: 0.0190
max pitch-chain p95 target velocity: 0.2760 rad/s
```

This preserves the lead while sharpening the next problem. The target is no
longer "prove in-envelope motion exists" or "stop the lunge" in isolation. The
next recipe must keep V8's no-lunge behavior while making nonzero command
tracking materially above standstill.
