# Phase 2 Rate165 Motion-Preserve CPU2240 Result

status: `HOLD_MOTION_PRESERVE_STANDSTILL_REGRESSION`

## Summary

A tiny local CPU motion-preservation PPO smoke was run from the corrected
rate165 PPO-loc warm-start to test whether a stricter preservation recipe can
avoid the Stage A standstill collapse before spending another Colab/A100 run.

It did not preserve walking. The exported step-2240 ONNX remains stable and
in-envelope, but the `x=0.08` compact gate regressed to planted double support
with near-zero forward progress.

## Artifact

- exported ONNX:
  `outputs/phase2_domain_randomization/stage_a_rate165_motion_preserve_cpu_smoke/smoke_20260703T130458Z_cpu/2026_07_03_090613_2240.onnx`
- exported ONNX sha256:
  `6ec74a1e418e5725c351ffbb8dadc11b4f4619846d3c82be5c12048295cb157c`
- run manifest:
  `outputs/phase2_domain_randomization/stage_a_rate165_motion_preserve_cpu_smoke/smoke_20260703T130458Z_cpu/smoke_manifest.final.json`
- manifest status: `HOLD_SMOKE_EXCEPTION`
- elapsed: `236.63 s`

The wrapper reported a smoke exception around final process handling, but it
did export an ONNX. The ONNX was gated directly below; treat the direct gates as
the decision evidence.

## Compact x=0.08 Gate

Gate:

```text
rough_terrain_backlash
terrain_hfield_z_scale=0.0001
reset_mode=home-support
bridge=fitted
seed=0
duration=1s
jax_platform=cpu
```

Evidence:

```text
outputs/analysis/PHASE2_RATE165_MOTION_PRESERVE_CPU2240_X008_COMPACT_GATE.md
outputs/analysis/phase2_rate165_motion_preserve_cpu2240_x008_compact_gate.json
```

Result:

- status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
- duration complete: `1/1`
- falls: `0/1`
- mean local vx: `0.0032 m/s`
- track ratio: `0.0394`
- single support: `0%`
- double support: `100%`
- max pitch-chain velocity p95: `0.7096 rad/s`
- corrected p95/max velocity excess: `0`
- max tracking p95: `0.0967 rad`

## Compact x=0.0 Gate

Evidence:

```text
outputs/analysis/PHASE2_RATE165_MOTION_PRESERVE_CPU2240_X0_COMPACT_GATE.md
outputs/analysis/phase2_rate165_motion_preserve_cpu2240_x0_compact_gate.json
```

Result:

- status: `PASS_CANDIDATE_SIM_GATE`
- duration complete: `1/1`
- falls: `0/1`
- mean local vx: `-0.0027 m/s`
- single support: `0%`
- double support: `100%`
- max pitch-chain velocity p95: `0.5342 rad/s`
- corrected p95/max velocity excess: `0`
- max tracking p95: `0.0613 rad`

## Decision

Reject this motion-preservation PPO smoke as a Phase 2 training path. It
preserves in-envelope quiet behavior, but it does so by collapsing the walking
warm-start back into planted double support.

Do not scale this exact recipe to a longer A100 run. The next offline training
attempt needs a stronger anti-standstill mechanism or a different student
training structure that preserves single-support walking before any domain
randomization escalation.
