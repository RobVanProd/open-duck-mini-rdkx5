# BC Trace Transition Spike Filter

status: `PASS_TRANSITION_SPIKE_FILTER_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces`
- vector_key: `action`
- joints: `['right_knee']`
- spike_velocity_rad_s: `3.75`
- transition_window_ticks: `2`
- drop_window_ticks: `1`
- output_mode: `rk_transition_spike_filtered`

## Summary

- traces: `8`
- samples_in: `4000`
- samples_out: `3124`
- samples_removed: `876`
- spike_ticks: `404`
- removed_contact_counts: `{'00': 2, '01': 7, '10': 406, '11': 461}`

| source | in | out | removed | transitions | spikes | spike_contacts | removed_contacts |
|---|---:|---:|---:|---:|---:|---|---|
| seed_000.jsonl | 500 | 392 | 108 | 138 | 52 | `{'10': 26, '11': 26}` | `{'10': 52, '11': 56}` |
| seed_001.jsonl | 500 | 387 | 113 | 135 | 52 | `{'10': 21, '11': 31}` | `{'10': 48, '11': 65}` |
| seed_002.jsonl | 500 | 395 | 105 | 124 | 47 | `{'10': 29, '11': 18}` | `{'10': 59, '11': 46}` |
| seed_003.jsonl | 500 | 388 | 112 | 143 | 52 | `{'00': 1, '10': 25, '11': 26}` | `{'00': 2, '01': 1, '10': 53, '11': 56}` |
| seed_004.jsonl | 500 | 393 | 107 | 123 | 48 | `{'10': 26, '11': 22}` | `{'01': 2, '10': 49, '11': 56}` |
| seed_005.jsonl | 500 | 386 | 114 | 122 | 55 | `{'10': 26, '11': 29}` | `{'01': 1, '10': 51, '11': 62}` |
| seed_006.jsonl | 500 | 386 | 114 | 139 | 53 | `{'10': 24, '11': 29}` | `{'01': 1, '10': 51, '11': 62}` |
| seed_007.jsonl | 500 | 397 | 103 | 122 | 45 | `{'10': 21, '11': 24}` | `{'01': 2, '10': 43, '11': 58}` |

## Gate

- This only creates a filtered dataset source.
- A pass here is not a policy pass.
- Rebuild the BC manifest and run the strict fitted-bridge candidate gate before drawing deployment conclusions.
