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
| `smoke_20260702T225504Z_gpu_2026_07_02_230416_40960` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0783 | `BELOW_MEASURED_ENVELOPE` | 0.1918 | NA | 0.0065 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230416_40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4191 | `BELOW_MEASURED_ENVELOPE` | 0.2138 | 0.2339 | 0.0187 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230713_81920` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0524 | `BELOW_MEASURED_ENVELOPE` | 0.1923 | NA | 0.0065 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230713_81920` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4132 | `BELOW_MEASURED_ENVELOPE` | 0.2113 | 0.1660 | 0.0133 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230734_122880` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1139 | `BELOW_MEASURED_ENVELOPE` | 0.1926 | NA | 0.0061 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230734_122880` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4296 | `BELOW_MEASURED_ENVELOPE` | 0.2160 | 0.1684 | 0.0135 |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260702T225504Z_gpu_2026_07_02_230416_40960` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4191 | 0.2138 | 0.0000 | 0.2339 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230734_122880` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4296 | 0.2160 | 0.0000 | 0.1684 |
| `smoke_20260702T225504Z_gpu_2026_07_02_230713_81920` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4132 | 0.2113 | 0.0000 | 0.1660 |

### Hold Reasons

- `smoke_20260702T225504Z_gpu_2026_07_02_230416_40960`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2339 < 0.2500; command 0.08: mean vx 0.0187 < 0.0200
- `smoke_20260702T225504Z_gpu_2026_07_02_230734_122880`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1684 < 0.2500; command 0.08: mean vx 0.0135 < 0.0200
- `smoke_20260702T225504Z_gpu_2026_07_02_230713_81920`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1660 < 0.2500; command 0.08: mean vx 0.0133 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
