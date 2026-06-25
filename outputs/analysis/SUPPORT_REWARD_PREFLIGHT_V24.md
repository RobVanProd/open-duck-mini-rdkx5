# Support Reward Preflight

status: `WARN_REWARD_TERMS_ZERO`

## Inputs

- reward overrides: `outputs/analysis/movement_bootstrap_v24_transition_propulsion_plan.json`
- phase: `phase1_transition_propulsion_probe`
- command_x: `0.04`
- duration_s: `0.2`
- seed: `0`
- bridge: `vanilla`
- jax_platform: `cpu`

## Results

- eval_returncode: `0`
- audit_returncode: `0`
- audit_status: `WARN_REWARD_TERMS_ZERO`
- eval_json: `/tmp/open_duck_support_reward_preflight_tool_smoke/eval/closed_loop_actuator_bridge_eval.json`
- audit_json: `/tmp/open_duck_support_reward_preflight_tool_smoke/reward_term_activation.json`
- audit_md: `/tmp/open_duck_support_reward_preflight_tool_smoke/REWARD_TERM_ACTIVATION.md`

## Term Audit

| term | scale | observed files | max abs stat | status |
|---|---:|---:|---:|---|
| action_magnitude | -0.0008 | 1 | 0.0010 | `OBSERVED_NONZERO` |
| action_rate | -0.0040 | 1 | 0.0010 | `OBSERVED_NONZERO` |
| base_height | -0.2500 | 1 | 0.0001 | `OBSERVED_NONZERO` |
| command_progress | 10.0000 | 1 | 13.3893 | `OBSERVED_NONZERO` |
| command_progress_failure | -150.0000 | 1 | 0.0000 | `OBSERVED_ZERO` |
| command_progress_shortfall | -46.0000 | 1 | 0.0000 | `OBSERVED_ZERO` |
| forward_contact_support | -0.0600 | 1 | 0.0000 | `OBSERVED_ZERO` |
| forward_contact_transition | 4.0000 | 1 | 4.0000 | `OBSERVED_NONZERO` |
| forward_double_support | -0.5000 | 1 | 0.5000 | `OBSERVED_NONZERO` |
| forward_double_support_dwell | -2.0000 | 1 | 0.0000 | `OBSERVED_ZERO` |
| forward_overshoot | -2.0000 | 1 | 2.5597 | `OBSERVED_NONZERO` |
| forward_pitch | -0.0500 | 1 | 0.0000 | `OBSERVED_NONZERO` |
| forward_pitch_rate | -0.0050 | 1 | 0.0003 | `OBSERVED_NONZERO` |
| forward_progress | 24.0000 | 1 | 24.0000 | `OBSERVED_NONZERO` |
| forward_shortfall | -46.0000 | 1 | 168.8170 | `OBSERVED_NONZERO` |
| forward_single_support | 0.2500 | 1 | 0.2500 | `OBSERVED_NONZERO` |
| forward_wrong_direction | -95.0000 | 1 | 190.4016 | `OBSERVED_NONZERO` |
| orientation | -0.0400 | 1 | 0.0001 | `OBSERVED_NONZERO` |
| stand_still | -1.0000 | 1 | 0.0000 | `OBSERVED_ZERO` |
| target_rate | -0.0002 | 1 | 0.0000 | `OBSERVED_ZERO` |
| tracking_lin_vel | 24.0000 | 1 | 10.1590 | `OBSERVED_NONZERO` |

## Safety

- robot_tests_run: `false`
- ssh_run: `false`
- deploy_run: `false`
- training_run: `false`
- runtime_behavior_changed: `false`
