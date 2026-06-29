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
| `smoke_20260629T062042Z_gpu_2026_06_29_022725_245760` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.2426 | `BELOW_MEASURED_ENVELOPE` | 0.1941 | NA | 0.0056 |
| `smoke_20260629T062042Z_gpu_2026_06_29_022725_245760` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5503 | `BELOW_MEASURED_ENVELOPE` | 0.2199 | 0.3035 | 0.0243 |

## Interesting Checkpoints

- `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760.onnx` command `0.080`: vx `0.0243`, ratio `0.3035`, vel_p95 `1.5503`, tracking_p95 `0.2199`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260629T062042Z_gpu_2026_06_29_022725_245760` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5503 | 0.2199 | 0.0000 | 0.3035 |

### Hold Reasons

- `smoke_20260629T062042Z_gpu_2026_06_29_022725_245760`: command 0.08: HOLD_CANDIDATE_TRACKING

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
