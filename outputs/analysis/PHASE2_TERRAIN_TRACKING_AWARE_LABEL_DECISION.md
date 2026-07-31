# Phase 2 Terrain Tracking-Aware Label Decision

status: `HOLD_TRACKING_AWARE_LABEL_FILTER_FREEZES`

This is an offline sim/data-curation result. It did not run robot tests, SSH,
deploy, grounded replay, or change robot runtime behavior.

## Question

Can the terrain live-oracle DAgger tracking plateau be fixed by rate-limiting
the oracle labels before fitting another PPO-compatible BC student?

## Inputs

- Source relabel traces:
  `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x008/rollouts_x008/student/seed_*/trace.jsonl`
- Preserved source slices:
  `outputs/analysis/phase2_terrain_safe_hard_step_slices/z0p*/seed_*/trace.jsonl`
- Zero-command trace:
  `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl`

## Label Filter

The offline label filter clipped pitch-chain action deltas to an equivalent
`2.25 rad/s` target-rate cap:

```text
left_hip_pitch, left_knee, left_ankle,
right_hip_pitch, right_knee, right_ankle
```

Artifacts:

```text
outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_LABEL_RATE_LIMIT.md
outputs/analysis/phase2_terrain_tracking_aware_label_rate_limit.json
outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_BC_MANIFEST.md
outputs/analysis/phase2_terrain_tracking_aware_bc_manifest.json
```

Result:

```text
traces clipped: 2
samples clipped source: 500
changed ticks: 343
changed contact counts: 01=28, 10=57, 11=258
```

Most edits occurred during double support, so the filter mainly damped
transition labels rather than producing a cleaner swing/advance transition.

## Student Fit

Artifact:

```text
outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_BC_STUDENT.md
outputs/analysis/phase2_terrain_tracking_aware_bc_student.json
```

Fit result:

```text
status: PASS_PPO_LOC_BC_FIT_SMOKE
samples: 1150
p95 action error: 0.023855
target-rate p95: 1.940176 rad/s
target-rate max: 2.531113 rad/s
```

The supervised fit was smooth and in-family, but this is not a candidate gate.

## Closed-Loop Gate

Artifact:

```text
outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
outputs/analysis/phase2_terrain_tracking_aware_bc_student_terrain_z002_gate_cpu.json
```

Gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted bridge
command_x: 0.08
duration: 5 s
seeds: 2,4
hard swing gate: enabled
```

Result:

| seed | status | vx | track ratio | max vel excess | max tracking p95 | single support | double support |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0107 | 0.1335 | 0.0507 | 0.2094 | 10.0% | 90.0% |
| 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0105 | 0.1314 | 0.0000 | 0.1963 | 4.0% | 96.0% |

## Decision

`HOLD_TRACKING_AWARE_LABEL_FILTER_FREEZES`

The label-rate cap nearly removed corrected-envelope excess and reduced
tracking pressure, but it also collapsed the gait into low-progress,
double-support stepping. This closes the simple global pitch-chain label filter
as the next candidate path.

Do not promote this student. Do not run robot validation. The next terrain
branch needs a label/training mechanism that preserves the swing/advance
transition while keeping the corrected per-joint envelope, not a global
smoothing pass that damps the transition away.
