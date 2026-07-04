# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_z0075_iter12_iter10_pass_control_manifest.json`
- dataset_id: `5f61f95b64a3c3f9`
- entries: `3`
- samples: `2250`
- weighted_samples: `9000.0000`

## Rules


## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| analysis/phase2_z0075_iter12_iter10_pass_control_traces/iter10_spike_local_rate150/seed_000/trace.jsonl | 750 | 4.0000 | 3000.0000 | `default` |
| analysis/phase2_z0075_iter12_iter10_pass_control_traces/iter10_spike_local_rate150/seed_004/trace.jsonl | 750 | 4.0000 | 3000.0000 | `default` |
| analysis/phase2_z0075_iter12_iter10_pass_control_traces/iter10_spike_local_rate150/seed_007/trace.jsonl | 750 | 4.0000 | 3000.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
