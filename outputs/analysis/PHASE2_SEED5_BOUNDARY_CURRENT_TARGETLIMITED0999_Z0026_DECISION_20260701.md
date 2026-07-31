# Phase 2 Seed-5 z=0.0026 Boundary Decision

status: `HOLD_SEED5_SUPPORT_FAILS_AT_Z0026`

This is an offline sim/eval decision artifact. No robot test, SSH, deploy,
grounded replay, training, tuning, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- parent boundary decision: `outputs/analysis/PHASE2_BOUNDARY_CURRENT_TARGETLIMITED0999_DECISION_20260701.md`

## Screen

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0026`
- bridge_mode: `fitted`
- seed: `5`
- duration: `15 s`
- push: disabled
- JAX platform: `cpu`

Artifacts:

- `outputs/analysis/PHASE2_SEED5_BOUNDARY_CURRENT_TARGETLIMITED0999_Z0026_X008.md`
- `outputs/analysis/phase2_seed5_boundary_current_targetlimited0999_z0026_x008.json`

## Result

| seed | status | samples | termination | mean vx | track ratio | base height min | max pitch vel p95 | p95 excess | max excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.2573 | -3.2164 | 0.0710 | 1.8292 | 0.0000 | 0.0000 | 0.1874 |

## Decision

Seed 5 fails at z `0.0026`, immediately above the z `0.0025` pass, with the
same early reverse/support-collapse signature seen at higher terrain heights.
The failure still has zero corrected-envelope velocity excess.

Do not use z `0.0030`, z `0.0035`, or z `0.005` as the next training rung for
this candidate lineage. The next trainable curriculum should target the narrow
z `0.0025 -> 0.0026` transition, with seed-5 support survival as the first
gate.

The attempted z `0.0027+` bracket loop was stopped after z `0.0026` failed,
because higher terrain heights are redundant once the first failing height is
identified.

Robot validation remains blocked.
