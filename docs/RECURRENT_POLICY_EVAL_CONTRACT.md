# Recurrent Policy Eval Contract

Status: `PASS_OFFLINE_EVAL_SCAFFOLD_READY`

This document defines the offline-only ONNX contract required to evaluate a
stateful/recurrent student inside the canonical fitted-bridge gate. It does not
approve robot testing, deployment, runtime changes, or training.

## Why This Exists

The `LIVE_ORACLE_DAGGER_PHASE_STUDENT` branch has now exhausted the deployable
static feed-forward variants:

- command-gated x0-safe/x0.08 policy: fixed x0 semantics, held at the x0.08
  tracking plateau
- phase-quadrant heads: regressed and produced a termination
- smooth phase blend: removed the hard transition but stayed at the plateau
- phase/command-modulated shared trunk: regressed with a seed collapse

The remaining hypothesis is that the student needs explicit live state across
ticks to represent the stance-transition action that the source-VX selector
retrieves from its window structure.

## Canonical Evaluator

The only promotion-style offline gate remains:

```text
tools/run_candidate_seed_sweep.py
  -> tools/eval_policy_with_actuator_bridge.py
  -> tools/closed_loop_sim_eval.py
```

with:

```text
task: flat_terrain_backlash
bridge: fitted
duration: 15 seconds
seeds: 0-7
x=0.08 and x=0.0 gates
```

The evaluator still defaults to the deployed stateless policy contract:

```text
obs[1,101] -> continuous_actions[1,14]
```

No existing policy changes behavior unless recurrent flags are passed.

## Stateful ONNX Contract

For recurrent diagnostics, the evaluator now supports an explicit stateful
ONNX contract:

```text
inputs:
  obs_input_name              [1,101]
  state_input_name_0          fixed shape, batch dimension may be dynamic
  ...

outputs:
  action_output_name          [1,14]
  state_output_name_0         same semantic state as state_input_name_0
  ...
```

Hidden state is initialized to zeros at environment reset and carried forward
tick by tick inside a single rollout. It resets between seeds and between
independent x=0.0 / x=0.08 gates.

The state input/output names must be supplied explicitly:

```bash
--policy-obs-input-name obs
--policy-action-output-name continuous_actions
--policy-state-input-names h_in
--policy-state-output-names h_out
```

For multiple state tensors, use comma-separated names in matching order.

## Rejection Rules

The evaluator rejects recurrent candidates when:

- a named observation/action/state input or output is missing
- state input and output counts differ
- a hidden-state tensor has a dynamic non-batch dimension
- the policy action output is not `[14]` after removing the batch dimension
- the Playground observation/action contract is not `101/14`

The evaluator must not infer, pad, truncate, or silently reorder hidden state.

## Runtime Boundary

This scaffold is offline-only. A recurrent ONNX that requires hidden inputs and
outputs is not deployable through the current RDK-X5 runtime until a separate
runtime adapter carries hidden state with verified reset semantics.

Promotion to robot candidate therefore still requires one of:

- a stateless `obs[1,101] -> actions[1,14]` export that clears the canonical
  gates, or
- a reviewed runtime adapter for hidden state, plus fidelity and reset tests.

## Hardware Calibration Note

The physical left-knee soft offset was corrected after the existing actuator
bridge fit:

```text
left_knee: -1.488 -> 0.0371
right_knee: 0.0798 unchanged
```

The old bridge fit remains useful for offline continuity, but it is now stale
for final robot-side validation. Before any robot motion is reconsidered, the
operator should re-run read-only/supported actuator tracking diagnostics on the
corrected hardware and refresh the bridge fit.

## Decision

```text
PASS_OFFLINE_EVAL_SCAFFOLD_READY
```

Next offline work may train or export a recurrent/live-state diagnostic and
gate it with the explicit hidden-state flags. Do not promote a recurrent policy
to robot testing until runtime hidden-state support exists or the policy is
distilled back to the fixed stateless contract.

## First Diagnostic Trainer

The branch now includes a minimal recurrent BC diagnostic:

```text
tools/train_recurrent_bc_student.py
```

It trains a small Elman-style recurrent student from contiguous trace windows
and exports:

```text
obs[1,101], h_in[1,H] -> continuous_actions[1,14], h_out[1,H]
```

Validation smoke:

```text
outputs/analysis/RECURRENT_BC_STUDENT_SMOKE.md
outputs/analysis/recurrent_bc_student_smoke.json
```

The smoke only verifies training/export/fidelity and stateful evaluator
execution. It is not a candidate policy and does not change the runtime
deployability boundary above.
