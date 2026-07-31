# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_z0075_iter11_reverse_oracle_manifest.json`
- dataset_id: `f42cc71c5126b2bf`
- entries: `2`
- samples: `462`
- weighted_samples: `184.8000`

## Rules


## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_z0075_iter11_reverse_oracle_relabel/phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_001/trace.jsonl | 418 | 0.4000 | 167.2000 | `default` |
| phase2_z0075_iter11_reverse_oracle_relabel/phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_005/trace.jsonl | 44 | 0.4000 | 17.6000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
