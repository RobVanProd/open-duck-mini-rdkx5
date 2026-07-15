# Ground-Up Torso-COM Reset-Estimator Same-Session Rate Handshake Preregistration — 2026-07-15

## Evidence and authority

At 2026-07-15T17:14:28-04:00 the operator reported a fresh Colab Resources-UI
reading of 79.36 available compute units, approximately 0 units/hour, and zero
active sessions. Independent `colab sessions` also reported zero active
sessions. This falsifies the acquisition assumption behind the prior
pre-allocation attestation correction: an idle account exposes no positive T4
rate to attest.

Decision: `REQUIRE_SAME_SESSION_PRETRAINING_RATE_HANDSHAKE`. The prior
correction's mechanical checks remain valid, but its positive-rate input cannot
be obtained while idle and it must not be launched with zero or a stale rate.

The operator then explicitly approved the corrected continuation. That approval
authorizes one fresh T4 allocation only after the zero-allocation contract below
passes. It does not waive the rate gate, limits, cleanup, or no-retry rule.

## Frozen correction

Only the rate-acquisition boundary changes:

1. Replace the three pre-allocation attestation CLI values with one required
   `--attestation-file` path. The path and its `.tmp` sibling must not exist at
   planning or allocation time.
2. Allocate the same fresh named T4 session and validate the exact named idle
   T4/GPU status before any upload.
3. Emit one machine-readable `GROUND_UP_RESET_ESTIMATOR_RATE_REQUEST=` marker,
   then wait at most 120 seconds for the local attestation JSON. Waiting counts
   against the unchanged 2,400-second total wall ceiling and preserves the
   unchanged 120-second stop reserve.
4. The operator need provide only the live Resources-UI rate and available
   units. The collector records receipt time, fixed source
   `COLAB_RESOURCES_UI_OPERATOR_ATTESTATION`, and exact session name in JSON.
5. Require exact session/source, a timezone-aware collector timestamp no more
   than 120 seconds old and no more than 60 seconds future, finite positive
   rate, at least 2.0 available units, and projected total cost
   `rate * 2400 / 3600 <= 2.0`.
6. Upload and training may begin only after the validated attestation is copied
   into the launch record. Timeout, malformed input, zero rate, insufficient
   balance, excessive rate, wrong session/source, or stale/future timestamp
   fails closed and stops the named session without upload or training.
7. Preserve the attestation file as evidence. Do not delete or rewrite it.

Every training job, asset, checkpoint, command, reward, seed, architecture,
horizon, wall/stop limit, recovery check, and behavior gate remains frozen.
There is one session and one training process; no resume, retry, or reuse.

## Zero-allocation contract

Before allocation, a CPU-only contract must prove:

- exact upstream failed-launch, idle-reading, prior-contract, hosted-package,
  job, and preregistration sources;
- plan/dry-run success with exactly 19 assets and unchanged session/lifecycle;
- the attestation path is absent and allocation remains false;
- source order is status validation, request/wait/validation, then first upload;
- the 120-second handshake is inside the total wall and stop-reserve helpers;
- 1.07/hour and 79.36 units pass at .713333 projected units;
- 3.0/hour passes exactly at 2.0; 3.000001, zero/nonfinite rate, balance below
  2.0, wrong source/session, malformed JSON, stale >120 seconds, and future
  >60 seconds fail;
- exact 120-old and 60-future boundaries pass;
- a deterministic local-file wait fixture passes without Colab;
- timeout/error paths precede every upload/training call and cleanup remains
  armed before allocation;
- session inventory remains unchanged at zero and no remote bytes/PPO steps
  occur.

Pass status is
`PASS_RESET_COM_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_CONTRACT`. Failure stops
without allocation. A pass plus the operator's recorded approval authorizes
one interactive corrected T4 launch. Once the request marker appears, only the
two live UI numbers are needed. No local GPU/iGPU, RDK-X5, runtime, robot, or
behavior evaluation is authorized.
