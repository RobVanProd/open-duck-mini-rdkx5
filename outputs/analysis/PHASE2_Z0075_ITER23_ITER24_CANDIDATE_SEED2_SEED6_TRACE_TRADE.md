# Phase 2 z0.0075 Iter23/Iter24 Candidate Seed2/Seed6 Trace Trade

status: `PASS_TRACE_TRADE_ANALYSIS_READY`

Offline trace comparison. No robot, SSH, deploy, grounded replay, runtime behavior change, or training was performed.

## Scope

- `iter23_candidate_*`: `policy/candidates/phase2_z0075_iter23_live_oracle_resetsettle10_history_context_rate150_20260704/candidate.onnx`, traced during iter24 live-oracle data collection.
- `iter24_candidate_*`: `policy/candidates/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_20260704/candidate.onnx`, traced after iter24 training.
- task: `rough_terrain_backlash`, command `x=0.08`, terrain hfield z scale `0.0075`, corrected fitted bridge, home-support reset settle `10`, pushes enabled.

## Summary

| case | samples | done | mean_vx | track_ratio | dx | pitch_p95 | pitch_max | height_min | single_support_pct | double_support_pct | sent_vel_p95 | sent_vel_max | tracking_p95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter23_candidate_seed2` | 282 | `True` | -0.0441 | -0.5509 | -0.1483 | 0.5337 | 1.4397 | 0.0646 | 22.0 | 78.0 | 1.4153 | 1.7971 | 0.0713 |
| `iter23_candidate_seed6` | 750 | `False` | 0.0265 | 0.3311 | 0.1154 | 0.1714 | 0.2290 | 0.1577 | 23.7 | 76.3 | 1.4321 | 1.7252 | 0.0719 |
| `iter24_candidate_seed2` | 750 | `False` | 0.0262 | 0.3278 | 0.1939 | 0.1822 | 0.2416 | 0.1590 | 24.0 | 76.0 | 1.4432 | 1.7868 | 0.0719 |
| `iter24_candidate_seed6` | 250 | `True` | -0.0453 | -0.5659 | -0.1337 | 0.5799 | 1.3745 | 0.0690 | 23.2 | 76.8 | 1.4001 | 1.6923 | 0.0712 |

## Interpretation

- Iter23 candidate: seed2 is the reverse/fall failure; seed6 is a full-duration pass.
- Iter24 candidate: seed2 becomes a full-duration pass; seed6 becomes the reverse/fall failure.
- The regressed seed6 failure is not an actuator-envelope problem: all-joint sent-target p95 remains around `1.40 rad/s`, max sent velocity remains below `1.70 rad/s`, and tracking p95 remains below `0.20 rad`.
- The failure signature is a seed-conditioned stability/recovery trade in the learned deployable map. The live-oracle aggregate is correcting the latest failed seed but is not preserving the previously recovered seed.

## Recommendation

Do not run robot validation. Before another full live-oracle iteration, adjust the next aggregate/training setup so seed2 recovery and seed6 recovery are both protected. A straight iter25 with only the latest aggregate risks continuing the seed2/seed6 whack-a-mole.
