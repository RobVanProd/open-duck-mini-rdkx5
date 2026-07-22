# Winner-v54 residual-teacher causal result

## Decision

- Status: `PASS_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC`.
- Decision: `SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY`.
- Result SHA-256:
  `74d2e7f2e8009eedd0c425aff575b136ef0cac5e1cd233072915c6f2a3de2680`.
- Preregistration SHA-256:
  `eeaca1134b4562ca93a8d33860d92ddba532e84fd3691454703023edd1b2b24b`.

The exact frozen 48-cell diagnostic passed all seven formal checks. It
performed no optimizer update, locomotion training, graph selection, robot or
RDK-X5 access, torque, or motion.

## Frozen intervention result

| Arm | Support passes | Total |
| --- | ---: | ---: |
| unchanged graph | 0 | 12 |
| full 14-D teacher | 12 | 12 |
| pitch teacher | 11 | 12 |
| graph pitch with non-pitch zeroed | 0 | 12 |

All 12 unchanged graph cells reproduce the corresponding Winner-v53 cells
bit-exactly. Every previous-action chain is exact, every JAX/ONNX hidden-state
comparison is at most `1e-7`, and all values are finite.

The preregistered classification is therefore:

- `pitch_output_causal`: 11 cells.
- `pitch_nonpitch_interaction`: 1 cell,
  `DISCOVERY_03 / P31_34_PITCH_WITH_P30_NONPITCH`.
- `teacher_insufficient`: 0 cells.
- `nonpitch_output_causal`: 0 cells.
- `either_single_intervention_rescues`: 0 cells.

The frozen full teacher passes all 12 cells, so the source teacher table is
sufficient for this population. Replacing only the six pitch-chain actions
rescues every cell except the one classified interaction. Zeroing non-pitch
outputs never rescues a cell.

## Alignment evidence

Across the 12 failed graph cells, the candidate-versus-bounded-teacher RMS
error averages `0.08516398383512673` over the six pitch-chain actions but only
`0.006177789539157603` over the eight non-pitch actions. Relative to the older
pitch-only source examined in Winner-v48, full-action training substantially
reduced mean non-pitch RMS (`0.024637238259528724` to
`0.006177789539157603`) while reducing mean pitch RMS only from
`0.09177286701325851` to `0.08516398383512673`.

This result does not authorize simply extending or rescaling the closed
full-action objective. It selects a prospective mechanism investigation aimed
at why the deployable graph cannot reproduce the configuration-specific pitch
teacher early enough. Existing response-identifiability evidence must be
audited before any new optimizer run is preregistered.

## Authority

Robot clearance remains false. This result authorizes only a separate,
prospective CPU-only preregistration derived from this frozen classification.
No deployment checkpoint, runtime asset freeze, Gate 5, hardware access,
torque, or motion is authorized.
