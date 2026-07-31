# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/pitch_chain_4p3_gate_aware_relabel_merged_manifest.json`
- dataset_id: `f08f5a4a84d67971`
- entries: `10`
- samples: `5000`
- weighted_samples: `16000.0000`

## Rules

- `gate_failure_relabel_source_vx_traces` -> `12.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| seed_001/trace.jsonl | 500 | 12.0000 | 6000.0000 | `gate_failure_relabel_source_vx_traces` |
| seed_004/trace.jsonl | 500 | 12.0000 | 6000.0000 | `gate_failure_relabel_source_vx_traces` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_000.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_001.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_002.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_003.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_004.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_005.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_006.jsonl | 500 | 1.0000 | 500.0000 | `default` |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_007.jsonl | 500 | 1.0000 | 500.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
