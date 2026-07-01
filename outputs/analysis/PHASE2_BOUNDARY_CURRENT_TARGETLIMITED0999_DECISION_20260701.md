# Phase 2 Current Target-Limited Terrain Boundary Decision

status: `HOLD_SEED5_SUPPORT_BOUNDARY_BELOW_Z003`

This is an offline sim/eval decision artifact. No robot test, SSH, deploy,
grounded replay, training, tuning, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- prior pass: `outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md`
- prior hold: `outputs/analysis/PHASE2_Z005_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_NOPUSH_DECISION_20260701.md`
- failure trace: `outputs/analysis/PHASE2_Z005_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_FAILURE_TRACE_DECISION_20260701.md`

## Boundary Screen

The screen tested the current target-limited command-gated candidate at
`x=0.08`, `rough_terrain_backlash`, corrected fitted bridge, no push, CPU
evaluator, seeds `1` and `5`.

Artifacts:

- `outputs/analysis/PHASE2_BOUNDARY_CURRENT_TARGETLIMITED0999_Z003_X008_SEED1_5.md`
- `outputs/analysis/phase2_boundary_current_targetlimited0999_z003_x008_seed1_5.json`
- `outputs/analysis/PHASE2_BOUNDARY_CURRENT_TARGETLIMITED0999_Z0035_X008_SEED1_5.md`
- `outputs/analysis/phase2_boundary_current_targetlimited0999_z0035_x008_seed1_5.json`
- `outputs/analysis/PHASE2_BOUNDARY_CURRENT_TARGETLIMITED0999_Z004_X008_SEED1_5.md`
- `outputs/analysis/phase2_boundary_current_targetlimited0999_z004_x008_seed1_5.json`

## Result

| terrain z | seed | status | samples | mean vx | track ratio | base height min | max pitch vel p95 | p95 excess | max excess | max tracking p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0030 | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0337 | 0.4214 | 0.1563 | 1.9232 | 0.0000 | 0.0000 | 0.1898 |
| 0.0030 | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 58 | -0.2465 | -3.0808 | 0.0788 | 1.8181 | 0.0000 | 0.0000 | 0.1844 |
| 0.0035 | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0316 | 0.3944 | 0.1564 | 1.9226 | 0.0000 | 0.0000 | 0.1917 |
| 0.0035 | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | -0.2577 | -3.2214 | 0.0740 | 1.8362 | 0.0000 | 0.0000 | 0.1890 |
| 0.0040 | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0310 | 0.3869 | 0.1564 | 1.9225 | 0.0000 | 0.0000 | 0.1941 |
| 0.0040 | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.2586 | -3.2330 | 0.0711 | 1.7621 | 0.0000 | 0.0000 | 0.1870 |

## Interpretation

The current target-limited candidate has meaningful terrain margin on seed 1:
it completes the full `15 s` at z `0.003`, `0.0035`, and `0.004` while staying
inside the corrected target-rate envelope.

Seed 5 remains the terrain-support boundary. It fails at all three tested
heights after roughly `56-58` samples, with backward velocity, low base height,
and zero corrected-envelope velocity excess. This matches the z=0.005 trace
diagnosis and rules out target-rate limiting as the next lever.

## Decision

Do not launch a direct z=0.005 reward-side support recipe from the current
state. The next useful Phase 2 step is a seed-5 support curriculum immediately
above the known passing terrain rung, not a broad terrain jump:

1. bracket the exact seed-5 cliff between z `0.0025` and z `0.0030` if more
   precision is needed;
2. train or source-mine at the smallest failing terrain height, with seed-5
   `x=0.0` support survival as the first gate;
3. preserve the z=0.0025 no-push/stronger-push passes and x=0.0 semantics;
4. only return to z=0.005 after seed 5 survives the intermediate support rung
   without corrected-envelope excess.

Robot validation remains blocked.
