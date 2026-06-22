# ROCm MJX Model Feature Audit

Last updated: 2026-06-22

## Purpose

This audit records Open Duck Mini MJCF/MuJoCo model features without stepping
MJX physics. It supports the local `7900 XTX` ROCm backend-debug workstream by
separating:

```text
model compile / reset evidence
from
ROCm failure during mjx_env.step(...)
```

No robot hardware, SSH, deployment, policy change, or training is involved.

## Command

Run with a Python environment that has `mujoco` available:

```bash
../envs/open-duck-playground/bin/python tools/audit_mjx_model_features.py \
  --playground-path ../Open_Duck_Playground \
  --xml ../Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml \
  --output-md outputs/analysis/ROCM_MJX_MODEL_FEATURE_AUDIT.md \
  --output-json outputs/analysis/rocm_mjx_model_feature_audit.json
```

## Current Result

The current compiled model audit is stored at:

```text
outputs/analysis/ROCM_MJX_MODEL_FEATURE_AUDIT.md
outputs/analysis/rocm_mjx_model_feature_audit.json
```

Key compiled counts:

```text
nq / nv / nu: 21 / 20 / 14
bodies / joints / geoms / sites / sensors: 18 / 15 / 47 / 5 / 15
meshes: 28
contact pairs: 0
equality constraints: 0
keyframes: 1
```

Contact-relevant compiled geoms:

```text
left_foot_bottom_tpu: mesh, contype=1, conaffinity=1, condim=3
right_foot_bottom_tpu: mesh, contype=1, conaffinity=1, condim=3
floor: plane, contype=1, conaffinity=0, condim=3
```

The static XML does not explicitly set `solref` / `solimp` on those three
contact items, but the compiled MuJoCo model resolves finite defaults:

```text
solref: [0.02, 1.0]
solimp: [0.9, 0.95, 0.001, 0.5, 2.0]
```

## Interpretation

The model compiles and can be reset in compatible local envs, while the local
ROCm hold appears at the full Open Duck `mjx_env.step(...)` call. The audit
points future minimization work at:

```text
mesh TPU foot collision against floor plane
reset-time collision checks
full 14-actuator articulated model stepping
```

It does not prove which feature causes the ROCm step hold. It gives a stable
feature inventory for the next reduced-model probe.

## Next ROCm Debug Step

If local ROCm work continues, the next useful tool would generate reduced MJCF
variants that preserve the 14-actuator contract when possible while toggling:

```text
mesh foot collision -> simple box/capsule foot collision
floor contact on/off
sensor blocks on/off
head/neck bodies on/off
visual mesh geoms removed
```

CUDA remains the full closed-loop eval/training backend. CPU remains useful for
reduced local correctness checks.
