# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `39e6cf5915c9e175`
- entries: `8`
- samples: `1651`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_008.jsonl | 0-499 | 500 | `True` | 0.0315 | 0.3941 | 2.2935 | 0.1820 | 0.0594 | 0.1487 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_009.jsonl | 0-33 | 34 | `True` | -0.4207 | -5.2590 | 1.6764 | 0.1577 | 1.4243 | 0.0615 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_010.jsonl | 0-499 | 500 | `True` | 0.0336 | 0.4204 | 2.2931 | 0.1830 | 0.0607 | 0.1514 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_011.jsonl | 0-499 | 500 | `True` | 0.0322 | 0.4020 | 2.2689 | 0.1821 | 0.0709 | 0.1587 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_012.jsonl | 0-36 | 37 | `True` | -0.3917 | -4.8958 | 1.8007 | 0.1611 | 1.3979 | 0.0629 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_013.jsonl | 0-21 | 22 | `True` | 0.0185 | 0.2317 | 2.3719 | 0.1954 | 0.2191 | 0.0854 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_014.jsonl | 0-36 | 37 | `True` | -0.0770 | -0.9624 | 2.4441 | 0.1547 | 0.2023 | 0.0752 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_015.jsonl | 0-20 | 21 | `True` | -0.0201 | -0.2512 | 2.2059 | 0.1678 | 0.0942 | 0.0673 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
