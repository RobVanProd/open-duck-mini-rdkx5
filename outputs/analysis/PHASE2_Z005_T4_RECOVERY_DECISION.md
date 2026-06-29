# Phase 2 z=0.005 T4 Recovery Decision

status: `HOLD_PHASE2_Z005_T4_GATE_INCOMPLETE`
generated_at: `2026-06-29T19:49:00Z`

This is a recovery artifact for the `phase2-z005-support` Colab run. It did
not touch the robot, SSH, deploy, run grounded replay, or change runtime
behavior.

## What Completed

- Colab session: `open-duck-l4`
- Hardware actually used: `T4`
- Pinned remote stack:
  - `jaxlib 0.7.2`
  - `brax 0.14.2`
  - `mujoco 3.9.0`
  - `mujoco-mjx 3.9.0`
  - `playground 0.0.5`
- Workflow: `phase2-z005-support`
- Restore checkpoint:
  `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- Training return code: `0`
- Training elapsed: `990.27934026 s`
- Corrected actuator bridge: enabled
- Terrain: `rough_terrain_backlash`
- Terrain hfield z scale: `0.005`
- Pushes: disabled
- Robot validation: not performed

## Recovered ONNX Exports

| step | sha256 | recovered path |
|---:|---|---|
| 40960 | `05931e5d5cf2b6230ff404f580b0d68a804d0c2c9c9aa726bd546b776e979c92` | `outputs/analysis/recovered_colab/open_duck_colab_cli_phase2-z005-support_20260629T184556Z/open_duck_training_phase2_z005_support_cli/smoke_20260629T184953Z_gpu/2026_06_29_190108_40960.onnx` |
| 81920 | `49ba524b35d470d9a03d9ed25ee039495f6a8d44489e0488a3e05a044004abcc` | `outputs/analysis/recovered_colab/open_duck_colab_cli_phase2-z005-support_20260629T184556Z/open_duck_training_phase2_z005_support_cli/smoke_20260629T184953Z_gpu/2026_06_29_190508_81920.onnx` |
| 122880 | `59f1ba30516e3019eef9c324304883ae37d69316e0a9469d136d87493ac6ce12` | `outputs/analysis/recovered_colab/open_duck_colab_cli_phase2-z005-support_20260629T184556Z/open_duck_training_phase2_z005_support_cli/smoke_20260629T184953Z_gpu/2026_06_29_190550_122880.onnx` |

## Reward Trace

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 24.411722 | 25.393875 |
| 40960 | 32.146736 | 27.939310 |
| 81920 | 32.249718 | 28.580282 |
| 122880 | 36.603050 | 28.471169 |

## Failure / Hold Reason

The training run completed, but the workflow later reported:

```text
HOLD_REMOTE_NO_SENTINEL: Colab workflow disappeared without exit sentinel
```

The partial artifact tarball was valid and extracted locally:

```text
outputs/analysis/colab_cli/open-duck-l4-phase2-z005-support-20260629T184546Z/open_duck_colab_cli_phase2-z005-support_20260629T184556Z_artifacts.tar.gz.partial
sha256: 3698a137f647889dcd207704535fed2f939716ee5c003fb8a1d4883ed2c8de86
```

The post-training checkpoint sweep did not complete and was not recovered in
the partial tarball. Therefore this run is not promotable.

## Decision

`HOLD_PHASE2_Z005_T4_GATE_INCOMPLETE`

The recovered ONNX files may be used for offline debug/evaluation. They are
not deployable candidates and do not authorize robot testing.
