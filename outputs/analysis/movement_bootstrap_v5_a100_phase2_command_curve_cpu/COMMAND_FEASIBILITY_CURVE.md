# Command Feasibility Curve

Offline closed-loop command sweep. This does not SSH, deploy, train, or
touch the robot.

policy: `outputs/analysis/colab_cli/open-duck-a100-v5-staged-curriculum-20260623T181611Z/extracted/open_duck_colab_cli_staged-curriculum_20260623T181617Z/open_duck_staged_curriculum_cli/02_phase2_feasible_low_command_fitted_bridge/smoke_20260623T182616Z_gpu/2026_06_23_183432_460800.onnx`
fit_json: `outputs/analysis/actuator_response_fit.json`
bridge_mode: `fitted`
duration_s: `5.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `True`

## Summary

| command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx | output |
|---:|---|---:|---|---:|---|---:|---:|---:|---|
| 0.040 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 1.0249 | `BELOW_MEASURED_ENVELOPE` | 0.0666 | 0.0645 | 0.0026 | `outputs/analysis/movement_bootstrap_v5_a100_phase2_command_curve_cpu/cmd_p0p040` |
| 0.060 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.6551 | `BELOW_MEASURED_ENVELOPE` | 0.0699 | 0.0499 | 0.0030 | `outputs/analysis/movement_bootstrap_v5_a100_phase2_command_curve_cpu/cmd_p0p060` |
| 0.080 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 61 | `fall_or_nan` | 4.1595 | `ABOVE_MEASURED_ENVELOPE` | 0.2392 | 3.2855 | 0.2628 | `outputs/analysis/movement_bootstrap_v5_a100_phase2_command_curve_cpu/cmd_p0p080` |

## Interpretation

- First command with pitch-chain p95 target velocity above the measured envelope: `0.08`.
- Treat this as a feasibility curve, not a deployability result. Robot validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass.
