# Phase 2 z=0.0075 Spike Mitigation Result

status: `HOLD_SPIKE_FIX_REGRESSES_OR_INSUFFICIENT`

## Scope

- Offline label curation, BC fitting, and sim screening only.
- No robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior changes were performed.

## Starting Point

Candidate:

`policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_phase_modulated_rate150_20260704/candidate.onnx`

The candidate fixed the targeted collapse modes but held on instantaneous
target-velocity excess and slow progress:

- `x=0.08 seed 7` no longer fell.
- `x=0.0 seed 0` no longer collapsed.
- `x=0.08` track ratio mean remained `0.3096`.
- max instantaneous velocity excess remained up to `3.0346 rad/s` across the compact screens.

## Spike Source

The rare max spikes are label-side as well as closed-loop-side: the curated
new iter0 `action` labels contained pitch-chain action deltas above the
corrected per-joint envelope even though their p95 rates were reasonable.

The largest held-screen violations were concentrated in pitch-chain joints:

- `x=0.08 seed 7`: right ankle, right knee, left ankle, left knee, left hip pitch.
- `x=0.0 seed 1`: right ankle, right hip pitch, left hip pitch, left ankle.

## Attempt A: Hard Per-Joint Label Caps

Tool change:

`tools/curate_bc_trace_records.py` now supports
`--per-joint-max-target-velocity-rad-s`.

Applied corrected pitch-chain caps to the three new iter0 traces:

```text
left_hip_pitch: 2.5
left_knee:      3.25
left_ankle:     2.75
right_hip_pitch:2.25
right_knee:     2.75
right_ankle:    2.0
```

Curated rows capped:

| joint index | joint | rows capped |
|---:|---|---:|
| 2 | `left_hip_pitch` | 17 |
| 3 | `left_knee` | 6 |
| 4 | `left_ankle` | 17 |
| 11 | `right_hip_pitch` | 19 |
| 12 | `right_knee` | 14 |
| 13 | `right_ankle` | 40 |

Fit:

- candidate: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_spike_capped_phase_modulated_rate150_20260704/candidate.onnx`
- sha256: `89b5422d41ab162cdc94b4316b360e1af841491c3b8519595992d79edf25cb40`
- dataset_id: `d3b90392d1b4b4f6`
- target-rate p95: `1.306787 rad/s`
- target-rate max: `2.179695 rad/s`

Screen:

| command | seed | status | samples | mean vx | track ratio | pitch p95 | height min | max excess | push success |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `x=0.08` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 194 | 0.1173 | 1.4660 | 0.8034 | -0.0078 | 0.7543 | 0.6667 |
| `x=0.08` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0232 | 0.2901 | 0.1575 | 0.1568 | 1.3301 | 0.9000 |

Decision: hard per-joint capping is too destructive. It reduces fit-level
target-rate max but removes enough transition behavior to bring back a seed-0
fall/lunge.

## Attempt B: Stronger Supervised Rate Penalty

Fit used the uncapped curated aggregate, with `target_rate_scale=10.0` and
`target_rate_limit_rad_s=2.0`.

- candidate: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_ratepen10_limit2_phase_modulated_20260704/candidate.onnx`
- sha256: `e251565ccd1f5adf54be631eb2ca6c50d37dbecc5f71e7289a57fed16040af6e`
- action MAE: `0.020880`
- action p95 abs error: `0.059004`
- target-rate p95: `1.344511 rad/s`
- target-rate max: `3.386143 rad/s`

Decision: stronger supervised rate penalty worsened BC fit and did not remove
the fit-level max spike enough to justify closed-loop screening.

## Aggregate Decision

`HOLD_SPIKE_FIX_REGRESSES_OR_INSUFFICIENT`

The rare spike rows are load-bearing transition labels. Hard capping them
causes gait collapse; a stronger generic supervised rate penalty does not
remove them enough. The next offline step should be spike-aware *state
coverage*, not stronger global smoothing:

1. collect full-observation traces around the spike ticks from the uncapped
   stable candidate,
2. relabel those states with the live oracle under a local trust-region/rate
   constraint,
3. fit from the expanded local state coverage,
4. rerun the same compact z=0.0075 intermediate-push screens.

Do not promote either spike-mitigation candidate and do not run robot-side
validation.
