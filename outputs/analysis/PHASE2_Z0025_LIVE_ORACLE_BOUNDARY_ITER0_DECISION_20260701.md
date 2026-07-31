# Phase 2 z=0.0025 Live-Oracle Boundary DAgger Iteration 0

status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

This was an offline CPU-only data collection and relabeling pass. It did not
SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Purpose

The z=0.0025 boundary candidate passes x=0.0 but holds at x=0.08 on four
boundary seeds:

- seeds 0 and 4: instantaneous left_hip_pitch target-velocity excess
- seeds 3 and 6: low forward progress

This iteration collected the current student's own visited states on those
boundary seeds, queried the corrected z=0.0024 source-vx oracle on those states,
and built an aggregate BC manifest for the next supervised student fit.

## Inputs

- student_policy: `outputs/analysis/colab_cli/open-duck-l4-z0025-artifact-phase2-z0025-boundary-20260701T090250Z/extracted/open_duck_colab_cli_phase2-z0025-boundary_20260701T090317Z/open_duck_training_phase2_z0025_boundary_cli/smoke_20260701T090648Z_gpu/2026_07_01_092118_122880.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- x=0.08 seeds: `0,3,4,6`
- x=0.0 seeds: `0-1`

## x=0.08 Student Rollout

| seed | status | samples | mean vx | track ratio | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0211 | 0.2641 | 0.5350 | 0.1919 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0169 | 0.2110 | 0.0000 | 0.1867 |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0215 | 0.2691 | 0.2280 | 0.1875 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0197 | 0.2465 | 0.0000 | 0.1863 |

Distribution: 0 falls, 4/4 duration complete, mean track ratio `0.2477`.

## x=0.0 Student Rollout

| seed | status | samples | mean vx | max vel excess | tracking p95 |
|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0005 | 0.0000 | 0.0629 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | -0.0002 | 0.0000 | 0.0642 |

Distribution: 0 falls, 2/2 duration complete, zero-command behavior preserved.

## Relabeling

- x=0.08 relabel status: `PASS_BC_TRACE_RELABEL_READY`
- x=0.08 traces: `4`
- x=0.08 samples_out: `3000`
- x=0.08 teacher model: `source_vx_blend`
- x=0.0 relabel status: `PASS_BC_TRACE_RELABEL_READY`
- x=0.0 traces: `2`
- x=0.0 samples_out: `1500`
- x=0.0 teacher model: `zero_action`

## Manifests

- x=0.08 manifest status: `PASS_BC_TRACE_MANIFEST_READY`
- x=0.08 dataset_id: `6170fe13a3123346`
- x=0.08 entries/samples: `4 / 3000`
- x=0.0 manifest status: `PASS_BC_TRACE_MANIFEST_READY`
- x=0.0 dataset_id: `8530328f24a25f51`
- x=0.0 entries/samples: `2 / 1500`
- aggregate manifest status: `PASS_FILTERED_BC_MANIFEST_READY`
- aggregate dataset_id: `e1d14b2c3f81d443`
- aggregate entries/samples: `14 / 10500`
- aggregate max_source_fraction: `0.0714`

## Decision

`PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

The iteration produced a usable aggregate BC manifest containing:

- the original corrected z=0.0024 source data,
- x=0.08 live-oracle relabels on the z=0.0025 boundary failure seeds, and
- x=0.0 zero-action preservation labels.

Next step: fit a supervised student from aggregate manifest
`outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`,
then screen it first on the same boundary seeds before spending a full 8-seed gate.

Robot validation remains blocked.
