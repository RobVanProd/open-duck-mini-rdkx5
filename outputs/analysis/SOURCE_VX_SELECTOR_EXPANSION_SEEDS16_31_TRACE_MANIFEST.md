# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `7ebbf93c49a92c8c`
- entries: `16`
- samples: `5652`
- bc_ready_entries: `16`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_016.jsonl | 0-499 | 500 | `True` | 0.0320 | 0.4005 | 2.3134 | 0.1809 | 0.0753 | 0.1594 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_017.jsonl | 0-499 | 500 | `True` | 0.0316 | 0.3947 | 2.2873 | 0.1793 | 0.0623 | 0.1549 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_018.jsonl | 0-499 | 500 | `True` | 0.0375 | 0.4686 | 2.2734 | 0.1815 | 0.0581 | 0.1534 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_019.jsonl | 0-23 | 24 | `True` | 0.0254 | 0.3170 | 2.4860 | 0.2269 | 0.1187 | 0.0726 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_020.jsonl | 0-26 | 27 | `True` | 0.1082 | 1.3528 | 2.4233 | 0.1975 | 0.3611 | 0.0720 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_021.jsonl | 0-499 | 500 | `True` | 0.0286 | 0.3581 | 2.3228 | 0.1791 | 0.0606 | 0.1540 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_022.jsonl | 0-499 | 500 | `True` | 0.0322 | 0.4028 | 2.3067 | 0.1818 | 0.0575 | 0.1549 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_023.jsonl | 0-499 | 500 | `True` | 0.0264 | 0.3305 | 2.2873 | 0.1807 | 0.0944 | 0.1546 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_024.jsonl | 0-499 | 500 | `True` | 0.0378 | 0.4724 | 2.3020 | 0.1791 | 0.0546 | 0.1542 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_025.jsonl | 0-22 | 23 | `True` | -0.3532 | -4.4149 | 2.1574 | 0.1228 | 0.5745 | 0.1132 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_026.jsonl | 0-32 | 33 | `True` | 0.0183 | 0.2285 | 2.7254 | 0.1709 | 0.0914 | 0.0745 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_027.jsonl | 0-499 | 500 | `True` | 0.0315 | 0.3939 | 2.2873 | 0.1815 | 0.0638 | 0.1579 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_028.jsonl | 0-44 | 45 | `True` | -0.0141 | -0.1766 | 2.2412 | 0.1723 | 0.1523 | 0.0718 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_029.jsonl | 0-499 | 500 | `True` | 0.0315 | 0.3937 | 2.2918 | 0.1806 | 0.0592 | 0.1559 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_030.jsonl | 0-499 | 500 | `True` | 0.0292 | 0.3646 | 2.3299 | 0.1828 | 0.0611 | 0.1571 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_031.jsonl | 0-499 | 500 | `True` | 0.0324 | 0.4055 | 2.2983 | 0.1793 | 0.0614 | 0.1556 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
