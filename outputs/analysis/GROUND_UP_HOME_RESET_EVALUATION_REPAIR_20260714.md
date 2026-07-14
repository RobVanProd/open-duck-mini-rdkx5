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

No behavior threshold, actuator bridge, command, seed, duration, policy,
reference phase, or simulator model changes. Previously saved policies must be
re-evaluated; prior randomized-reset classifications are not silently reused.

Local CPU only. No training, Colab, GPU, RDK-X5, or robot access is authorized.
