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
