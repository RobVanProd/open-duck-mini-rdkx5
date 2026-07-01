# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `1`
- rung: `z005_seed5_short_recovery_precheck`
- student_policy: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `1.0`
- command_x: `0.08`
- duration_s: `2.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.005`
- min_swing_segments_per_foot: `None`
- min_swing_rel_x_range_p95_m: `None`
- min_swing_peak_lift_m: `None`
- x008_seeds: `5`
- x0_seeds: `5`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short`
- x008_rollout_dir: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 2.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.005 --command-x 0.08 --seeds 5 --trace-seeds 5 --output-dir outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x008 --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x008/student/seed_005
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
duration_s: `2.0`
seeds: `[5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.2654 | -3.3180 | 0.0683 | 0.0677 | 1.9250 | 0.0000 | 0.0833 | 0.1968 | 0.0286 | 0 | 0.0000 | 7.1429 | 91.0714 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 1 | 1 | 0 | 56.0000 | 56 | 56 | -3.3180 | -0.2654 | 0.0683 | 0.0677 | 0.0000 | 0.0833 | 0.0286 | 0.0000 | 0.0000 | 7.1429 | 91.0714 | 0.0000 | NA |

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
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 2.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.005 --command-x 0.0 --seeds 5 --trace-seeds 5 --output-dir outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x0 --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x0/student/seed_005
SEED_SWEEP_DONE policy=student seed=5 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `2.0`
seeds: `[5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 61 | `fall_or_nan` | -0.2589 | NA | 0.0759 | 0.0512 | 1.2575 | 0.0000 | 0.0000 | 0.1953 | 0.0308 | 2 | 0.0080 | 8.1967 | 85.2459 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 1 | 1 | 0 | 61.0000 | 61 | 61 | NA | -0.2589 | 0.0759 | 0.0512 | 0.0000 | 0.0000 | 0.0308 | 2.0000 | 0.0080 | 8.1967 | 85.2459 | 0.0000 | NA |

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
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/relabel_x008 --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=1
samples_out=56
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/relabel_x0 --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=1
samples_out=61
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_1_x008 --source-parent-depth 3 --min-entries 1
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=c84223490bea53c3
entries=1
samples=56
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_1_x0 --source-parent-depth 3 --min-entries 1
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=4858c62af8ad983d
entries=1
samples=61
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --manifest outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_aggregate_manifest.json --min-entries 3 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=ca062df6fc861084
kept_entries=10
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
