# Phase 2 Swing Phase-Advance Next Recipe

status: `HOLD_PHASE_ADVANCE_HOOK_MISSING`
stage: `phase2_swing_phase_advance`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Diagnostic Input

- diagnostic: `outputs/analysis/phase2_swing_clearance_diagnostic_z0024.json`
- diagnostic_sha256: `daeb7caabf2ab47692dbf2ad6a9c3eb2e14db1e373811be1b8e0d9ceb1ee0018`
- verdict: `LATENCY_LIMITED`
- classification_counts: `{'LATENCY_LIMITED': 8}`
- selected_fix_branch: `phase-advance swing commands relative to the corrected 3-tick actuator delay`
- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- candidate_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0024`
- command_x: `0.08`
- max_rate_utilization_peak: `1.7949730157852173`
- mean_planted_pct_during_phase_swing: `88.0728216565956`

## Hook Audit

- status: `HOLD_PHASE_ADVANCE_HOOK_MISSING`
- hook_present: `False`
- joystick: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py`
- runner: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/runner.py`
- rewards: `/home/lsd/robots/Open_Duck_Playground/playground/common/rewards.py`

Existing hooks:

- forward_swing_clearance fires on first_contact using swing_peak_lift.
- forward_swing_advance fires on first_contact using swing_peak_forward_advance.
- forward_swing_balance penalizes one-sided swing usage.

Missing hook:

- A default-off phase-advanced swing objective that evaluates lift/advance against phase + advance_ticks before the measured 3-tick actuator delay.

## Recipe Intent

- Act on the LATENCY_LIMITED swing-clearance verdict, not on generic terrain or support failure.
- Advance the swing lift/advance objective by roughly the corrected 3-tick actuator delay.
- Keep bridge limits canonical; do not increase global target-rate allowance.
- Warm-start from the Phase 2 gain099 candidate/trainable checkpoint; do not train from scratch.
- Gate x=0.08 and x=0.0 on the corrected bridge after any implementation.

## Required Default-Off Hook

- `config`: `reward_config.forward_swing_phase_advance_ticks, default 0`
- `runner_cli`: `--forward_swing_phase_advance_ticks`
- `semantics`: `['Use phase-primary swing segmentation.', 'Compute the rewarded swing side from phase advanced by N control ticks.', 'Reward/penalize lift and forward advance before touchdown so lift starts before the measured actuator lag.', 'Report the configured advance ticks in training manifests and gate artifacts.']`
- `initial_values_to_test`: `[1, 2, 3]`
- `canonical_first_try`: `3`

## Acceptance After Hook

- Training manifests show forward_swing_phase_advance_ticks explicitly.
- No corrected per-joint velocity-limit excess at x=0.08.
- z=0.0024 x=0.08 and x=0.0 corrected-bridge gates remain 8/8.
- Gentle-push z=0.0024 regressions remain 8/8.
- Swing diagnostic rerun shows lower planted percentage during phase-commanded swing without higher rate utilization.

## Falsifiers

- If phase advance reduces planted swing but breaks x=0.0 command semantics, reject the candidate.
- If phase advance only improves clearance by exceeding corrected pitch-chain limits, reject the recipe.
- If ticks 1-3 all preserve latency-limited planted swing, return to structural gait-duration/knee-bend branch.
