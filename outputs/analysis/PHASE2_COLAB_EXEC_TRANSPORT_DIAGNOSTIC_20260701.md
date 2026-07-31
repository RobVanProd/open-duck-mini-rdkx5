# Phase 2 Colab Exec Transport Diagnostic

status: `PASS_COLAB_EXEC_TINY_DIAGNOSTIC`
session: `open-duck-l4-execdiag`
hardware_reported: `L4`
date_utc: `2026-07-01`

## Summary

The detached `colab console` path repeatedly lost the remote workflow sentinel
for the z=0.0025 Phase 2 recipe. A fresh L4 session was therefore tested with
`tools/run_colab_cli_cuda_workflow.py --exec-remote` on a tiny
`training-smoke-diagnostic` workload.

The `colab exec` transport completed successfully and downloaded a final
artifact bundle.

## Evidence

- workflow: `training-smoke-diagnostic`
- command mode: `--exec-remote`
- smoke shape: `1 env`, `8 timesteps`, `batch size 1`
- JAX platform: `gpu` / `cuda`
- artifact: `outputs/analysis/colab_cli/open-duck-l4-execdiag-training-smoke-diagnostic-20260701T031824Z/open_duck_colab_cli_training-smoke-diagnostic_20260701T031852Z_artifacts.tar.gz`
- artifact size bytes: `2662498`
- artifact sha256: `288c40b15c390519f9b4b7864980edc0941868022926349eb6df2f97d6e0ffaa`

| stage | status | elapsed_s |
|---|---|---:|
| `00_python_jax_device` | `PASS` | 2.1894 |
| `01_import_training_stack` | `PASS` | 56.6193 |
| `02_smoke_dry_run` | `PASS` | 0.0880 |
| `03_smoke_run` | `PASS` | 464.5555 |

## Interpretation

`colab exec` is the preferred transport for the next Phase 2 Colab attempt. It
survived the CUDA/JAX/Brax/MJX import path and a real tiny PPO smoke where the
detached console path has repeatedly produced lost-sentinel holds.

This is infrastructure evidence only. It does not produce a deployable policy
and does not satisfy the Phase 2 z=0.0025 gate.

## Follow-up Run

The full `phase2-z0025-boundary` source-generation workflow was launched on the
same session via `--exec-remote --skip-deps` using candidate name
`phase2_z0025_boundary_l4_exec`.

As of this artifact, that full workflow is still pending. Do not promote any
candidate until the full workflow returns artifacts and the canonical corrected
bridge gates are inspected.

## Scope

No robot tests, SSH, deploy, grounded replay, policy overwrite, or runtime
behavior change occurred.

