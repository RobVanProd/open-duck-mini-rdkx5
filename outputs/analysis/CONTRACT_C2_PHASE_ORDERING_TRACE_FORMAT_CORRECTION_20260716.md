# Contract C2 Phase Ordering Trace-Format Correction

Status: `PREREGISTERED_CORRECTION_BEFORE_FORMAL_OUTCOME_AGGREGATION`

The initial execution produced one 600-tick raw trace, then stopped before the
cell was aggregated because the wrapper expected `phase_index` at the trace
root. The evaluator emits that value under `oracle_state` only when
`trace_oracle_state=True`.

The sole authorized correction is to enable this read-only trace field and
read `oracle_state.phase_index`. It does not change policy input, phase order,
action, physics, gate, matrix, materiality rule, or any frozen threshold. The
partial raw trace is invalidated as a formal outcome and the complete matrix
restarts at cell 1, overwriting it.

The wrapper now also reports the evaluator's returned diagnostic if no trace
is produced. No outcome-driven parameter change is authorized.

CPU simulation only. Robot clearance remains `NO`.
