# Phase 2 z=0.0025 Live-Oracle x0 Seed5 Soft-Zero Iter2 Data Decision

status: `PASS_DATA_READY__FIT_NEXT_STUDENT`

This was an offline live-oracle data-collection iteration. It did not train
PPO, SSH, deploy, run robot tests, touch hardware, or change runtime behavior.

## Input

- parent candidate: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- parent sha256: `f00ba8a89f4e24e7c393309acd434cbc95132473aa3df562dacf4fe527049822`
- corrected source manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0025`
- x=0.08 seeds: `0-7`
- x=0.0 seeds: `5`
- x=0.0 relabel mode: `zero_action`
- x=0.0 zero-action alpha: `0.50`
- evaluator platform: `cpu`

## Output Artifacts

Committed summary artifacts:

```text
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_iteration.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_x008_rollout.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_x0_rollout.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_x008_relabel.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_x0_relabel.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_x008_manifest.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_x0_manifest.json
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_aggregate_manifest.json
```

The full trace directory is about 95 MB because it includes full-observation
JSONL traces. Those raw traces remain local unless deliberately archived.

## x=0.08 Rollout Result

The parent/source candidate reproduced the prior positive-command result:

```text
status:                    PASS_CANDIDATE_SIM_GATE for all 8 seeds
duration complete:         8/8
falls:                     0/8
mean track ratio:          0.3742
mean local vx:             0.0299 m/s
max pitch velocity p95:    1.9234 rad/s
velocity excess:           0.0000
max tracking p95:          0.1953 rad
```

This confirms the z=0.0025 parent remains a useful positive-motion source under
the corrected bridge.

## x=0.0 Seed-5 Rollout Result

The targeted zero-command pocket was reproduced:

```text
status:                    HOLD_CANDIDATE_FALL_OR_TERMINATION
samples:                   43
termination:               fall_or_nan
mean local vx:             -0.3468 m/s
base height min:           0.0575 m
max pitch velocity p95:    0.5823 rad/s
velocity excess:           0.0000
max tracking p95:          0.2106 rad
```

This is not a velocity-envelope failure. It is still the seed-5 zero-command
support/collapse pocket.

## Relabel / Manifest Result

Relabeling completed:

```text
x=0.08 relabel:     8 traces, 6000 samples
x=0.0 relabel:      1 trace, 43 samples, zero_action alpha 0.50
x=0.08 manifest:    dataset_id 04447d35724a6b50, 8 entries, 6000 samples
x=0.0 manifest:     dataset_id bc49e139cbe6b1ea, 1 entry, 43 samples
aggregate manifest: dataset_id 8229af2c3e92a70d, 17 entries, 12043 samples
```

The aggregate manifest is ready for the next supervised student fit, but it is
not a candidate policy. The `x=0.0` seed-5 labels are corrective labels from a
failure pocket, not positive gait evidence; the next fit must be gated first on
the short `x=0.0` seed-5 repair check before any full-gate or A100 scaling.

## Decision

`PASS_DATA_READY__FIT_NEXT_STUDENT`

Next aligned step:

1. Fit the next deployable student from aggregate manifest
   `8229af2c3e92a70d`.
2. Gate immediately on short `z=0.0025`, `x=0.0`, seed 5.
3. Only if seed 5 survives, run full `x=0.0` seeds 0-7.
4. Only if zero-command passes, re-run full `x=0.08` seeds 0-7.
5. Do not run robot validation or push/terrain scaling from this data alone.
