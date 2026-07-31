# Phase 2 z0.0026 Corrected Source Live-Oracle Iter0 Phase/Contact Student

status: `HOLD_ITER0_PHASE_CONTACT_LOW_PROGRESS`

## Summary

The corrected `z=0.0026` live-oracle iteration completed data collection,
relabeling, aggregate-manifest construction, and a first deployable
phase/contact-modulated BC student fit.

The student is stable and safely inside the corrected actuator envelope, but it
does not preserve enough of the source gait's forward motion. It holds the
`x=0.08` gate for low forward progress, not for fall, not for over-envelope
target rate, and not for seed fragility.

No robot test, SSH, deploy, grounded replay, PPO training, or runtime behavior
change was performed.

## Data Iteration

Iteration artifact:

```text
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/live_oracle_dagger_iteration.json
```

Status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`

Conditions:

- student: `policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
- teacher manifest:
  `outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json`
- task: `rough_terrain_backlash`
- terrain hfield z-scale: `0.0026`
- reset mode: `home-support`
- bridge: corrected fitted bridge
- `x=0.08` seeds: `0..7`
- `x=0.0` seeds: `0..1`

Aggregate manifest:

```text
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/live_oracle_dagger_aggregate_manifest.json
```

Aggregate status: `PASS_FILTERED_BC_MANIFEST_READY`

- dataset id: `3cd753b3ccf6ef63`
- input entries: `18`
- kept entries: `18`
- rejected entries: `0`
- samples: `13500`
- source files: `18`

## Student Fit

Student:

```text
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_phase_contact_student/candidate.onnx
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_phase_contact_student/candidate_mlp.npz
```

Hashes:

- ONNX sha256:
  `d6eaf8ed1d81e4adb9edb5858639da03e1b9001eaf99f13accdd2918029985f4`
- NPZ sha256:
  `8b257a56a48b31d04afe5cb9e41f2e5958029177dfcd2ae5b9fb0391a13f75bc`

Fit artifact:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER0_PHASE_CONTACT_STUDENT.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_phase_contact_student.json
```

Fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

- samples: `13500`
- context indices: `[6, 97, 98, 99, 100]`
- MAE: `0.002194`
- p95 action error: `0.005862`
- max action error: `0.015811`
- target-rate p95: `1.504374 rad/s`
- target-rate max: `1.771649 rad/s`
- ONNX p95 abs error: `0.00000012`
- ONNX max abs error: `0.00000024`

## Corrected x=0.08 Gate

Gate artifact:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER0_PHASE_CONTACT_X008_GATE.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_phase_contact_x008_gate.json
```

Result: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

- `8/8` seeds completed full duration.
- falls: `0/8`
- mean local vx: `0.0106 m/s`
- track ratio: `0.1326`
- body pitch p95: `0.1156 rad`
- base height min: `0.1523 m`
- max pitch-chain p95 velocity: `1.6166 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0000 rad/s`
- max tracking p95: `0.1642 rad`
- single support: `8.8000%`
- double support: `91.2000%`

## Interpretation

Compared with the corrected source parent:

| metric | source parent | iter0 phase/contact student |
|---|---:|---:|
| track ratio | `0.4130` | `0.1326` |
| mean vx | `0.0330` | `0.0106` |
| max pitch vel p95 | `1.7269` | `1.6166` |
| max tracking p95 | `0.1859` | `0.1642` |
| single support | `27.7333%` | `8.8000%` |
| double support | `72.2667%` | `91.2000%` |

The deployable student retained low target rates and stability but smoothed away
the stance-transition behavior that creates forward motion. This is the same
motion-attenuation family seen in earlier memoryless distillations, now
reproduced under the corrected bridge and `z=0.0026` home-support gate.

Do not promote this candidate and do not run robot validation. The next
authorized step is another live-oracle iteration on the student's own
low-progress rollout states or a representation change with explicit state
memory. Do not return to scalar reward-only A100 continuation for this failure.
