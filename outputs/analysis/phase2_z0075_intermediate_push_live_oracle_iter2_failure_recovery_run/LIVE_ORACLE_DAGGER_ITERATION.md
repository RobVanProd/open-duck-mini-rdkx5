# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `2`
- rung: `phase_modulated_z0075_failure_recovery`
- student_policy: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_20260704/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `1.0`
- command_x: `0.08`
- duration_s: `15.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.0075`
- reset_mode: `playground`
- eval_push_enable: `True`
- eval_push_interval_s: `1.0`-`1.5`
- eval_push_magnitude: `0.075`-`0.125`
- push_recovery_window_s: `1.2`
- min_swing_segments_per_foot: `None`
- min_swing_rel_x_range_p95_m: `None`
- min_swing_peak_lift_m: `None`
- x008_seeds: `1-5`
- x0_seeds: `0-1`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run`
- x008_rollout_dir: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_20260704/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0075 --eval-push-enable --eval-push-interval-min-s 1.0 --eval-push-interval-max-s 1.5 --eval-push-magnitude-min 0.075 --eval-push-magnitude-max 0.125 --push-recovery-window-s 1.2 --push-recovery-max-abs-pitch-rad 0.8 --push-recovery-min-base-height-m 0.08 --command-x 0.08 --seeds 1-5 --trace-seeds 1-5 --output-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
SEED_SWEEP_START policy=student seed=2 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008/student/seed_002
SEED_SWEEP_DONE policy=student seed=2 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
SEED_SWEEP_START policy=student seed=3 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008/student/seed_003
SEED_SWEEP_DONE policy=student seed=3 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
SEED_SWEEP_START policy=student seed=4 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008/student/seed_004
SEED_SWEEP_DONE policy=student seed=4 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008/student/seed_005
SEED_SWEEP_DONE policy=student seed=5 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[1, 2, 3, 4, 5]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[1, 2, 3, 4, 5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 560 | `fall_or_nan` | 0.0617 | 0.7718 | 0.3217 | -0.0135 | 1.5313 | 0.0000 | 0.0000 | 0.1789 | 0.0589 | 14 | 0.0069 | 26.4286 | 73.0357 | 10 | 0.8000 |
| `student` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 643 | `fall_or_nan` | 0.0439 | 0.5482 | 0.2792 | 0.0025 | 1.5330 | 0.0000 | 1.9168 | 0.1834 | 0.0604 | 10 | 0.0111 | 16.0187 | 83.6703 | 11 | 0.9091 |
| `student` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 85 | `fall_or_nan` | -0.2159 | -2.6989 | 0.1622 | 0.0708 | 2.0590 | 0.0000 | 2.3114 | 0.1575 | 0.0349 | 1 | 0.0060 | 10.5882 | 87.0588 | 1 | 0.0000 |
| `student` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 478 | `fall_or_nan` | 0.0569 | 0.7113 | 0.3303 | -0.0115 | 1.4998 | 0.0000 | 0.1771 | 0.1692 | 0.0578 | 4 | 0.0072 | 14.2259 | 85.3556 | 8 | 0.8750 |
| `student` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.2883 | -3.6031 | 0.0359 | 0.0875 | 3.4897 | 1.4589 | 3.2400 | 0.3202 | 0.0290 | 2 | 0.0085 | 6.2500 | 85.4167 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 5 | 5 | 0 | 362.8000 | 48 | 643 | -0.8542 | -0.0683 | 0.2259 | 0.0272 | 0.2918 | 1.5290 | 0.0482 | 6.2000 | 0.0079 | 14.7023 | 82.9074 | 6.0000 | 0.6460 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.

```

### 2. x0_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_20260704/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0075 --eval-push-enable --eval-push-interval-min-s 1.0 --eval-push-interval-max-s 1.5 --eval-push-magnitude-min 0.075 --eval-push-magnitude-max 0.125 --push-recovery-window-s 1.2 --push-recovery-max-abs-pitch-rad 0.8 --push-recovery-min-base-height-m 0.08 --command-x 0.0 --seeds 0-1 --trace-seeds 0-1 --output-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x0 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x0/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x0/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=PASS_CANDIDATE_SIM_GATE returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0005 | NA | 0.0039 | 0.1529 | 0.0695 | 0.0000 | 0.0000 | 0.0324 | 0.0181 | 0 | 0.0000 | 0.1333 | 99.8667 | 12 | 0.9167 |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0005 | NA | 0.0624 | 0.1568 | 0.0775 | 0.0000 | 0.0000 | 0.0448 | 0.0033 | 0 | 0.0000 | 0.6667 | 99.2000 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 0 | 2 | 750.0000 | 750 | 750 | NA | -0.0005 | 0.0331 | 0.1548 | 0.0000 | 0.0000 | 0.0107 | 0.0000 | 0.0000 | 0.4000 | 99.5333 | 12.5000 | 0.9199 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.

```

### 3. x008_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/relabel_x008 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=5
samples_out=1814
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/relabel_x0 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=1500
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_2_x008 --source-parent-depth 3 --min-entries 5
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=e518de15e8f9e0cb
entries=5
samples=1814
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_2_x0 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=3488cc74affefdad
entries=2
samples=1500
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_run/live_oracle_dagger_aggregate_manifest.json --manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json --min-entries 8 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=ad1f4a6a5446d648
kept_entries=68
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
