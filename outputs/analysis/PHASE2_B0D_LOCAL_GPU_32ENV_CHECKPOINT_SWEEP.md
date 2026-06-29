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
| `smoke_20260629T075706Z_gpu_2026_06_29_040028_20480` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0937 | `BELOW_MEASURED_ENVELOPE` | 0.1936 | NA | 0.0058 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040028_20480` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5725 | `BELOW_MEASURED_ENVELOPE` | 0.2208 | 0.2475 | 0.0198 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040220_40960` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.1807 | `BELOW_MEASURED_ENVELOPE` | 0.1936 | NA | 0.0060 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040220_40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5795 | `BELOW_MEASURED_ENVELOPE` | 0.2189 | 0.2452 | 0.0196 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040251_61440` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.2404 | `BELOW_MEASURED_ENVELOPE` | 0.1943 | NA | 0.0055 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040251_61440` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5850 | `BELOW_MEASURED_ENVELOPE` | 0.2199 | 0.2575 | 0.0206 |

## Interesting Checkpoints

- `outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu/2026_06_29_040251_61440.onnx` command `0.080`: vx `0.0206`, ratio `0.2575`, vel_p95 `1.5850`, tracking_p95 `0.2199`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `smoke_20260629T075706Z_gpu_2026_06_29_040251_61440` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5850 | 0.2199 | 0.0000 | 0.2575 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040028_20480` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5725 | 0.2208 | 0.0000 | 0.2475 |
| `smoke_20260629T075706Z_gpu_2026_06_29_040220_40960` | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 1/2 | 2/2 | 1.5795 | 0.2189 | 0.0000 | 0.2452 |

### Hold Reasons

- `smoke_20260629T075706Z_gpu_2026_06_29_040251_61440`: command 0.08: HOLD_CANDIDATE_TRACKING
- `smoke_20260629T075706Z_gpu_2026_06_29_040028_20480`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2475 < 0.2500; command 0.08: mean vx 0.0198 < 0.0200
- `smoke_20260629T075706Z_gpu_2026_06_29_040220_40960`: command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2452 < 0.2500; command 0.08: mean vx 0.0196 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
