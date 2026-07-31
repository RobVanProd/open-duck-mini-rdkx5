# Contract C2 Phase Ordering Preregistration

Status: `PREREGISTERED_BEFORE_OUTCOME_CELLS`

## Question

Compare the deployed `OBSERVE_THEN_ADVANCE` imitation-phase order with the
counterfactual `ADVANCE_THEN_OBSERVE` order. The former is also the training
match: the policy consumes the current observation and the simulator advances
the imitation reference during the subsequent transition.

The evaluator option is default-false. This study does not edit the frozen
runtime.

## Frozen matrix

Run both protected persistent checkpoints, P30, commands x = 0.074, 0.077 and
0.080, seeds 100 and 101, for 600 ticks under both orderings. This is 12 cells
per ordering and 24 cells total. Reset, reference, applied-target input,
measured bridge, hard-vector transform, actual-centered guard, conservative
envelope, candidate thresholds, bilateral-gait requirement, tracking p95 <=
0.20 rad, zero saturation and zero measured rate excess remain unchanged.

## Frozen interpretation

An effect is material if any paired cell changes pass/fail, survival or
termination; if absolute tracking-p95 delta is at least 0.01 rad; or if
absolute measured-rate-excess delta exceeds 0.00001 rad/s. Otherwise the
effect is negligible and the deployed ordering is retained. A material result
only triggers review against the identified training match; it does not
authorize a runtime edit.

Input and tool hashes are frozen in
`contract_c2_phase_ordering_preregistration.json`. Outcome-driven changes are
forbidden.

CPU simulation only. No training, hosted allocation, robot, RDK-X5, GPU or
iGPU access. Robot clearance remains `NO`.
