# Local ROCm Status - 2026-06-25

status: `HOLD_LOCAL_ROCM_KFD`

This is an offline workstation backend check after the local firmware/BIOS
update. It did not run robot tests, SSH, deploy, train, or modify runtime
behavior.

## Summary

The local AMD stack is currently blocked below JAX/MJX:

- `rocm-smi` sees two AMD devices.
- `rocminfo` fails before listing agents:

```text
ROCk module is loaded
Unable to open /dev/kfd read-write: Invalid argument
lsd is member of render group
```

- JAX in `../envs/open-duck-playground/bin/python` is `0.8.2` and fails ROCm
  backend initialization:

```text
RuntimeError: Unable to initialize backend 'rocm': FAILED_PRECONDITION:
No visible GPU devices.
```

- `HSA_OVERRIDE_GFX_VERSION=11.0.0` does not change the failure.

This means the local 7900 XTX path is not ready for Open Duck JAX/MJX training
yet. The current practical GPU path remains CUDA/Colab.

## Local Evidence

```text
kernel: Linux LSD 7.0.0-22-generic
rocm-core: 7.2.1.70201-81~24.04
hipcc: HIP version 7.2.53211
user groups: lsd ... render
/dev/kfd: root render, 660
/dev/dri/renderD128: root render, 660
/dev/dri/renderD129: root render, 660
amdgpu cwsr_enable: 1
```

Recent kernel log excerpt:

```text
amdgpu 0000:7c:00.0: ring gfx_0.0.0 timeout
amdgpu 0000:7c:00.0: Ring gfx_0.0.0 reset failed
amdgpu 0000:7c:00.0: GPU mode2 reset failed
amdgpu 0000:7c:00.0: ASIC reset failed with error, -62
amdgpu 0000:7c:00.0: GPU Recovery Failed: -62
```

Package note:

```text
ROCm 7.2.1 packages are installed from repo.radeon.com.
Ubuntu 7.1 libamdhip64-7 and libhsa-runtime64-1 packages are also installed.
ldconfig shows both /opt/rocm-7.2.1 and /usr/lib ROCm runtime libraries.
```

That package/runtime mixing may be relevant, but the immediate blocker is that
`rocminfo` cannot use `/dev/kfd`.

## External Leads

Relevant external reports and docs:

- ROCm issue with the same `rocminfo` `/dev/kfd` `Invalid argument` symptom:
  <https://github.com/ROCm/ROCm/issues/4043>
- ROCm issue with `/dev/kfd` `Invalid argument` despite render group:
  <https://github.com/ROCm/ROCm/issues/6166>
- AMD ROCm installation prerequisites:
  <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html>
- AMD ROCm quick start:
  <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html>
- System76 ROCm instructions note that the user must be in the `render` group
  and that a reboot may be needed after group changes:
  <https://system76.com/support/articles/rocm>

The local user is already in `render`, so this is not the simple missing-group
case.

## Recommended Next Backend Step

Do not run Open Duck training on local ROCm until a minimal stack passes:

```bash
rocminfo
../envs/open-duck-playground/bin/python -c 'import jax; print(jax.devices())'
```

Next local debug actions should be system-level and explicit:

1. Reboot/power-cycle once after the amdgpu reset failure.
2. Recheck `rocminfo`.
3. If still failing, clean up ROCm runtime mixing so the runtime libraries come
   consistently from `/opt/rocm-7.2.1`.
4. Only after `rocminfo` passes, rerun the repo ROCm/MJX isolation matrix.

CUDA/Colab remains the preferred path for V21 candidate work until this
`/dev/kfd` hold is cleared.
