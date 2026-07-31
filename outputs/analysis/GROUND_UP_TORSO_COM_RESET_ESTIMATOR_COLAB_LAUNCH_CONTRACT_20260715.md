# Ground-Up Torso-COM Reset-Estimator Colab Launch Contract

status: `PASS_RESET_COM_ESTIMATOR_COLAB_LAUNCH_CONTRACT`

All 20 frozen launch checks pass. The contract created zero sessions, uploaded
zero remote bytes, downloaded zero remote bytes, and ran zero training steps.

## Frozen launch

- CLI version: `0.6.0`.
- Session: `open-duck-reset-estimator-t4`.
- Accelerator: `T4`.
- Session/process count: one/one.
- Total session wall ceiling: 2,400 seconds, beginning before allocation.
- Compute ceiling: 2.0 units.
- Resume/retry/adopt-existing-session surfaces: absent.
- Allocation requires the explicit `--allow-colab-allocation` flag.
- Cleanup becomes mandatory immediately before `colab new`, including a
  partial-allocation/nonzero-CLI outcome.
- A fixed 120-second stop reserve is subtracted from every allocation/status/
  upload/exec/download work timeout.

The external remaining-time timeout includes allocation and all 19 exact
uploads, so remote setup and training cannot extend the total wall ceiling.
Named-session cleanup is in `finally`; no command addresses another session.
A passing recovery additionally requires stop return code zero and total
allocation-through-cleanup time `<=2400.0` seconds. Recovered files remain
nonpromotable if either cleanup condition fails.

## Compute-rate boundary

The exact status parser reproduces the reported 1.07-unit/hour rate as a
0.713333-unit maximum projection over 2,400 seconds, below the 2.0 ceiling. A
3.10-unit/hour control projects to 2.066667 and is rejected before uploads or
execution. Missing, nonfinite, or nonpositive rates also fail closed.

## Dry run and assets

The dry run stages and hash-validates exactly 19 regular nonsymlink assets,
records the exact T4 `new/status/upload/exec/download/stop` commands, and exits
with `PASS_DRY_RUN_NO_ALLOCATION`. The active-session inventory is identical
before and after: no active sessions.

The download contract contains only the hosted manifest and artifact archive,
uses temporary local names, verifies the remote result marker/hash/byte count,
checks the manifest fields, and atomically finalizes both files. The launch
record preserves commands, stdout, rate projection, recovery hashes, cleanup,
and elapsed session time.

Contract JSON SHA-256:
`4d3b281ad35fed6d891a5382cd56a521427be17c6eaa74c9b7aa8ece9150abaf`.

## Authority

This contract does not authorize allocation. The exact helper and dry plan are
ready, but a user must explicitly approve the single hosted
`RESET_EST_LATCH_U05` run before `--allow-colab-allocation` may be supplied.
Training, behavior evaluation, GPU/iGPU, RDK-X5, runtime, deployment, torque,
motors, and robot access remain unauthorized.
