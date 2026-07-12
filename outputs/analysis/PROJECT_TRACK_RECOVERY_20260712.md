# Project Track Recovery

status: `POLICY_DEVELOPMENT_ONLY_NO_ROBOT_CLEARANCE`

The frozen hard-vector projection preregistration states that a pass authorizes
architecture work only, not hardware. The projection passed, but its result
incorrectly changed the next step to runtime review. That is the divergence.

The active policy problem remains:

1. produce a policy—not a command wrapper or runtime motion modifier—that
   respects the measured per-joint actuator envelope;
2. pass the frozen x=0 and x=.08 offline gates, including zero-command
   semantics, motion floors, tracking, support, and velocity excess;
3. complete the repository's formal policy-clearance decision before any
   robot power-on or hardware validation for that candidate.

Known rejected routes remain closed: scalar zero-label sweeps, command-gated
wrapper promotion, independent phase heads, one-shot phase modulation,
supervised recurrent BC, supervised rate refits, and the calibrated
penalty-PPO recipe that collapsed to standing.

Commits `b4398f1` and `9d89d0f` were reverted by `6cf6069` and `d634aee`.
Later hardware records are retained only to describe actual operational state;
they provide no policy-qualification credit. No robot, network, deployment,
GPU, Colab, or training action is authorized by this recovery record.
