# Target Source Decision

This note records the current offline target-source decision. It is not a robot
test plan and not training permission.

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

