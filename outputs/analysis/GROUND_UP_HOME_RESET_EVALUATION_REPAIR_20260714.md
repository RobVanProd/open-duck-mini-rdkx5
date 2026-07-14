# Ground-Up Home-Reset Evaluation Repair

status: `CORRECTNESS_REPAIR_BEFORE_REEVALUATION`

`evaluate_ground_up_policy.py` previously inherited
`ClosedLoopConfig.reset_mode="playground"`. That conflicts with the nominal and
reference-residual preregistrations, which freeze deterministic home reset and
zero base velocity.

The wrapper now:

- defaults explicitly to `home-support`;
- passes the selected mode into `ClosedLoopConfig`;
- records the selected reset mode in every evaluation artifact;
- retains `playground` only as an explicit diagnostic option.

The first repaired invocation exposed a second boundary assumption before any
policy result was emitted: `home-support` expected optional in-environment
actuator-bridge and foot-history fields that do not exist in the pinned base
Playground checkout. Optional histories are now reset only when present, using
their actual stored shape rather than a non-existent config. The external
fitted bridge remains the sole actuator model for this evaluator.

No behavior threshold, actuator bridge, command, seed, duration, policy,
reference phase, or simulator model changes. Previously saved policies must be
re-evaluated; prior randomized-reset classifications are not silently reused.

Local CPU only. No training, Colab, GPU, RDK-X5, or robot access is authorized.

The hardware-vector diagnostic then exposed a reporting-only aggregation bug:
a positive-command-only campaign was forced to overall hold because it had no
x=0 rows. Absence of an unrequested x=0 condition is now treated as vacuously
finite; when x=0 is requested, every x=0 row must still complete. Per-run
emergence evidence and all behavior thresholds are unchanged.
