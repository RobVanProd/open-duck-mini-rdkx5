# Phase 2 Phase/Context PPO Warm-Start Decision

status: `PASS_PHASE_CONTEXT_PPO_WARMSTART_READY`

Offline sim/training readiness only; no robot, SSH, deploy, grounded replay, or robot runtime changes.

## Decision

Stage A DR may proceed from the verified phase/context-preserving PPO step-0 checkpoint. Robot validation remains blocked.

## Artifacts

- checkpoint: `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- checkpoint absolute path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- checkpoint present: `True`
- step0 ONNX: `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0.onnx`
- step0 ONNX sha256: `5d41eab6945f7e64e5b3d9c15ab38ba388ba38e616fd5c04bbf46f5b9237d626`
- reference parent ONNX: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- reference parent ONNX sha256: `5cadefcb3582043eb989a0e7c65ea9e2702a0815ba46c9ffe1c70b1f68f1db8f`
- BC NPZ: `outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate_mlp.npz`
- BC NPZ sha256: `1e22aa3c06a451e3ee4da32e58c6b45b881cdf87ea8ed8738c541b6dccb3e9c8`

## Export Fidelity

- samples: `3750`
- p95 abs error: `0.0`
- max abs error: `0.0`

## Corrected-Bridge Gates

### x=0.08 rough+push

- duration complete: `8 / 8`
- falls: `0`
- mean local vx: `0.027774` m/s
- mean track ratio: `0.347175`
- max pitch vel p95 max: `1.561374` rad/s
- p95 velocity excess max: `0.000000` rad/s
- max velocity excess max: `0.000000` rad/s
- max tracking p95 max: `0.191429` rad
- push success mean: `0.918590`

### x=0.0 rough+push

- duration complete: `8 / 8`
- falls: `0`
- mean local vx: `0.000821` m/s
- max allowed |mean vx|: `0.005000` m/s
- max pitch vel p95 max: `0.034779` rad/s
- p95 velocity excess max: `0.000000` rad/s
- max velocity excess max: `0.000000` rad/s
- max tracking p95 max: `0.043771` rad
- push success mean: `0.918590`

## Next Work

- Launch Stage A dry-run PPO from the absolute checkpoint path recorded here.
- Use --ppo_policy_network phase_modulated and matching context/trunk settings when restoring.
- Start with narrow randomization on rough_terrain_backlash and re-run corrected-bridge x=0.08/x=0.0 full8 gates after the stage.

Robot validation remains blocked.
