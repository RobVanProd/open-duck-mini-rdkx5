# Ground-Up Torso-COM Reset-Estimator Same-Session Hosted Launch Result — 2026-07-15

## Decision

`STOP_NO_RETRY_HOSTED_GPU_EXPANSION_EQUIVALENCE_FAILED`

The approved same-session handshake worked exactly: the live 1.07/hour rate
and 79.36-unit balance arrived 5.855427 seconds before validation, projected
the full wall ceiling at .713333 units, and allowed the 19 frozen uploads.

The hosted job then failed before PPO at the checkpoint-expansion gate. Its
only reported failed check was `step_zero_outputs_exact`, whose frozen ceiling
is 1e-7. The training command occurs after this gate in source and was never
reached. Therefore training processes and PPO steps are zero, no checkpoint or
policy artifact was recovered, and behavior remains unevaluated.

## Cleanup and compute evidence

- One fresh named T4 session.
- Hosted script wall: 77.009848 seconds.
- Total session wall: 184.648470 seconds.
- Named stop returned 0; independent inventory reports zero active sessions.
- Elapsed wall at the attested rate projects to .054881628639 units. This is a
  projection, not an exact billed-usage claim.

The remote expansion function wrote its detailed report before raising, but a
failed-job report was not included in the frozen download set and the session
was correctly stopped. The actual actor/critic error magnitude is therefore
unknown. Do not label it numerical drift, relax 1e-7, or infer the closest
value.

Raw evidence is hash locked in the result JSON. The launch record contains the
complete remote traceback and command transcript.

## Authority boundary

The no-retry rule closes this launch. This is a pretraining GPU-topology method
failure, not a policy result. A valid successor requires a separate
report-before-raise GPU expansion diagnostic that captures the exact per-z
actor/critic errors without PPO. No further Colab allocation, training,
behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action is
authorized by this result.
