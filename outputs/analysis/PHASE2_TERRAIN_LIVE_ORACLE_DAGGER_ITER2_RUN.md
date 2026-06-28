# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `2`
- rung: `terrain_window_live_oracle`
- student_policy: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter1_bc_student/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_terrain_safe_hard_step_bc_manifest.json`
- x008_teacher_model_kind: `blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `1.0`
- command_x: `0.08`
- duration_s: `5.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.002`
- min_swing_segments_per_foot: `1`
- min_swing_rel_x_range_p95_m: `0.003`
- min_swing_peak_lift_m: `0.005`
- x008_seeds: `2,4`
- x0_seeds: `0`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002`
- x008_rollout_dir: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=outputs/analysis/phase2_terrain_live_oracle_dagger_iter1_bc_student/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 5.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.002 --command-x 0.08 --seeds 2,4 --trace-seeds 2,4 --output-dir outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x008 --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_rollout.json --min-swing-segments-per-foot 1 --min-swing-rel-x-range-p95-m 0.003 --min-swing-peak-lift-m 0.005
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=2 timeout_s=1920 output_dir=outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x008/student/seed_002
SEED_SWEEP_DONE policy=student seed=2 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=4 timeout_s=1920 output_dir=outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x008/student/seed_004
SEED_SWEEP_DONE policy=student seed=4 status=HOLD_CANDIDATE_TRACKING returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[2, 4]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[2, 4]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0397 | 0.4968 | 0.0968 | 0.1511 | 3.8770 | 1.1270 | 0.2399 | 0.0111 | 10 | 0.0123 | 35.2000 | 64.8000 | 0 | NA |
| `student` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0459 | 0.5737 | 0.1173 | 0.1507 | 3.6812 | 0.9312 | 0.2411 | 0.0128 | 8 | 0.0176 | 30.4000 | 69.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.5352 | 0.0428 | 0.1071 | 0.1509 | 1.0291 | 0.0119 | 9.0000 | 0.0149 | 32.8000 | 67.2000 | 0.0000 | NA |

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
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=outputs/analysis/phase2_terrain_live_oracle_dagger_iter1_bc_student/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 5.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.002 --command-x 0.0 --seeds 0 --trace-seeds 0 --output-dir outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x0 --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x0/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=PASS_CANDIDATE_SIM_GATE returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0010 | NA | 0.0250 | 0.1519 | 0.3702 | 0.0000 | 0.0639 | 0.0211 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 1 | 0 | 1 | 250.0000 | 250 | 250 | NA | -0.0010 | 0.0250 | 0.1519 | 0.0000 | 0.0211 | 0.0000 | 0.0000 | 0.8000 | 99.2000 | 0.0000 | NA |

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
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_terrain_safe_hard_step_bc_manifest.json --knn-k 3 --blend-alpha 0.85 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind blend --trace-glob 'outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x008 --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=500
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_terrain_safe_hard_step_bc_manifest.json --knn-k 3 --blend-alpha 0.85 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x0 --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=1
samples_out=250
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_2_x008 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=39c0d4fdfda5cc1f
entries=2
samples=500
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_2_x0 --source-parent-depth 3 --min-entries 1
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=8936d8529133a044
entries=1
samples=250
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_terrain_live_oracle_dagger/iter_001/live_oracle_dagger_aggregate_manifest.json --manifest outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_aggregate_manifest.json --min-entries 4 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=95c271e9e6f65634
kept_entries=13
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
