# Command Feasibility Curve

Offline closed-loop command sweep. This does not SSH, deploy, train, or
touch the robot.

policy: `outputs/analysis/colab_cli/open-duck-a100-v5-staged-curriculum-20260623T181611Z/extracted/open_duck_colab_cli_staged-curriculum_20260623T181617Z/open_duck_staged_curriculum_cli/03_phase3_expand_toward_x008_fitted_bridge/smoke_20260623T183443Z_gpu/2026_06_23_184259_460800.onnx`
fit_json: `outputs/analysis/actuator_response_fit.json`
bridge_mode: `fitted`
duration_s: `5.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `True`

## Summary

| command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx | output |
|---:|---|---:|---|---:|---|---:|---:|---:|---|
| 0.000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 62 | `fall_or_nan` | 5.1573 | `ABOVE_MEASURED_ENVELOPE` | 0.2095 | NA | 0.2529 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p000` |
| 0.020 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 109 | `fall_or_nan` | 4.0802 | `ABOVE_MEASURED_ENVELOPE` | 0.1442 | 7.3145 | 0.1463 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p020` |
| 0.040 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 1.0697 | `BELOW_MEASURED_ENVELOPE` | 0.1012 | 0.0430 | 0.0017 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p040` |
| 0.060 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 1.2235 | `BELOW_MEASURED_ENVELOPE` | 0.0826 | 0.0376 | 0.0023 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p060` |
| 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 1.4159 | `BELOW_MEASURED_ENVELOPE` | 0.0783 | 0.0389 | 0.0031 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p080` |
| 0.100 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.8798 | `BELOW_MEASURED_ENVELOPE` | 0.0870 | 0.0525 | 0.0052 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p100` |
| 0.120 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 1.0454 | `BELOW_MEASURED_ENVELOPE` | 0.1212 | 0.0586 | 0.0070 | `outputs/analysis/movement_bootstrap_v5_a100_command_feasibility_curve_cpu/cmd_p0p120` |

## Interpretation

- First command with pitch-chain p95 target velocity above the measured envelope: `0.0`.
- Treat this as a feasibility curve, not a deployability result. Robot validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass.
