# Phase 2 z=0.0075 Intermediate-Push Live-Oracle Iter0 Decision

status: `PASS_CURATED_LIVE_ORACLE_LABELS_READY`

## Scope

- Offline sim/data curation only.
- No robot tests, SSH, deploy, grounded replay, training, or runtime behavior changes were performed.
- This artifact records how the push-aware live-oracle DAgger iter0 traces were handled before any student fit.

## Input Run

- iteration report: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_run/LIVE_ORACLE_DAGGER_ITERATION.md`
- raw aggregate: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_run/live_oracle_dagger_aggregate_manifest.json`
- student: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- push interval: `1.0-1.5 s`
- push magnitude: `0.075-0.125`

## Raw Rollout Read

| command | seed | raw status | samples | mean vx | track ratio | pitch p95 | height min | p95 excess | push success | decision |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `x=0.08` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0265 | 0.3313 | 0.1602 | 0.1527 | 0.0000 | 0.9167 | keep full |
| `x=0.08` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 582 | 0.0598 | 0.7473 | 0.2914 | -0.0052 | 0.0000 | 0.8750 | truncate before collapse |
| `x=0.0` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 62 | -0.2639 | NA | 0.0091 | 0.0721 | 2.5959 | 0.0000 | drop |
| `x=0.0` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | -0.0002 | NA | 0.0672 | 0.1568 | 0.0000 | 0.9231 | keep full |

The raw aggregate is syntactically BC-ready but not fit-safe: it admits a zero-command fall/reverse trace and a moving trace with a final collapse tail. Those traces must not be used as positive labels without curation.

## Curation

- kept `x=0.08 seed 0` full trace.
- kept `x=0.08 seed 7` through tick `500`; this removes the late pitch/base-height collapse while preserving the useful push-response segment.
- dropped `x=0.0 seed 0`; it is an early backward/fall/over-envelope failure.
- kept `x=0.0 seed 1` full trace.

## Curated Outputs

| artifact | status | dataset_id | entries | samples |
|---|---|---|---:|---:|
| `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_x008_curated_manifest.json` | `PASS_BC_TRACE_MANIFEST_READY` | `7109acd7b0c71b8a` | 2 | 1251 |
| `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_x0_curated_manifest.json` | `PASS_BC_TRACE_MANIFEST_READY` | `ec68b86f107c4844` | 1 | 750 |
| `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json` | `PASS_FILTERED_BC_MANIFEST_READY` | `88de24bcd82435ee` | 57 | 42501 |

## Decision

- `raw_aggregate_fit_approved`: `False`
- `curated_aggregate_fit_approved`: `True`
- `next_fit_manifest`: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json`

The next supervised student fit should use only the curated aggregate. Do not train from the raw iter0 aggregate, because it contains known failure labels.

## Next Step

Fit a small phase/command-conditioned BC student from the curated aggregate, then gate it on the canonical corrected-bridge evaluator before any further promotion. If the fit regresses x=0.0 stillness or repeats the x=0.08 push fall, add another live-oracle iteration from the fitted student's own failure states rather than returning to scalar PPO reward tuning.
