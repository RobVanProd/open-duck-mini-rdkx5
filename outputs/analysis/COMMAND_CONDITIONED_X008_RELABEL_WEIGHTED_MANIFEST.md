# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/command_conditioned_x008_relabel_merged_manifest.json`
- dataset_id: `547172c400c25c49`
- entries: `21`
- samples: `11250`
- weighted_samples: `13250.0000`

## Rules

- `command_conditioned_x008_relabel_seed0_seed5_traces` -> `3.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| seed_000/trace.jsonl | 500 | 3.0000 | 1500.0000 | `command_conditioned_x008_relabel_seed0_seed5_traces` |
| seed_000/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_001/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_002/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_003/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_004/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_005/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_005/trace.jsonl | 500 | 3.0000 | 1500.0000 | `command_conditioned_x008_relabel_seed0_seed5_traces` |
| seed_006/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_007/trace.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_000.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_001.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_002.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_003.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_004.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_005.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_006.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_007.jsonl | 500 | 1.0000 | 500.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
