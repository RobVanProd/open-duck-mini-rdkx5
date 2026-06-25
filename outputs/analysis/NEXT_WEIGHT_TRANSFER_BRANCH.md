# Next Weight-Transfer Branch Decision

status: `PLAN_LATERAL_CONTAINED_STANCE_PROPULSION`

This is an offline planning artifact. It does not run simulation,
training, robot SSH, deployment, or hardware tests.

## Input Evidence

| field | value |
|---|---:|
| `gate_status` | `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET` |
| `gate_artifacts` | `62` |
| `failure_status` | `HOLD_FORWARD_IMPULSE_PRIMARY` |
| `seed_rows_scanned` | `3384` |
| `stable_actuator_rows` | `1370` |
| `support_ready_rows` | `1027` |
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
| `sagittal_propulsion_status` | `HOLD_PUSH_INEFFECTIVE` |
| `sagittal_propulsion_mean_future_vx_delta_m_s` | `0.0055900691995368545` |
| `sagittal_propulsion_pass_count` | `1` |
| `sagittal_softgate_status` | `HOLD_PUSH_INEFFECTIVE` |
| `sagittal_softgate_mean_future_vx_delta_m_s` | `0.0006837656833296326` |
| `sagittal_softgate_pass_count` | `1` |

## Decision

Design a stance propulsion controller with active lateral support containment. The sagittal stance-feedback primitive creates small local impulse, but it is not seed robust, and soft gating mostly removes the impulse.

## Rationale

- No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.
- The aggregate failure remains HOLD_FORWARD_IMPULSE_PRIMARY with zero rows satisfying stability, support, and forward progress together.
- The original foot-placement push measured as ineffective.
- The sagittal stance-feedback replacement improved mean future vx delta slightly, but still produced zero seed-robust 100/150 tick modes.
- The softgated sagittal follow-up kept the hold and reduced the already-small forward impulse.
- This means the missing mechanism is lateral containment that permits propulsion to stay active, not another direct push-amplitude or push-throttle sweep.

## Required Next Design

- stateful stance-side selection
- explicit lateral body placement over the stance foot
- swing-foot placement and clearance objective
- active lateral containment while stance propulsion remains enabled
- stance-support propulsion that is not only a direct push-amplitude increase
- lateral velocity and base-y drift penalties
- pitch and base-height guards
- measured actuator-envelope scoring
- 100-150 tick seed-robust PASS_WEIGHT_TRANSFER_TARGET gate

## Stop Rules

- Do not launch PPO/BC from current target sources.
- Do not run robot validation, grounded replay, or x=0.08.
- Do not widen the same sagittal/softgate grid without adding an active lateral support mechanism.
- Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- policy/runtime changes
- PPO/BC before target gate pass
- another nearby scalar teacher-grid expansion
