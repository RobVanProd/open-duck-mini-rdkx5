# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `0`
- rung: `corrected_terrain_support_source_precheck`
- student_policy: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `1.0`
- command_x: `0.08`
- duration_s: `15.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.005`
- min_swing_segments_per_foot: `None`
- min_swing_rel_x_range_p95_m: `None`
- min_swing_peak_lift_m: `None`
- x008_seeds: `0-7`
- x0_seeds: `0-1`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0`
- x008_rollout_dir: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.005 --command-x 0.08 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008 --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
SEED_SWEEP_START policy=student seed=2 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_002
SEED_SWEEP_DONE policy=student seed=2 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
SEED_SWEEP_START policy=student seed=3 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_003
SEED_SWEEP_DONE policy=student seed=3 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
SEED_SWEEP_START policy=student seed=4 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_004
SEED_SWEEP_DONE policy=student seed=4 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_005
SEED_SWEEP_DONE policy=student seed=5 status=HOLD_CANDIDATE_FALL_OR_TERMINATION returncode=0
SEED_SWEEP_START policy=student seed=6 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_006
SEED_SWEEP_DONE policy=student seed=6 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
SEED_SWEEP_START policy=student seed=7 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_007
SEED_SWEEP_DONE policy=student seed=7 status=HOLD_CANDIDATE_TARGET_VELOCITY returncode=0
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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0295 | 0.3689 | 0.1375 | 0.1527 | 2.3867 | 0.0000 | 1.4810 | 0.1954 | 0.0130 | 22 | 0.0097 | 23.3333 | 76.6667 | 0 | NA |
| `student` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0345 | 0.4313 | 0.1229 | 0.1565 | 2.3839 | 0.0000 | 0.7091 | 0.1921 | 0.0123 | 20 | 0.0101 | 28.1333 | 71.7333 | 0 | NA |
| `student` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0345 | 0.4309 | 0.1279 | 0.1514 | 2.3611 | 0.0000 | 0.6891 | 0.1937 | 0.0133 | 15 | 0.0222 | 26.9333 | 73.0667 | 0 | NA |
| `student` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0264 | 0.3304 | 0.1363 | 0.1559 | 2.3679 | 0.0000 | 2.4900 | 0.1929 | 0.0126 | 17 | 0.0194 | 23.3333 | 76.6667 | 0 | NA |
| `student` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0346 | 0.4327 | 0.1356 | 0.1508 | 2.3941 | 0.0000 | 0.8358 | 0.1922 | 0.0130 | 18 | 0.0087 | 24.9333 | 75.0667 | 0 | NA |
| `student` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.2654 | -3.3180 | 0.0683 | 0.0677 | 1.9250 | 0.0000 | 0.0833 | 0.1968 | 0.0286 | 0 | 0.0000 | 7.1429 | 91.0714 | 0 | NA |
| `student` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0333 | 0.4159 | 0.1156 | 0.1533 | 2.4032 | 0.0000 | 1.2722 | 0.1926 | 0.0190 | 23 | 0.0043 | 26.4000 | 73.6000 | 0 | NA |
| `student` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0287 | 0.3584 | 0.1171 | 0.1564 | 2.3814 | 0.0000 | 2.4900 | 0.1941 | 0.0137 | 18 | 0.0146 | 23.0667 | 76.9333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 8 | 1 | 7 | 663.2500 | 56 | 750 | -0.0687 | -0.0055 | 0.1201 | 0.1431 | 0.0000 | 1.2563 | 0.0157 | 16.6250 | 0.0111 | 22.9095 | 76.8506 | 0.0000 | NA |

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
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.005 --command-x 0.0 --seeds 0-1 --trace-seeds 0-1 --output-dir outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x0 --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x0/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x0/student/seed_001
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
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0166 | 0.1527 | 0.3546 | 0.0000 | 0.0000 | 0.0631 | 0.0015 | 0 | 0.0000 | 0.4000 | 99.6000 | 0 | NA |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0414 | 0.1565 | 0.2922 | 0.0000 | 0.0000 | 0.0637 | 0.0062 | 1 | 0.0004 | 1.0667 | 98.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 0 | 2 | 750.0000 | 750 | 750 | NA | 0.0003 | 0.0290 | 0.1546 | 0.0000 | 0.0000 | 0.0038 | 0.5000 | 0.0002 | 0.7333 | 99.2000 | 0.0000 | NA |

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
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/relabel_x008 --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=8
samples_out=5306
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/relabel_x0 --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=1500
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_0_x008 --source-parent-depth 3 --min-entries 8
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=de4b5fdfc2876f75
entries=8
samples=5306
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_0_x0 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=063ef866d1b49d72
entries=2
samples=1500
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --manifest outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_aggregate_manifest.json --min-entries 11 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=3f68992af82062f7
kept_entries=18
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
