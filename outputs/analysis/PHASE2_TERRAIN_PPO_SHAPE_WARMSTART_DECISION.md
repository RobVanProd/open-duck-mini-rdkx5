# Phase 2 Terrain PPO-Shape Warm-Start Decision

status: `PASS_TRANSITION_PRESERVING_PPO_WARMSTART_READY`

This is an offline sim/training-plumbing result. It did not run robot tests,
SSH, deploy, grounded replay, or change robot runtime behavior.

## Purpose

The useful terrain live-oracle DAgger iter2 student preserved forward
rough-terrain transition structure but was trained as a `[256,256]` BC MLP,
which cannot be converted directly into the local PPO actor checkpoint format.
This step refit the same aggregate manifest with the PPO actor architecture
`[512,256,128]`, verified closed-loop behavior, and exported a PPO step-0 ONNX
plus local Orbax restore checkpoint.

## PPO-Shape BC Fit

Artifacts:

```text
outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_ITER2_PPO_SHAPE_BC_STUDENT.md
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_bc_student.json
```

Input manifest:

```text
outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_aggregate_manifest.json
```

Fit:

```text
hidden_sizes: [512, 256, 128]
samples: 2511
p95 action error: 0.026690
target-rate p95: 1.614097 rad/s
```

## PPO-Shape Closed-Loop Gate

Artifacts:

```text
outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_ITER2_PPO_SHAPE_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_bc_student_terrain_z002_gate_cpu.json
```

Result on `rough_terrain_backlash`, `z=0.002`, corrected fitted bridge:

| seed | status | vx | track ratio | max vel excess | max tracking p95 | single support | double support |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | `HOLD_CANDIDATE_TRACKING` | 0.0510 | 0.6379 | 0.8783 | 0.2546 | 39.2% | 60.8% |
| 4 | `HOLD_CANDIDATE_TRACKING` | 0.0486 | 0.6080 | 0.8127 | 0.2552 | 32.4% | 67.6% |

This preserves the transition/progress behavior and reproduces the same
tracking/envelope hold as the prior iter2 student.

## PPO Step-0 Export

Artifacts:

```text
outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_ITER2_PPO_SHAPE_STEP0_FIDELITY.md
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_fidelity.json
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0.onnx
```

Local ignored restore checkpoint:

```text
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_checkpoint
```

Fidelity:

```text
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
samples checked: 2048
p95 abs error: 0.00000013
max abs error: 0.00000036
```

Step-0 ONNX gate:

```text
outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_ITER2_PPO_SHAPE_STEP0_TERRAIN_Z002_GATE_CPU.md
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_terrain_z002_gate_cpu.json
```

| seed | status | vx | track ratio | max vel excess | max tracking p95 | single support | double support |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | `HOLD_CANDIDATE_TRACKING` | 0.0532 | 0.6652 | 0.7987 | 0.2598 | 38.4% | 61.6% |
| 4 | `HOLD_CANDIDATE_TRACKING` | 0.0476 | 0.5947 | 0.8291 | 0.2533 | 32.0% | 68.0% |

## Decision

`PASS_TRANSITION_PRESERVING_PPO_WARMSTART_READY`

The PPO-shaped step-0 export is not a robot candidate, but it is the correct
local warm-start for the next offline transition-preserving PPO fine-tune. It
keeps the rough-terrain transition behavior that the global label filter
destroyed, and leaves only the corrected tracking/envelope violation for the
next branch to address.

Next branch should restore from:

```text
outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_checkpoint
```

and keep a strong restore-policy KL / behavior prior while applying
closed-loop corrected-envelope and actuator-tracking penalties. Robot
validation remains blocked.
