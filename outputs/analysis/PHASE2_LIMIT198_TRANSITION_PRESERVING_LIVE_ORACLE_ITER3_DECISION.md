# Phase 2 Limit198 Transition-Preserving Live-Oracle Iter3 Decision

status: `PASS_LIVE_ORACLE_ITER3_DATA_READY`
generated_at: `2026-07-03T18:42:55Z`

Offline-only data-generation run. No robot test, SSH, deploy, grounded replay,
runtime behavior change, or PPO training was performed.

## Config

- student policy: `policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx`
- teacher manifest: `outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0026`
- reset mode: `home-support`
- bridge mode: `fitted`
- JAX platform: `cpu`
- duration: `15.0s`
- x=0.08 seeds: `0-7`
- x=0.0 seeds: `0-7`
- x=0.08 teacher: `source_vx_blend`
- x=0.0 teacher: `zero_action`
- swing gates: `segments>=1`, `rel_x_range_p95>=0.003m`, `peak_lift>=0.005m`

## x=0.08 Rollout

The current student passed the rough-terrain z=0.0026 corrected-bridge screen on
all eight seeds. This is evidence that the live-oracle collection path is usable;
it is not a new promoted candidate.

| metric | value |
|---|---:|
| runs | 8 |
| duration complete | 8 |
| falls | 0 |
| mean local vx | 0.026152 m/s |
| track ratio | 0.326902 |
| body pitch p95 | 0.132014 rad |
| base height min | 0.152235 m |
| max pitch vel p95 | 1.750218 rad/s |
| p95 velocity excess | 0.000000 rad/s |
| max velocity excess | 0.000000 rad/s |
| max tracking p95 | 0.189158 rad |
| min swing peak lift | 0.012331 m |
| min swing segments | 18 |
| min swing rel-x range p95 | 0.011641 m |
| single support | 25.20% |
| double support | 74.80% |

## x=0.0 Rollout

The zero-command pass confirms the collection recipe preserves command
conditioning while adding zero-action labels for the standing state.

| metric | value |
|---|---:|
| runs | 8 |
| duration complete | 8 |
| falls | 0 |
| mean local vx | 0.000062 m/s |
| body pitch p95 | 0.016838 rad |
| base height min | 0.152360 m |
| max pitch vel p95 | 0.056107 rad/s |
| p95 velocity excess | 0.000000 rad/s |
| max velocity excess | 0.000000 rad/s |
| max tracking p95 | 0.031987 rad |
| single support | 0.00% |
| double support | 100.00% |

## Relabel And Manifest

| artifact | status | entries/traces | samples |
|---|---|---:|---:|
| x=0.08 relabel | `PASS_BC_TRACE_RELABEL_READY` | 8 | 6000 |
| x=0.0 relabel | `PASS_BC_TRACE_RELABEL_READY` | 8 | 6000 |
| x=0.08 manifest | `PASS_BC_TRACE_MANIFEST_READY` | 8 | 6000 |
| x=0.0 manifest | `PASS_BC_TRACE_MANIFEST_READY` | 8 | 6000 |
| aggregate manifest | `PASS_FILTERED_BC_MANIFEST_READY` | 54 | 40500 |

The aggregate manifest rejected 0 entries and is ready for the next supervised
transition-preserving student fit.

## Decision

Proceed to fit a phase/contact or transition-preserving student from the
aggregate manifest, then run the canonical corrected-bridge x=0.08 and x=0.0
gates before any Phase 2 randomization widening. Do not promote this data
collection run as a robot candidate and do not start grounded validation from it.
