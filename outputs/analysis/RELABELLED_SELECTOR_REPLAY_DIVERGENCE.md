# Selector Replay Divergence

status: `HOLD_REPLAY_DIVERGES_BEFORE_SELECTOR_WINDOW`

This compares bounded sequence replay traces against their source traces. It does not step simulation, train, deploy, SSH, run robot tests, or change runtime behavior.

| policy | seed | samples | prefix_end | action_err95 | pitch_err95 | height_err95 | vy_err95 | contact_mismatch_% | first_divergence |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| aec48152eb9eae44_trace_full_obs_foot | seed_000 | 250 | 154 | 0.1291 | 0.0845 | 0.0043 | 0.2286 | 19.2000 | `0` |
| aec48152eb9eae44_trace_full_obs_foot | seed_001 | 38 | 154 | 0.0000 | 0.4088 | 0.0409 | 1.1136 | 60.5263 | `0` |
| 5e3ac8cda5c15017_trace_full_obs_foot | seed_000 | 250 | 38 | 0.9771 | 0.1291 | 0.0095 | 0.1834 | 37.2000 | `0` |
| 5e3ac8cda5c15017_trace_full_obs_foot | seed_001 | 36 | 38 | 0.0000 | 0.3350 | 0.0395 | 1.1101 | 66.6667 | `0` |
| c7a94febd1c20ec4_trace_full_obs_foot | seed_000 | 250 | 72 | 0.8621 | 0.0398 | 0.0055 | 0.2034 | 32.8000 | `5` |
| c7a94febd1c20ec4_trace_full_obs_foot | seed_001 | 33 | 72 | 0.0000 | 0.3965 | 0.0365 | 1.2364 | 81.8182 | `0` |

## Interpretation

- Early divergence before `prefix_end` means open-loop prefix replay cannot reliably recreate the source state.
- If the replay diverges before the selector window, use state-aligned replay or a closed-loop selector before BC/export.
