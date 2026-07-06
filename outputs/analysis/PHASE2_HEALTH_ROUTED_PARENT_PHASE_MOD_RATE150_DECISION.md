# Phase 2 Health-Routed Parent Phase-Modulated Rate150 Decision

status: `PASS_HEALTH_ROUTED_PARENT_READY_FOR_PHASE2_DR_WARMSTART`

## Context

The eval-only health-gated router showed that passing behavior exists across
the compact z=0.0075 rough+push corrected-bridge screen by selecting different
iter24/iter25 branches from prefix-observable health metrics. That router is
not itself a deployable policy. This experiment compressed the selected passing
branches into one fixed-contract ONNX parent:

```text
obs[1,101] -> continuous_actions[1,14]
```

No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or PPO
training were performed.

## Training Data

The routed-pass x=0.08 manifest used the exact branches selected by the
health-gated router:

| seed | source branch |
|---:|---|
| 0 | iter24 |
| 1 | iter25 |
| 2 | iter24 |
| 6 | iter25 |
| 7 | iter24 |

This was merged with iter24 x=0.0 zero-action relabeled traces for command
semantics.

- x=0.08 manifest: `outputs/analysis/phase2_health_routed_pass_parent_x008_manifest.json`
- aggregate manifest: `outputs/analysis/phase2_health_routed_pass_parent_aggregate_manifest.json`
- aggregate entries: `7`
- aggregate samples: `5250`

## Candidate

- promoted ONNX: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- promoted ONNX sha256: `5cadefcb3582043eb989a0e7c65ea9e2702a0815ba46c9ffe1c70b1f68f1db8f`
- source ONNX: `outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate.onnx`
- source NPZ: `outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate_mlp.npz`
- source NPZ sha256: `1e22aa3c06a451e3ee4da32e58c6b45b881cdf87ea8ed8738c541b6dccb3e9c8`
- architecture: phase-modulated BC student
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- activation: `swish`
- modulation scale: `0.5`

## Fit Smoke

- status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- samples: `5250`
- MAE: `0.002635`
- p95 abs error: `0.007022`
- max abs error: `0.024591`
- target-rate p95: `1.368084 rad/s`
- target-rate max: `1.593542 rad/s`
- ONNX p95 abs error: `0.00000012`
- ONNX max abs error: `0.00000027`

## Corrected-Bridge Gates

Gate setup:

- task: `rough_terrain_backlash`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge mode: `fitted`
- terrain hfield z scale: `0.0075`
- push perturbations: enabled, `0.075-0.125`, interval `1.0-1.5 s`
- reset mode: `home-support`
- reset settle ticks: `10`
- duration: `15 s`

### x=0.08 Full8

- report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PASS_PARENT_PHASE_MOD_RATE150_X008_FULL8_GATE.md`
- JSON sha256: `2712b84d9e1c78c35b0edb3067d248459c9180ff56862a1043452f9ae6ecce02`
- duration complete: `8 / 8`
- falls: `0 / 8`
- mean vx: `0.027774 m/s`
- mean track ratio: `0.347175`
- body pitch p95 mean/max: `0.180684 / 0.207607 rad`
- base height min mean/min: `0.158173 / 0.155161 m`
- max pitch target velocity p95 mean/max: `1.544649 / 1.561374 rad/s`
- max tracking p95 mean/max: `0.186904 / 0.191429 rad`
- velocity-envelope excess p95/max: `0.000000 / 0.000000 rad/s`
- push success mean: `0.918590`

### x=0.0 Full8

- report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PASS_PARENT_PHASE_MOD_RATE150_X000_FULL8_GATE.md`
- JSON sha256: `7350a30fa46e14091eb794f33aa9206ff8b7255dd73dab1b9470859dcafacc3d`
- duration complete: `8 / 8`
- falls: `0 / 8`
- mean vx: `0.000821 m/s`
- body pitch p95 mean/max: `0.070467 / 0.074610 rad`
- base height min mean/min: `0.160952 / 0.160703 m`
- max pitch target velocity p95 mean/max: `0.034084 / 0.034779 rad/s`
- max tracking p95 mean/max: `0.042462 / 0.043771 rad`
- velocity-envelope excess p95/max: `0.000000 / 0.000000 rad/s`
- push success mean: `0.918590`

## Decision

This parent is the first compressed, deployable-shape policy in this line that
preserves both:

- x=0.08 rough+push forward walking under the corrected bridge across all 8
  seeds; and
- x=0.0 command semantics across all 8 seeds.

It is therefore the current Phase 2 DR warm-start candidate. Domain
randomization should start from this ONNX, not from the eval-only router and
not from the failed iter24-iter27 BC continuations.

Robot validation remains blocked. The next step is Stage A domain-randomized
offline training from this parent with weak/narrow randomization first, then
the same corrected-bridge x=0.08 and x=0.0 gates before widening the
curriculum.
