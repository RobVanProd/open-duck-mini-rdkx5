# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_snippet_augmented_manifest.json`
- dataset_id: `9f4ba6b1c342d17b`
- entries: `74`
- samples: `51294`
- weighted_samples: `51889.0000`

## Rules

- `phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets` -> `6.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets/seed_000/push_000_70c15afbddc5679d.jsonl | 90 | 6.0000 | 540.0000 | `phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets` |
| analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets/seed_000/push_001_52fa7376aaf9cfc5.jsonl | 29 | 6.0000 | 174.0000 | `phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 501 | 1.0000 | 501.0000 | `default` |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_000/trace.jsonl | 110 | 1.0000 | 110.0000 | `default` |
| rollouts_x008/student/seed_001/trace.jsonl | 560 | 1.0000 | 560.0000 | `default` |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_002/trace.jsonl | 643 | 1.0000 | 643.0000 | `default` |
| rollouts_x008/student/seed_003/trace.jsonl | 85 | 1.0000 | 85.0000 | `default` |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_004/trace.jsonl | 478 | 1.0000 | 478.0000 | `default` |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_005/trace.jsonl | 48 | 1.0000 | 48.0000 | `default` |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
