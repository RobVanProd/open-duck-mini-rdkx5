# ROCm MJX Loop Mode Probe Summary

generated_at: `2026-06-22T12:02:00Z`

## Executive Summary

The reduced-model loop-mode probe found a local ROCm workaround lead:

```text
GPU baseline, n_substeps=10, loop_mode=scan: TIMEOUT
GPU baseline, n_substeps=10, loop_mode=fori: TIMEOUT
GPU baseline, n_substeps=10, loop_mode=python: PASS
GPU baseline, n_substeps=10, loop_mode=python_block_each: PASS
```

This means the local 7900 XTX issue is not "10 sequential MJX steps can never
run on ROCm." It is tied to compiling/lowering the substep loop through JAX
control-flow primitives such as `lax.scan` and `lax.fori_loop`.

## Commands Run

Each command used the baseline Open Duck model, `JAX_PLATFORM_NAME=gpu`, and
`n_substeps=10` through `tools/probe_reduced_mjx_models.py`.

```bash
../envs/open-duck-playground/bin/python tools/probe_reduced_mjx_models.py \
  --source-xml-dir ../Open_Duck_Playground/playground/open_duck_mini_v2/xmls \
  --env-python ../envs/open-duck-playground/bin/python \
  --platforms gpu \
  --variants baseline \
  --n-substeps 10 \
  --loop-mode scan \
  --timeout-s 60 \
  --output-dir outputs/analysis/rocm_mjx_reduced_model_probe_loop_scan
```

The same command was run with:

```text
--loop-mode fori
--loop-mode python
--loop-mode python_block_each
```

## Result Matrix

| loop_mode | platform | n_substeps | result | elapsed_s |
|---|---|---:|---|---:|
| `scan` | `gpu` | 10 | `TIMEOUT` | 60.13 |
| `fori` | `gpu` | 10 | `TIMEOUT` | 60.08 |
| `python` | `gpu` | 10 | `PASS` | 43.82 |
| `python_block_each` | `gpu` | 10 | `PASS` | 43.40 |

## Interpretation

The current local ROCm backend hold is specifically associated with JAX/XLA
control-flow lowering of repeated `mjx.step(...)`, not with a single raw
`mjx.step` and not with host-driven sequential stepping.

This may allow a slow local ROCm correctness-eval workaround that replaces
`mujoco_playground._src.mjx_env.step(...)` with a host Python substep loop.
That would not be a training solution, but it could help local debugging.

CUDA remains the full closed-loop eval/training backend. CPU remains valid for
reduced local correctness checks. No robot hardware, SSH, deployment, training,
or runtime behavior changes were involved.
