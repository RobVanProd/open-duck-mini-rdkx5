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
| `smoke_20260630T032116Z_gpu_2026_06_30_033004_40960` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0675 | `BELOW_MEASURED_ENVELOPE` | 0.1939 | NA | 0.0066 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033004_40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5504 | `BELOW_MEASURED_ENVELOPE` | 0.2177 | 0.2026 | 0.0162 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033254_81920` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1462 | `BELOW_MEASURED_ENVELOPE` | 0.1947 | NA | 0.0047 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033254_81920` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5486 | `BELOW_MEASURED_ENVELOPE` | 0.2175 | 0.2377 | 0.0190 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033316_122880` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1179 | `BELOW_MEASURED_ENVELOPE` | 0.1951 | NA | 0.0054 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033316_122880` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.4881 | `BELOW_MEASURED_ENVELOPE` | 0.2161 | 0.3016 | 0.0241 |

## Interesting Checkpoints

- `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T031718Z/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T031748Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260630T032116Z_gpu/2026_06_30_033316_122880.onnx` command `0.080`: vx `0.0241`, ratio `0.3016`, vel_p95 `1.4881`, tracking_p95 `0.2161`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260630T032116Z_gpu_2026_06_30_033316_122880` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.4881 | 0.2161 | 0.0000 | 0.3016 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033254_81920` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5486 | 0.2175 | 0.0000 | 0.2377 |
| `smoke_20260630T032116Z_gpu_2026_06_30_033004_40960` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5504 | 0.2177 | 0.0000 | 0.2026 |

### Hold Reasons

- `smoke_20260630T032116Z_gpu_2026_06_30_033316_122880`: command 0.08: HOLD_CANDIDATE_TRACKING
- `smoke_20260630T032116Z_gpu_2026_06_30_033254_81920`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2377 < 0.2500; command 0.08: mean vx 0.0190 < 0.0200
- `smoke_20260630T032116Z_gpu_2026_06_30_033004_40960`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2026 < 0.2500; command 0.08: mean vx 0.0162 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
