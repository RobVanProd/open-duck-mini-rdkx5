# Local Training Smoke Startup Diagnostic Summary

status: `PASS_LOCAL_STARTUP_DIAGNOSTIC`

## Context

The Colab GPU smoke currently holds as `HOLD_REMOTE_NO_SENTINEL`. A staged
startup diagnostic was added so the next remote run can identify whether the
failure happens during JAX device compute, training-stack imports, smoke
dry-run startup, or the tiny PPO loop.

This local CPU run validates that the diagnostic itself works through all
stages.

Robot touched: `false`.

## Command

```bash
python3 tools/diagnose_training_smoke_startup.py \
  --platform cpu \
  --jax-platforms cpu \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --output-dir outputs/analysis/local_training_smoke_startup_diagnostic_cpu_run \
  --timeout-s 180 \
  --smoke-timeout-s 1200 \
  --smoke-num-timesteps 8 \
  --export-min-step 1 \
  --ppo-num-envs 2 \
  --ppo-batch-size 2 \
  --run-smoke
```

## Result

All stages passed:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
```

The actual tiny PPO smoke completed in about `45.31s` on local CPU.

## Interpretation

The startup diagnostic is valid locally. The next Colab run should use
`--workflow training-smoke-diagnostic`; if the remote job disappears again, the
poller now also attempts to recover the remote workflow output directory as
`partial_remote_output`.
