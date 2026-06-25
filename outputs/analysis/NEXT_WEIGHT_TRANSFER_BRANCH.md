# Next Weight-Transfer Branch Decision

status: `PLAN_UPSTREAM_SIM_MORPHOLOGY_AUDIT`

This is an offline planning artifact. It does not run simulation,
training, robot SSH, deployment, or hardware tests.

## Input Evidence

| field | value |
|---|---:|
| `gate_status` | `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET` |
| `gate_artifacts` | `66` |
| `failure_status` | `HOLD_FORWARD_IMPULSE_PRIMARY` |
| `seed_rows_scanned` | `3896` |
| `stable_actuator_rows` | `1380` |
| `support_ready_rows` | `1464` |
| `forward_ready_rows` | `23` |
| `stable_and_support_rows` | `9` |
| `stable_and_forward_rows` | `0` |
| `support_and_forward_rows` | `9` |
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
| `stance_relative_status` | `HOLD_PUSH_INEFFECTIVE` |
| `stance_relative_mean_future_vx_delta_m_s` | `0.009873367809772528` |
| `stance_relative_pass_count` | `None` |
| `stance_relative_velocity_cap_status` | `HOLD_PUSH_INEFFECTIVE` |
| `stance_relative_velocity_cap_mean_future_vx_delta_m_s` | `0.008331105330308024` |
| `stance_relative_velocity_cap_pass_count` | `None` |
| `reference_push_status` | `HOLD_REFERENCE_CONTACT_MISMATCH` |
| `reference_best_single_future_vx_delta_m_s` | `-0.015789685055672173` |
| `reference_max_single_actual_double_pct` | `42.3161505981703` |

## Decision

Stop the local stance-relative teacher loop and audit the upstream walking setup against the local sim/morphology/reference contract. The upstream/reference gait fails the same forward push-effectiveness question in this sim, so another lateral-damping teacher variant is not the default next move.

## Rationale

- No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.
- The teacher push-effectiveness reads show weak forward acceleration and lateral leakage.
- The matched x=0.04 reference only creates positive forward delta while violating lateral stability and the actuator envelope.
- The original upstream Playground reference key also fails when evaluated against the detached origin/main code path: no positive reference-single future-vx delta and all tested modes remain holds.
- This points above the local teacher recipe: compare the upstream walking setup, MJCF, contact parameters, reference file, and morphology before authorizing more teacher variants.

## Required Next Design

- identify the exact upstream walking Playground commit/reference/checkpoint
- compare MJCF, masses, foot geometry, friction, solver settings, actuator config, and termination rules
- run the same reference push-effectiveness read in the expected upstream setup if available
- decide whether the blocker is controller design, local sim drift, or morphology/feasibility
- only return to teacher generation after the sim/morphology contract is reviewed

## Stop Rules

- Do not continue PLAN_STANCE_RELATIVE_LATERAL_DAMPING as the default branch.
- Do not launch PPO/BC from current target sources.
- Do not run robot validation, grounded replay, or x=0.08.
- Do not relax teacher target velocity above the measured envelope to buy forward speed.
- Do not generate another nearby stance-relative teacher variant until the upstream/local contract is audited.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- policy/runtime changes
- PPO/BC before target gate pass
- another nearby scalar teacher-grid expansion
