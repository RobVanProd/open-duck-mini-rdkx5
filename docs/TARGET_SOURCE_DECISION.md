# Target Source Decision

This note records the current offline target-source decision. It is not a robot
test plan and not training permission.

Generated audit artifact:

```text
outputs/analysis/TARGET_SOURCE_AUDIT.md
```

## Status

The project needs low-command target data before another supervised or PPO
training attempt:

```text
command_x: 0.04
window: 50 samples preferred
required seeds: seed_000 and seed_002
required outcome: forward motion with lateral, posture, contact, actuator, and
tracking metrics inside gates
```

The current target-source candidates are all holds.

## Joint-Sinusoid Primitive

The original low-dimensional sine primitive family can produce many seed0
windows but does not generalize to seed2.

Current best path:

```text
seed0: pass
seed2: forward and lateral often pass
seed2 blocker: single_contact_pattern_dominates
best seed2 contact dominance: 98%
robust modes: 0
```

Decision:

```text
Do not continue broad random grids around the same primitive family.
```

## Contact-Break Micro-Grid

A focused micro-grid around the best near-pass candidate increased seed0
coverage but did not improve seed2 contact dominance.

Result:

```text
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
best seed2 contact_dominance: 98%
50-sample curated windows: 70
curated source: seed_000 only
```

Decision:

```text
Do not train from this data.
Do not run another local contact-break micro-grid without a new contact model.
```

## Lift-Pulse Primitive

The generator now supports default-off lift-pulse controls:

```text
--lift-duties
--lift-scales
```

The lift-pulse search preserved forward/lateral metrics for some seed2
near-misses but still failed contact dominance.

Result:

```text
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
seed2 single_contact_pattern_dominates: 96 / 96 modes
best seed2 contact_dominance: 98%
best seed2 contact_transitions: 2 / 50 samples
```

Decision:

```text
Joint-space lift shaping is not enough.
```

## Foot-Clearance Probe

Future primitive traces now include measured foot-site height:

```text
foot_site_z_m
```

A stronger lift probe still failed seed2 contact-state gates.

Result:

```text
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
seed2 single_contact_pattern_dominates: 48 / 48 modes
seed2 too_few_contact_transitions: 48 / 48 modes
best seed2 foot_site_z_p95: 0.0159 m
best seed2 contact_transitions: 2 / 50 samples
```

Decision:

```text
More knee-lift amplitude inside this primitive family is not the next useful
axis. The commanded joint lift is not becoming reliable swing clearance.
```

## Matched Reference Motion

The corrected x=0.04 reference has coherent analytic intent:

```text
reference progress ratio: 1.0512
linvel_x_mean: 0.0426 m/s
contact transitions per period: 4
```

But direct reference-target rollouts are not yet a usable target source:

```text
raw/projected/contact-gated/contact-synchronized reference rollouts: hold
contact-synchronized mismatch improves to about 4.36%
but rollout still falls 7 / 8 seeds and mean vx is negative
curated seed windows: 0
```

Decision:

```text
Do not use raw matched-reference targets for BC/PPO yet.
The reference is useful as contact-timing evidence, not as a direct target set.
```

## Recommendation

The next target-source implementation should be one of:

```text
1. contact-state optimizer:
   optimize the existing primitive directly against measured contact pattern,
   foot_site_z_m, base height, and worst-seed score

2. IK/reference primitive:
   synthesize swing-foot placement and solve joint targets, then run through
   the normal sim/action/rate-limit path

3. contact-timed reference snippets:
   use the matched reference contact schedule as timing, but generate targets
   that are dynamically trackable under the real actuator envelope
```

Training remains blocked until the target source produces:

```text
50-sample curated windows >= 8
curated source files >= 2
at least one mode passing seed_000 and seed_002
seed2 contact_dominance <= 95%
seed2 contact_transitions >= 3 over 50 samples
sent_target_velocity_p95 <= 2.5 rad/s
joint_tracking_p95 <= 0.12 rad
```

## Dynamic Hip-Roll Target Source

The primitive generator now supports default-off dynamic hip-roll shaping:

```text
--hip-roll-amps
--hip-roll-phase-offsets
```

This is the first primitive axis that produced 50-sample curated windows from
both seed_000 and seed_002:

```text
broad dynamic-roll curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 42
curated source files: 2
curated modes: 36
```

The strict same-mode seed-robust objective still holds:

```text
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
best near-pass:
  mode: primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65
  seed_000: vx=0.0413 m/s, vy95=0.1234 m/s, contact_dominance=92%, contact_transitions=3
  seed_002: vx=0.0417 m/s, vy95=0.1110 m/s, contact_dominance=94%, contact_transitions=4
  remaining failure: seed_000 high_lateral_velocity by about 0.0034 m/s
```

A focused refinement around that near-pass did not improve the 50-sample gate:

```text
refine objective score: HOLD_NO_SEED_ROBUST_TARGETS
refine 50-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS
refine 50-sample curated windows: 3
refine 25-sample curation: PASS_CURATED_DATASET_SEED_READY
```

Decision:

```text
Do not train from the dynamic-roll dataset yet under the current strict gate.
Treat it as the strongest target-source evidence so far.
Next search should stay broad in the dynamic-roll family, reduce seed_000
lateral velocity on the best near-pass, and preserve seed_002 contact
transitions/forward progress. Do not narrow so aggressively that 50-sample
curated coverage disappears.
```

## Dynamic Hip-Roll Lateral Fix

A broader follow-up search kept the dynamic-roll family but targeted the
remaining seed_000 lateral miss without over-narrowing the grid.

Result:

```text
objective score: PASS_SEED_ROBUST_TARGETS
robust 50-sample modes: 2
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 70
curated source files: 2
curated modes: 63
seed robustness audit: PASS_SEED_ROBUST_TARGETS
robust curated modes: 3
```

Best objective-scored robust mode:

```text
mode: primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55

seed_000:
  vx=0.0416 m/s
  vy95=0.0716 m/s
  contact_dominance=90%
  contact_transitions=3
  failures=none

seed_002:
  vx=0.0437 m/s
  vy95=0.0736 m/s
  contact_dominance=94%
  contact_transitions=4
  failures=none
```

Decision:

```text
The target-source layer is now unblocked for a small reviewed offline
imitation/BC smoke using the dynamic-roll lateral-fix target windows.
Robot validation remains blocked.
Do not skip the offline BC/replay gate.
Do not treat this as permission for PPO or hardware tests.
```
