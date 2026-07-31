# Phase 2 Iter3 Phase-Modulated Rate180 Decision

status: `PASS_PHASE2_RATE180_CORRECTED_BRIDGE_GATES`
generated_at: `2026-07-03T19:45:18Z`

Offline-only behavior-cloning fit and corrected-bridge seed gates. No robot
test, SSH, deploy, grounded replay, runtime behavior change, or PPO training was
performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_20260703/candidate.onnx`
- ONNX sha256: `b658c3380d1ad3dbd8912c988a3ff0e4b019735f220cf56351e9c783f328d5b1`
- NPZ: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_20260703/student.npz`
- NPZ sha256: `6ecbeffc9037658386b3ec2c3722f30e5dc5ae31547c7182550140e11666a505`
- source manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- contract: `obs[1,101] -> continuous_actions[1,14]`

## Fit

| metric | value |
|---|---:|
| samples | 40500 |
| action MAE | 0.007582 |
| action p95 abs error | 0.024502 |
| action max abs error | 0.318274 |
| target-rate p95 | 1.394986 rad/s |
| target-rate max | 2.009591 rad/s |
| ONNX verify max abs error | 0.00000024 |

## Corrected-Bridge Gates

Both gates used `rough_terrain_backlash`, z=0.0026, `home-support` reset,
fitted corrected-knee actuator bridge, CPU evaluator, 15s duration, and seeds
0-7.

| command | status | seeds | falls | track ratio | mean vx | max pitch vel p95 | max vel excess | max tracking p95 | support |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0.08 | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.440467 | 0.035237 | 1.771620 | 0.000000 | 0.189108 | 28.0% single |
| 0.00 | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | NA | 0.000169 | 0.047043 | 0.000000 | 0.033892 | 100.0% double |

The x=0.08 gate also passed the explicit swing gates:

- min swing segments: `18`
- min swing rel-x range p95: `0.011434 m`
- min swing peak lift: `0.014507 m`

## Decision

Promote this as the current offline Phase 2 corrected-bridge candidate for the
next robustness step. Do not run grounded validation from this decision alone.
The next offline step is to evaluate this candidate under the next staged
Phase 2 robustness screen, starting with weak dynamics randomization and gentle
pushes before widening terrain or disturbance ranges.
