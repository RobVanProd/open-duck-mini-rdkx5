# Command Feasibility Curve

Offline closed-loop command sweep. This does not SSH, deploy, train, or
touch the robot.

policy: `outputs/analysis/colab_cli/open-duck-a100-v5-staged-curriculum-20260623T181611Z/extracted/open_duck_colab_cli_staged-curriculum_20260623T181617Z/open_duck_staged_curriculum_cli/01_phase1_feasible_low_command_mild_bridge/smoke_20260623T181701Z_gpu/2026_06_23_182604_368640.onnx`
fit_json: `outputs/analysis/actuator_response_fit.json`
bridge_mode: `fitted`
duration_s: `5.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `True`

## Summary

| command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx | output |
|---:|---|---:|---|---:|---|---:|---:|---:|---|
| 0.040 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.2780 | `BELOW_MEASURED_ENVELOPE` | 0.0670 | 0.0455 | 0.0018 | `outputs/analysis/movement_bootstrap_v5_a100_phase1_command_curve_cpu/cmd_p0p040` |
| 0.060 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.3107 | `BELOW_MEASURED_ENVELOPE` | 0.0708 | 0.0459 | 0.0028 | `outputs/analysis/movement_bootstrap_v5_a100_phase1_command_curve_cpu/cmd_p0p060` |
| 0.080 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 80 | `fall_or_nan` | 1.9529 | `BELOW_MEASURED_ENVELOPE` | 0.1429 | 2.3652 | 0.1892 | `outputs/analysis/movement_bootstrap_v5_a100_phase1_command_curve_cpu/cmd_p0p080` |

## Interpretation

- No command in this sweep exceeded the measured velocity envelope.
- Treat this as a feasibility curve, not a deployability result. Robot validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass.
