# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.0, 0.08]`
bridge_mode: `fitted`
duration_s: `1.0`
velocity_envelope_rad_s: `[2.0, 3.25]`
min_promote_vx_m_s: `0.02`
min_promote_ratio: `0.25`
run: `True`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `smoke_20260629T201321Z_gpu_2026_06_29_202411_40960` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1686 | `BELOW_MEASURED_ENVELOPE` | 0.1914 | NA | 0.0072 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202411_40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4355 | `BELOW_MEASURED_ENVELOPE` | 0.2132 | 0.1663 | 0.0133 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202800_81920` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1666 | `BELOW_MEASURED_ENVELOPE` | 0.1914 | NA | 0.0060 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202800_81920` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4369 | `BELOW_MEASURED_ENVELOPE` | 0.2130 | 0.1730 | 0.0138 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202842_122880` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1596 | `BELOW_MEASURED_ENVELOPE` | 0.1918 | NA | 0.0060 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202842_122880` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4361 | `BELOW_MEASURED_ENVELOPE` | 0.2132 | 0.1699 | 0.0136 |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260629T201321Z_gpu_2026_06_29_202800_81920` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4369 | 0.2130 | 0.0000 | 0.1730 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202842_122880` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4361 | 0.2132 | 0.0000 | 0.1699 |
| `smoke_20260629T201321Z_gpu_2026_06_29_202411_40960` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4355 | 0.2132 | 0.0000 | 0.1663 |

### Hold Reasons

- `smoke_20260629T201321Z_gpu_2026_06_29_202800_81920`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1730 < 0.2500; command 0.08: mean vx 0.0138 < 0.0200
- `smoke_20260629T201321Z_gpu_2026_06_29_202842_122880`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1699 < 0.2500; command 0.08: mean vx 0.0136 < 0.0200
- `smoke_20260629T201321Z_gpu_2026_06_29_202411_40960`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1663 < 0.2500; command 0.08: mean vx 0.0133 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
