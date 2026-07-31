# Phase 2 Full-8 Router Trainable Conversion Decision

status: `HOLD_TRAINABLE_ROUTER_COMPRESSION_NOT_PROMOTABLE`

## Router Source

The promoted router remains the current deployable offline source, but it is an ONNX router composition rather than a PPO-restorable checkpoint. Full-observation traces were regenerated from the router to test whether its behavior can be compressed into a PPO-compatible single actor.

- router x=0.08: `8/8` duration complete, falls `0`, mean vx `0.0276`, velocity excess max `0.0000`
- router x=0.0: `8/8` duration complete, falls `0`, mean vx `0.0007`, velocity excess max `0.0000`

## Trace Dataset

- manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json`
- status: `PASS_BC_TRACE_MANIFEST_READY`
- entries: `16`
- samples: `12000`

## PPO-Loc Compression Results

| student | fit status | train p95 abs error | target-rate max | x=0.08 passes | falls | mean vx | velocity excess max | decision |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `unweighted` | `PASS_PPO_LOC_BC_FIT_SMOKE` | `0.004127` | `1.8881` | `6/8` | `2` | `0.0365` | `0.0000` | HOLD, not DR warm-start |
| `seed56_weighted` | `PASS_PPO_LOC_BC_FIT_SMOKE` | `0.004912` | `1.8650` | `6/8` | `2` | `0.0408` | `0.0000` | HOLD, not DR warm-start |

## Decision

Do not launch domain-randomized PPO from either PPO-loc student. Both preserve low target-rate behavior in supervised fit metrics but fail the closed-loop x=0.08 full-8 corrected-bridge gate at seeds 5 and 6. This keeps Phase 2 DR blocked on a trainable warm-start conversion, not on the deployable router source.

recommended_next: `Use the captured full-observation router traces for a branch-aware/stateful trainable conversion or online DAgger; do not launch DR from the failing PPO-loc students.`

No robot, SSH, deploy, grounded replay, or runtime behavior change was performed.
