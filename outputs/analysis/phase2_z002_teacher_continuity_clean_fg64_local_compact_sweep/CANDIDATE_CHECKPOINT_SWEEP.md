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
| `smoke_20260630T043450Z_gpu_2026_06_30_044434_40960` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0601 | `BELOW_MEASURED_ENVELOPE` | 0.1942 | NA | 0.0057 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044434_40960` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5646 | `BELOW_MEASURED_ENVELOPE` | 0.2200 | 0.2598 | 0.0208 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044727_81920` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1026 | `BELOW_MEASURED_ENVELOPE` | 0.1947 | NA | 0.0066 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044727_81920` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5218 | `BELOW_MEASURED_ENVELOPE` | 0.2174 | 0.3029 | 0.0242 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044749_122880` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1428 | `BELOW_MEASURED_ENVELOPE` | 0.1951 | NA | 0.0063 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044749_122880` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5089 | `BELOW_MEASURED_ENVELOPE` | 0.2175 | 0.3174 | 0.0254 |

## Interesting Checkpoints

- `outputs/analysis/colab_cli/open-duck-a100-clean-phase2-z002-teacher-continuity-20260630T043357Z/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T043420Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260630T043450Z_gpu/2026_06_30_044749_122880.onnx` command `0.080`: vx `0.0254`, ratio `0.3174`, vel_p95 `1.5089`, tracking_p95 `0.2175`
- `outputs/analysis/colab_cli/open-duck-a100-clean-phase2-z002-teacher-continuity-20260630T043357Z/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T043420Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260630T043450Z_gpu/2026_06_30_044727_81920.onnx` command `0.080`: vx `0.0242`, ratio `0.3029`, vel_p95 `1.5218`, tracking_p95 `0.2174`
- `outputs/analysis/colab_cli/open-duck-a100-clean-phase2-z002-teacher-continuity-20260630T043357Z/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T043420Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260630T043450Z_gpu/2026_06_30_044434_40960.onnx` command `0.080`: vx `0.0208`, ratio `0.2598`, vel_p95 `1.5646`, tracking_p95 `0.2200`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260630T043450Z_gpu_2026_06_30_044749_122880` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5089 | 0.2175 | 0.0000 | 0.3174 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044727_81920` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5218 | 0.2174 | 0.0000 | 0.3029 |
| `smoke_20260630T043450Z_gpu_2026_06_30_044434_40960` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5646 | 0.2200 | 0.0000 | 0.2598 |

### Hold Reasons

- `smoke_20260630T043450Z_gpu_2026_06_30_044749_122880`: command 0.08: HOLD_CANDIDATE_TRACKING
- `smoke_20260630T043450Z_gpu_2026_06_30_044727_81920`: command 0.08: HOLD_CANDIDATE_TRACKING
- `smoke_20260630T043450Z_gpu_2026_06_30_044434_40960`: command 0.08: HOLD_CANDIDATE_TRACKING

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
