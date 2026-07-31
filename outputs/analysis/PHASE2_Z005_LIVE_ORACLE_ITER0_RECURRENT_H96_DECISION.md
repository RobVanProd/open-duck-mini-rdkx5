# Phase 2 z=0.005 Live-Oracle Iter0 Recurrent H96 Decision

status: `HOLD_ITER0_RECURRENT_CLOSED_LOOP_UNSTABLE`

This is an offline recurrent diagnostic. It did not run robot tests, SSH,
deploy, grounded replay, PPO training, or runtime behavior changes.

## Fit

- manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0_aggregate_manifest.json`
- samples: `12806`
- sequences: `18`
- model: recurrent BC diagnostic, hidden dim `96`, sequence length `32`
- ONNX: `outputs/analysis/phase2_z005_live_oracle_iter0_recurrent_h96_candidate/candidate.onnx`
- ONNX sha256: `cadf7e0a2c47691d230a062755aaff7d8f7dbfc5d2b9fac341838a00c5dd2363`
- p95 action error: `0.044005`
- target-rate p95: `1.717053 rad/s`
- target-rate max: `3.890466 rad/s`
- ONNX action fidelity max error: `0.00000053`
- ONNX hidden fidelity max error: `0.00000072`

The recurrent fit is diagnostic only. It is not robot-deployable without a
runtime hidden-state adapter.

## z=0.005 x=0.08 Stateful Gate

- gate report: `outputs/analysis/PHASE2_Z005_LIVE_ORACLE_ITER0_RECURRENT_H96_GATE_X008.md`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- bridge: corrected fitted bridge
- stateful policy flags: `obs`, `continuous_actions`, `h_in`, `h_out`
- seeds: `0-7`
- duration: `15s`

| metric | value |
|---|---:|
| pass seeds | 0 / 8 |
| falls | 8 / 8 |
| duration complete | 0 / 8 |
| samples mean | 124 |
| mean track ratio | -1.2363 |
| mean vx | -0.0989 m/s |
| p95 velocity excess mean | 3.2400 rad/s |
| max pitch vel p95 | 5.2400 rad/s on every seed |
| max tracking p95 range | 0.1895-0.2503 rad |

The recurrent policy destabilizes faster than the phase-modulated feed-forward
student and hits the simulator's 5.24 rad/s target slew ceiling on every seed.

## Decision

Do not promote this ONNX. Do not continue supervised-rate-only recurrent BC
tweaks on this aggregate.

The result falsifies the simple "memory alone fixes z=0.005" explanation for
this iter0 data. The next branch needs a stronger corrected z=0.005 source or
closed-loop correction pressure that changes the seed-5 support state, not a
larger hidden state or another scalar target-rate penalty.
