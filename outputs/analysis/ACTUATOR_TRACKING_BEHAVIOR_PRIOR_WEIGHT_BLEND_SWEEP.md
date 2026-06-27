# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.0, 0.08]`
bridge_mode: `fitted`
duration_s: `1.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
min_promote_vx_m_s: `0.02`
min_promote_ratio: `0.25`
run: `True`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `step0` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.4147 | `BELOW_MEASURED_ENVELOPE` | 0.1904 | NA | 0.0042 |
| `step0` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.9323 | `BELOW_MEASURED_ENVELOPE` | 0.2233 | 0.2692 | 0.0215 |
| `step40960` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.6348 | `BELOW_MEASURED_ENVELOPE` | 0.1970 | NA | 0.0104 |
| `step40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.2288 | `BELOW_MEASURED_ENVELOPE` | 0.2182 | 0.1043 | 0.0083 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p0500` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.2771 | `BELOW_MEASURED_ENVELOPE` | 0.1868 | NA | 0.0049 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p0500` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.8523 | `BELOW_MEASURED_ENVELOPE` | 0.2217 | 0.3158 | 0.0253 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p1000` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.2078 | `BELOW_MEASURED_ENVELOPE` | 0.1852 | NA | 0.0047 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p1000` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.8671 | `BELOW_MEASURED_ENVELOPE` | 0.2204 | 0.2504 | 0.0200 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p2000` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.1000 | `BELOW_MEASURED_ENVELOPE` | 0.1856 | NA | 0.0043 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p2000` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.9040 | `BELOW_MEASURED_ENVELOPE` | 0.2206 | 0.3075 | 0.0246 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p3500` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.0518 | `BELOW_MEASURED_ENVELOPE` | 0.1867 | NA | 0.0046 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p3500` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.7879 | `BELOW_MEASURED_ENVELOPE` | 0.2189 | 0.2101 | 0.0168 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p5000` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.8077 | `BELOW_MEASURED_ENVELOPE` | 0.1877 | NA | 0.0050 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p5000` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.6619 | `BELOW_MEASURED_ENVELOPE` | 0.2160 | 0.1016 | 0.0081 |

## Interesting Checkpoints

- `outputs/analysis/actuator_tracking_behavior_prior_weight_blends/blend_alpha_0p0500.onnx` command `0.080`: vx `0.0253`, ratio `0.3158`, vel_p95 `1.8523`, tracking_p95 `0.2217`
- `outputs/analysis/actuator_tracking_behavior_prior_weight_blends/blend_alpha_0p2000.onnx` command `0.080`: vx `0.0246`, ratio `0.3075`, vel_p95 `1.9040`, tracking_p95 `0.2206`
- `outputs/analysis/colab_cli/open-duck-behavior-prior-a100-candidate-only-20260627T102348Z/extracted/open_duck_colab_cli_candidate-only_20260627T102437Z/open_duck_training_runs_cli/smoke_20260627T102504Z_gpu/2026_06_27_102952_0.onnx` command `0.080`: vx `0.0215`, ratio `0.2692`, vel_p95 `1.9323`, tracking_p95 `0.2233`
- `outputs/analysis/actuator_tracking_behavior_prior_weight_blends/blend_alpha_0p1000.onnx` command `0.080`: vx `0.0200`, ratio `0.2504`, vel_p95 `1.8671`, tracking_p95 `0.2204`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p0500` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.8523 | 0.2217 | 0.0000 | 0.3158 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p2000` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.9040 | 0.2206 | 0.0000 | 0.3075 |
| `step0` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.9323 | 0.2233 | 0.0000 | 0.2692 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p1000` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.8671 | 0.2204 | 0.0000 | 0.2504 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p3500` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.7879 | 0.2189 | 0.0000 | 0.2101 |
| `step40960` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.2288 | 0.2182 | 0.0000 | 0.1043 |
| `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p5000` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.6619 | 0.2160 | 0.0000 | 0.1016 |

### Hold Reasons

- `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p0500`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_TRACKING
- `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p2000`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_TRACKING
- `step0`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_TRACKING
- `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p1000`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_TRACKING
- `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p3500`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.2101 < 0.2500; command 0.08: mean vx 0.0168 < 0.0200
- `step40960`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1043 < 0.2500; command 0.08: mean vx 0.0083 < 0.0200
- `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p5000`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio 0.1016 < 0.2500; command 0.08: mean vx 0.0081 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
