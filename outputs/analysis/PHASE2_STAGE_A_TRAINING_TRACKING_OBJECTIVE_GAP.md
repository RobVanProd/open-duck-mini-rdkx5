# Stage A Training Tracking Objective-Gap Audit

Status: **TRAINING_TRACKING_OBJECTIVE_GAP_CONFIRMED**

The training penalty and compact acceptance gate measure different quantities:

- training: `mean pseudo-Huber(sent_target - applied_target) across 14 joints`;
- gate: `max pitch-chain p95 abs(sent_target - actual_joint_position)`.

| experiment | step | x | status | bridge surrogate p95 max | joint gate p95 max | gap | ratio |
|---|---:|---:|---|---:|---:|---:|---:|
| `no_prior` | 81,920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 0.0910 | 0.1907 | 0.0997 | 2.10 |
| `no_prior` | 81,920 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1023 | 0.2121 | 0.1098 | 2.07 |
| `no_prior` | 163,840 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 0.0921 | 0.1905 | 0.0985 | 2.07 |
| `no_prior` | 163,840 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 0.0992 | 0.2169 | 0.1177 | 2.19 |
| `no_prior` | 245,760 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 0.0939 | 0.1918 | 0.0979 | 2.04 |
| `no_prior` | 245,760 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 0.0996 | 0.2164 | 0.1169 | 2.17 |
| `progress_failure` | 81,920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 0.0906 | 0.1990 | 0.1084 | 2.20 |
| `progress_failure` | 81,920 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0953 | 0.2143 | 0.1190 | 2.25 |
| `progress_failure` | 163,840 | 0.00 | `HOLD_CANDIDATE_TRACKING` | 0.0939 | 0.2038 | 0.1100 | 2.17 |
| `progress_failure` | 163,840 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 0.0989 | 0.2162 | 0.1173 | 2.19 |
| `progress_failure` | 245,760 | 0.00 | `HOLD_CANDIDATE_TRACKING` | 0.0954 | 0.2095 | 0.1141 | 2.20 |
| `progress_failure` | 245,760 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1006 | 0.2166 | 0.1160 | 2.15 |

## Summary

- evaluations: `12`
- bridge-surrogate pass but joint-gate fail: `8`
- unmodeled gap mean/range: `0.1104` / `[0.0979, 0.1190]` rad
- gate/surrogate ratio mean/range: `2.15` / `[2.04, 2.25]`

## Decision

The existing actuator-tracking reward is not evidence that the compact joint-tracking constraint is optimized. Do not tune its scalar as a substitute. Any next training hypothesis must first define and wire a direct actual-joint tracking surrogate, then pass a CPU-only contract check before preregistered training.

No training, deployment, robot access, or GPU use was authorized or performed.
