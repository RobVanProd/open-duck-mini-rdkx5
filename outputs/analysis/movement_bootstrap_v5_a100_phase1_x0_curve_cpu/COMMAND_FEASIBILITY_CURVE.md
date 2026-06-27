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
| 0.000 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.3714 | `BELOW_MEASURED_ENVELOPE` | 0.0830 | NA | 0.0049 | `outputs/analysis/movement_bootstrap_v5_a100_phase1_x0_curve_cpu/cmd_p0p000` |

## Interpretation

- No command in this sweep exceeded the measured velocity envelope.
- Treat this as a feasibility curve, not a deployability result. Robot validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass.
