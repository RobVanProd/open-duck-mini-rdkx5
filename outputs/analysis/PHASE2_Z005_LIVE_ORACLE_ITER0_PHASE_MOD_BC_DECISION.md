# Phase 2 z=0.005 Live-Oracle Iter0 Phase-Mod BC Decision

status: `HOLD_ITER0_PHASE_MOD_STUDENT_NOT_PROMOTABLE`

This is an offline student-fit/gate decision. It did not run robot tests, SSH,
deploy, grounded replay, PPO training, or runtime behavior changes.

## Fit

- manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0_aggregate_manifest.json`
- samples: `12806`
- model: phase/command-modulated feed-forward BC student
- ONNX: `outputs/analysis/phase2_z005_live_oracle_iter0_phase_mod_bc_candidate/candidate.onnx`
- ONNX sha256: `2fb9e4c791970dae3dc3069aa5fc037bb51b4fbc9e91d8938c44e80d1bf1e3ef`
- p95 action error: `0.018830`
- target-rate p95: `1.783167 rad/s`
- target-rate max: `2.163395 rad/s`
- ONNX fidelity max error: `0.00000021`

The supervised fit itself is clean and in-envelope. The closed-loop gate did
not pass.

## z=0.005 x=0.08 Gate

- gate report: `outputs/analysis/PHASE2_Z005_LIVE_ORACLE_ITER0_PHASE_MOD_BC_GATE_X008.md`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- bridge: corrected fitted bridge
- seeds: `0-7`
- duration: `15s`

| metric | value |
|---|---:|
| pass seeds | 1 / 8 |
| duration complete | 7 / 8 |
| falls | 1 / 8 |
| mean track ratio | -0.1398 |
| mean vx | -0.0112 m/s |
| p95 velocity excess mean | 0.0000 |
| max velocity excess mean | 0.0387 |
| max tracking p95 range | 0.1886-0.1984 rad |
| single support mean | 20.72% |
| double support mean | 78.57% |

Seed 5 still terminates early at 54 samples with backward velocity and low base
height. The surviving seeds are mostly stable but under-progress, so this fit
reduced target-rate demand without solving the z=0.005 support/forward-motion
problem.

## Decision

Do not promote this ONNX. Do not run robot validation. Do not run x=0.0 gate as
a promotion check because x=0.08 already failed.

The result is useful as a first live-oracle student datapoint:

- the aggregate manifest can be fit cleanly into a deployable ONNX,
- rate demand is low and within the corrected bridge envelope,
- the seed-5 terrain support collapse survives distillation,
- the source/oracle is still too weak or too double-support-heavy for z=0.005.

Next offline work should change the source/representation, not apply another
scalar reward tweak. Viable next branches:

1. collect an additional live-oracle iteration from this student's z=0.005
   visited states, but only if the oracle/source is strengthened for seed-5
   support states;
2. move to the next representation rung with explicit frame history or
   recurrence for diagnostic comparison;
3. build a stronger corrected z=0.005 support source instead of relying on
   z=0.0024 pass traces.
