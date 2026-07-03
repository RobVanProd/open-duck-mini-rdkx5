# Phase 2 z0.0026 Phase/Single-Support A100 Runtime Hold

status: `HOLD_A100_RUNTIME_NO_FINAL_CANDIDATE`

## Summary

The preregistered home-reset `z=0.0026` phase/single-support recipe was launched
on Colab A100 after commit `eeebb85`, but the larger A100 training chunks did
not produce a final manifest or candidate ONNX.

This is a runtime/execution hold, not a robot result and not a candidate gate
result. No robot test, SSH, deploy, grounded replay, or runtime behavior change
was performed.

## Inputs

- Branch: `codex/live-oracle-dagger-phase-student`
- Recipe artifact:
  `outputs/analysis/PHASE2_HOME_RESET_Z0026_PHASE_SINGLE_SUPPORT_NEXT_RECIPE_20260703.md`
- Recipe commit: `eeebb85`
- Warm-start checkpoint:
  `outputs/analysis/phase2_restore_checkpoints/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- Corrected bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- Corrected bridge sha256:
  `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- Terrain/reset convention: `rough_terrain_backlash`, `z=0.0026`,
  home-support reset.

## Runtime Findings

1. A tiny A100 diagnostic profile compiled and exported:
   - `16` envs
   - batch size `128`
   - `5120` requested timesteps
   - export observed at step `10240`
   - This proved the reward path and restore path can compile/export at small
     scale.

2. Larger A100 profiles did not produce a promotable candidate:
   - The first full launch reached setup / `STEP: 0` and then disappeared
     without a final manifest or ONNX.
   - A `40960` run without disabling CUDA command buffers failed with
     `RESOURCE_EXHAUSTED: Failed to instantiate CUDA graph: CUDA_ERROR_OUT_OF_MEMORY`.
   - A retry with command buffers disabled got past that OOM in the first
     session but later failed with `cuSolver internal error`.
   - A fresh A100 session using the corrected XLA flag syntax produced no
     Python traceback, no final manifest, no checkpoint/export lines, and no
     candidate ONNX. The recorded process was gone when probed.

3. Correct XLA flag syntax for this wrapper path is:

```text
--phase2-final-training-args-json '[
  "--xla-flags=--xla_gpu_enable_command_buffer=",
  "--xla-python-client-preallocate",
  "false",
  ...
]'
```

Passing `["--xla-flags", "--xla_gpu_enable_command_buffer="]` is invalid here
because argparse treats the value beginning with `--` as another option.

## Preserved Artifact

Downloaded Colab archive:

```text
outputs/analysis/colab_cli/phase2_singlesupport2/open_duck_phase2_singlesupport2_20260703T065703Z_artifacts.tar.gz
```

sha256:

```text
faa87d3a7cd18040cd9f7f5c34057450b3c436fca70951086ec89248af15f47f
```

The archive contains only:

- `smoke_manifest.start.json`
- `smoke_manifest.live.json`
- `stdout.txt`
- `stderr.txt`
- `events.out...` with size `0`
- the temporary terrain XML backup

No `smoke_manifest.final.json` and no `.onnx` candidate were produced.

## Current Compute State

The Colab session `open-duck-a100-phase2-singlesupport2` was checked for live
Python training processes, found idle, archived, and stopped. `colab sessions`
reported no active sessions after stop.

## Decision

Gate result:

```text
HOLD_A100_RUNTIME_NO_FINAL_CANDIDATE
```

Do not interpret this as a failed policy. The recipe has not yet produced a
candidate that can be screened against the corrected bridge.

## Recommended Next Runtime Step

Use the smallest profile that is known to compile/export as the starting point,
then scale carefully:

1. Relaunch from a fresh A100 session with command buffers disabled.
2. Run a short chunk that exports and download it immediately.
3. If stable, continue with smaller chunks from the exported checkpoint instead
   of one long `40960+` run.
4. If `cuSolver` reappears on a fresh session, reduce parallelism further
   (`8` envs, smaller batch) before changing the recipe.

Do not move to robot validation from this hold.
