# Phase 2 z=0.0075 Spike-Capped Phase-Modulated Rate150 Candidate

status: `HOLD_REGRESSED_STABILITY`

This is an offline negative-control candidate. It was fit from the same
curated live-oracle iter0 dataset after applying corrected per-joint
pitch-chain velocity caps to the three new iter0 traces.

It is not deployable and is not a robot-test authorization.

## Files

- `candidate.onnx`
  - sha256: `89b5422d41ab162cdc94b4316b360e1af841491c3b8519595992d79edf25cb40`
- `student.npz`
  - sha256: `2f75caf39fb99bdf7233ac3918c99e08b67f8288bd104a5a761cef08352ac47c`

## Fit

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_spike_capped/live_oracle_dagger_spike_capped_aggregate_manifest.json`
- dataset_id: `d3b90392d1b4b4f6`
- action MAE: `0.011763`
- action p95 abs error: `0.037640`
- action max abs error: `0.786255`
- target-rate p95: `1.306787 rad/s`
- target-rate max: `2.179695 rad/s`

## Decision

The label cap reduced target-rate max in the fit, but the closed-loop
`x=0.08` z=0.0075 intermediate-push screen regressed to a seed-0 fall at 194
samples. This shows the rare high-rate transition labels are partially
load-bearing and cannot be removed by hard caps alone.
