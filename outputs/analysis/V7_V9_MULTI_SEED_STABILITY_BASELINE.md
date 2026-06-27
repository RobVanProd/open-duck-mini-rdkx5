# V7 / V9 Multi-Seed Stability Baseline

status: `HOLD_NO_ROBOT_VALIDATION`

This is an offline CPU closed-loop sim baseline. It did not SSH, deploy, train,
touch the robot, or change runtime behavior.

## Purpose

The one-second checkpoint sweep made V9 look like the best middle point between
V7's lunge and V8's standstill. The full-duration two-seed recheck then showed
V9 had more than one failure mode. This baseline measures those failures as a
distribution instead of a pair of anecdotes.

Command:

```text
command_x: 0.08
bridge_mode: fitted
duration: 15 s
seeds: 0-7
jax_platform: cpu
```

Evidence:

```text
outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/CANDIDATE_SEED_SWEEP.md
outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/V9_SEED0_TRACE_ANALYSIS.md
outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/V9_SEED1_TRACE_ANALYSIS.md
outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/V7_SEED0_TRACE_ANALYSIS.md
outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/V7_SEED1_TRACE_ANALYSIS.md
```

## Distribution Result

| policy | seeds | falls | duration complete | mean samples | min samples | max samples | mean track ratio | mean local vx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V7 checkpoint anchor | 8 | 5 | 3 | 311.75 | 28 | 750 | 0.2351 | 0.0188 |
| V9 progress balanced | 8 | 5 | 3 | 312.00 | 27 | 750 | 0.3282 | 0.0263 |

V9 did not materially improve the stability distribution versus V7. Both
policies fall on `5/8` seeds and collapse into low-forward-progress standstill
on `3/8` seeds.

## Failure Modes

The same seed indices produce similar surface failures for V7 and V9:

- seeds `0` and `6`: forward lunge / pitch-over
- seed `5`: reverse/negative local velocity failure
- seeds `1` and `7`: early base-height/contact collapse
- seeds `2`, `3`, and `4`: full-duration low-forward-progress standstill

This means V9 is not a single-defect policy waiting for one scalar fix. It has
low stability margin across several directions: overdrive, under-support, and
standstill.

## Trace Comparison

V9 seed 0:

```text
samples: 73
first done tick: 72
mean local vx: 0.2217 m/s
track ratio: 2.7707
body pitch abs p95: 1.2604 rad
base height min: 0.0305 m
contact events: 10
```

V9 seed 1:

```text
samples: 32
first done tick: 31
mean local vx: 0.0185 m/s
track ratio: 0.2314
body pitch abs p95: 0.0496 rad
base height min: 0.0672 m
contact events: 5
left foot contact count: 30
right foot contact count: 2
```

Seed 0 is the lunge/pitch-over mode. Seed 1 is not a speed-overshoot failure;
it is an early support/contact/base-height collapse with little pitch growth.

Both failures remain below the actuator target-velocity threshold and have `0%`
action saturation, so actuator budget and saturation are still not the active
limit for these candidates.

## V10 Implication

V10 should be graded by distribution shift, not a single seed. The baseline to
beat is:

```text
fall rate: 5/8
mean samples: about 312
standstill rate: 3/8
no seed passes useful full-duration forward tracking
```

A real improvement would move this distribution, for example:

```text
fewer falls,
later fall samples,
higher mean local vx without track-ratio overshoot,
lower body pitch on lunge seeds,
higher base height / better support on buckle seeds,
fewer standstill duration-complete seeds.
```

The V10 objective should keep the broad penalty set:

- forward-speed overshoot,
- pitch and pitch-rate growth,
- base-height collapse,
- contact/support timing,
- teacher/trust-region continuity for gait shape.

Do not narrow V10 to speed-overshoot alone. The seed-1 and seed-7 failures show
that under-support/contact collapse is a separate observed failure surface.
