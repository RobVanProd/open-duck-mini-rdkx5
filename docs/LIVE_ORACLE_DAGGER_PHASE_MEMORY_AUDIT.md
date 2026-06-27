# Live-Oracle DAgger Phase / Memory Audit

Status: `PASS_OBS_HAS_DEPLOYABLE_PHASE_MEMORY`

This audit clarifies the representation ladder for
`LIVE_ORACLE_DAGGER_PHASE_STUDENT` without changing the deployed policy
contract.

## Fixed Contract

The deployable contract remains:

```text
obs[1,101] -> continuous_actions[1,14]
```

Any candidate that requires a larger ONNX input is not deployable through the
current RDK-X5 runtime path unless a separate runtime wrapper is explicitly
designed, implemented, and verified.

## Existing Memory In The 101-Observation Contract

The deployed observation already contains state and phase memory:

```text
obs[41:83]   action_history          42 values = 3 * 14 actions
obs[83:97]   previous_motor_targets  14 values
obs[97:99]   foot_contacts           2 values
obs[99:101]  phase                   2 values
```

So the first deployable "memory" rung should exploit the memory that already
exists inside the canonical `101` values before producing a larger ONNX graph.

## Rung Interpretation

### Rung 1: Frame-Stack Precheck

A literal `k=4` frame stack would create:

```text
4 * 101 = 404 input values
```

That is useful as a diagnostic but is not promotable under the fixed contract.
For a deployable rung-1 attempt, use the existing action-history,
previous-target, contact, and phase fields already present in `obs[101]`, then
close the live-oracle loop on the current student's visited states.

If a 404-input frame-stack student is ever run, mark it explicitly:

```text
NON_DEPLOYABLE_FRAME_STACK_DIAGNOSTIC
```

and do not compare it as a robot candidate.

### Rung 2: Explicit Phase Conditioning

The canonical observation contains phase in `obs[99:101]`. A phase-conditioned
student can preserve the same ONNX input contract by using those two fields to
select or blend phase-specific action heads inside the graph.

Required before promotion:

```text
verify obs[99:101] matches the Playground phase convention during canonical eval
verify ONNX input remains [1,101]
verify action fidelity <= 1e-6
```

### Rung 3: Recurrent Student

A GRU/LSTM student requires explicit hidden state handling. It is not a drop-in
replacement for the current ONNX contract unless the runtime carries hidden
state and the export contract documents additional inputs/outputs.

Required before promotion:

```text
document hidden-state shape
verify runtime hidden-state update semantics
verify ONNX fidelity with hidden state
run x=0.0 and x=0.08 canonical gates
```

## Decision

For the next executable step, run the live-oracle DAgger loop using the existing
`obs[101]` contract and treat it as the deployable phase/memory baseline:

```text
status: PASS_OBS_HAS_DEPLOYABLE_PHASE_MEMORY
next: run_live_oracle_dagger_iteration.py
```

Do not produce or promote a 404-input frame-stack ONNX as a robot candidate.

## Recurrent Eval Follow-Up

After the deployable static phase/memory variants held at the x=0.08 tracking
plateau, the evaluator was extended with explicit stateful ONNX support for
offline diagnostics:

```text
docs/RECURRENT_POLICY_EVAL_CONTRACT.md
outputs/analysis/LIVE_ORACLE_RECURRENT_EVAL_READINESS.md
```

This does not change the deployed runtime contract. A recurrent candidate with
hidden-state inputs/outputs is an offline sim diagnostic until either:

- it is distilled back into the fixed `obs[1,101] -> actions[1,14]` contract, or
- a separate RDK-X5 runtime hidden-state adapter is designed, implemented, and
  verified.
