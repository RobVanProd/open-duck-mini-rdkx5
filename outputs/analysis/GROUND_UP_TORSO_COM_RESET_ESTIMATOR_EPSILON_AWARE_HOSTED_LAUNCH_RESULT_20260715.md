# Ground-Up Torso-COM Reset-Estimator Epsilon-Aware Hosted Launch Result — 2026-07-15

## Decision

`STOP_NO_RETRY_PREINSTALL_JAX_IMPORT_CONTAMINATION`

The single-use launch failed before checkpoint restore, expansion reporting, or
PPO. The named T4 session stopped successfully after `89.500354046` seconds;
independent session inventory reports zero active sessions. Compute use is
`UNMEASURED`.

## Evidence and cause

All 24 assets uploaded and the frozen job completed checkout, patching,
compilation, and package installation. Its separate post-install device process
passed far enough for the job to enter `hosted_expand`. The main process then
failed while constructing `orbax.checkpoint.PyTreeCheckpointer`, during JAX
CUDA-plugin import, with:

`TypeError: type 'jaxlib.mlir._mlir_libs._mlir.ir.Value' is not subscriptable`

The correction wrapper imports `jax` at line 106 before calling the original
job at line 135. The original job installs/upgrades JAX/JAXLIB inside that same
process before expansion. Consequently Python retained the pre-install JAX
module while later imports resolved newly installed JAXLIB/plugin files. The
separate device-check subprocess was clean because it started after install;
the wrapper process was not. This exact import-order difference explains why
the original diagnostic path reached expansion while this wrapper did not.

No training command appears in captured output, no result marker or manifest/
archive exists, and failure occurs before checkpoint restore. This is a wrapper
environment-order failure, not a policy, checkpoint-expansion, or behavior
result. The consumed launch may not be retried.

Raw hashes: launch plan `d4c6cda2...a1b461d`; launch record
`d16f571e...d755d6`.

## Authority

Only a separately preregistered one-line import-order correction may follow.
No training, behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot
action is authorized by this failed launch.

