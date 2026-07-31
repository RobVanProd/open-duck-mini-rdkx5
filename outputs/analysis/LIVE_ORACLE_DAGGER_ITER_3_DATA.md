# Live-Oracle DAgger Iteration

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This is one offline live-oracle DAgger iteration plan/run. It does not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Config

- iteration: `3`
- rung: `deployable_obs101_phase_memory_soft_x0_alpha020`
- student_policy: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`
- teacher_manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- x008_teacher_model_kind: `source_vx_blend`
- x0_teacher_model_kind: `zero_action`
- x0_zero_action_alpha: `0.2`
- command_x: `0.08`
- duration_s: `15.0`
- x008_seeds: `0-7`
- x0_seeds: `0-1`
- run: `True`

## Outputs

- output_dir: `outputs/analysis/live_oracle_dagger_phase_student/iter_003`
- x008_rollout_dir: `outputs/analysis/live_oracle_dagger_phase_student/iter_003/rollouts_x008`
- x0_rollout_dir: `outputs/analysis/live_oracle_dagger_phase_student/iter_003/rollouts_x0`
- x008_relabel_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x008_manifest.json`
- x0_relabel_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x0_manifest.json`
- aggregate_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json`

## Commands

### 1. x008_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind source_vx_blend --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_003/rollouts_x008/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/live_oracle_dagger_phase_student/iter_003/relabel_x008 --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X008_RELABEL.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x008_relabel.json --gate-command-x 0.08
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=8
samples_out=6000
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X008_RELABEL.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x008_relabel.json

```

### 2. x0_live_oracle_relabel

status: `returncode=0`

```bash
python3 tools/relabel_bc_trace_actions.py --teacher-manifest outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json --knn-k 5 --blend-alpha 0.8 --vx-blend-alpha 1.0 --vx-blend-threshold-m-s 0.02 --source-vx-threshold-m-s 0.02 --alt-exclude-source-regex seed_004 --output-parent-depth 3 --gate-aware-sample-weights --teacher-model-kind zero_action --zero-action-alpha 0.2 --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_003/rollouts_x0/student/seed_*/trace.jsonl' --output-trace-dir outputs/analysis/live_oracle_dagger_phase_student/iter_003/relabel_x0 --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X0_RELABEL.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x0_relabel.json --gate-command-x 0.0
```

stdout tail:

```text
status=PASS_BC_TRACE_RELABEL_READY
traces=2
samples_out=1500
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X0_RELABEL.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x0_relabel.json

```

### 3. x008_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_003/relabel_x008/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X008_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x008_manifest.json --command-x 0.08 --default-mode live_oracle_iter_3_x008 --source-parent-depth 3 --min-entries 8
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=668a9f0688a767e3
entries=8
samples=6000
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x008_manifest.json

```

### 4. x0_manifest

status: `returncode=0`

```bash
python3 tools/build_bc_manifest_from_traces.py --trace-glob 'outputs/analysis/live_oracle_dagger_phase_student/iter_003/relabel_x0/*/student/seed_*/trace.jsonl' --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X0_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x0_manifest.json --command-x 0.0 --default-mode live_oracle_iter_3_x0 --source-parent-depth 3 --min-entries 2
```

stdout tail:

```text
status=PASS_BC_TRACE_MANIFEST_READY
dataset_id=baf50de5bc2e2148
entries=2
samples=1500
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x0_manifest.json

```

### 5. aggregate_manifest

status: `returncode=0`

```bash
python3 tools/filter_bc_manifest.py --manifest outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json --manifest outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x008_manifest.json --manifest outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_x0_manifest.json --output-md outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md --output-json outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json --min-entries 11 --min-samples 1 --min-mean-vx -10 --max-vy-abs-p95 999 --max-pitch-abs-p95 999 --min-base-height -10 --max-sent-velocity-p95 999 --max-tracking-p95 999
```

stdout tail:

```text
status=PASS_FILTERED_BC_MANIFEST_READY
dataset_id=dd100c5ef85b4c48
kept_entries=18
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
wrote outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json

```

## Gate

- A dry run only proves the live-oracle iteration is planned.
- A run that completes produces aggregated correction data for the next
  student fit.
- No output from this tool is a deployable candidate; candidates must
  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.
