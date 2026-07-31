# Ground-Up Temporal-Tail Objective Decision

status: `TAIL_EXCEEDANCE_MECHANISM_SELECTED_FOR_CPU_CONTRACT_ONLY`

## Measured facts

- The applied-target actor observes the fitted actuator state, walks for all
  600 ticks, and has zero measured target-rate excess.
- At x=.074, 2M lowers mean pitch-chain target error from .07931 to .07517 rad
  while increasing worst-joint p95 from .22229 to .22913 rad and the fraction
  of left-knee samples above .20 from 9.83% to 10.67%.
- The same mean-versus-tail split occurs across the command set: the failure is
  concentrated in the upper tracking-error tail, not a global mean collapse.
- The current ground-up objective has no sent-target-versus-actual-position
  term. Its imitation term follows the polynomial reference, not the external
  hardware tracking gate.
- The repository's earlier direct joint-target experiment used a mean
  pseudo-Huber cost and failed both compact gates. That exact mean-cost
  formulation remains closed and will not be repeated.
- Generic restore KL and behavior-prior recipes previously lost forward
  progress. They are not selected by this evidence.

## Selected causal mechanism

The only next mechanism selected is a default-off pitch-chain tracking-tail
diagnostic that is zero at or below the existing .20 rad gate and positive only
for the excess above it. It must compare the same sent target and actual joint
position on the same six pitch-chain indices used by evaluation.

This selects the quantity to wire and verify; it does not select its training
aggregation, scale, or optimizer treatment. Before any hosted run:

1. prove on CPU that the diagnostic exactly matches an independent NumPy
   implementation on frozen 600-tick traces;
2. prove it is zero below/at .20 and monotonic above .20;
3. prove default-off dynamics, observations, rewards, and exports are exact;
4. preregister a bounded scale/constraint search and full 600-tick stop rule;
5. retain a no-tail-objective control from the same source checkpoint.

No training is authorized by this decision. No threshold, existing gate, or
hardware boundary changes.
