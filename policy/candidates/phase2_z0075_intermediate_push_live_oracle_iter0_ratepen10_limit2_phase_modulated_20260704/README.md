# Phase 2 z=0.0075 Rate-Penalty10 Limit2 Phase-Modulated Candidate

status: `HOLD_FIT_SPIKES_REMAIN`

This is an offline negative-control candidate. It was fit from the uncapped
curated live-oracle iter0 aggregate with a stronger supervised adjacent-rate
penalty (`target_rate_scale=10.0`, `target_rate_limit_rad_s=2.0`).

It is not deployable and is not a robot-test authorization.

## Files

- `candidate.onnx`
  - sha256: `e251565ccd1f5adf54be631eb2ca6c50d37dbecc5f71e7289a57fed16040af6e`
- `student.npz`
  - sha256: `987c2faa617070434ec9a724d1ccc03ad1e02f541c273743eeb1a826b9fd38cc`

## Fit

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json`
- action MAE: `0.020880`
- action p95 abs error: `0.059004`
- action max abs error: `1.691553`
- target-rate p95: `1.344511 rad/s`
- target-rate max: `3.386143 rad/s`

## Decision

The stronger supervised rate penalty worsened action fit and did not remove
the fit-level max spike enough to justify closed-loop screening. This path is
not promoted.
