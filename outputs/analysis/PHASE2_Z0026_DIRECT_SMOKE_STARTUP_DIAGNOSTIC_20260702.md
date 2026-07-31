# Phase 2 z0.0026 Direct Smoke Startup Diagnostic

status: `HOLD_PPO_STARTUP_DISAPPEARS_AFTER_RESTORE_KL`

## Context

The previous A100 foreground diagnostic showed the high-level Colab workflow disappeared
after `RUN_PLANNED`, but before returning useful smoke-run artifacts. This follow-up bypassed
the generated high-level Colab driver and launched `tools/run_actuator_bridge_training_smoke.py`
directly in a detached Colab process.

This was diagnostic-only:

- no robot
- no SSH
- no deploy
- no grounded replay
- no promotable candidate

## Probe 1: Bad Manual Flag

The first direct command returned `2` because the manually assembled command included:

`--enable-actuator-bridge`

That flag is not accepted by `tools/run_actuator_bridge_training_smoke.py`; the bridge is
default-on at the smoke-runner layer. This was a manual probe construction error, not a
policy or trainer result.

## Probe 2: Corrected Direct Smoke Command

The corrected command removed `--enable-actuator-bridge` and reused the already-installed
A100 session.

Inputs:

- workflow family: `phase2-z002-teacher-continuity`
- restore checkpoint: `outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920`
- terrain z-scale: `0.0026`
- timesteps: `512`
- PPO envs: `4`
- episode length: `256`
- batch size: `64`
- post-training gates: not run

Downloaded evidence:

- `outputs/analysis/colab_cli/direct_probe2_20260702T0211Z/open_duck_direct_phase2_probe2_manual_collect.tar.gz`
- extracted smoke dir:
  `outputs/analysis/colab_cli/direct_probe2_20260702T0211Z/extracted/open_duck_direct_phase2_training2/smoke_20260702T021124Z_gpu`

## Result

The direct smoke command reached the real smoke runner and created:

- `smoke_manifest.start.json`
- `smoke_manifest.live.json`
- `stdout.txt`
- `stderr.txt`

The latest live manifest says:

- status: `RUNNING`
- child pid: `2223`
- elapsed: `330.0s`
- poll returncode: `None`

The process later disappeared with no final manifest.

The stdout tail reached:

- `Observation size: 101`
- PPO params printed
- `Enabled restore-policy KL loss: scale=7.5 ...`
- `Skipping checkpoint/export at step 0; export_min_step=1`

The stderr tail only showed:

- `mujoco_menagerie` clone progress
- one JAX overflow warning from `jax/_src/abstract_arrays.py`

No traceback, Python exception, ONNX export, checkpoint, or final smoke manifest was
produced.

## Interpretation

This localizes the current startup hold below the high-level Colab workflow:

1. Colab setup and dependency installation are not the blocker.
2. The smoke runner argument parsing is not the blocker after removing the bad manual flag.
3. The Playground env instantiates and reports the 101-observation contract.
4. The run reaches restore-policy KL setup.
5. The process disappears during the first PPO/JAX compile/update window.

This is not a reward result and not a candidate result. It is a trainer/runtime startup
hold for this narrow Phase 2 restored run shape.

## Next Isolation

Run direct smoke-startup isolation with one variable changed at a time:

1. restore checkpoint only, no behavior prior, same tiny PPO shape.
2. behavior prior only, no restore-policy KL.
3. no restore checkpoint and no behavior prior, same tiny PPO shape.
4. CPU fallback for the same tiny command if GPU still disappears.

The next useful result is the smallest option among restore checkpoint, behavior prior,
restore-policy KL, and GPU PPO compile that reproduces the disappearance.
