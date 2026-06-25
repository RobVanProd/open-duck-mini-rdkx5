# Next Weight-Transfer Branch Decision

status: `PLAN_FOOT_PLACEMENT_MPC_TEACHER`

This is an offline planning artifact. It does not run simulation,
training, robot SSH, deployment, or hardware tests.

## Input Evidence

| field | value |
|---|---:|
| `gate_status` | `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET` |
| `gate_artifacts` | `45` |
| `failure_status` | `HOLD_FORWARD_IMPULSE_PRIMARY` |
| `seed_rows_scanned` | `2068` |
| `stable_actuator_rows` | `1017` |
| `support_ready_rows` | `526` |
| `forward_ready_rows` | `15` |
| `stable_and_support_rows` | `9` |
| `stable_and_forward_rows` | `0` |
| `support_and_forward_rows` | `1` |
| `all_three_rows` | `0` |
| `leg_extension_100_status` | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `leg_extension_100_robust_modes` | `0` |
| `leg_extension_150_status` | `HOLD_NO_SEED_ROBUST_TARGETS` |
| `leg_extension_150_robust_modes` | `0` |

## Decision

Design a finite-horizon state-feedback teacher/optimizer that chooses stance side, lateral body placement, swing-foot placement, and forward push timing together.

## Rationale

- No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.
- Forward-ready rows are rare, and no row satisfies stability, support, and forward progress together.
- The default-off stance knee/ankle push-off probe also held, so the missing mechanism is not a local distal push term inside the existing support-state teacher.
- Existing rows show support/contact can improve, but usable forward impulse remains coupled to lateral velocity or pitch margin.

## Required Next Design

- stateful stance-side selection
- explicit lateral body placement over the stance foot
- swing-foot placement and clearance objective
- forward push timed after support loading
- lateral velocity and base-y drift penalties
- pitch and base-height guards
- measured actuator-envelope scoring
- 100-150 tick seed-robust PASS_WEIGHT_TRANSFER_TARGET gate

## Stop Rules

- Do not launch PPO/BC from current target sources.
- Do not run robot validation, grounded replay, or x=0.08.
- Do not widen the same local teacher grid unless a new state variable or objective is added.
- Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- policy/runtime changes
- PPO/BC before target gate pass
- another nearby scalar teacher-grid expansion
