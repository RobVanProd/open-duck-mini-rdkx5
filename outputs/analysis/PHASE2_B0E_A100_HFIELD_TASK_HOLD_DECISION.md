# Phase 2 B0E A100 Workflow Task Hold

status: `HOLD_B0E_CUDA_WORKFLOW_TASK_MISMATCH_FIXED`

## Purpose

The first `phase2-b0e` run on the newly created `open-duck-a100` Colab session
validated the CUDA stack but did not train. It failed before PPO because the
Phase 2 CUDA recipe applied a terrain hfield z-scale override while the wrapper
defaulted to `flat_terrain`.

This was offline-only. No robot tests, SSH, deploy, grounded replay, runtime
behavior changes, or policy overwrite were performed.

## Verified Before Failure

```text
session: open-duck-a100
hardware: A100
jax: 0.7.2
jaxlib: 0.7.2
brax: 0.14.2
mujoco: 3.9.0
mujoco-mjx: 3.9.0
jax backend: gpu
jax device: cuda:0
policy/sim contract: PASS_POLICY_SIM_CONTRACT
```

## Failure

```text
No hfield size attribute found in
/content/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml
```

The root cause was in `tools/run_colab_cli_cuda_workflow.py`: the Phase 2
B0D/B0E CUDA recipe did not pass `--task rough_terrain_backlash` to
`tools/run_actuator_bridge_training_smoke.py`, so the wrapper used its default
task while still applying `--terrain-hfield-z-scale 0.002`.

## Fix

The Phase 2 CUDA recipe now explicitly passes:

```text
--task rough_terrain_backlash
```

This is a workflow fix only. The failed A100 run produced no trained candidate.
