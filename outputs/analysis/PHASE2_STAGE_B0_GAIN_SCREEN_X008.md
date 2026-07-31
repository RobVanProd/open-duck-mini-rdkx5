# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.08]`
bridge_mode: `fitted`
duration_s: `15.0`
velocity_envelope_rad_s: `[2.0, 3.25]`
min_promote_vx_m_s: `0.02`
min_promote_ratio: `0.35`
run: `True`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `phase2_stage_b0_491k_action_gain_b0_491k_gain105` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.6641 | `BELOW_MEASURED_ENVELOPE` | 0.1925 | 0.2176 | 0.0174 |
| `phase2_stage_b0_491k_action_gain_b0_491k_gain110` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.7030 | `BELOW_MEASURED_ENVELOPE` | 0.1911 | 0.2083 | 0.0167 |
| `phase2_stage_b0_491k_action_gain_b0_491k_gain115` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.2245 | `BELOW_MEASURED_ENVELOPE` | 0.1164 | 0.0219 | 0.0018 |
| `phase2_stage_b0_491k_action_gain_b0_491k_gain120` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.5958 | `BELOW_MEASURED_ENVELOPE` | 0.0911 | 0.0096 | 0.0008 |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `phase2_stage_b0_491k_action_gain_b0_491k_gain105` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.6641 | 0.1925 | 0.0000 | 0.2176 |
| `phase2_stage_b0_491k_action_gain_b0_491k_gain110` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.7030 | 0.1911 | 0.0000 | 0.2083 |
| `phase2_stage_b0_491k_action_gain_b0_491k_gain115` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.2245 | 0.1164 | 0.0000 | 0.0219 |
| `phase2_stage_b0_491k_action_gain_b0_491k_gain120` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 0.5958 | 0.0911 | 0.6667 | 0.0096 |

### Hold Reasons

- `phase2_stage_b0_491k_action_gain_b0_491k_gain105`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2176 < 0.3500; command 0.08: mean vx 0.0174 < 0.0200
- `phase2_stage_b0_491k_action_gain_b0_491k_gain110`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2083 < 0.3500; command 0.08: mean vx 0.0167 < 0.0200
- `phase2_stage_b0_491k_action_gain_b0_491k_gain115`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0219 < 0.3500; command 0.08: mean vx 0.0018 < 0.0200
- `phase2_stage_b0_491k_action_gain_b0_491k_gain120`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0096 < 0.3500; command 0.08: mean vx 0.0008 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
