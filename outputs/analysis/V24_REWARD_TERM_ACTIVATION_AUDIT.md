# Reward Term Activation Audit

status: `HOLD_REWARD_TERMS_MISSING`

## Inputs

- reward overrides: `outputs/analysis/colab_cli/open-duck-l4-v24-staged-curriculum-20260625T165454Z/recovered/extracted/open_duck_staged_curriculum_cli_open_duck_colab_cli_staged-curriculum_20260625T165508Z/01_phase1_transition_propulsion_probe/phase_01_seed_gate_xp0p040/phase_reward_overrides.json`
- phase: `phase1_transition_propulsion_probe`
- eval path: `outputs/analysis/colab_cli/open-duck-l4-v24-staged-curriculum-20260625T165454Z/recovered/extracted/open_duck_staged_curriculum_cli_open_duck_colab_cli_staged-curriculum_20260625T165508Z/01_phase1_transition_propulsion_probe/phase_01_seed_gate_xp0p040/phase_01`
- eval files: `6`

## Term Audit

| term | scale | expected metric | observed files | max abs stat | status |
|---|---:|---|---:|---:|---|
| action_magnitude | -0.0008 | `cost/action_magnitude` | 6 | 0.0001 | `OBSERVED_NONZERO` |
| action_rate | -0.0040 | `cost/action_rate` | 6 | 0.0003 | `OBSERVED_NONZERO` |
| base_height | -0.2500 | `cost/base_height` | 6 | 0.0020 | `OBSERVED_NONZERO` |
| command_progress | 10.0000 | `reward/command_progress` | 6 | 85.3120 | `OBSERVED_NONZERO` |
| command_progress_failure | -150.0000 | `cost/command_progress_failure` | 6 | 150.0000 | `OBSERVED_NONZERO` |
| command_progress_shortfall | -46.0000 | `cost/command_progress_shortfall` | 6 | 3669.2522 | `OBSERVED_NONZERO` |
| forward_contact_support | -0.0600 | `cost/forward_contact_support` | 6 | 0.0600 | `OBSERVED_NONZERO` |
| forward_contact_transition | 4.0000 | `reward/forward_contact_transition` | 0 | NA | `MISSING` |
| forward_double_support | -0.5000 | `cost/forward_double_support` | 0 | NA | `MISSING` |
| forward_double_support_dwell | -2.0000 | `cost/forward_double_support_dwell` | 0 | NA | `MISSING` |
| forward_overshoot | -2.0000 | `cost/forward_overshoot` | 6 | 1.9740 | `OBSERVED_NONZERO` |
| forward_pitch | -0.0500 | `cost/forward_pitch` | 6 | 0.0092 | `OBSERVED_NONZERO` |
| forward_pitch_rate | -0.0050 | `cost/forward_pitch_rate` | 6 | 0.0321 | `OBSERVED_NONZERO` |
| forward_progress | 24.0000 | `reward/forward_progress` | 6 | 24.0000 | `OBSERVED_NONZERO` |
| forward_shortfall | -46.0000 | `cost/forward_shortfall` | 6 | 65480.3320 | `OBSERVED_NONZERO` |
| forward_single_support | 0.2500 | `reward/forward_single_support` | 0 | NA | `MISSING` |
| forward_wrong_direction | -95.0000 | `cost/forward_wrong_direction` | 6 | 131670.6094 | `OBSERVED_NONZERO` |
| orientation | -0.0400 | `cost/orientation` | 6 | 0.0400 | `OBSERVED_NONZERO` |
| stand_still | -1.0000 | `cost/stand_still` | 6 | 0.0000 | `OBSERVED_ZERO` |
| target_rate | -0.0002 | `cost/target_rate` | 6 | 0.0000 | `OBSERVED_ZERO` |
| tracking_lin_vel | 24.0000 | `reward/tracking_lin_vel` | 6 | 23.9802 | `OBSERVED_NONZERO` |

## Interpretation

Configured nonzero reward scales were missing from the recovered eval reward-term summaries. Treat the gate as behaviorally valid, but do not claim those terms were observed during eval without a trace that contains them.

Missing terms:

- `forward_contact_transition`
- `forward_double_support`
- `forward_double_support_dwell`
- `forward_single_support`

No robot tests, SSH, deployment, runtime behavior changes, or training were performed by this audit.
