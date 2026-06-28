# Phase 2 Action-Space Correction / Command Conditioning Decision

status: `PARTIAL_PASS_ACTION_SPACE_CORRECTION_HOLD_COMMAND_CONDITIONED_SWING`

## Scope

Offline-only follow-up to the transition-protected relabel branch.

No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or
training from scratch were performed.

## Starting Point

The transition-protected BC student broke the rough-terrain tracking/envelope
plateau, but seed 4 lacked swing. The seed-4 weighted student restored swing,
but reintroduced tracking/envelope excess.

Full seed-4 traces showed the seed-weighted tracking hold was dominated by
pitch-chain components, especially right knee / right ankle and then left knee.
This branch tested explicit per-joint action-space corrections instead of
global smoothing or scalar reward PPO.

## Action-Space Corrections

Three sequential label corrections were tested on the seed-weighted traces:

```text
1. cap right_knee at 2.25 rad/s
2. cap right_ankle at 2.00 rad/s
3. cap left_knee at 2.25 rad/s
```

The final corrected manifest kept the seed-weighted source motion while making
trace-level labels envelope-safe:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_MANIFEST.md
seed 2 vx: 0.0409 m/s, sent_vel95 1.9524 rad/s, tracking p95 0.1662 rad
seed 4 vx: 0.0335 m/s, sent_vel95 1.9720 rad/s, tracking p95 0.1682 rad
```

## x=0.08 Rough Gate

The plain feed-forward student trained from the three-joint corrected x=0.08
manifest passed the rough-terrain diagnostic gate:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md

seed 2: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.4784
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1989 rad
  min swing segments: 6
  min rel-x range p95: 0.0140 m

seed 4: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.4738
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1913 rad
  min swing segments: 6
  min rel-x range p95: 0.0106 m
```

This is the first local rough-terrain `z=0.002` diagnostic pass on both seeds
with forward motion, zero corrected-envelope excess, tracking p95 under
`0.20 rad`, and swing/advance present.

## Command Semantics Hold

The same plain feed-forward student did not preserve x=0 command semantics:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_BC_STUDENT_X0_TERRAIN_Z002_GATE_CPU.md
seed 2/4 mean vx: 0.0442 / 0.0369 m/s
```

It still walked forward on a zero command, so it is not promotable.

Adding zero-command samples to a plain feed-forward BC student collapsed the
x=0.08 gait, even without extra x0 weighting:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_COMMAND_UNWEIGHTED_BC_STUDENT_X008_TERRAIN_Z002_GATE_CPU.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 2/4 track ratio: 0.0587 / 0.0699
```

With x0 weight `4.0`, the collapse was stronger:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_COMMAND_BC_STUDENT_X008_TERRAIN_Z002_GATE_CPU.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 2/4 track ratio: 0.0399 / 0.0366
```

## Phase/Command-Modulated Student

A phase/command-modulated BC student was then trained on the unweighted command
manifest. This preserved command semantics:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_PHASECMD_BC_STUDENT_X0_TERRAIN_Z002_GATE_CPU.md
seed 2/4 mean vx: -0.0008 / 0.0032 m/s
seed 2/4 max velocity excess: 0.0000 / 0.0000 rad/s
seed 2/4 max tracking p95: 0.0472 / 0.0419 rad
```

On x=0.08 rough terrain, it preserved tracking/envelope and passed seed 2, but
seed 4 still missed the hard swing/advance gate:

```text
artifact: outputs/analysis/PHASE2_SEED4_WEIGHTED_KNEE_ANKLE_LEFTKNEE_LIMIT_PHASECMD_BC_STUDENT_X008_TERRAIN_Z002_GATE_CPU.md
seed 2: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.4622
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1830 rad
  min swing segments: 4
  min rel-x range p95: 0.0047 m

seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  track ratio: 0.3900
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1902 rad
  min swing segments: 1
  min rel-x range p95: 0.0003 m
```

## Interpretation

The per-joint action-space correction works for forward rough terrain. The
remaining blocker is no longer terrain tracking/envelope; it is combining:

```text
x=0.08 rough-terrain swing/advance
x=0.0 command preservation
corrected-bridge tracking/envelope
```

Plain feed-forward BC averages the command modes into either walking at zero
command or standing at x=0.08. Phase/command modulation preserves zero-command
semantics but still needs seed-4 swing recovery.

## Decision

Proceed with a command-conditioned architecture branch, not more scalar
weighting or global smoothing:

```text
base source: three-joint action-space corrected labels
architecture: command/phase-conditioned or phase/contact-conditioned
next target: recover seed-4 swing/advance while preserving x=0.0 mean |vx| <= 0.005
gate: rough_terrain_backlash z=0.002 seeds 2,4 at x=0.08 and x=0.0
```

Robot validation remains blocked.
