# Next Weight-Transfer Branch Decision

status: `PLAN_REPLACE_STANCE_PROPULSION_PRIMITIVE`

This is an offline planning artifact. It does not run simulation,
training, robot SSH, deployment, or hardware tests.

## Input Evidence

| field | value |
|---|---:|
| `gate_status` | `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET` |
| `gate_artifacts` | `58` |
| `failure_status` | `HOLD_FORWARD_IMPULSE_PRIMARY` |
| `seed_rows_scanned` | `2872` |
| `stable_actuator_rows` | `1250` |
| `support_ready_rows` | `789` |
| `forward_ready_rows` | `15` |
| `stable_and_support_rows` | `9` |
| `stable_and_forward_rows` | `0` |
| `support_and_forward_rows` | `1` |
| `all_three_rows` | `0` |
| `leg_extension_100_status` | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `leg_extension_100_robust_modes` | `0` |
| `leg_extension_150_status` | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `leg_extension_150_robust_modes` | `0` |
| `push_effectiveness_status` | `HOLD_PUSH_INEFFECTIVE` |
| `push_mean_allowed_pct` | `27.536204051439626` |
| `push_mean_future_vx_delta_m_s` | `-0.00031139696306279403` |

## Decision

Design a new stance-support propulsion primitive. The existing foot-placement push is present often enough to evaluate, but it does not create reliable forward acceleration and couples into lateral velocity.

## Rationale

- No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.
- The aggregate failure remains HOLD_FORWARD_IMPULSE_PRIMARY with zero rows satisfying stability, support, and forward progress together.
- The corrected relative-yaw recovery probe showed high switch readiness, so yaw-gate measurement is not the primary blocker.
- The push-effectiveness analyzer measured the current push primitive as HOLD_PUSH_INEFFECTIVE.
- This means the next branch should change the propulsion mechanism under stance support, not make the same pitch-chain push earlier, later, or more frequent.

## Required Next Design

- stateful stance-side selection
- explicit lateral body placement over the stance foot
- swing-foot placement and clearance objective
- new stance-support propulsion primitive, not the existing pitch-chain push
- lateral velocity and base-y drift penalties
- pitch and base-height guards
- measured actuator-envelope scoring
- 100-150 tick seed-robust PASS_WEIGHT_TRANSFER_TARGET gate

## Stop Rules

- Do not launch PPO/BC from current target sources.
- Do not run robot validation, grounded replay, or x=0.08.
- Do not widen the same push/advance/clearance/yaw/recovery grid.
- Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- policy/runtime changes
- PPO/BC before target gate pass
- another nearby scalar teacher-grid expansion
