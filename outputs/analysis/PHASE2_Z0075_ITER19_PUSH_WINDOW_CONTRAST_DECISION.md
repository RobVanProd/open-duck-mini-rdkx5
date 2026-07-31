# Phase 2 z=0.0075 Iter19 Push-Window Contrast Decision

status: `PASS_ITER19_CONTRAST_AUDIT_NEXT_MULTIVARIATE_GATE`

This is offline sim/analysis only. It did not train, SSH, deploy, run robot
tests, grounded replay, or change runtime behavior.

## Question

Iter18 showed that a deployable single-channel `obs[1]` threshold attenuation
wrapper does not repair the seed0 first-push lunge. Iter19 asks whether the
existing traces contain enough contrast to build a more specific recovery gate,
or whether the failure is not separable from pass behavior in the current
observation stream.

## Inputs

| label | role | trace |
|---|---|---|
| `seed0_lunge_fail` | full-gain seed0 first-push lunge | `outputs/analysis/phase2_z0075_iter13_seed0_push_failure_trace/iter13_push_window_recovery_rate150/seed_000/trace.jsonl` |
| `seed0_gain095_pass` | eval-only gain-0.95 seed0 pass | `outputs/analysis/phase2_z0075_iter13_gain095_seed0_trace/iter13_gain095/seed_000/trace.jsonl` |
| `seed6_gain095_collapse` | eval-only gain-0.95 seed6 late collapse | `outputs/analysis/phase2_z0075_iter13_gain095_seed6_trace/iter13_gain095/seed_006/trace.jsonl` |

Audit:

- markdown: `outputs/analysis/PHASE2_Z0075_ITER19_PUSH_WINDOW_CONTRAST_AUDIT.md`
- json: `outputs/analysis/phase2_z0075_iter19_push_window_contrast_audit.json`
- early-window markdown: `outputs/analysis/PHASE2_Z0075_ITER19_PUSH_WINDOW_EARLY_CONTRAST_AUDIT.md`
- early-window json: `outputs/analysis/phase2_z0075_iter19_push_window_early_contrast_audit.json`
- tool: `tools/analyze_push_window_contrasts.py`

## Main Findings

The seed0 forward-lunge failure is clearly different from the seed0 gain-0.95
pass during the first push window:

| field | seed0 lunge | seed0 gain-0.95 pass |
|---|---:|---:|
| first-push mean vx | 0.2536 | 0.0088 |
| first-push max abs pitch | 1.4228 | 0.2069 |
| first-push min base height | 0.0216 | 0.1584 |
| first-push `obs[1]` mean | 1.0007 | -0.0170 |
| first-push `obs[1]` p95 | 4.9609 | 0.7990 |

The early-window audit, restricted to ticks `push-20` through `push+10`, shows
why Iter18's `obs[1]` threshold fired too late. In the early window,
`obs[1]` is only a weak separator (`0.0735` vs `0.0037` mean), while the best
early separators are `obs[88]`, `obs[46]`, `obs[60]`, `obs[74]`, and `obs[18]`.
Those channels separate before the full lunge/pitchover state has developed.

The seed6 gain-0.95 late collapse is a different mode, not the same lunge:

| field | seed6 gain-0.95 collapse | seed0 gain-0.95 pass |
|---|---:|---:|
| late-window mean vx | -0.2283 | 0.0122 |
| late-window max abs pitch | 1.4153 | 0.1776 |
| late-window min base height | 0.0556 | 0.1574 |
| late-window `obs[1]` mean | -1.0923 | 0.0160 |
| late-window `obs[3]` mean | 1.5567 | -0.9117 |

The audit confirms that the state stream contains useful contrast. It also
explains why Iter18 failed: `obs[1]` alone can detect part of the seed0 lunge
signature, but a scalar thresholded output scale is too blunt and does not model
the seed6 opposite-sign collapse.

## Decision

`PASS_ITER19_CONTRAST_AUDIT_NEXT_MULTIVARIATE_GATE`

Do not continue single-channel threshold attenuation or global gain sweeps. The
next deployable recovery attempt should be multivariate and push-window
specific, with explicit controls for both known regressions:

1. seed0 full-gain first-push lunge
2. seed0 gain-0.95 first-push pass
3. seed6 gain-0.95 late backward/base-height collapse

The candidate must still preserve:

- corrected bridge envelope compliance
- rough z=0.0075 no-push locomotion
- seeds 2 and 6 intermediate-push behavior
- x=0.0 command semantics

## Next Branch

Build a small offline lunge/collapse contrast model over observation windows,
then use it only to gate a recovery action or recovery-label selection. Do not
promote a wrapper unless it passes the existing fail-seed gate for seeds `0,2,6`
under rough z=0.0075, `home-support`, and intermediate push.

The first candidate gate should be based on early lunge separators, not late
outcome indicators. Treat `obs[1]` as an outcome/lunge-amplitude channel unless
validated with the early-window audit.
