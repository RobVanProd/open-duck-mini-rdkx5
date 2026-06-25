# Next Weight-Transfer Branch Decision

status: `PLAN_MINE_PUBLISHED_POLICY_PROPULSION`

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
| `reference_backlash_push_status` | `HOLD_REFERENCE_CONTACT_MISMATCH` |
| `reference_backlash_best_single_future_vx_delta_m_s` | `-0.005149568369172915` |
| `reference_backlash_max_single_actual_double_pct` | `51.0204` |
| `contact_physics_status` | `HOLD_CONTACT_FRICTION_SOLVER_NOT_SUFFICIENT` |
| `contact_probe_best_single_future_vx_delta_m_s` | `-0.018235080486016852` |
| `published_policy_status` | `PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION` |
| `published_policy_seed_count` | `8` |
| `published_policy_duration_complete_count` | `8` |
| `published_policy_moving_seed_count_ratio_ge_0p5` | `7` |
| `published_policy_mean_local_vx_m_s` | `0.053972023295584225` |
| `published_policy_mean_tracking_ratio` | `0.7293516661565436` |
| `published_policy_single_support_future_vx_delta_m_s` | `0.004151348076938894` |
| `mechanism_comparison_status` | `PASS_POLICY_REFERENCE_MECHANISM_SPLIT` |
| `policy_actual_single_support_pct` | `44.8` |
| `reference_contact_synchronized_actual_single_support_pct` | `19.25` |
| `reference_requested_single_future_vx_delta_m_s` | `-0.005149568369172915` |
| `policy_pitch_chain_target_velocity_p95_rad_s` | `3.0488` |
| `reference_contact_synchronized_pitch_chain_target_velocity_p95_rad_s` | `4.9811` |

## Decision

Stop the local stance-relative teacher loop and mine the published policy's
closed-loop propulsion mechanism. The upstream/reference target path fails the
same forward push-effectiveness question in this sim, including the README's
`flat_terrain_backlash` task, but the published `BEST_WALK_ONNX_2` policy
does produce stable closed-loop forward locomotion in that task.

## Rationale

- No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.
- The teacher push-effectiveness reads show weak forward acceleration and lateral leakage.
- The matched x=0.04 reference only creates positive forward delta while violating lateral stability and the actuator envelope.
- The original upstream Playground reference key also fails when evaluated against the detached origin/main code path: no positive reference-single future-vx delta and all tested modes remain holds.
- The same key also fails on `flat_terrain_backlash`: best reference-single future-vx delta remains negative at `-0.0051 m/s`.
- The morphology/reference-file audit shows XML and polynomial reference assets match upstream byte-for-byte, so the next split is the published closed-loop policy, not another open-loop reference/teacher variant.
- A temporary contact-physics probe using stronger floor friction and solver iterations improved contact matching but did not improve forward impulse (`-0.0051 -> -0.0182 m/s`), so low floor friction / low solver iterations alone are not the root fix.
- The published policy completed all eight 5-second upstream-main
  `flat_terrain_backlash` seeds. Seven of eight seeds tracked the command with
  local x ratio >= 0.5, mean local vx was `0.0540 m/s`, and mean
  single-support 0.1s future vx delta was positive at `+0.0042 m/s`.
- The mechanism comparison shows the policy creates more actual single-support
  time (`44.8%` vs `19.25%` for the best reference-target variant), while the
  reference-requested single-support windows still have negative 0.1s future vx
  delta (`-0.0051 m/s`). The policy also keeps pitch-chain p95 target velocity
  lower (`3.0488 rad/s` vs `4.9811 rad/s`).

## Required Next Design

- extract a compact published-policy state/action/contact template from the
  successful closed-loop traces
- test whether imitation/BC or a trust-region teacher around that template can
  preserve the policy's actual single-support schedule without exceeding the
  measured actuator envelope
- only return to open-loop teacher generation if the state-action/contact
  template path fails a defined offline gate

## Stop Rules

- Do not continue PLAN_STANCE_RELATIVE_LATERAL_DAMPING as the default branch.
- Do not launch PPO/BC from current target sources.
- Do not run robot validation, grounded replay, or x=0.08.
- Do not relax teacher target velocity above the measured envelope to buy forward speed.
- Do not generate another nearby stance-relative teacher variant until the
  published-policy propulsion mechanism is compared against the failed
  reference-target path.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- policy/runtime changes
- PPO/BC before target gate pass
- another nearby scalar teacher-grid expansion
