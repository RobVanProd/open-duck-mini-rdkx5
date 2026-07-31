# Ground-Up Torso-COM Reset-Estimator Behavior Evaluator Preregistration — 2026-07-15

## Scope

The hosted artifact and the two frozen transformed policy graphs pass their
contracts. The existing CPU evaluator defaults to the historical 115-D actor
observation and has no switch for the already-contracted reset-estimator input.
This preregisters only the evaluator plumbing needed to execute the frozen later
evaluation in the hosted-training preregistration.

## Frozen implementation contract

1. Add one default-false `policy_reset_com_estimator_input` field to
   `ClosedLoopConfig`, one matching opt-in CLI flag, and one reporting field.
2. When true, set only the composed environment config's existing
   `ground_up_reset_com_estimator_input=True` before environment construction.
   When false, behavior and reporting outside the new false-valued input field
   remain unchanged.
3. Preserve dynamics override ordering: construct the environment, name-resolve
   `trunk_assembly`, apply the body-2 X-only model override, then perform the
   deterministic home reset. The environment's existing reset code alone reads
   and latches the estimator; the evaluator must not inject or recompute it.
4. Before behavior, a CPU-only contract must prove:
   - default-off reset remains 115-D and has no latch key;
   - enabled nominal/-.05/+.05 resets are 116-D, contain the latch at index 101,
     retain the final 14-D reference action, and mutate only body 2 X for the
     endpoint models;
   - the three latch values match the independent frozen estimator within 1e-6
     and are finite, bounded, and strictly ordered;
   - the transformed ONNX graphs have exact 116-D input hashes and the evaluator
     remains CPU-only;
   - zero policy steps and zero formal behavior cells execute.

## Frozen behavior matrix

If the contract passes, run exactly 12 matrices / 48 cells:

- two checkpoints: 1,003,520 and 2,007,040;
- two measured fits: P30 and P31/34;
- conditions: NOMINAL, `TORSO_COM_X_NEG=-.05 m`, and
  `TORSO_COM_X_POS=+.05 m`;
- commands x=0/.074/.077/.080; one mechanically inherited seed 167931544;
- 600 ticks, deterministic home-support reset, exact per-run readback,
  estimator input enabled, applied-target observation enabled, CPU only.

Every prior x=0 and moving gate remains unchanged: duration complete, bilateral
gait for moving commands, zero saturation, zero measured rate excess, tracking
p95 <=.20 rad, and all prior nominal/x=0 thresholds. There is no stop-at-first-
failure rule. The arm advances only if both checkpoints pass all 48 cells.
Otherwise close it without retry, midpoint, closest-checkpoint promotion, or
training-reward selection.

No training, Colab, local GPU/iGPU, RDK-X5, runtime, robot, deployment, torque,
or motor action is authorized. Even a behavior pass is not robot clearance and
requires a separate next preregistration.

