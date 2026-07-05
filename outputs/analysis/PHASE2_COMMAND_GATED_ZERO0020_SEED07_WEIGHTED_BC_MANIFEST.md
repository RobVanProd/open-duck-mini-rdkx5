# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json`
- dataset_id: `716fd971d4b33945`
- entries: `10`
- samples: `7500`
- weighted_samples: `10500.0000`

## Rules

- `x008_gate.*seed_00[07].*` -> `3.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_000/trace.jsonl | 750 | 3.0000 | 2250.0000 | `x008_gate.*seed_00[07].*` |
| seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| seed_007/trace.jsonl | 750 | 3.0000 | 2250.0000 | `x008_gate.*seed_00[07].*` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
