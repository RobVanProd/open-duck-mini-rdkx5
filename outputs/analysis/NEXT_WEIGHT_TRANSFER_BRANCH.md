# Next Weight-Transfer Branch Decision

status: `PASS_SOURCE_VX_SELECTOR_SMOKE`

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
| `command_sweep_status` | `WARN_COMMAND_SPECIFIC_PROPULSION_OVER_ENVELOPE` |
| `straight_x004_moving_seed_count_ratio_ge_0p5` | `0` |
| `straight_x004_mean_tracking_ratio` | `0.0468` |
| `straight_x004_pitch_chain_target_velocity_p95_max_joint_rad_s` | `1.2742` |
| `straight_x008_moving_seed_count_ratio_ge_0p5` | `7` |
| `straight_x008_mean_tracking_ratio` | `0.7998` |
| `straight_x008_pitch_chain_target_velocity_p95_max_joint_rad_s` | `5.1546` |
| `turning_command_pitch_chain_target_velocity_p95_max_joint_rad_s` | `4.6157` |
| `command_grid_status` | `HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE` |
| `straight_x005_moving_seed_count_ratio_ge_0p5` | `0 / 2` |
| `straight_x006_moving_seed_count_ratio_ge_0p5` | `0 / 2` |
| `straight_x007_moving_seed_count_ratio_ge_0p5` | `0 / 2` |
| `turn_scale050_to_090_moving_seed_count_ratio_ge_0p5` | `0 / 2 at every tested scale` |
| `turn_scale100_moving_seed_count_ratio_ge_0p5` | `2 / 2` |
| `turn_scale100_pitch_chain_target_velocity_p95_max_seed_rad_s` | `5.0147` |
| `teacher_template_status` | `PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS` |
| `straight_x008_moving_in_envelope_pct` | `70.55` |
| `straight_x008_moving_single_in_envelope_pct` | `32.80` |
| `straight_x008_safe_moving_single_future_vx_delta_m_s` | `0.0039` |
| `turning_moving_in_envelope_pct` | `63.70` |
| `turning_moving_single_in_envelope_pct` | `28.90` |
| `turning_safe_moving_single_future_vx_delta_m_s` | `0.0034` |
| `teacher_window_curation_status` | `PASS_CURATED_DATASET_SEED_READY` |
| `teacher_window_curated_count` | `259 / 301` |
| `teacher_dataset_manifest_status` | `PASS_TARGET_DATASET_MANIFEST_READY` |
| `teacher_dataset_entries` | `259` |
| `teacher_dataset_source_rollout_dirs` | `16` |
| `teacher_dataset_samples` | `6475` |
| `teacher_dataset_sanity_status` | `PASS_TARGET_DATASET_SANITY_CHECK` |
| `teacher_dataset_bc_readiness_status` | `PASS_TARGET_DATASET_BC_READY` |
| `teacher_dataset_bc_smoke_status` | `PASS_BC_FIT_SMOKE_FORWARD_REPLAY` |
| `teacher_dataset_bc_smoke_command` | `straight x=0.08` |
| `teacher_dataset_bc_smoke_mean_vx_range_m_s` | `0.0673-0.0688` |
| `teacher_dataset_bc_smoke_sent_velocity_p95_range_rad_s` | `2.4224-2.5628` |
| `teacher_dataset_bc_gate_status` | `HOLD_BC_REPLAY_TERMINATED` |
| `teacher_dataset_bc_gate_command` | `straight x=0.08` |
| `teacher_dataset_bc_gate_duration_s` | `5` |
| `teacher_dataset_bc_gate_seeds` | `8` |
| `teacher_dataset_bc_gate_duration_complete_count` | `7` |
| `teacher_dataset_bc_gate_forward_moving_seed_count_ratio_ge_0p5` | `5 / 8` |
| `teacher_dataset_bc_gate_near_standstill_seed_count` | `2 / 8` |
| `teacher_dataset_bc_gate_fall_or_reverse_seed_count` | `1 / 8` |
| `teacher_sequence_replay_status` | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| `teacher_sequence_replay_policy_set` | `aggregate` |
| `teacher_sequence_replay_seam_corrected_sent_velocity_p95_rad_s` | `0.2660` |
| `teacher_sequence_replay_no_seam_sent_velocity_p95_rad_s` | `0.2853` |
| `teacher_sequence_replay_mean_vx_range_m_s` | `-0.0108 to +0.0113` |
| `teacher_dataset_mlp_bc_gate_status` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` |
| `teacher_dataset_mlp_bc_gate_model` | `JAX/Optax MLP 64x64` |
| `teacher_dataset_mlp_bc_gate_moving_seed_count` | `1 / 8` |
| `teacher_dataset_mlp_bc_gate_mean_vx_range_m_s` | `-0.0225 to +0.0296` |
| `teacher_dataset_mlp_bc_gate_sent_velocity_p95_rad_s` | `5.2400` |
| `teacher_dataset_mlp_rate_reg_status` | `HOLD_BC_REPLAY_TERMINATED` |
| `teacher_dataset_mlp_rate_reg_sent_velocity_p95_rad_s` | `5.2400` |
| `teacher_dataset_mlp_rate_reg_terminated_seed_count` | `3 / 8` |
| `teacher_dataset_mlp_consistency_status` | `HOLD_BC_REPLAY_TERMINATED` |
| `teacher_dataset_mlp_consistency_sent_velocity_p95_rad_s` | `5.2400` |
| `teacher_dataset_mlp_consistency_terminated_seed_count` | `3 / 8` |
| `teacher_dataset_linear_bc_gate_status` | `HOLD_BC_REPLAY_TERMINATED` |
| `teacher_dataset_linear_bc_gate_moving_seed_count` | `0 / 8` |
| `teacher_dataset_linear_bc_gate_mean_vx_range_m_s` | `-0.3080 to +0.0077` |
| `teacher_dataset_linear_bc_gate_sent_velocity_p95_range_rad_s` | `0.7319 to 3.0866` |
| `teacher_dataset_blend075_bc_gate_status` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` |
| `teacher_dataset_blend075_bc_gate_moving_seed_count` | `5 / 8` |
| `teacher_dataset_blend075_bc_gate_terminated_seed_count` | `0 / 8` |
| `teacher_dataset_blend080_bc_gate_status` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` |
| `teacher_dataset_blend080_bc_gate_moving_seed_count` | `5 / 8` |
| `teacher_dataset_blend080_bc_gate_terminated_seed_count` | `0 / 8` |
| `teacher_dataset_blend080_bc_gate_near_standstill_seeds` | `1, 4, 7` |
| `teacher_dataset_blend080_bc_gate_moving_sent_velocity_p95_range_rad_s` | `2.4171 to 2.4710` |
| `teacher_dataset_blend090_bc_gate_status` | `HOLD_BC_REPLAY_TERMINATED` |
| `teacher_dataset_blend090_bc_gate_moving_seed_count` | `4 / 8` |
| `teacher_dataset_blend090_bc_gate_terminated_seed_count` | `1 / 8` |
| `teacher_dataset_knn3_bc_gate_status` | `HOLD_BC_REPLAY_TERMINATED` |
| `teacher_dataset_knn3_bc_gate_moving_seed_count` | `4 / 8` |
| `teacher_dataset_knn3_bc_gate_terminated_seed_count` | `1 / 8` |

## Decision

Stop the local stance-relative teacher loop and stop searching nearby command
cells for an envelope-safe whole published-policy template. The
upstream/reference target path fails the same forward push-effectiveness
question in this sim, and the published `BEST_WALK_ONNX_2` policy proves
closed-loop propulsion exists in vanilla sim. The compact command-grid screen
found movement only when the whole command cell exceeded the measured
per-joint pitch-chain velocity envelope, but the moving published-policy traces
contain substantial low-rate moving windows that should be mined as the next
teacher substrate. That substrate now has a curated manifest and a tiny kNN
BC smoke that preserves forward motion inside the target-rate envelope for a
short closed-loop replay, but the longer 8-seed kNN replay gate still holds
because one seed falls/reverses and two seeds collapse to near-standstill. A
single averaged action-sequence replay is even more conservative: it completes
without falling but stays near standstill. A plain one-step MLP clone also
holds: it fits the dataset offline but produces high-rate, low-progress
closed-loop behavior. First offline target-rate and observation-consistency
regularizers did not fix the closed-loop target-rate failure. A linear ridge
student is smoother, but too weak and still has a fall/reverse seed. A blended
kNN+linear student with kNN weight `0.80` is the best cheap baseline so far:
it keeps five moving seeds and removes the kNN seed-3 fall, but seeds `1`, `4`,
and `7` still freeze near standstill.

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
- The command sweep shows straight `x=0.04` is not an easy existence-proven
  gate: all eight seeds complete, but moving seeds with track ratio >= 0.5 are
  `0 / 8`, and mean track ratio is only `0.0468`.
- Straight `x=0.08` and the upstream turning command do move in vanilla sim,
  but their max-joint pitch-chain p95 target velocities remain above the
  measured envelope (`5.1546 rad/s` and `4.6157 rad/s` respectively).
- The compact command-grid screen checked straight `x=0.05`, `x=0.06`,
  `x=0.07`, and scaled upstream-turning commands from `0.50` to `1.00`. Every
  lower straight/turning cell had `0 / 2` moving seeds. The only moving grid
  cell was full-scale upstream turning with `2 / 2` moving seeds and
  max-seed pitch-chain p95 target velocity `5.0147 rad/s`.
- The teacher-window extraction shows that the moving command cells still
  contain low-rate closed-loop propulsion windows: straight `x=0.08` has
  `70.55%` moving + in-envelope ticks and `32.80%` moving + single-support +
  in-envelope ticks; the upstream turning command has `63.70%` and `28.90%`
  respectively. Those safe moving single-support windows have positive 0.1s
  future-vx deltas (`+0.0039 m/s` and `+0.0034 m/s`).
- The realized-window pipeline curated `259 / 301` low-rate teacher windows
  into a `6475`-sample BC-ready manifest across `16` rollout directories. The
  manifest sanity check passed, and a tiny kNN BC smoke completed two
  straight-`x=0.08` closed-loop seeds with mean vx `0.0673-0.0688 m/s` and
  sent-target velocity p95 `2.4224-2.5628 rad/s`.
- A longer 8-seed, 5-second kNN replay gate is a hold, not a pass. Five of
  eight seeds moved forward with track ratio >= `0.5`, seeds 4 and 7 completed
  but stayed near standstill, and seed 3 fell/reversed after 79 samples. This
  preserves the dataset-substrate finding, but it rules out treating the toy
  kNN replay as a robust student policy.
- Aggregate sequence replays, with and without periodic seam correction, also
  hold. They complete all eight seeds but drive only `-0.0108` to
  `+0.0113 m/s`, with sent-target velocity p95 around `0.266-0.285 rad/s`.
  This rules out a single averaged action loop as the missing student. The
  student needs state-conditioned imitation from the low-rate windows.
- A first JAX/Optax MLP BC smoke also holds. It completed all eight seeds, but
  only one seed exceeded `0.02 m/s`, one seed moved backward, and every seed
  hit `5.24 rad/s` sent-target velocity p95. This rules out naive one-step
  supervised action error as the only objective.
- Pairwise target-rate regularization and observation-noise consistency
  regularization were both tested as default-off MLP options. Both still hit
  `5.24 rad/s` sent-target velocity p95 on every seed and introduced
  fall/reverse terminations. Local offline regularization alone is not enough.
- The linear ridge baseline is smoother, with sent-target velocity p95 staying
  below `3.09 rad/s`, but it has zero moving seeds and one fall/reverse seed.
  A smooth one-step model is not sufficient either.
- Blending kNN with the linear ridge model is useful but not sufficient. Blend
  `0.75` and `0.80` both complete all eight seeds and preserve five moving
  seeds; blend `0.80` is the best cheap baseline because moving-seed
  sent-target velocity p95 stays around `2.42-2.47 rad/s` while the seed-3
  fall is gone. The remaining failure is seed-dependent freeze on seeds
  `1`, `4`, and `7`. Blend `0.90` and kNN `k=3` both reintroduce a seed-3
  fall/reverse and are worse than blend `0.80`.
- A traced blend `0.80` replay classifies that remaining freeze as
  `HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT`: moving seeds spend about `46.24%`
  in single support with pitch-chain sent-target velocity p95 around
  `3.19 rad/s`, while frozen seeds spend about `97.20%` in double support with
  pitch-chain sent-target velocity p95 around `0.40 rad/s`.
- The traced raw kNN `k=5` replay exposes the global-blend tradeoff: raw kNN
  moves seed `1` but seed `3` falls/reverses after 79 samples, while blend
  `0.80` rescues seed `3` but freezes seed `1`. Seeds `4` and `7` freeze in
  both.
- A narrow global-blend sweep (`0.75`, `0.80`, `0.82`, `0.85`, `0.88`, `0.90`)
  confirms there is no scalar-alpha notch: `0.75-0.88` all move only seeds
  `0/2/3/5/6` and freeze `1/4/7`; `0.90` reintroduces the seed-3 termination.
- A simple double-support dwell selector also fails: switching to raw kNN after
  5 double-support ticks reintroduces the seed-3 termination, while switching
  after 10 or 20 ticks preserves the blend `0.80` freeze pattern.
- A velocity-gated blend is the first selector that beats blend `0.80`: base
  blend `0.80`, raw-kNN blend `1.00`, and switch condition
  `local vx >= -0.02 m/s` move seeds `0/1/2/3/5/6` with zero terminations.
  Seeds `4` and `7` still freeze in double support.
- A source-filtered velocity selector is the first offline replay pass:
  primary model uses the full curated teacher dataset, alternate model excludes
  source labels matching `_seed4/`, source switch is `local vx >= +0.02 m/s`,
  and internal blend switch remains `local vx >= -0.02 m/s`. It passes both the
  5s and 10s straight-`x=0.08` CPU replay gates with all eight seeds moving,
  zero terminations, and sent-target velocity p95 around `2.43-2.53 rad/s`.

## Required Next Design

- design a reviewed state-conditioned imitation/pretraining experiment from the
  curated low-rate closed-loop teacher-window manifest
- train or constrain the student from those windows, not from the full
  over-envelope published-policy trajectory
- include closed-loop target-rate/action-smoothness selection or training
  feedback; do not optimize supervised action error alone
- use kNN/linear/MLP/sequence smoke results as baselines; the next student must
  combine kNN-like local motion with linear/sequence-like smoothness and
  multi-seed stability
- convert or distill the source-filtered velocity selector into a reviewed
  portable student; do not deploy the selector as-is
- preserve the 8/8 moving, 0/8 termination result across stricter offline gates,
  especially fitted actuator bridge evaluation
- add closed-loop selection pressure against quiet double-support dwell; further
  smoothing alone is likely to preserve the freeze
- avoid treating one global kNN/linear blend coefficient as the final selector;
  the next attempt should be state-conditioned or closed-loop-selected
- do not treat a dwell-to-raw-kNN switch as sufficient; it was tested and did
  not beat blend `0.80`
- grade the student on coherent forward motion and max-joint pitch-chain p95
  target velocity, not only mean pitch-chain target velocity
- evaluate any learned student with longer multi-seed closed-loop gates before
  treating the kNN smoke as meaningful beyond proof-of-dataset
- do not promote a student path unless it beats the 8-seed kNN gate by
  preserving forward motion across seeds without fall/reverse or freeze modes

## Stop Rules

- Do not continue PLAN_STANCE_RELATIVE_LATERAL_DAMPING as the default branch.
- Do not launch PPO/BC from current target sources.
- Do not run robot validation, grounded replay, or x=0.08.
- Do not relax teacher target velocity above the measured envelope to buy forward speed.
- Do not treat straight `x=0.04` as the default first gate until a policy
  actually clears it.
- Do not treat the published moving command cells as robot-ready while their
  max-joint pitch-chain p95 target velocities exceed the measured envelope.
- Do not keep searching small neighboring command cells without a new reason;
  the first compact grid found the same activation cliff.
- Do not treat the kNN BC smoke as a deployable policy; it is only a proof that
  the curated low-rate windows can drive a toy closed-loop imitation replay.
- Do not ignore the 8-seed kNN gate hold; the next student must solve the
  seed-dependent fall/freeze modes, not merely reproduce the 2-seed smoke.
- Do not use a single averaged action sequence as the student; aggregate
  sequence replay removes the propulsion signal.
- Do not treat plain one-step MLP BC as solved; the first MLP smoke hits the
  target-rate limit while mostly failing forward motion.
- Do not assume offline pairwise/noise regularization solves one-step BC; the
  first two regularized MLP smokes still hit the target-rate limit and
  terminated seeds.
- Do not fall back to linear ridge as the solution; the linear baseline is
  smoother but does not move.
- Do not call blend `0.80` solved; it is only the current best cheap baseline
  to beat.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- policy/runtime changes
- PPO/BC before target gate pass
- another nearby scalar teacher-grid expansion
