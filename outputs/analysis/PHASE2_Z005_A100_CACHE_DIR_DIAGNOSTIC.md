# Phase 2 Z005 A100 Cache Dir Diagnostic

status: `HOLD_A100_XLA_CACHE_DIR_MISSING_FULL_SHAPE`

## Summary

- workflow: `phase2-z005-support`
- session: `open-duck-l4`
- hardware: `A100`
- robot_touched: `false`
- ssh_performed: `false`
- deploy_performed: `false`
- grounded_replay_performed: `false`
- promoted_candidate: `false`

The full-shape A100 run reached PPO step 0, then failed inside JAX/XLA before producing a candidate. The failure was not a policy gate result.

```text
jaxlib._jax.XlaRuntimeError: NOT_FOUND: .tmp/jax_cache/xla_gpu_per_fusion_autotune_cache_dir not found
```

## Evidence

Full run:

- local run dir: `outputs/analysis/colab_cli/open-duck-l4-phase2-z005-support-20260630T063132Z`
- remote training dir: `/content/open_duck_training_phase2_z005_support_cli/smoke_20260630T063643Z_gpu`
- status: `HOLD_SMOKE_RUN`
- returncode: `1`
- elapsed_s: `389.5586`
- summary step line: `STEP: 0 reward: 21.705751419067383 reward_std: 24.509244918823242`
- export: none

Reduced compile probe:

- local run dir: `outputs/analysis/colab_cli/open-duck-l4-phase2-z005-support-20260630T064207Z`
- remote training dir: `/content/open_duck_training_phase2_z005_support_cli/smoke_20260630T064239Z_gpu`
- status: `PASS_SMOKE_RUN`
- returncode: `0`
- elapsed_s: `508.9631`
- checkpoint: `/content/open_duck_training_phase2_z005_support_cli/smoke_20260630T064239Z_gpu/2026_06_30_064828_1280`

## Follow-Up

Patch the Colab workflow and the smoke wrapper to create:

```text
.tmp/jax_cache/xla_gpu_per_fusion_autotune_cache_dir
```

under the relevant repo/checkouts before launching JAX/MJX training, then rerun a bounded A100 probe before retrying the full `phase2-z005-support` run.
