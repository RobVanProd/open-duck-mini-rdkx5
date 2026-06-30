# Phase 2 Corrected Terrain Source Decision

status: `PASS_CORRECTED_Z0024_SOURCE_READY__PLAN_Z005_LIVE_ORACLE_NEXT`

This is an offline planning/source artifact. It did not run robot tests, SSH,
deploy, grounded replay, training, or runtime behavior changes.

## Source Manifest

- source manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- source report: `outputs/analysis/PHASE2_Z0024_CORRECTED_TERRAIN_SOURCE_MANIFEST.md`
- dataset_id: `d8498b665c201936`
- entries: `8`
- samples: `6000`
- bc_ready_entries: `8`
- source traces: `z=0.0024`, `rough_terrain_backlash`, `x=0.08`, corrected bridge

The source traces are the current candidate's 8/8 passing rough-terrain traces
under the corrected bridge. They are not deployable policy artifacts; they are
seed material for a corrected terrain-aware oracle/student path.

## Source Quality

| seed | vx | track ratio | sent_vel95 | track95 | height_min |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.0312 | 0.3894 | 1.8327 | 0.1586 | 0.1519 |
| 1 | 0.0352 | 0.4396 | 1.8268 | 0.1591 | 0.1563 |
| 2 | 0.0350 | 0.4377 | 1.8553 | 0.1595 | 0.1512 |
| 3 | 0.0288 | 0.3602 | 1.8353 | 0.1570 | 0.1552 |
| 4 | 0.0347 | 0.4337 | 1.8328 | 0.1592 | 0.1506 |
| 5 | 0.0303 | 0.3794 | 1.8159 | 0.1576 | 0.1464 |
| 6 | 0.0345 | 0.4317 | 1.8488 | 0.1581 | 0.1532 |
| 7 | 0.0291 | 0.3632 | 1.8582 | 0.1587 | 0.1565 |

All entries are under the corrected bridge target-rate envelope and are
BC-ready. The source still represents a slow, double-support-heavy gait; it is
not sufficient evidence for `z=0.005` robustness.

## z=0.005 Failure Context

The paired trace decision in
`outputs/analysis/PHASE2_Z005_VS_Z0024_SEED5_TRACE_DECISION.md` shows the
current candidate's `z=0.005` seed-5 failure is a terrain/support collapse:

- forward velocity and pitch diverge first at 0.48s,
- base height diverges later at 1.02s,
- the failing trace stays within corrected per-joint pitch-chain velocity limits,
- the scalar support/swing reward branch is exhausted.

That makes the next valid offline path a corrected-source/live-oracle terrain
support iteration, not another scalar reward run.

## Planned Next Iteration

Dry-run status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DRY_RUN`

Ignored local plan artifacts:

- `outputs/analysis/PHASE2_Z005_LIVE_ORACLE_TERRAIN_SUPPORT_ITER0_PLAN.md`
- `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0_plan.json`

Planned run:

- student: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- teacher/base manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- bridge: corrected fitted bridge
- x=0.08 rollout: seeds `0-7`, 15s, full obs
- x=0.0 rollout: seeds `0-1`, 15s, full obs
- relabel: live oracle over the student's z=0.005 visited states
- output: aggregate manifest for the next student fit

## Decision

Proceed next with the bounded z=0.005 live-oracle terrain-support iteration
using the corrected z=0.0024 source manifest.

Do not:

- use historical old-bridge source-VX manifests,
- launch another scalar support/swing reward run,
- promote the current candidate for grounded terrain testing,
- run robot validation before the corrected z=0.005 gate clears.
