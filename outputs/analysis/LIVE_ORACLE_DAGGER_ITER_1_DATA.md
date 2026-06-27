# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `1`
- rung: `deployable_obs101_phase_memory_command_aware_x0`
- student_policy: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`
- teacher_manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- command_x: `0.08`
- duration_s: `15.0`
- x008_seeds: `0-7`
- x0_seeds: `0-1`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/live_oracle_dagger_phase_student/iter_001`
- x008_rollout_dir: `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `returncode=0`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx --fit-json outputs/analysis/actuator_response_fit.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task flat_terrain_backlash --jax-platform cpu --trace-full-obs --run --command-x 0.08 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008 --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=2 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_002
SEED_SWEEP_DONE policy=student seed=2 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=3 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_003
SEED_SWEEP_DONE policy=student seed=3 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=4 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_004
SEED_SWEEP_DONE policy=student seed=4 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=5 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_005
SEED_SWEEP_DONE policy=student seed=5 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=6 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_006
SEED_SWEEP_DONE policy=student seed=6 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=7 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_007
SEED_SWEEP_DONE policy=student seed=7 status=HOLD_CANDIDATE_TRACKING returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0468 | 0.5849 | 0.1002 | 0.1520 | 3.6293 | 0.2605 |
| `student` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0440 | 0.5497 | 0.0986 | 0.1556 | 3.6645 | 0.2628 |
| `student` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0489 | 0.6116 | 0.0990 | 0.1509 | 3.6195 | 0.2601 |
| `student` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0432 | 0.5402 | 0.1002 | 0.1546 | 3.6621 | 0.2641 |
| `student` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0451 | 0.5633 | 0.1003 | 0.1506 | 3.6791 | 0.2645 |
| `student` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0458 | 0.5724 | 0.0978 | 0.1462 | 3.6534 | 0.2612 |
| `student` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0410 | 0.5126 | 0.0996 | 0.1557 | 3.6537 | 0.2649 |
| `student` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0444 | 0.5553 | 0.0987 | 0.1559 | 3.6661 | 0.2665 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.5613 | 0.0449 | 0.0993 | 0.1527 |

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
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx --fit-json outputs/analysis/actuator_response_fit.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task flat_terrain_backlash --jax-platform cpu --trace-full-obs --run --command-x 0.0 --seeds 0-1 --trace-seeds 0-1 --output-dir outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x0 --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_rollout.json
```

stdout tail:

```text
SEED_SWEEP_START policy=student seed=0 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x0/student/seed_000
SEED_SWEEP_DONE policy=student seed=0 status=HOLD_CANDIDATE_TRACKING returncode=0
SEED_SWEEP_START policy=student seed=1 timeout_s=1920 output_dir=outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x0/student/seed_001
SEED_SWEEP_DONE policy=student seed=1 status=HOLD_CANDIDATE_TRACKING returncode=0
# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1]`
trace_seeds: `[0, 1]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0465 | NA | 0.1009 | 0.1520 | 3.7183 | 0.2565 |
| `student` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0443 | NA | 0.0950 | 0.1556 | 3.7185 | 0.2594 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 0 | 2 | 750.0000 | 750 | 750 | NA | 0.0454 | 0.0979 | 0.1538 |

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
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/live_oracle_dagger_phase_student/iter_001/relabel_x008 --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=8
samples_out=6000
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_relabel.json

```

### 4. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/live_oracle_dagger_phase_student/iter_001/relabel_x0 --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=1500
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_relabel.json

```

### 5. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_001/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_1_x008 --source-parent-depth 3 --min-entries 8
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=3710e548f88bbeb7
entries=8
samples=6000
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_manifest.json

```

### 6. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_001/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_1_x0 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=07f2f3b8b26354c0
entries=2
samples=1500
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_manifest.json

```

### 7. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json --manifest outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_aggregate_manifest.json --min-entries 11 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=da574d6dc548afbb
kept_entries=18
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_001/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
