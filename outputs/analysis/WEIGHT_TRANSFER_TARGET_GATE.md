# Weight-Transfer Target Gate

status: `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET`

This is an offline gate read over existing target-generation objective-score
artifacts. It does not run simulation, training, robot SSH, deployment, or
hardware tests.

## Gate

```text
PASS_WEIGHT_TRANSFER_TARGET:
  100-150 tick target or rollout has meaningful forward progress, low lateral
  drift, stable pitch/height, in-envelope target velocities, and multiple useful
  support transitions across the required reset seeds.
```

## Inputs

| artifact | window | status |
|---|---:|---|
| `target_objective_score_dynamic_roll_lateral_fix_100.json` | 100 ticks | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `target_objective_score_dynamic_roll_lateral_fix_150.json` | 150 ticks | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `target_objective_score_weight_transfer_dynamic_roll_lateral_fix_100.json` | 100 ticks | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `target_objective_score_weight_transfer_dynamic_roll_lateral_fix_150.json` | 150 ticks | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `target_generator_dynamic_roll_lateral_fix_window_curation_100.json` | 100 ticks | `HOLD_INSUFFICIENT_CURATED_WINDOWS` |
| `target_generator_dynamic_roll_lateral_fix_window_curation_150.json` | 150 ticks | `HOLD_INSUFFICIENT_CURATED_WINDOWS` |
| `TARGET_GENERATOR_BIASED_MULTISEED_WINDOW_MINE.md` | 25 ticks | `PASS_REALIZED_WINDOWS_AVAILABLE` |

## 100-Tick Result

The dynamic-roll lateral-fix 100-tick objective score found no robust modes:

```text
trace_files: 320
mode_count: 160
robust_mode_count: 0
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Main rejection reasons:

| reason | count |
|---|---:|
| low_forward_velocity | 312 |
| single_contact_pattern_dominates | 148 |
| too_few_contact_transitions | 26 |
| high_lateral_velocity | 11 |
| low_base_height | 13 |

The top-ranked mode still failed both required seeds:

| seed | mean vx | contact pct | contact transitions | hard failures |
|---|---:|---|---:|---|
| seed_000 | 0.0211 m/s | `{'01': 6.0, '10': 3.0, '11': 91.0}` | 7 | low_forward_velocity |
| seed_002 | 0.0238 m/s | `{'01': 2.0, '10': 2.0, '11': 96.0}` | 5 | low_forward_velocity, single_contact_pattern_dominates |

The explicit weight-transfer rescore made the support failure visible:

| metric | count |
|---|---:|
| double_support_dominates | 310 |
| too_little_single_support | 294 |
| single_support_not_balanced | 198 |

Top explicit-rescore mode:

| seed | mean vx | double support | single support | min side-only support | hard failures |
|---|---:|---:|---:|---:|---|
| seed_000 | 0.0176 m/s | 90.0% | 10.0% | 4.0% | low_base_height, low_forward_velocity |
| seed_002 | 0.0213 m/s | 94.0% | 6.0% | 2.0% | double_support_dominates, low_forward_velocity, too_little_single_support |

## 150-Tick Result

The dynamic-roll lateral-fix 150-tick objective score also found no robust
modes:

```text
trace_files: 320
mode_count: 160
robust_mode_count: 0
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Main rejection reasons:

| reason | count |
|---|---:|
| low_forward_velocity | 312 |
| single_contact_pattern_dominates | 295 |
| too_few_contact_transitions | 17 |
| low_base_height | 11 |

The top-ranked mode still failed both required seeds:

| seed | mean vx | contact pct | contact transitions | hard failures |
|---|---:|---|---:|---|
| seed_000 | 0.0132 m/s | `{'01': 4.0, '10': 2.67, '11': 93.33}` | 9 | low_base_height, low_forward_velocity |
| seed_002 | 0.0147 m/s | `{'01': 1.33, '10': 2.67, '11': 96.0}` | 7 | low_forward_velocity, single_contact_pattern_dominates |

The explicit weight-transfer rescore is stronger at 150 ticks:

| metric | count |
|---|---:|
| double_support_dominates | 312 |
| too_little_single_support | 312 |
| single_support_not_balanced | 293 |

Top explicit-rescore mode:

| seed | mean vx | double support | single support | min side-only support | hard failures |
|---|---:|---:|---:|---:|---|
| seed_000 | 0.0093 m/s | 95.33% | 4.67% | 2.0% | double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support |
| seed_002 | 0.0117 m/s | 95.33% | 4.67% | 1.33% | double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support |

## Short-Window Contrast

Short 25-tick windows can contain useful in-envelope forward motion, but they
are mostly pre-fall or double-support-dominated snippets:

```text
TARGET_GENERATOR_BIASED_MULTISEED_WINDOW_MINE.md:
  status: PASS_REALIZED_WINDOWS_AVAILABLE
  top windows: 0.04-0.08 m/s
  contacts commonly 80-100% double support
```

This explains why the short dynamic-roll fragments are useful evidence but not
a sustained walking target.

## Decision

The current data does not pass `PASS_WEIGHT_TRANSFER_TARGET`.

The failed 100/150-tick gate gives a more precise branch than another prior
scale run:

```text
current generator family:
  can create short in-envelope motion hints
  cannot yet create a sustained low-command weight-transfer target

next useful work:
  modify the target generator/objective to reward sustained forward progress,
  support alternation, useful single-support dwell, low lateral drift, and
  pitch/height stability over 100-150 ticks.
```

Do not launch PPO/BC from the existing short fragment table as if it were a
full walking target. Generate or verify a sustained weight-transfer target
first.

## Tooling Update

`tools/score_target_candidates_objective.py` now exposes support-shape criteria
without changing the default historical behavior:

```text
--max-double-support-pct
--max-no-support-pct
--min-single-support-pct
--min-each-single-support-pct
```

The stricter rescoring used:

```text
max_double_support_pct: 90
min_single_support_pct: 8
min_each_single_support_pct: 2
```

## Weight-Transfer Probe Search

A bounded CPU-only probe searched 72 new support-biased primitives with larger
hip-roll bias/amp and lift pulses:

```text
artifact: outputs/analysis/TARGET_GENERATOR_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_WEIGHT_TRANSFER_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_WEIGHT_TRANSFER_PROBE_150.md
seeds: 0,2
duration: 3.0 s
status: PASS_TARGET_SEARCH_RAN
```

This probe improved the support-shape failure on the top candidates, but it did
not produce forward motion:

| window | robust modes | top seed0 vx | top seed2 vx | top seed0 support | top seed2 support | result |
|---|---:|---:|---:|---|---|---|
| 100 ticks | 0 | 0.0045 m/s | 0.0043 m/s | 85% double / 15% single | 87% double / 12% single | low forward velocity |
| 150 ticks | 0 | 0.0018 m/s | 0.0035 m/s | 86% double / 14% single | 88% double / 12% single | low forward velocity |

Reason counts:

| artifact | low_forward_velocity | double_support_dominates | too_little_single_support |
|---|---:|---:|---:|
| `target_objective_score_weight_transfer_probe_100.json` | 144 | 95 | 62 |
| `target_objective_score_weight_transfer_probe_150.json` | 144 | 107 | 94 |

Interpretation: simply adding stronger roll/lift pulses to this primitive family
can create more support transitions, but it does not create useful forward
locomotion. The generator needs a different objective/mechanism that couples
support transfer to forward displacement, not just stronger foot unweighting.

## Stance-Push Probe Search

The primitive tool was extended with default-off stance-push parameters:

```text
--stance-push-amps
--stance-ankle-scales
```

These add a stance-leg hip-pitch offset, with optional ankle coupling, only
while that side is not in its lift phase. Historical/default primitive behavior
is unchanged when the flags are left at `0.0`.

A bounded CPU-only stance-push probe searched 48 candidates:

```text
artifact: outputs/analysis/TARGET_GENERATOR_STANCE_PUSH_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_STANCE_PUSH_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_STANCE_PUSH_PROBE_150.md
seeds: 0,2
duration: 3.0 s
status: PASS_TARGET_SEARCH_RAN
```

Result:

| window | robust modes | top seed0 vx | top seed2 vx | top seed0 support | top seed2 support | result |
|---|---:|---:|---:|---|---|---|
| 100 ticks | 0 | 0.0089 m/s | 0.0108 m/s | 88% double / 12% single | 92% double / 8% single | low forward velocity |
| 150 ticks | 0 | 0.0028 m/s | 0.0061 m/s | 90% double / 10% single | 91.33% double / 8.67% single | low forward velocity |

Reason counts:

| artifact | low_forward_velocity | double_support_dominates | too_little_single_support |
|---|---:|---:|---:|
| `target_objective_score_stance_push_probe_100.json` | 96 | 81 | 47 |
| `target_objective_score_stance_push_probe_150.json` | 96 | 94 | 80 |

Interpretation: simple stance push is not enough either. It raises the top
100-tick velocity from near-zero to about `0.01 m/s`, but it still misses the
`0.04 m/s` gate badly and degrades over 150 ticks. The next generator needs
closed-loop or phase-aware coupling between body velocity, body pitch, and
contact state, rather than only open-loop per-joint sinusoid terms.

## Velocity-Feedback Stance-Push Probe

The primitive tool was extended with another default-off term:

```text
--velocity-push-gains
--velocity-push-limit
```

This adds a clipped stance-push correction proportional to
`command_x - local_vx` before each primitive step. Historical/default primitive
behavior is unchanged when the gain is `0.0`.

A bounded CPU-only velocity-feedback probe searched 32 candidates:

```text
artifact: outputs/analysis/TARGET_GENERATOR_VELOCITY_FEEDBACK_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_VELOCITY_FEEDBACK_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_VELOCITY_FEEDBACK_PROBE_150.md
seeds: 0,2
duration: 3.0 s
status: PASS_TARGET_SEARCH_RAN
```

Result:

| window | robust modes | top seed0 vx | top seed2 vx | top seed0 support | top seed2 support | result |
|---|---:|---:|---:|---|---|---|
| 100 ticks | 0 | 0.0070 m/s | 0.0061 m/s | 89% double / 11% single | 90% double / 10% single | low forward velocity |
| 150 ticks | 0 | 0.0031 m/s | 0.0058 m/s | 86.67% double / 13.33% single | 92% double / 8% single | low forward velocity |

Reason counts:

| artifact | low_forward_velocity | double_support_dominates | too_little_single_support |
|---|---:|---:|---:|
| `target_objective_score_velocity_feedback_probe_100.json` | 63 | 51 | 35 |
| `target_objective_score_velocity_feedback_probe_150.json` | 63 | 57 | 49 |

Interpretation: simple local-vx feedback into the same stance-push primitive is
still not enough. The primitive family can produce safe, mostly upright
standing/shuffling, but not sustained low-command forward locomotion. The next
useful generator should change structure: plan contact phases and body motion
together, or use a controller/teacher with state feedback over CoM, pitch, and
stance-foot loading rather than only feeding velocity error into joint sinusoids.

## Closed-Loop Weight-Transfer Teacher Probe

The next step added a separate state-feedback teacher probe rather than another
scalar term on the primitive generator:

```text
tool: tools/probe_closed_loop_weight_transfer_teacher.py
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_SCORE_150.md
seeds: 0,2
duration: 3.0 s
status: HOLD_NO_SEED_ROBUST_TARGETS
```

This first teacher couples support phase, local velocity, lateral velocity,
body pitch, base height, and current contacts. It improved raw rollout forward
velocity compared with the earlier primitive probes, but it still did not pass
the sustained gate:

| result | 100 ticks | 150 ticks |
|---|---:|---:|
| robust modes | 0 | 0 |
| top aggregate rollout mean vx | 0.0232 m/s | 0.0232 m/s |
| best scored seed2 vx | 0.0050 m/s | 0.0047 m/s |
| dominant failures | low forward velocity, high lateral velocity | low forward velocity, high lateral velocity |

Interpretation: state feedback is directionally useful, but the first teacher
is not the answer. It creates more contact transitions and higher raw forward
motion than the open-loop probes, but it trades that for side motion and still
cannot produce seed-robust `0.04 m/s` forward displacement over 100-150 ticks.

The next teacher revision should reduce lateral impulse while preserving the
support transitions:

```text
separate lateral load shift from forward push
add a stronger local_vy damping term
gate stance push until lateral velocity is bounded
add body-y / CoM-centering feedback, not only hip-roll correction
```

## Closed-Loop Weight-Transfer Teacher V2 Probe

The teacher was then extended with body-y centering and lateral-speed push
gating:

```text
tool flags:
  --body-y-gains
  --push-lateral-gates

artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

| metric | value |
|---|---:|
| top aggregate rollout mean vx | 0.0305 m/s |
| 100-tick robust modes | 0 |
| 150-tick robust modes | 0 |
| best scored 100-tick seed0 / seed2 vx | -0.0006 / 0.0002 m/s |
| best scored 150-tick seed0 / seed2 vx | 0.0003 / 0.0011 m/s |

Interpretation: v2 exposes the current tradeoff. Some candidates move closer
to the `0.04 m/s` target in raw rollout summaries, but those same candidates
fail lateral velocity in the objective score. The objective-ranked candidates
that keep lateral velocity near gate lose forward motion. This suggests the
next teacher cannot be only roll/push feedback; it needs a more explicit
forward step geometry or foot-placement/CoM planner that can generate forward
displacement without side impulse.

## Closed-Loop Weight-Transfer Teacher V3 Probe

V3 added explicit foot-placement geometry:

```text
tool flags:
  --swing-hip-reaches
  --stance-retract-scales
  --pitch-targets

artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

| metric | value |
|---|---:|
| top aggregate rollout mean vx | 0.0337 m/s |
| 100-tick robust modes | 0 |
| 150-tick robust modes | 0 |
| top scored 100-tick seed0 / seed2 vx | 0.0104 / 0.0155 m/s |
| top scored 150-tick seed0 / seed2 vx | 0.0072 / 0.0102 m/s |
| top scored 100-tick seed0 / seed2 vy95 | 0.1371 / 0.1341 m/s |

Interpretation: explicit swing reach and stance retract improve raw forward
motion again, but the same coupled failure remains. The best scored windows
have useful support alternation and low target velocities, yet still miss both
the `0.04 m/s` forward gate and the `0.12 m/s` lateral gate. This suggests the
next generator needs a more principled planner, such as a lateral-first balance
phase followed by a forward step phase, or an offline optimizer that explicitly
penalizes lateral impulse while preserving forward displacement.

## Staged Weight-Transfer Planner Probe

The staged planner tested that lateral-first branch directly:

```text
tool: tools/probe_staged_weight_transfer_planner.py
artifact: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_PROBE.md
score_100: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_100.md
score_150: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

| metric | value |
|---|---:|
| 100-tick robust modes | 0 |
| 150-tick robust modes | 0 |
| top 100-tick seed0 / seed2 vx | 0.0015 / 0.0034 m/s |
| top 100-tick seed0 / seed2 vy95 | 0.1149 / 0.1197 m/s |
| top 100-tick seed0 / seed2 double support | 89% / 85% |
| top 100-tick seed0 / seed2 single support | 11% / 15% |

Interpretation: explicit balance gating fixes the lateral gate for the best
windows, but it suppresses forward displacement almost completely. This is a
useful negative result. The project now has both sides of the tradeoff:

```text
aggressive teacher terms: more forward velocity, lateral impulse too high
staged balance gates: lateral velocity acceptable, forward velocity near zero
```

Do not keep widening random grids over either form. The next target-source
generator should optimize over a short horizon or use a richer body-state
controller that explicitly trades lateral error, support state, and forward
impulse.

The next branch is specified in:

```text
docs/WEIGHT_TRANSFER_OPTIMIZER_PLAN.md
```

The first optimizer and forward-intent teacher runs refined the conclusion:

```text
optimizer displacement probe:
  HOLD_OPTIMIZER_NO_ROBUST_TARGET
  best local dx: -0.0070 / 0.0030 m

forward-intent teacher probe:
  HOLD_NO_SEED_ROBUST_TARGETS
  top 100-tick local dx: 0.0518 / 0.0420 m
  top 100-tick vy95: 0.1917 / 0.1859 m/s
```

This confirms the target-source blocker with a corrected local-frame
displacement metric: forward displacement can be forced, but not yet while
preserving the lateral gate.

## Lateral-Refined Forward-Intent Teacher Probe

A focused CPU-only refinement then searched around the forward-intent teacher
family with stronger lateral/body-y feedback and push gating:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

| window | robust modes | top scored seed0 vx / dx | top scored seed2 vx / dx | top scored seed0 / seed2 vy95 | dominant result |
|---|---:|---:|---:|---:|---|
| 100 ticks | 0 | 0.0131 m/s / 0.0261 m | 0.0186 m/s / 0.0371 m | 0.1270 / 0.1093 m/s | low forward displacement, mostly double support |
| 150 ticks | 0 | 0.0137 m/s / 0.0411 m | 0.0124 m/s / 0.0372 m | 0.1562 / 0.1650 m/s | low forward displacement, high lateral velocity |

The highest-displacement individual windows still fail the same tradeoff:

```text
100 ticks:
  best local dx: 0.0850 m on seed2
  vy95: 0.3083 m/s

150 ticks:
  best local dx: 0.0912 m on seed0
  vy95: 0.2634 m/s
```

Interpretation: targeted lateral/body-y refinement did not decouple forward
displacement from lateral impulse. The best objective-ranked windows become
more conservative and miss forward progress; the best displacement windows
still exceed the lateral gate badly. This is a stop sign for more nearby
teacher-grid expansion.

## Current Decision

The target-source campaign now has the trace read requested by the contact
hypothesis:

```text
raw polynomial reference path:
  asks for alternating single support, but closed-loop rollout remains mostly
  double support; direct reference/BC labels are not valid.

dynamic-roll / teacher target path:
  short fragments and some teacher windows can produce forward displacement,
  but sustained seed-robust targets either stay double-support/conservative or
  spend too much lateral velocity.
```

So the next branch should not be:

```text
- stronger pitch-chain prior scale
- another contact-bit adapter around the same short table
- another nearby random grid over the same teacher terms
```

The next useful work is a structurally different contact/weight-transfer
objective or controller that explicitly prices:

```text
1. useful left/right single-support alternation,
2. low lateral velocity/base-y drift,
3. forward displacement over 100-150 ticks,
4. base-height and pitch stability,
5. in-envelope target velocity.
```

Training remains blocked until a target source passes this gate.
