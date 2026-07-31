# V13 Training-Reward Replay Summary

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

## Purpose

After the V13 A100 phase-1 gate, the original candidate-gate reward table was
misleading because the closed-loop evaluator used default Playground reward
settings and did not replay the command-progress termination path. The evaluator
was updated to:

- load staged-plan reward overrides with `--reward-overrides-json`
- apply reward scales, command-progress failure settings, and clip bounds
- call `_update_command_window_progress()`
- call `_get_command_progress_failure()`
- clip reward using the env reward config instead of hardcoded `[0, 10000]`

This summary records the replay of the V13 phase-1 ONNX under the full V13
phase-1 training reward settings.

Note: the first reward replay exposed a plan-manifest issue: the staged-plan JSON
omitted several core phase fields such as `tracking_lin_vel_scale`,
`alive_scale`, and `target_rate_scale`, and it did not record the hardcoded
`tracking_ang_vel_scale=0.0` training flag. The planner now writes the full
phase dataclass payload plus the reward-relevant hardcoded command settings, and
this result uses that corrected manifest.

## Command

```bash
JAX_PLATFORMS=cpu ../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --eval-role candidate \
  --policy outputs/analysis/movement_bootstrap_v13_a100_phase1_gate/2026_06_24_055252_245760.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 5 \
  --bridge-mode fitted \
  --jax-platform cpu \
  --reward-overrides-json outputs/analysis/movement_bootstrap_v13_training_plan.json \
  --reward-overrides-phase phase1_signed_failure_low_command \
  --output-dir outputs/analysis/movement_bootstrap_v13_phase1_training_reward_replay_cpu_full
```

## Result

```text
overall_status: HOLD_CANDIDATE_FALL_OR_TERMINATION
candidate_gate_status: HOLD_CANDIDATE_FALL_OR_TERMINATION
termination: fall_or_nan
samples: 80
forward_tracking_ratio: 0.04657
mean local vx: 0.0037 m/s
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.07784
max_sent_target_velocity_p95_rad_s: 0.37816
reward_mean: -0.38404
reward_min: -2.76543
```

Relevant reward/diagnostic terms:

```text
applied reward override keys include:
  tracking_lin_vel_scale
  tracking_ang_vel_scale = 0.0
  alive_scale
  imitation_scale
  target_rate_scale
  actuator_tracking_scale
  forward_progress_scale
  command_progress_failure_scale
diagnostic/command_progress_failure max: 1.0
diagnostic/command_progress_failure mean: 0.0125
cost/command_progress_failure max: 120.0
cost/command_progress_failure mean: 1.5
diagnostic/command_progress_ratio mean: 0.02715
cost/command_progress_shortfall mean: 9.8619
cost/forward_shortfall mean: 10.2641
reward/alive mean: 0.0200
reward/tracking_lin_vel mean: 0.6022
reward/tracking_ang_vel omitted: scale is 0.0
reward/forward_progress mean: 1.3931
```

## Interpretation

The full training-equivalent replay proves the V13 command-progress failure
mechanic is active and the core reward scales are now applied: the phase-1
candidate terminates at the configured 80-step warmup boundary, receives the
signed terminal failure cost, and has a negative mean reward.

The remaining issue is therefore not missing termination or missing reward
plumbing. The policy still learned a low-motion behavior that survives until the
progress-failure boundary instead of discovering forward motion. Another A100
recipe should not be launched until the next training change targets this
short-lived low-motion local optimum directly.

Robot validation remains blocked.
