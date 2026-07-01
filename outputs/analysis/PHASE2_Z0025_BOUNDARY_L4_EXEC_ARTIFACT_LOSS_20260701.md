# Phase 2 z=0.0025 Boundary L4 Exec Artifact Loss

status: `HOLD_COLAB_ARTIFACT_LOST_AFTER_REMOTE_PROGRESS`

## Summary

The Colab L4 exec-remote path progressed past the previous transport hold. The remote
workflow completed dependency reuse, CUDA contract audit, Phase 2 z=0.0025 training,
training-run summary, checkpoint sweep, and multiple no-push corrected-bridge seed gates.

The run then lost the Colab CLI websocket transport during the final gentle-push
regression gate. The session was gone by the time local recovery was attempted, so the
remote artifact bundle could not be downloaded.

This is infrastructure evidence, not a policy verdict. The run produced useful evidence
that the exec-remote path can survive the training and no-push gate portions, but the
candidate and gate JSONs were not recovered locally.

## Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z0025-boundary \
  --session open-duck-l4-execdiag \
  --candidate-name phase2_z0025_boundary_l4_exec \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-timeout-s 10800 \
  --exec-remote \
  --exec-remote-timeout-s 14400 \
  --skip-deps \
  --run
```

## Remote Progress Reached

- Pinned stack reused successfully:
  - JAX/JAXLIB `0.7.2`
  - Brax `0.14.2`
  - MuJoCo/MJX `3.9.0`
  - Playground `0.0.5`
- CUDA contract audit returned `0`.
- Phase 2 z=0.0025 training returned `0`.
- Training summary returned `0`.
- Checkpoint sweep returned `0`.
- Selected checkpoint in remote log:
  - status: `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
  - selected policy: `/content/open_duck_training_phase2_z0025_boundary_cli/smoke_20260701T033216Z_gpu/2026_07_01_034313_40960.onnx`
- Completed seed gates before transport loss:
  - z=0.0025 x=0.08 no-push returned `0`
  - z=0.0025 x=0.0 no-push returned `0`
  - z=0.002 x=0.08 no-push regression returned `0`
  - z=0.002 x=0.0 no-push regression returned `0`

## Failure

The Colab CLI connection failed during:

```text
z=0.002 x=0.08 gentle-push regression seed gate
```

Error:

```text
RuntimeError: Connection was lost.
```

Afterward, `colab sessions` reported no active sessions, and no artifact bundle existed
locally in the run directory.

## Decision

Do not score this as a candidate pass or hold, because the JSON/ONNX artifacts were lost.

Next run should split the workflow:

1. Run training + checkpoint sweep only with `--phase2-skip-post-training-gates`, so the
   candidate artifact is downloaded before slow CPU gates.
2. Run seed gates afterward from the recovered local ONNX.
3. Keep push gates as a separate short workflow so a transport drop cannot lose the
   training artifact.

Robot validation remains blocked.
