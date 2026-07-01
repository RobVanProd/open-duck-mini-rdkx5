# Phase 2 z=0.0025 Boundary L4 Hold

status: `HOLD_REMOTE_NO_SENTINEL`
workflow: `phase2-z0025-boundary`
session: `open-duck-l4-phase2f`
hardware_reported: `L4`
date_utc: `2026-07-01`

## Summary

- A fresh Colab L4 session was created after the local reboot.
- The local package-only check passed for `phase2-z0025-boundary`.
- The remote workflow uploaded and unpacked the RDK and Playground archives.
- The remote pinned stack was correct: JAX/JAXLIB `0.7.2`, Brax `0.14.2`, MuJoCo/MJX `3.9.0`, Playground `0.0.5`.
- The remote policy/sim contract audit passed on CUDA: `obs=101`, `actions=14`, actuator order matched, JAX backend `gpu`, device `cuda:0`.
- The remote process then disappeared without writing the expected exit sentinel.
- A partial artifact bundle was recovered, but it only contains the contract audit outputs.

## Interpretation

This is not a policy result and not a z=0.0025 gate result. Treat it as a
remote Colab/session runtime hold. The last trustworthy Phase 2 terrain result
remains the z=0.0024 passing source boundary, and the z=0.0025 source-generation
rung still needs a completed GPU run.

## Evidence

- run_dir: `outputs/analysis/colab_cli/open-duck-l4-phase2f-phase2-z0025-boundary-20260701T030822Z`
- partial artifact: `open_duck_colab_cli_phase2-z0025-boundary_20260701T030900Z_artifacts_partial_output.tar.gz`
- recovered audit: `partial_remote_output/open_duck_colab_cli_phase2-z0025-boundary_20260701T030900Z/POLICY_SIM_CONTRACT_AUDIT_CUDA.md`
- local package manifest status: `PASS_COLAB_PACKAGE_ONLY_READY`
- package RDK sha256: `4e982ea657bbab547af5abc7a55648bac30af5e8f560dae58d7b2d0adcb6380e`
- package Playground sha256: `c5c11aca5a4b45c512b090d4f968448c61de1a469611470e1ae2200682a5e423`

## Scope

No robot tests, SSH, deploy, grounded replay, policy overwrite, runtime behavior
change, or completed training occurred.

## Next

Retry the same `phase2-z0025-boundary` source-generation workflow on a stable
Colab session, preferably with the browser tab attached to the session URL so
the web UI maintains the gateway heartbeat. Do not promote partial artifacts.
