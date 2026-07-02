# Phase 2 z0.0026 A100 Foreground Startup Diagnostic

status: `HOLD_PHASE2_STARTUP_DISAPPEARS_AFTER_RUN_PLANNED`

## Context

This diagnostic was launched after adding live smoke-run manifests to
`tools/run_actuator_bridge_training_smoke.py`.

It intentionally used a tiny bounded run, not a promotable training attempt:

- session: `open-duck-a100-phase2-diag`
- workflow: `phase2-z002-teacher-continuity`
- restore checkpoint: `outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920`
- terrain z-scale: `0.0026`
- timesteps: `512`
- PPO envs: `4`
- post-training gates: disabled
- robot / SSH / deploy / grounded replay: not used

## Remote Stack

The remote environment was correct before the failure window:

- `jaxlib 0.7.2`
- `brax 0.14.2`
- `mujoco 3.9.0`
- `mujoco-mjx 3.9.0`
- `playground 0.0.5`
- JAX backend: `gpu`
- JAX device: `CudaDevice(id=0)`
- `jax.device_put_replicated`: present

## Result

The remote log reaches the smoke-run manifest and prints:

`status: RUN_PLANNED`

The planned child command is the expected GPU `runner.py` command under:

`/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T015304Z_gpu`

Then the remote workflow disappears:

- no `COLAB_CLI_ARTIFACT`
- no exit sentinel
- no artifact bundle
- no Python traceback
- no `Killed` line in the captured log
- no matching remote `python3`, `runner.py`, or `run_actuator` process remained when probed
- no smoke manifests were copied back from the remote output directory

The A100 session was stopped after inspection, and `colab sessions` reported no active
sessions.

## Interpretation

This is not evidence that the reward variant failed, improved, or regressed. The run did
not reach PPO training or ONNX export.

The failure is earlier than the previous no-export interpretation: it occurs immediately
after `run_actuator_bridge_training_smoke.py` emits the dry manifest and before useful
smoke-run artifacts can be bundled back by the high-level Colab workflow.

Treat this as a remote startup / Colab transport / process-lifetime failure, not a Phase 2
policy result.

## Next Step

Do not launch more reward variants through the high-level workflow until this startup path
is isolated.

Next diagnostic should run the exact `tools/run_actuator_bridge_training_smoke.py --run`
command directly in the Colab session, outside the generated high-level driver, with a
small timeout and explicit manual download of:

- the smoke output directory
- `stdout.txt`
- `stderr.txt`
- `smoke_manifest.start.json`
- `smoke_manifest.live.json`
- `smoke_manifest.final.json` if present

If direct smoke also disappears after `RUN_PLANNED`, debug `run_actuator_bridge_training_smoke.py`
startup under Colab. If direct smoke reaches `runner.py`, the generated high-level driver
or foreground console transport is the failing layer.
