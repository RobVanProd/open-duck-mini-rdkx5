# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DRY_RUN`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `2`
- rung: `z0025_x0_seed5_softzero_repair`
- student_policy: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `0.5`
- command_x: `0.08`
- duration_s: `15.0`
- task: `rough_terrain_backlash`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- terrain_hfield_z_scale: `0.0025`
- min_swing_segments_per_foot: `None`
- min_swing_rel_x_range_p95_m: `None`
- min_swing_peak_lift_m: `None`
- x008_seeds: `0-7`
- x0_seeds: `5`
- run: `False`

## Outputs

- output_dir: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2`
- x008_rollout_dir: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `not_run`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0025 --command-x 0.08 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/rollouts_x008 --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x008_rollout.json
```

### 2. x0_student_rollout

status: `not_run`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0025 --command-x 0.0 --seeds 5 --trace-seeds 5 --output-dir outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/rollouts_x0 --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x0_rollout.json
```

### 3. x008_live_oracle_relabel

status: `not_run`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/relabel_x008 --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

### 4. x0_live_oracle_relabel

status: `not_run`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 0.5 --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/relabel_x0 --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

### 5. x008_manifest

status: `not_run`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_2_x008 --source-parent-depth 3 --min-entries 8
```

### 6. x0_manifest

status: `not_run`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_2_x0 --source-parent-depth 3 --min-entries 1
```

### 7. aggregate_manifest

status: `not_run`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json --manifest outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2/live_oracle_dagger_aggregate_manifest.json --min-entries 10 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
