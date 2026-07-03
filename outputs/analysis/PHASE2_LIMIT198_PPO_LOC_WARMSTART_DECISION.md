# Phase 2 Limit198 PPO-Loc Warm-Start Decision

status: `PASS_TRAINABLE_PHASE2_WARMSTART_READY`

Generated offline. No PPO updates, robot tests, SSH, deployment, grounded
replay, or runtime behavior changes were performed.

## Summary

The promoted right-ankle-limit198 phase-modulated candidate is deployable as
ONNX, but it is not directly restorable into the existing Brax PPO actor
because its NPZ uses a context/modulation branch:

```text
output_mode: phase_modulated_tanh_loc
context_indices: [6, 97, 98, 99, 100]
```

A PPO-compatible `tanh(loc)` surrogate was therefore trained from the same
limit198 manifest, converted to a step-0 PPO checkpoint/export, and gated
before any DR/PPO updates.

## Artifacts

PPO-loc BC student:

```text
outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate_mlp.npz
outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate.onnx
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STUDENT.md
outputs/analysis/phase2_limit198_ppo_loc_warmstart_student.json
```

Step-0 PPO checkpoint/export:

```text
outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint
outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0.onnx
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_EXPORT_FIDELITY.md
outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_export_fidelity.json
```

Gate evidence:

```text
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_X008_GATE.md
outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_x008_gate.json
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_X0_GATE.md
outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_x0_gate.json
```

Hashes:

- PPO-loc BC ONNX:
  `a48c82c0f5719016b3e8bfae7817351b5413fac0e1babcf70de05e1f3652c237`
- PPO-loc BC NPZ:
  `cfb62315014dfc83ef0c654a8386bc39eb0ec9f7305e10adfa10216827ab0d15`
- step-0 PPO ONNX:
  `1dc894eebc144d790f1a6b4be6ada5a05e748f215f2053c72610347955deb3bb`

## Fit And Fidelity

- BC fit status: `PASS_PPO_LOC_BC_FIT_SMOKE`
- samples: `28500`
- weighted samples: `84460`
- target-rate p95: `1.4220 rad/s`
- target-rate max: `2.3070 rad/s`
- step-0 export status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`
- fidelity samples: `2048`
- p95 abs action error: `1.49e-7`
- max abs action error: `3.87e-7`

## Corrected-Bridge Gates

Canonical evaluator:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0026
reset_mode: home-support
bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
duration: 15s
seeds: 0..7
```

`x=0.08` result:

- status: `PASS_CANDIDATE_SIM_GATE`
- duration complete: `8/8`
- falls: `0/8`
- mean local vx: `0.0332 m/s`
- track ratio: `0.4151`
- single support: `28.1333%`
- double support: `71.8667%`
- max pitch-chain p95 velocity: `1.7417 rad/s`
- corrected p95 velocity excess: `0.0000`
- corrected max velocity excess: `0.0000`
- max tracking p95: `0.1823 rad`

`x=0.0` result:

- status: `PASS_CANDIDATE_SIM_GATE`
- duration complete: `8/8`
- falls: `0/8`
- mean local vx: `0.0001 m/s`
- double support: `100.0000%`
- max pitch-chain p95 velocity: `0.0245 rad/s`
- corrected max velocity excess: `0.0000`
- max tracking p95: `0.0322 rad`

## Decision

Use `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint` as
the current trainable Phase 2 warm-start for the next offline DR stage.

The previous Stage A scalar PPO/DR recipe is still rejected because it erased
single-support walking. Any next DR run must be a bounded Stage A variant from
this step-0 checkpoint and must preserve:

- nonzero x=0.08 forward progress,
- nonzero single support,
- zero corrected velocity excess,
- x=0.0 stillness.

Robot validation remains blocked.
