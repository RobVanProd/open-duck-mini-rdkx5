# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.08]`
bridge_mode: `fitted`
duration_s: `15.0`
velocity_envelope_rad_s: `[2.0, 3.25]`
min_promote_vx_m_s: `0.02`
min_promote_ratio: `0.4`
run: `True`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `smoke_20260628T073620Z_gpu_2026_06_28_033952_163840` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.4199 | `BELOW_MEASURED_ENVELOPE` | 0.1615 | 0.0467 | 0.0037 |
| `smoke_20260628T073620Z_gpu_2026_06_28_034157_327680` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.4216 | `BELOW_MEASURED_ENVELOPE` | 0.0768 | 0.0059 | 0.0005 |
| `smoke_20260628T073620Z_gpu_2026_06_28_034241_491520` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.3632 | `BELOW_MEASURED_ENVELOPE` | 0.0728 | 0.0060 | 0.0005 |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260628T073620Z_gpu_2026_06_28_033952_163840` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.4199 | 0.1615 | 0.0000 | 0.0467 |
| `smoke_20260628T073620Z_gpu_2026_06_28_034241_491520` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 0.3632 | 0.0728 | 0.0000 | 0.0060 |
| `smoke_20260628T073620Z_gpu_2026_06_28_034157_327680` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 0.4216 | 0.0768 | 0.0000 | 0.0059 |

### Hold Reasons

- `smoke_20260628T073620Z_gpu_2026_06_28_033952_163840`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0467 < 0.4000; command 0.08: mean vx 0.0037 < 0.0200
- `smoke_20260628T073620Z_gpu_2026_06_28_034241_491520`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0060 < 0.4000; command 0.08: mean vx 0.0005 < 0.0200
- `smoke_20260628T073620Z_gpu_2026_06_28_034157_327680`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.0059 < 0.4000; command 0.08: mean vx 0.0005 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
