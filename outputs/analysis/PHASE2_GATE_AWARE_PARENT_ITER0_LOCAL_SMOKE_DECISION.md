# Phase 2 Gate-Aware Parent Iter0 Local Smoke Decision

status: `HOLD_GATE_AWARE_PARENT_REWARDED_FREEZE`

This was an offline local ROCm smoke run only. It did not SSH, deploy, touch
the robot, run grounded replay, or modify robot runtime behavior.

## Restore Point

- source checkpoint: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_checkpoint`
- source ONNX: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0.onnx`
- source ONNX sha256: `d7af39a6255f7303a742b07ac87333c503534c73bd5b16766fa2ad3f4ae1e28f`

## Training Smoke

- output dir: `outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke/smoke_20260705T151050Z_gpu`
- final manifest: `outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke/smoke_20260705T151050Z_gpu/smoke_manifest.final.json`
- status: `PASS_SMOKE_RUN`
- elapsed: `480.0 s`
- platform request: `gpu` / `rocm`
- local JAX observed before launch: `0.8.2`, backend `gpu`, device `RocmDevice(id=0)`
- restore-policy KL scale: `8.0`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0075`
- push range: `0.075-0.125`
- robot touched: `false`

Exported ONNX artifacts:

| step | ONNX | sha256 |
|---:|---|---|
| 15360 | `outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke/smoke_20260705T151050Z_gpu/2026_07_05_111520_15360.onnx` | `8179d5686d3dc242c3a05f4d47747c62ab1e60256009605a1e65e0b6053acfc2` |
| 30720 | `outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke/smoke_20260705T151050Z_gpu/2026_07_05_111742_30720.onnx` | `9d246a73b1542e669e38b69094dbce6f1b998ae0ac1493f3dd09d6cdc3a5e84d` |
| 46080 | `outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke/smoke_20260705T151050Z_gpu/2026_07_05_111820_46080.onnx` | `a1fc8cc37925e469c1a9a85ca9e301343979065bbf3735678d7e0d3fc726cf0a` |

## Compact x=0.08 Gate

Gate artifact:

```text
outputs/analysis/PHASE2_GATE_AWARE_PARENT_ITER0_LOCAL_SMOKE_X008_GATE.md
outputs/analysis/phase2_gate_aware_parent_iter0_local_smoke_x008_gate.json
```

Settings:

- command: `x=0.08`
- task: `rough_terrain_backlash`
- bridge: corrected fitted actuator bridge
- platform: CPU gate
- duration: `15 s`
- seeds: `0,1,2,6,7`
- terrain hfield z scale: `0.0075`
- reset: `home-support`, settle `10`
- pushes: enabled, `0.075-0.125`

Result:

| policy | pass | falls | mean vx | mean track ratio | p95 vel excess | max vel excess | single support | double support |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0_15360` | 0/5 | 0 | 0.0015 | 0.0186 | 0.0000 | 0.1717 | 0.0% | 100.0% |
| `iter0_30720` | 0/5 | 0 | 0.0015 | 0.0193 | 0.0000 | 0.0000 | 0.0% | 100.0% |
| `iter0_46080` | 0/5 | 0 | 0.0016 | 0.0194 | 0.0000 | 0.0000 | 0.0% | 100.0% |

All 15 policy/seed runs completed the duration but failed as
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.

## Decision

The bounded on-policy parent iteration hit the pre-registered stop condition:
it lowered the x=0.08 pass count below the step-0 baseline (`3/5` to `0/5`).

The failure is not a corrected-envelope violation and not a fall. It is a
rewarded standstill: the policies remain stable, keep target rates very low,
stay in double support for the full rollout, and produce almost no forward
motion.

Do not launch long Phase 2 domain randomization from these exports. Do not run
the x=0.0 gate for these exports; the moving gate already rejects them. The
next branch must change the objective/structure so behavior preservation is
not optimized away by the reward, for example an explicit closed-loop teacher
constraint, router/wrapper-preserving training target, or another trainable
structure that first clears the compact behavior-preservation gate.
