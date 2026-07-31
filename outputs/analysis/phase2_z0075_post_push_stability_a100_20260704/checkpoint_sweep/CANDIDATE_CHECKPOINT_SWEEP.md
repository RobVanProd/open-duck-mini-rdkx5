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
| `phase2_b0g_40960` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.1732 | `BELOW_MEASURED_ENVELOPE` | 0.2060 | NA | -0.0067 |
| `phase2_b0g_40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.3241 | `BELOW_MEASURED_ENVELOPE` | 0.3120 | 0.1001 | 0.0080 |
| `phase2_b0g_81920` | 0.000 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 50 | `duration_complete` | 1.2445 | `BELOW_MEASURED_ENVELOPE` | 0.1950 | NA | -0.0079 |
| `phase2_b0g_81920` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5179 | `BELOW_MEASURED_ENVELOPE` | 0.3120 | 0.0898 | 0.0072 |
| `phase2_b0g_122880` | 0.000 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 50 | `duration_complete` | 1.1975 | `BELOW_MEASURED_ENVELOPE` | 0.1876 | NA | -0.0073 |
| `phase2_b0g_122880` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.4520 | `BELOW_MEASURED_ENVELOPE` | 0.3065 | 0.0636 | 0.0051 |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `phase2_b0g_40960` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.3241 | 0.3120 | 0.0000 | 0.1001 |
| `phase2_b0g_81920` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.5179 | 0.3120 | 0.0000 | 0.0898 |
| `phase2_b0g_122880` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.4520 | 0.3065 | 0.0000 | 0.0636 |

### Hold Reasons

- `phase2_b0g_40960`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1001 < 0.2500; command 0.08: mean vx 0.0080 < 0.0200
- `phase2_b0g_81920`: command 0: HOLD_CANDIDATE_TARGET_VELOCITY; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0898 < 0.2500; command 0.08: mean vx 0.0072 < 0.0200
- `phase2_b0g_122880`: command 0: HOLD_CANDIDATE_TARGET_VELOCITY; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0636 < 0.2500; command 0.08: mean vx 0.0051 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
