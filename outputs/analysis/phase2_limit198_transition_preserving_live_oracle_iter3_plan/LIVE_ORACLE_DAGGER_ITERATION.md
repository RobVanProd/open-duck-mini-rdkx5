# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DRY_RUN`

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
- run: `False`

## Outputs

- output_dir: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan`
- x008_rollout_dir: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_student_rollout

status: `not_run`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0026 --reset-mode home-support --command-x 0.08 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/rollouts_x008 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x008_rollout.json --min-swing-segments-per-foot 1 --min-swing-rel-x-range-p95-m 0.003 --min-swing-peak-lift-m 0.005
```

### 2. x0_student_rollout

status: `not_run`

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py --policies student=policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --duration 15.0 --bridge-mode fitted --task rough_terrain_backlash --jax-platform cpu --trace-full-obs --run --terrain-hfield-z-scale 0.0026 --reset-mode home-support --command-x 0.0 --seeds 0-7 --trace-seeds 0-7 --output-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/rollouts_x0 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x0_rollout.json
```

### 3. x008_live_oracle_relabel

status: `not_run`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/relabel_x008 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

### 4. x0_live_oracle_relabel

status: `not_run`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 1.0 --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/relabel_x0 --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

### 5. x008_manifest

status: `not_run`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_3_x008 --source-parent-depth 3 --min-entries 8
```

### 6. x0_manifest

status: `not_run`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_3_x0 --source-parent-depth 3 --min-entries 8
```

### 7. aggregate_manifest

status: `not_run`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json --manifest outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_aggregate_manifest.json --min-entries 17 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
