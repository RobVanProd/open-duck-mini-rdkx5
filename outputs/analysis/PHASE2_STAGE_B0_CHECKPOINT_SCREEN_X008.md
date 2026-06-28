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
| `smoke_20260628T075006Z_gpu_2026_06_28_035337_163840` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.6049 | `BELOW_MEASURED_ENVELOPE` | 0.1939 | 0.1752 | 0.0140 |
| `smoke_20260628T075006Z_gpu_2026_06_28_035542_327680` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.6030 | `BELOW_MEASURED_ENVELOPE` | 0.1915 | 0.1817 | 0.0145 |
| `smoke_20260628T075006Z_gpu_2026_06_28_035626_491520` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 1.6286 | `BELOW_MEASURED_ENVELOPE` | 0.1918 | 0.1898 | 0.0152 |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260628T075006Z_gpu_2026_06_28_035626_491520` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.6286 | 0.1918 | 0.0000 | 0.1898 |
| `smoke_20260628T075006Z_gpu_2026_06_28_035542_327680` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.6030 | 0.1915 | 0.0000 | 0.1817 |
| `smoke_20260628T075006Z_gpu_2026_06_28_035337_163840` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/1 | 1/1 | 1.6049 | 0.1939 | 0.0000 | 0.1752 |

### Hold Reasons

- `smoke_20260628T075006Z_gpu_2026_06_28_035626_491520`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1898 < 0.4000; command 0.08: mean vx 0.0152 < 0.0200
- `smoke_20260628T075006Z_gpu_2026_06_28_035542_327680`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1817 < 0.4000; command 0.08: mean vx 0.0145 < 0.0200
- `smoke_20260628T075006Z_gpu_2026_06_28_035337_163840`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1752 < 0.4000; command 0.08: mean vx 0.0140 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
