# ROCm After-Reset Recheck

Date: 2026-06-22

Purpose: verify whether a full power/reset cycle cleared the local RX 7900 XTX
Open Duck MJX stepping blocker.

## Result

Gate: `HOLD_PLAYGROUND_GPU_STEP`

The reset did not clear the local ROCm/MJX Open Duck stepping blocker.

## Environment

- GPU: Radeon RX 7900 XTX, `gfx1100`
- ROCm driver: `7.0.0-22-generic`
- Python env: `../envs/open-duck-playground/bin/python`
- JAX: `0.8.2`
- JAX backend/device: `gpu` / `RocmDevice(id=0)`
- MuJoCo: `3.9.0`
- mujoco-mjx: `3.9.0`

## Default ROCm Check

With no `HSA_OVERRIDE_GFX_VERSION` override:

| check | result | note |
|---|---|---|
| basic JAX arithmetic | PASS | `sum 240.0` |
| JAX jit/scan | PASS | isolation row passed |
| minimal MJX step | PASS | isolation row passed |
| Open Duck contract-only | PASS | isolation row passed |
| Open Duck XML/contact audit | PASS | isolation row passed |
| Open Duck reset | PASS | about 42 s |
| Open Duck reset finite-state probe | PASS | about 42 s |
| Open Duck direct `mjx_env.step` | TIMEOUT | 120 s timeout |
| Open Duck direct `mjx_env.step` JIT | FAIL | ROCm abort, return code `-6` |
| Open Duck one-step vanilla | TIMEOUT | 120 s timeout |

The isolation run was intentionally stopped after the decisive one-step rows to
avoid spending more time on redundant multi-step variants.

## Bad Override Check

With:

```bash
HSA_OVERRIDE_GFX_VERSION=11.0.0
```

even basic JAX GPU and CPU-labelled subtests aborted with:

```text
ROCM_ERROR_ILLEGAL_ADDRESS
Failed setting context
```

Conclusion: do not use `HSA_OVERRIDE_GFX_VERSION=11.0.0` for this local setup.
The RX 7900 XTX is already detected as `gfx1100` by ROCm.

## Interpretation

This remains a local ROCm/MJX execution problem specific to the full Open Duck
MJX step. It is not a basic GPU visibility issue, not a policy/sim contract
issue, and not evidence that the robot needs more motion tests.

Continue to use CUDA/Colab for full closed-loop eval and candidate training
until the local ROCm issue is fixed upstream or with a reviewed environment
change.
