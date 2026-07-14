# Ground-Up Tracking-Error Decomposition Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_AUDIT`

The tail, pitch-rate, and actor-SWA screens preserve gait but repeatedly fail
the same `0.20 rad` sent-target-to-actual tracking boundary. Before changing
training or runtime, every failing trace is decomposed using the exact identity:

`sent - actual = (sent - applied) + (applied - actual)`

The audit uses seed 100 from 78 unique policy/command traces; seed 101 remains a
reproduction check. On the maximum-p95 pitch joint of each failing trace, every
above-threshold tick is assigned exactly one class:

- both bridge and servo components individually exceed `0.20 rad`;
- bridge alone is sufficient;
- servo alone is sufficient;
- neither component is sufficient alone, but their aligned sum exceeds the
  boundary (`COMPOUND_SUBTHRESHOLD`).

Each trace family receives its strict-majority class. A causal implementation
is selected only if TAIL, RATE, and SWA independently have the same non-mixed
majority. A compound result selects only preregistration of a CPU contract for
an absolute sent-target guard centered on measured actual position. It does not
authorize that implementation yet.

No policy/runtime modification, training, Colab, local GPU, RDK-X5, robot,
deployment, torque, or motor access is authorized by this audit.
