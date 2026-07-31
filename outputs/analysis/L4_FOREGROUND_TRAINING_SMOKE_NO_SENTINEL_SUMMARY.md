# L4 Foreground Training Smoke No-Sentinel Summary

status: `HOLD_L4_FOREGROUND_TRAINING_SMOKE_NO_SENTINEL`

## Context

After detached `training-smoke` runs disappeared without exit sentinels on both
A100 and L4, the Colab helper added a foreground remote mode. Foreground mode
runs the remote driver directly inside `colab console` and writes the exit
sentinel after the driver returns.

Command:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4-smoke-foreground \
  --workflow training-smoke \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

Robot touched: `false`.

## Result

The pinned stack again initialized correctly:

```text
jax 0.7.2
jaxlib 0.7.2
brax 0.14.2
mujoco 3.9.0
mujoco-mjx 3.9.0
playground 0.0.5
backend gpu [CudaDevice(id=0)]
has_device_put_replicated True
```

The foreground console launched the remote driver and reached the tiny PPO smoke
command. The Colab console connection then closed before the script wrote the
foreground exit sentinel:

```text
status: HOLD_REMOTE_NO_SENTINEL
unchanged_log_polls: 0
idle_no_exit_polls: 2
```

No final manifest, ONNX, checkpoint, stdout/stderr artifact bundle, or remote
exit code was recovered.

## Interpretation

The no-sentinel failure is not explained solely by the detached `setsid` wrapper.
Even foreground console execution loses the remote process/session while the
minimal GPU PPO smoke is running.

The remaining likely split is:

- generic Colab GPU PPO/Brax runtime crash or session termination
- runner-level failure that is hidden because Colab drops the process before
  stdout/stderr can be packaged

The next local check is to run the same tiny smoke on CPU outside Colab. If CPU
passes locally, keep recipe iteration local/CPU or another stable backend until
the Colab GPU smoke can be made observable.

Robot validation remains blocked.
