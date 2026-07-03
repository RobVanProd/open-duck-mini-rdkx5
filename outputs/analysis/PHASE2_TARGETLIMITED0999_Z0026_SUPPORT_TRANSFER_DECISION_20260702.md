# Phase 2 Target-Limited z=0.0026 Support-Transfer Decision

status: `HOLD_Z0026_MOVING_COMMAND_SUPPORT_TRANSFER`

## Summary

The current target-limited command-gated baseline already solves the current
`z=0.0025` rough-terrain rung. The next terrain step, `z=0.0026`, fails on
seed 5 under moving command, but not as a simple zero-command reset collapse.

At `z=0.0026`, `x=0.0` seed 5 survives the 2-second short gate in-envelope.
At the same terrain height, `x=0.08` seed 5 falls at 57 samples with reverse
velocity and height collapse, while staying inside the corrected actuator
velocity envelope.

This was offline sim/eval/analysis only. No robot test, SSH, deploy, grounded
replay, training, tuning, policy overwrite, or runtime behavior change was
performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0026`
- bridge_mode: `fitted`
- jax_platform: `cpu`

## Short Gates

Artifacts:

- `outputs/analysis/PHASE2_TARGETLIMITED0999_Z0026_X0_SEED5_SHORT.md`
- `outputs/analysis/phase2_targetlimited0999_z0026_x0_seed5_short.json`
- `outputs/analysis/PHASE2_TARGETLIMITED0999_Z0026_X008_SEED5_TRACE_SHORT.md`
- `outputs/analysis/phase2_targetlimited0999_z0026_x008_seed5_trace_short.json`

| command | seed | status | samples | mean vx | track ratio | base min | max pitch vel p95 | p95 vel excess | max tracking p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `0.00` | 5 | `HOLD_CANDIDATE_TRACKING` | 100 | 0.0123 | NA | 0.1457 | 2.8524 | 0.0000 | 0.2042 |
| `0.08` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.2573 | -3.2164 | 0.0710 | 1.8292 | 0.0000 | 0.1874 |

## Trace Analysis

Artifact:

- `outputs/analysis/PHASE2_TARGETLIMITED0999_Z0026_X008_SEED5_TRACE_ANALYSIS.md`
- `outputs/analysis/phase2_targetlimited0999_z0026_x008_seed5_trace_analysis.json`

The `x=0.08` failure is classified as:

```text
REVERSE_HEIGHT_COLLAPSE
```

Key onset events:

- first no-contact: tick `0`
- first one-foot contact: tick `5`
- first reverse velocity: tick `10` / `0.20 s`
- first low height: tick `54` / `1.08 s`
- done/fall: tick `56` / `1.12 s`

Contact distribution during the failed trace:

- no contact `(0,0)`: `5` samples
- left-only/right-only one-foot support: `6` samples total
- double support `(1,1)`: `46` samples

Pitch-chain velocity stayed inside the corrected envelope. Max p95 target
velocity was `1.8292 rad/s`; max instantaneous pitch-chain target velocity was
within limits. The failure is therefore not caused by actuator over-commanding.

## Decision

The next Phase 2 repair should target moving-command support transfer at the
smallest failing terrain step, `z=0.0026`, with seed 5 as the first gate.

Do not spend the next run on:

- another zero-command-only seed-5 reset repair;
- BEST zero-command support scaling;
- a direct jump to `z=0.003+` or `z=0.005`;
- global progress-pressure or scalar reward retuning.

Recommended next branch:

```text
Use the target-limited command-gated candidate as the parent.
Train or synthesize a z=0.0026 seed-5 moving-support correction at x=0.08,
preserving the existing z=0.0025 x=0.0/x=0.08 stronger-push pass and corrected
velocity-envelope compliance.
```

Immediate gates for that branch:

1. `z=0.0026`, `x=0.08`, seed 5, short 2-second gate: must remove the
   reverse-height collapse without velocity excess.
2. `z=0.0026`, `x=0.0`, seed 5, short 2-second gate: must preserve standing
   semantics and support.
3. Only then run 8-seed/full-duration gates.
