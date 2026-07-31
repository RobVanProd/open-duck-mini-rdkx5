# Live-Oracle Recurrent Eval Readiness

status: `PASS_OFFLINE_EVAL_SCAFFOLD_READY`

## Summary

The static feed-forward phase/memory variants have been run and did not break
the canonical x=0.08 fitted-bridge tracking plateau. The next useful software
step is a recurrent/live-state student, but that requires an explicit evaluator
contract because the deployed policy path is stateless.

## What Changed

- `tools/closed_loop_sim_eval.py` now supports explicit stateful ONNX I/O.
- `tools/eval_policy_with_actuator_bridge.py` exposes stateful ONNX flags and
  reports full ONNX input/output metadata when inspected.
- `tools/run_candidate_seed_sweep.py` passes the same stateful flags through
  the canonical multi-seed gate.
- `tools/train_recurrent_bc_student.py` trains and exports a minimal
  `obs,h_in -> action,h_out` recurrent BC diagnostic from contiguous trace
  windows.
- Stateless `obs[1,101] -> actions[1,14]` policies use the old default path.

## New Flags

```bash
--policy-obs-input-name OBS_INPUT
--policy-action-output-name ACTION_OUTPUT
--policy-state-input-names H_IN[,C_IN]
--policy-state-output-names H_OUT[,C_OUT]
```

Hidden state is initialized to zeros at rollout reset and carried tick to tick.
It resets between seeds.

## Gate Boundary

This is an offline evaluator scaffold only. It does not make recurrent ONNX
deployable on the robot. A recurrent candidate may be used to test the
representation hypothesis in sim, but robot promotion still requires either a
stateless export or a separate reviewed runtime hidden-state adapter.

## Smoke Result

The first recurrent BC smoke used:

```text
manifest: outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json
hidden_dim: 32
sequence_length: 16
steps: 80
```

It produced a valid ONNX with fidelity under `1e-6` and the stateful evaluator
executed it with `h_in -> h_out`. The smoke is intentionally too short and
undertrained to be a candidate.

## Hardware Note

The corrected physical left-knee offset means the existing hardware-derived
actuator bridge is stale for final robot validation. Keep using it for branch
continuity, but re-fit after supported/read-only hardware diagnostics before
any robot-side candidate gate.

## Decision

```text
PASS_OFFLINE_EVAL_SCAFFOLD_READY
```
