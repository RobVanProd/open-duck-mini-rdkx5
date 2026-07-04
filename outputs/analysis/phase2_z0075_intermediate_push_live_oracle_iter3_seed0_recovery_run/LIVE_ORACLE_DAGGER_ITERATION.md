# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `3`
- rung: `phase_modulated_z0075_seed0_push_recovery`
- student_policy: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_20260704/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `1.0`
- command_x: `0.08`
- duration_s: `15.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.0075`
- reset_mode: `home-support`
- eval_push_enable: `True`
- eval_push_interval_s: `1.0`-`1.5`
- eval_push_magnitude: `0.075`-`0.125`
- push_recovery_window_s: `1.2`
- min_swing_segments_per_foot: `None`
- min_swing_rel_x_range_p95_m: `None`
- min_swing_peak_lift_m: `None`
- x008_seeds: `0,7`
- x0_seeds: `0-1`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run`
- x008_rollout_dir: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_20260704/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0075 --reset-mode home-support --eval-push-enable --eval-push-interval-min-s 1.0 --eval-push-interval-max-s 1.5 --eval-push-magnitude-min 0.075 --eval-push-magnitude-max 0.125 --push-recovery-window-s 1.2 --push-recovery-max-abs-pitch-rad 0.8 --push-recovery-min-base-height-m 0.08 --command-x 0.08 --seeds 0,7 --trace-seeds 0,7 --output-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x008 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x008/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
SEED_SWEEP_START policy=student seed=7 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x008/student/seed_007
SEED_SWEEP_DONE policy=student seed=7 status=PASS_CANDIDATE_SIM_GATE returncode=0
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
seeds: `[0, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 110 | `fall_or_nan` | 0.1799 | 2.2491 | 1.0237 | 0.0140 | 1.5880 | 0.0000 | 0.0000 | 0.1990 | 0.0591 | 0 | 0.0000 | 13.6364 | 84.5455 | 1 | 0.0000 |
| `student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0331 | 0.4139 | 0.1668 | 0.1532 | 1.5988 | 0.0000 | 0.0000 | 0.1844 | 0.0174 | 17 | 0.0212 | 25.6000 | 74.4000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 1 | 1 | 430.0000 | 110 | 750 | 1.3315 | 0.1065 | 0.5953 | 0.0836 | 0.0000 | 0.0000 | 0.0382 | 8.5000 | 0.0106 | 19.6182 | 79.4727 | 5.5000 | 0.4500 |

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
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_20260704/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0075 --reset-mode home-support --eval-push-enable --eval-push-interval-min-s 1.0 --eval-push-interval-max-s 1.5 --eval-push-magnitude-min 0.075 --eval-push-magnitude-max 0.125 --push-recovery-window-s 1.2 --push-recovery-max-abs-pitch-rad 0.8 --push-recovery-min-base-height-m 0.08 --command-x 0.0 --seeds 0-1 --trace-seeds 0-1 --output-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x0 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x0/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x0/student/seed_001
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
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0010 | NA | 0.0702 | 0.1533 | 0.0228 | 0.0000 | 0.0000 | 0.0421 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0584 | 0.1533 | 0.0226 | 0.0000 | 0.0000 | 0.0405 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 0 | 2 | 750.0000 | 750 | 750 | NA | 0.0009 | 0.0643 | 0.1533 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.5000 | 0.9199 |

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
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/relabel_x008 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=860
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/relabel_x0 --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=1500
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_3_x008 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=43bdc25b8b38d29e
entries=2
samples=860
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_3_x0 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=7f035dbf33d2c450
entries=2
samples=1500
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json --manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json --min-entries 5 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=ddbeda5b717074b6
kept_entries=72
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
