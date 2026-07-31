# Command Feasibility Curve

Offline closed-loop command sweep. This does not SSH, deploy, train, or
touch the robot.

policy: `policy/BEST_WALK_ONNX_2.onnx`
fit_json: `outputs/analysis/actuator_response_fit.json`
bridge_mode: `fitted`
duration_s: `5.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `True`

## Summary

| command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx | output |
|---:|---|---:|---|---:|---|---:|---:|---:|---|
| 0.000 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.5331 | `BELOW_MEASURED_ENVELOPE` | 0.0629 | NA | 0.0014 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p000` |
| 0.020 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.5229 | `BELOW_MEASURED_ENVELOPE` | 0.0645 | 0.0628 | 0.0013 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p020` |
| 0.040 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.6609 | `BELOW_MEASURED_ENVELOPE` | 0.0624 | 0.0366 | 0.0015 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p040` |
| 0.060 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.7821 | `BELOW_MEASURED_ENVELOPE` | 0.0940 | 0.0296 | 0.0018 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p060` |
| 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 4.7277 | `ABOVE_MEASURED_ENVELOPE` | 0.2171 | 0.2155 | 0.0172 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p080` |
| 0.100 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 5.2400 | `ABOVE_MEASURED_ENVELOPE` | 0.2403 | 0.3647 | 0.0365 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p100` |
| 0.120 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 5.2400 | `ABOVE_MEASURED_ENVELOPE` | 0.2459 | 0.3746 | 0.0449 | `outputs/analysis/best_walk_command_feasibility_curve_cpu/cmd_p0p120` |

## Interpretation

- First command with pitch-chain p95 target velocity above the measured envelope: `0.08`.
- Treat this as a feasibility curve, not a deployability result. Robot validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass.
