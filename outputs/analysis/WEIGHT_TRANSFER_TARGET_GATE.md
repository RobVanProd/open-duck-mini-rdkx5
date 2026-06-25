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

