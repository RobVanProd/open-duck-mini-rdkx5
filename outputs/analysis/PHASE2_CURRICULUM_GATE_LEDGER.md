# Phase 2 Curriculum Gate Ledger

status: `PASS_PHASE2_CURRICULUM_GATES_READY_TO_ADVANCE`
generated_at: `2026-07-04T01:16:36Z`

This is a read-only stage-advancement ledger. It did not train, SSH, deploy, or touch the robot.

## Candidate

- candidate: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- candidate_sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`

## Stage Status

| stage | status | held gates | missing gates | advance if pass |
|---|---|---|---|---|
| `stage_a2_z002_regression` | `PASS_STAGE` | `none` | `none` | `stage_z005_support` |
| `stage_z005_support` | `PASS_STAGE` | `none` | `none` | `stage_z005_gentle_push` |
| `stage_z005_gentle_push` | `PASS_STAGE` | `none` | `none` | `stage_z005_stronger_push_or_terrain` |

## Gate Matrix

| gate | status | runs | falls | complete | x | z | push | track ratio mean | vx mean | max tracking p95 | max vel excess | push success | reasons |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| `z002_x008_nopush` | `PASS_GATE` | 8 | 0 | 8 | 0.080 | 0.002 | `False` | 0.3787 | 0.0303 | 0.1888 | 0.0000 | NA | none |
| `z002_x000_nopush` | `PASS_GATE` | 8 | 0 | 8 | 0.000 | 0.002 | `False` | NA | 0.0001 | 0.0328 | 0.0000 | NA | none |
| `z002_x008_gentle_push` | `PASS_GATE` | 8 | 0 | 8 | 0.080 | 0.002 | `True` | 0.3806 | 0.0304 | 0.1892 | 0.0000 | 0.9704 | none |
| `z002_x000_gentle_push` | `PASS_GATE` | 8 | 0 | 8 | 0.000 | 0.002 | `True` | NA | 0.0002 | 0.0374 | 0.0000 | 0.9704 | none |
| `z005_x008_nopush` | `PASS_GATE` | 8 | 0 | 8 | 0.080 | 0.005 | `False` | 0.3715 | 0.0297 | 0.1838 | 0.0000 | NA | none |
| `z005_x000_nopush` | `PASS_GATE` | 8 | 0 | 8 | 0.000 | 0.005 | `False` | NA | 0.0005 | 0.0345 | 0.0000 | NA | none |
| `z005_x008_gentle_push` | `PASS_GATE` | 8 | 0 | 8 | 0.080 | 0.005 | `True` | 0.3829 | 0.0306 | 0.1890 | 0.0000 | 0.9704 | none |
| `z005_x000_gentle_push` | `PASS_GATE` | 8 | 0 | 8 | 0.000 | 0.005 | `True` | NA | 0.0005 | 0.0402 | 0.0000 | 0.9704 | none |

## Decision

- current_stage: `stage_z005_stronger_push_or_terrain`
- decision: required gates are clear for the next curriculum rung.
