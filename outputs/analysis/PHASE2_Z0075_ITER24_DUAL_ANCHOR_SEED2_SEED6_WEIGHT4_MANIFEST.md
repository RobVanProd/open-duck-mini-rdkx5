# Phase 2 z0.0075 Iter24 Dual-Anchor Seed2/Seed6 Weight4 Manifest

status: `PASS_WEIGHTED_DUAL_ANCHOR_MANIFEST_READY`

Offline manifest weighting artifact. No robot, SSH, deploy, grounded replay, runtime behavior change, or training was performed.

## Purpose

Iter24 recovered seed2 but regressed seed6. This manifest upweights the two pass anchors that must both survive:

- iter23 candidate seed6 pass trace
- iter24 candidate seed2 pass trace

Each entry has `sample_weight = 4.0`, which the BC training loader multiplies by row-level `sample_weight`.

## Summary

- source manifest: `outputs/analysis/phase2_z0075_iter24_dual_anchor_seed2_seed6_manifest.json`
- weighted manifest: `outputs/analysis/phase2_z0075_iter24_dual_anchor_seed2_seed6_weight4_manifest.json`
- entries: `2`
- samples: `1500`
- entry sample weight: `4.0`

| source | samples | mean_vx | pitch95 | height_min | sent_vel95 | tracking95 | weight |
|---|---:|---:|---:|---:|---:|---:|---:|
| `iter_024_history_context_resetsettle10_seed2_active/rollouts_x008/student/seed_006/trace.jsonl` | 750 | 0.0265 | 0.1714 | 0.1577 | 1.4321 | 0.1392 | 4.0 |
| `analysis/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_trace_seed2_6/iter24/seed_002/trace.jsonl` | 750 | 0.0262 | 0.1822 | 0.1590 | 1.4432 | 0.1397 | 4.0 |
