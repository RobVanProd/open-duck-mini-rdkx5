# Right-Knee Rate-Limit Curation Sweep

status: `HOLD_RIGHT_KNEE_RATE_LIMIT_CURATION_NOT_ROBOT_READY`

## Summary

| limit | changed_ticks | dataset_id | smoke_status | smoke_complete | smoke_moving | smoke_track_ratio | smoke_sent_p95_max | smoke_tracking_p95_max | strict_status | strict_complete | strict_moving | strict_track_ratio | strict_sent_p95_max | strict_tracking_p95_max |
|---|---:|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| uncurated | 0 | `original` | `PASS_BC_FIT_SMOKE_FORWARD_REPLAY` | 8 | 8 | 0.5833 | 2.2134 | 0.1843 | `HOLD_EXACT_BLEND_ONNX_RIGHT_KNEE_RATE_TRACKING` | 8 | 8 | 0.5768 | 5.1118 | 0.2800 |
| 4.7 | 408 | `80c1b243ae91154e` | `PASS_BC_FIT_SMOKE_FORWARD_REPLAY` | 8 | 8 | 0.5922 | 2.2247 | 0.1841 | `not_run` | NA | NA | NA | NA | NA |
| 4.3 | 493 | `301851591b7988f1` | `PASS_BC_FIT_SMOKE_FORWARD_REPLAY` | 8 | 8 | 0.5927 | 2.2216 | 0.1845 | `HOLD_STRICT_EVAL_TARGET_VELOCITY_GATE` | 8 | 8 | 0.5992 | 4.2994 | 0.2773 |
| 4.0 | 642 | `18356a4d75aabe60` | `HOLD_BC_REPLAY_TERMINATED` | 7 | 7 | 0.1789 | 2.2236 | 0.1841 | `not_run` | NA | NA | NA | NA | NA |
| 3.75 | 739 | `d00ca78f667676e1` | `HOLD_BC_REPLAY_TERMINATED` | 7 | 7 | 0.2091 | 2.2047 | 0.1824 | `not_run` | NA | NA | NA | NA | NA |

## Failed Smoke Seeds

- uncurated: `[]`
- 4.7: `[]`
- 4.3: `[]`
- 4.0: `['seed_005']`
- 3.75: `['seed_005']`

## Changed Contact Counts

- 4.7: `{'10': 199, '11': 209}`
- 4.3: `{'10': 216, '11': 277}`
- 4.0: `{'00': 1, '01': 6, '10': 277, '11': 358}`
- 3.75: `{'00': 1, '01': 6, '10': 351, '11': 381}`

## Interpretation

- The teacher/source selector traces contain right-knee action discontinuities; offline curation can limit those action deltas before BC export.
- Hard limits at 4.0 and 3.75 rad/s break the smoke replay, primarily by terminating seed 5; they are too aggressive for this trace family.
- Softer right-knee caps at 4.7 and 4.3 rad/s preserve 8/8 smoke forward replay.
- The strongest passing cap, 4.3 rad/s, still fails the strict ONNX multi-seed fitted-backlash gate: all seeds move and complete, but right_knee remains both the fastest and worst-tracking pitch-chain joint, with p95 sent velocity around 4.20-4.30 rad/s and p95 tracking around 0.27 rad.
- Compared with the uncurated strict ONNX summary, 4.3 reduces max pitch-chain sent-target p95 from about 5.11 to 4.30 rad/s while preserving forward motion, but it does not reach the conservative 2.5 rad/s gate or the 3.75 rad/s fitted-envelope check.
- This confirms right-knee discontinuities are a real source issue, but simple one-joint rate curation is not sufficient to produce a robot-ready policy.
- No robot motion, SSH, deploy, runtime behavior change, or training was performed.

recommended_next: `re-curate the teacher/source data with a dynamics-aware method instead of hard one-joint action clipping; inspect right-knee phase/contact discontinuities and consider source-window rejection or multi-joint smoothing before another ONNX export.`
