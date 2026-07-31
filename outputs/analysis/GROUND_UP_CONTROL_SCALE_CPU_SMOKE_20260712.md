# Ground-Up Control Scale CPU Smoke

status: `PASS_CONTROL_SCALE_PATCH_CPU_SMOKE`

The minimal PPO-scale patch was applied to a detached clean checkout of
`b9be205ac64488c23504ca42e5ec790337adeec3`. It changes only runner-exposed PPO
scale fields; environment configuration, reference motion, rewards,
observations, actions, dynamics, randomization, and export code remain unchanged.

CPU smoke configuration:

- timesteps requested: `1,024` (trainer completed at step `1,280`)
- environments: `4`
- evaluations: `1`
- episode length: `100`
- unroll: `10`
- batch/minibatches/updates: `32/1/1`
- task: `flat_terrain_backlash`
- backend: CPU only

Results:

- reset/train/update: pass
- step-0 checkpoint and ONNX export: pass
- step-1,280 checkpoint and ONNX export: pass
- final evaluation reward mean/std: `11.78017 / 5.12998`
- step-0 ONNX SHA256: `48c48016d0d86084605a7a68c04a7e0fff6e1a9ec9fa4d5424877fca46a3939b`
- step-1,280 ONNX SHA256: `2924f87980da17fa8d10816efa7c5d0c344a328e3d0b1ca13290a39ad48b2c7c`

This is a wiring smoke, not gait evidence. The early trained action shown by the
exporter is near saturation on several dimensions, so this checkpoint is not a
candidate and must not be evaluated or promoted as one.

No robot, local GPU, Colab, deployment, or motor action was used.
