# Sim-to-Real Findings Digest

This digest extracts the durable findings from the current evidence branch so
they are readable without walking the full PR history. It is offline-only
documentation. It does not authorize robot tests, deployment, training, SSH, or
runtime behavior changes.

## Current State

The robot-side diagnostic campaign cleared the basic contract checks:

```text
home pose / static balance: mostly cleared
IMU upright and tilt: mostly cleared
joint identity/sign: mostly cleared
suspended x=0.0: mostly cleared
slow actuator sine sweeps: mostly cleared
```

The first serious failure was suspended `x=0.08`: the gait looked coherent in
the air, but the pitch-chain joints lagged the commanded target waveform. The
project has since been offline: actuator modeling, sim reproduction, training
candidate gates, reference audits, and target-source search. Grounded replay
and robot validation remain blocked.

## Finding 1: The Original Policy Is Actuator-Hostile

Evidence:

```text
artifact: outputs/analysis/ACTUATOR_RESPONSE_FIT.md
artifact: outputs/analysis/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
artifact: docs/ACTUATOR_SIM_BRIDGE_SPEC.md
```

Result:

```text
suspended x=0.08 pitch-chain p95 tracking: roughly 0.12-0.21 rad
effective lag: about 3-4 ticks
fitted delay: about 3 ticks
effective velocity limits: about 2.25-3.75 rad/s
```

Interpretation:

```text
BEST_WALK_ONNX_2 produces a target waveform that is too sharp for the measured
actuator chain. Runtime damping or lower slew limits can reduce target
velocity, but they also destroy the learned gait. The long-term fix is to train
or select policies that command trackable motion, not to clip an incompatible
gait after the fact.
```

## Finding 2: The Reference-Motion Key Can Be Wrong for the Command

Evidence:

```text
artifact: outputs/analysis/REFERENCE_MOTION_SEED_AUDIT.md
artifact: outputs/analysis/REFERENCE_GRID_INTERPOLATION.md
artifact: outputs/analysis/REFERENCE_MOTION_OVERRIDE.md
artifact: SIM2REAL_RESULTS_SUMMARY.md
```

Result:

```text
requested command: x=0.04, y=0.0, yaw=0.0
nearest raw reference key: x=0.074, y=-0.037, yaw=-0.074
matched override: x≈0.0426, y≈-0.0021, yaw≈0
```

Interpretation:

```text
V19 did not test useful imitation seeding; it trained against a faster,
side-biased, yaw-biased reference and then gated on slow straight walking.
V20 corrected that mismatch with a synthesized override, but the corrected
reference still did not become a usable closed-loop controller or PPO seed.
```

This is a reusable pipeline finding: off-grid command lookup can silently select
a reference that contradicts the gate.

## Finding 3: Contact/Weight Transfer Is the Current Blocker

Evidence:

```text
artifact: outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20.md
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_DISCRIMINATOR.md
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE.md
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_100.md
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_150.md
```

Raw polynomial reference:

```text
contact mismatch: about 67-69%
actual sim contact: mostly double support
reference contact: expects alternating single support much more often
```

Dynamic-roll / teacher target path:

```text
short fragments can contain in-envelope forward motion
binary contact labels can sometimes be matched
100-150 tick target gate still fails
```

Latest lateral-refine result:

```text
100-tick robust modes: 0
150-tick robust modes: 0

best objective-ranked windows:
  too little forward displacement or too much double support

highest-displacement windows:
  forward dx exists, but vy95 is 0.26-0.31 m/s
```

Interpretation:

```text
The current target families either create forward displacement through lateral
impulse, or preserve lateral/contact gates by suppressing forward displacement.
The missing mechanism is sustained weight transfer: useful single-support
alternation, low lateral momentum, stable pitch/height, and forward progress at
the same time.
```

## Current Stop Rules

Do not run:

```text
- robot validation
- grounded replay
- another x=0.08 robot test
- another prior-scale-only PPO run
- another contact-bit adapter around the same short table
- another nearby random teacher-grid expansion
```

until an offline target source or learner passes the current 100-150 tick
weight-transfer gate.

## Next Useful Offline Work

The next branch should implement a structurally different contact/weight-transfer
objective or controller:

```text
1. explicitly price left/right single-support alternation,
2. penalize unproductive double-support dwell during commanded motion,
3. control lateral velocity and base-y drift,
4. preserve base height and pitch,
5. require local-frame forward displacement,
6. keep sent target velocity inside the measured actuator envelope.
```

See:

```text
docs/WEIGHT_TRANSFER_OBJECTIVE_BRIEF.md
docs/TARGET_SOURCE_EXIT_DECISION.md
```

## Finding 4: The Current Target-Source Branch Is Exhausted

Evidence:

```text
artifact: outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
artifact: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE.md
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_PROBE.md
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_PROBE.md
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_PROBE.md
doc: docs/TARGET_SOURCE_EXIT_DECISION.md
```

Result:

```text
dynamic-roll fragments:
  mostly double support

open-loop single-support primitives:
  still double-support dominated and low displacement

support-readiness gate:
  improves contact discipline but freezes forward motion

stateful support phase:
  phase transitions alone do not create propulsion
```

Interpretation:

```text
The missing piece is no longer just a better scalar gate, prior scale, phase
clock, or pitch-chain stance push. The next branch needs a structurally
different propulsion/contact model: a horizon-based teacher/optimizer,
explicit contact/weight-transfer objective, or closed-loop reference generator
that reacts to body and contact state.
```
