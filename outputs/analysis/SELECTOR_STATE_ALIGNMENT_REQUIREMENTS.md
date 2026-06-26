# Selector State Alignment Requirements

status: `HOLD_STATE_ALIGNMENT_TRACE_CONTRACT_INCOMPLETE`

The relabelled selector replay now fails before the selected windows because
open-loop prefix replay diverges from the source trace. The next branch is
state-aligned replay or a closed-loop selector, but exact state-aligned replay
cannot be built from the current source traces.

## Current Trace Fields

Available in `trace_full_obs_footpos.jsonl`:

- `base_x_m`, `base_y_m`, `base_height_m`
- `body_pitch_rad`
- `local_linvel_m_s`
- `actual_position_rad`
- `sent_target_rad`
- `target_pre_rate_limit_rad`
- `foot_contacts`
- `foot_site_pos_m`
- `obs_state`

Missing for exact MJX state reset:

- full `qpos`
- full `qvel`
- full base quaternion, not pitch only
- control / motor target state at the source tick
- delayed action/history state if the replay is meant to match policy internals

## Decision

Do not approximate state-aligned replay from pitch, local velocity, and joint
position alone. That would create a new confound.

Next offline options:

1. Regenerate the published-policy source traces with full `qpos`, `qvel`,
   `ctrl`, and motor target state, then implement exact state-aligned replay.
2. Skip static state alignment and build a closed-loop selector that chooses
   source actions from the current observation/contact state.

No robot tests, SSH, deploy, training, or runtime behavior changes are needed
for either option.
