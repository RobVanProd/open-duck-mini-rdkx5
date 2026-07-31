# Phase 2 z=0.0026 Teacher-Continuity A100 Medium Probe

timestamp_utc: `2026-07-02T03:45:07Z`
branch: `codex/live-oracle-dagger-phase-student`
head: `114d0a1834a9cabc7d2e22f491d7f6001574f334`

## Executive Summary

Gate result: `HOLD_ARTIFACT_NOT_RECOVERED`

The A100 `colab exec` path successfully ran the medium teacher-continuity training command and a 1-second checkpoint sweep, but the remote artifact bundle was not recoverable after the exec returned. The generated ONNX therefore cannot be promoted, fully gated, or used as evidence beyond startup/runtime success.

## Command

```text
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z002-teacher-continuity \
  --session open-duck-a100-startup \
  --candidate-name phase2_z0026_teacher_continuity_a100_medium_probe \
  --phase2-num-timesteps 20480 \
  --phase2-ppo-num-envs 8 \
  --phase2-ppo-num-evals 1 \
  --phase2-episode-length 256 \
  --phase2-ppo-batch-size 64 \
  --phase2-ppo-num-minibatches 1 \
  --phase2-ppo-num-updates-per-batch 1 \
  --phase2-skip-post-training-gates \
  --exec-remote \
  --exec-remote-timeout-s 7200 \
  --timeout-s 7800 \
  --skip-deps \
  --run
```

## Evidence

- A100 session: `open-duck-a100-startup`
- JAX/JAXlib pin: `0.7.2`
- Remote training command return code: `0`
- Remote training output root: `/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T032051Z_gpu`
- Exported checkpoint reported by the remote sweep: `/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T032051Z_gpu/2026_07_02_032700_20480.onnx`
- Remote checkpoint sweep return code: `0`
- Sweep selection line: `CANDIDATE_SELECTED_CHECKPOINT best_available_but_not_promoted HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
- Remote artifact path reported: `/content/open_duck_colab_cli_phase2-z002-teacher-continuity_20260702T031840Z_artifacts.tar.gz`
- Manual download after exec returned: `File or directory not found`
- Remote `/content` file API listing after exec returned: `File or directory not found`

## Local Evidence Files

- `outputs/analysis/colab_cli/open-duck-a100-startup-phase2-z002-teacher-continuity-20260702T031832Z/exec_remote.log`
- `exec_remote.log` sha256: `82298a080e5f96d19d1a63040f80b9bea5db8f7e19c4bd58543b8efac4dfefe3`
- driver sha256: `c18ba1477906fbecc3a4c9e05870aa62f6e2df912b3d504c8b66cc3af9bb0fa5`

## Interpretation

This is not a policy pass and not a policy failure. It proves the medium teacher-continuity recipe can start, train, export, and run a short CPU checkpoint sweep on the A100 stack, but the artifact collection path failed after `colab exec` returned.

Do not promote this run. Re-run through a polling/download path that can collect the artifact bundle before the remote `/content` namespace disappears.
