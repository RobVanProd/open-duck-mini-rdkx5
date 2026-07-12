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
| `smoke_20260711T234701Z_gpu_2026_07_11_235724_81920` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.9912 | `BELOW_MEASURED_ENVELOPE` | 0.1906 | NA | 0.0056 |
| `smoke_20260711T234701Z_gpu_2026_07_11_235724_81920` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5496 | `BELOW_MEASURED_ENVELOPE` | 0.2127 | 0.2196 | 0.0176 |
| `smoke_20260711T234701Z_gpu_2026_07_12_000047_163840` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0036 | `BELOW_MEASURED_ENVELOPE` | 0.1907 | NA | 0.0057 |
| `smoke_20260711T234701Z_gpu_2026_07_12_000047_163840` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5620 | `BELOW_MEASURED_ENVELOPE` | 0.2178 | 0.2796 | 0.0224 |
| `smoke_20260711T234701Z_gpu_2026_07_12_000115_245760` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1983 | `BELOW_MEASURED_ENVELOPE` | 0.1920 | NA | 0.0055 |
| `smoke_20260711T234701Z_gpu_2026_07_12_000115_245760` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5399 | `BELOW_MEASURED_ENVELOPE` | 0.2170 | 0.2651 | 0.0212 |

## Interesting Checkpoints

- `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T234701Z_gpu/2026_07_12_000047_163840.onnx` command `0.080`: vx `0.0224`, ratio `0.2796`, vel_p95 `1.5620`, tracking_p95 `0.2178`
- `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T234701Z_gpu/2026_07_12_000115_245760.onnx` command `0.080`: vx `0.0212`, ratio `0.2651`, vel_p95 `1.5399`, tracking_p95 `0.2170`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260711T234701Z_gpu_2026_07_12_000047_163840` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5620 | 0.2178 | 0.0000 | 0.2796 |
| `smoke_20260711T234701Z_gpu_2026_07_12_000115_245760` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5399 | 0.2170 | 0.0000 | 0.2651 |
| `smoke_20260711T234701Z_gpu_2026_07_11_235724_81920` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5496 | 0.2127 | 0.0000 | 0.2196 |

### Hold Reasons

- `smoke_20260711T234701Z_gpu_2026_07_12_000047_163840`: command 0.08: HOLD_CANDIDATE_TRACKING
- `smoke_20260711T234701Z_gpu_2026_07_12_000115_245760`: command 0.08: HOLD_CANDIDATE_TRACKING
- `smoke_20260711T234701Z_gpu_2026_07_11_235724_81920`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2196 < 0.2500; command 0.08: mean vx 0.0176 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
