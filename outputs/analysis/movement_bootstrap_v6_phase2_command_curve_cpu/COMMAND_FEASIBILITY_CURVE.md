# Command Feasibility Curve

Offline closed-loop command sweep. This does not SSH, deploy, train, or
touch the robot.

policy: `outputs/analysis/colab_cli/open-duck-a100-v6-staged-curriculum-20260623T194912Z/extracted/open_duck_colab_cli_staged-curriculum_20260623T194923Z/open_duck_staged_curriculum_cli/02_phase2_stabilize_motion_low_step/smoke_20260623T195927Z_gpu/2026_06_23_200742_307200.onnx`
fit_json: `outputs/analysis/actuator_response_fit.json`
bridge_mode: `fitted`
duration_s: `15.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `True`

## Summary

| command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx | output |
|---:|---|---:|---|---:|---|---:|---:|---:|---|
| 0.060 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.1741 | `BELOW_MEASURED_ENVELOPE` | 0.0570 | 0.0079 | 0.0005 | `outputs/analysis/movement_bootstrap_v6_phase2_command_curve_cpu/cmd_p0p060` |
| 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.1390 | `BELOW_MEASURED_ENVELOPE` | 0.0620 | 0.0121 | 0.0010 | `outputs/analysis/movement_bootstrap_v6_phase2_command_curve_cpu/cmd_p0p080` |

## Interpretation

- No command in this sweep exceeded the measured velocity envelope.
- Treat this as a feasibility curve, not a deployability result. Robot validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass.
