# Phase 2 Early-Lunge Recovery Labels

status: `PASS_EARLY_LUNGE_RECOVERY_LABELS_READY`

Offline-only curation. Failing rollout observations are preserved and
selected actions are replaced with aligned pass-control actions. No
training, deployment, SSH, robot test, or runtime change was performed.

## Inputs

- fail_trace: `outputs/analysis/phase2_command_gated_zero0020_seed5_failure_trace/command_gated_zero0020/seed_005/trace.jsonl`
- pass_trace: `outputs/analysis/phase2_rate160_z0075_intermediate_push_seed5_trace/phase_mod_rate160/seed_005/trace.jsonl`
- output_trace: `outputs/analysis/phase2_command_gated_seed5_rate160_antilunge_relabel/seed_005/trace.jsonl`

## Gate

- indices: `[88, 46, 60, 74, 18]`
- threshold: `5.0`
- tick_window: `80-157`

## Summary

- selected_samples: `24`
- dataset_id: `7e03cac8eb74dd64`
- score_p50: `6.505734837043746`
- score_p95: `8.292117712565966`
- action_delta_p95: `0.12318237847648561`

## Manifest Entry

| source | ticks | samples | mode | mean_vx | pitch_p95 | base_min |
|---|---:|---:|---|---:|---:|---:|
| command_gated_seed5_rate160_antilunge_transfer | 80-157 | 24 | `seed5_rate160_antilunge_transfer` | 0.3357 | 1.3837 | -0.0058 |

## Interpretation

- This artifact is a data input for the next BC student only.
- It is not a candidate policy and is not promotable by itself.
- Gate seeds 0, 2, and 6 before any full promotion test.
