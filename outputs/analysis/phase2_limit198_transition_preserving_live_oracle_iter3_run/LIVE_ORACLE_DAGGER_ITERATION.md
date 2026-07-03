# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `3`
- rung: `transition_preserving_limit198_z0026`
- student_policy: `policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `1.0`
- command_x: `0.08`
- duration_s: `15.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.0026`
- reset_mode: `home-support`
- min_swing_segments_per_foot: `1`
- min_swing_rel_x_range_p95_m: `0.003`
- min_swing_peak_lift_m: `0.005`
- x008_seeds: `0-7`
- x0_seeds: `0-7`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run`
- x008_rollout_dir: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0026 --reset-mode home-support --command-x 0.08 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_rollout.json --min-swing-segments-per-foot 1 --min-swing-rel-x-range-p95-m 0.003 --min-swing-peak-lift-m 0.005
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=2 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_002
SEED_SWEEP_DONE policy=student seed=2 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=3 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_003
SEED_SWEEP_DONE policy=student seed=3 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=4 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_004
SEED_SWEEP_DONE policy=student seed=4 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_005
SEED_SWEEP_DONE policy=student seed=5 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=6 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_006
SEED_SWEEP_DONE policy=student seed=6 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=7 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_007
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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3269 | 0.0262 | 0.1320 | 0.1522 | 0.0000 | 0.0000 | 0.0123 | 18.0000 | 0.0116 | 25.2000 | 74.8000 | 0.0000 | NA |

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
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0026 --reset-mode home-support --command-x 0.0 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=2 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_002
SEED_SWEEP_DONE policy=student seed=2 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=3 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_003
SEED_SWEEP_DONE policy=student seed=3 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=4 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_004
SEED_SWEEP_DONE policy=student seed=4 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_005
SEED_SWEEP_DONE policy=student seed=5 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=6 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_006
SEED_SWEEP_DONE policy=student seed=6 status=PASS_CANDIDATE_SIM_GATE returncode=0
SEED_SWEEP_START policy=student seed=7 timeout_s=1920 output_dir=outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_007
SEED_SWEEP_DONE policy=student seed=7 status=PASS_CANDIDATE_SIM_GATE returncode=0
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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0168 | 0.1524 | 0.0561 | 0.0000 | 0.0000 | 0.0320 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0001 | 0.0168 | 0.1524 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |

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
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/relabel_x008 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=8
samples_out=6000
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/relabel_x0 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=8
samples_out=6000
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_3_x008 --source-parent-depth 3 --min-entries 8
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=198e418bc59b5f5f
entries=8
samples=6000
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_3_x0 --source-parent-depth 3 --min-entries 8
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=54137b89d961da53
entries=8
samples=6000
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json --manifest outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json --min-entries 17 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=b539bb4793ffdd67
kept_entries=54
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
