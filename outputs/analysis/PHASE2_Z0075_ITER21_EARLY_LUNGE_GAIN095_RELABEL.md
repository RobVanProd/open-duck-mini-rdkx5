# Phase 2 Early-Lunge Recovery Labels

status: `PASS_EARLY_LUNGE_RECOVERY_LABELS_READY`

Offline-only curation. Failing rollout observations are preserved and
selected actions are replaced with aligned pass-control actions. No
training, deployment, SSH, robot test, or runtime change was performed.

## Inputs

- fail_trace: `outputs/analysis/phase2_z0075_iter13_seed0_push_failure_trace/iter13_push_window_recovery_rate150/seed_000/trace.jsonl`
- pass_trace: `outputs/analysis/phase2_z0075_iter13_gain095_seed0_trace/iter13_gain095/seed_000/trace.jsonl`
- output_trace: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_relabel/seed_000/trace.jsonl`

## Gate

- indices: `[88, 46, 60, 74, 18]`
- threshold: `5.0`
- tick_window: `0-140`

## Summary

- selected_samples: `31`
- dataset_id: `0bffa7f052bca127`
- score_p50: `6.9688567643905355`
- score_p95: `9.237299416386081`
- action_delta_p95: `0.18809791104868046`

## Manifest Entry

| source | ticks | samples | mode | mean_vx | pitch_p95 | base_min |
|---|---:|---:|---|---:|---:|---:|
| phase2_z0075_iter21_early_lunge_gain095_relabel/seed_000/trace.jsonl | 19-92 | 31 | `iter21_early_lunge_gain095_relabel` | 0.1385 | 0.5418 | 0.1476 |

## Interpretation

- This artifact is a data input for the next BC student only.
- It is not a candidate policy and is not promotable by itself.
- Gate seeds 0, 2, and 6 before any full promotion test.
