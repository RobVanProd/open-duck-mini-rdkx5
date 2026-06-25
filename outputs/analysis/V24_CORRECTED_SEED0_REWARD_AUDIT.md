# Reward Term Activation Audit

status: `WARN_REWARD_TERMS_ZERO`

## Inputs

- reward overrides: `outputs/analysis/colab_cli/open-duck-l4-v24-staged-curriculum-20260625T165454Z/recovered/extracted/open_duck_staged_curriculum_cli_open_duck_colab_cli_staged-curriculum_20260625T165508Z/01_phase1_transition_propulsion_probe/phase_01_seed_gate_xp0p040/phase_reward_overrides.json`
- phase: `phase1_transition_propulsion_probe`
- eval path: `/tmp/open_duck_v24_corrected_seed0_trace`
- eval files: `1`

## Term Audit

| term | scale | expected metric | observed files | max abs stat | status |
|---|---:|---|---:|---:|---|
| action_magnitude | -0.0008 | `cost/action_magnitude` | 1 | 0.0001 | `OBSERVED_NONZERO` |
| action_rate | -0.0040 | `cost/action_rate` | 1 | 0.0003 | `OBSERVED_NONZERO` |
| base_height | -0.2500 | `cost/base_height` | 1 | 0.0001 | `OBSERVED_NONZERO` |
| command_progress | 10.0000 | `reward/command_progress` | 1 | 15.2895 | `OBSERVED_NONZERO` |
| command_progress_failure | -150.0000 | `cost/command_progress_failure` | 1 | 150.0000 | `OBSERVED_NONZERO` |
| command_progress_shortfall | -46.0000 | `cost/command_progress_shortfall` | 1 | 9.8054 | `OBSERVED_NONZERO` |
| forward_contact_support | -0.0600 | `cost/forward_contact_support` | 1 | 0.0000 | `OBSERVED_ZERO` |
| forward_contact_transition | 4.0000 | `reward/forward_contact_transition` | 1 | 2.3675 | `OBSERVED_NONZERO` |
| forward_double_support | -0.5000 | `cost/forward_double_support` | 1 | 0.5000 | `OBSERVED_NONZERO` |
| forward_double_support_dwell | -2.0000 | `cost/forward_double_support_dwell` | 1 | 0.0000 | `OBSERVED_ZERO` |
| forward_overshoot | -2.0000 | `cost/forward_overshoot` | 1 | 0.0113 | `OBSERVED_NONZERO` |
| forward_pitch | -0.0500 | `cost/forward_pitch` | 1 | 0.0000 | `OBSERVED_NONZERO` |
| forward_pitch_rate | -0.0050 | `cost/forward_pitch_rate` | 1 | 0.0001 | `OBSERVED_NONZERO` |
| forward_progress | 24.0000 | `reward/forward_progress` | 1 | 24.0000 | `OBSERVED_NONZERO` |
| forward_shortfall | -46.0000 | `cost/forward_shortfall` | 1 | 220.7499 | `OBSERVED_NONZERO` |
| forward_single_support | 0.2500 | `reward/forward_single_support` | 1 | 0.2500 | `OBSERVED_NONZERO` |
| forward_wrong_direction | -95.0000 | `cost/forward_wrong_direction` | 1 | 271.5356 | `OBSERVED_NONZERO` |
| orientation | -0.0400 | `cost/orientation` | 1 | 0.0000 | `OBSERVED_NONZERO` |
| stand_still | -1.0000 | `cost/stand_still` | 1 | 0.0000 | `OBSERVED_ZERO` |
| target_rate | -0.0002 | `cost/target_rate` | 1 | 0.0000 | `OBSERVED_ZERO` |
| tracking_lin_vel | 24.0000 | `reward/tracking_lin_vel` | 1 | 23.9791 | `OBSERVED_NONZERO` |

## Interpretation

All configured nonzero reward terms were present, but at least one remained zero in the recovered summaries.

No robot tests, SSH, deployment, runtime behavior changes, or training were performed by this audit.
