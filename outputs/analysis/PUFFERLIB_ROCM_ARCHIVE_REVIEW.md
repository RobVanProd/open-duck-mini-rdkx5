# PufferLib ROCm Archive Review

generated_at: `2026-06-22T13:30:00Z`

## Source

- archive: `/home/lsd/Downloads/PufferLib.rar`
- archive type: RAR v5
- size: `279087741` bytes
- listed entries: `8029`
- key reviewed file: `PUFFERLIB_ROCM_PORT_RUNBOOK.md`

The archive was inspected without system package installation. `rarfile` was
used for listing, and a user-space unpack of the Debian `unrar-free` package was
used to extract only the top-level runbook into `/tmp`.

## What It Contains

The reviewed runbook documents a PufferLib ROCm port targeting:

- AMD Radeon RX 7900 XT / RDNA3 / `gfx1100`
- native Windows ROCm SDK wheel stack
- PyTorch HIP runtime
- HIP runtime builds through `hipcc`
- hipBLAS / rocBLAS / hipRAND / rocRAND linkage
- HIP graph capture through PufferLib's CUDA-shaped graph path
- WSL ROCm 7.2 and RCCL smoke coverage
- PufferLib Ocean `vecenv.h` environments

## Relevance To Open Duck

This is useful as evidence that `gfx1100` / RDNA3 can be a workable ROCm target
for a PufferLib/PyTorch/HIP stack. It is not a direct fix for the current Open
Duck local backend blocker.

Current Open Duck local blocker:

```text
HOLD_PLAYGROUND_GPU_STEP
```

Smallest failing path remains the Open Duck Playground MJX/JAX stepping path on
the local RX 7900 XTX. Basic JAX GPU arithmetic, JAX scan, minimal MJX, Open
Duck contract construction, and Open Duck reset pass; the full Open Duck
`mjx_env.step(...)` path still times out or aborts on ROCm.

The PufferLib runbook does not document:

- JAX or XLA configuration
- MuJoCo MJX stepping
- `mjx_env.step(...)`
- JAX `lax.scan` lowering around repeated MJX steps
- a Linux JAX/ROCm package pin for Open Duck Playground
- a fix for `ROCM_ERROR_ILLEGAL_ADDRESS` in the Open Duck MJX step path

## Practical Conclusion

Do not treat `PufferLib.rar` as the missing 7900 XTX MJX fix.

It may be useful later only if the project intentionally explores a separate
PufferLib/PyTorch training stack. That would be a new integration project,
because the current Open Duck actuator-bridge training path is JAX/MJX through
Open Duck Playground.

Current project backend decision remains:

```text
CUDA/Colab: confirmed full closed-loop eval/training backend
CPU: reduced local correctness checks only
local RX 7900 XTX ROCm: backend-debug workstream, still held at Open Duck MJX step
```

## Notes

- The archive reinforces that `gfx1100` is the relevant RDNA3 architecture
  target family.
- It does not override the local evidence that `HSA_OVERRIDE_GFX_VERSION=11.0.0`
  is harmful in this JAX/MJX environment.
- No robot tests, SSH, deploy, training, policy changes, or runtime changes were
  performed for this review.
