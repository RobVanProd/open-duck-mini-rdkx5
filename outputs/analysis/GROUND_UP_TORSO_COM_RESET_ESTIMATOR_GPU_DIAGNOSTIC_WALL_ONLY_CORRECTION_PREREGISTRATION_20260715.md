# Ground-Up Torso-COM Reset-Estimator GPU Diagnostic Wall-Only Correction Preregistration — 2026-07-15

## Evidence and authorization

Two live attempts show that Resources-UI rate acquisition is not reliably
available within an automated session boundary: it succeeded once after a
longer interaction, then remained 0/hour through the diagnostic's frozen
60-second window. The diagnostic failed before upload and cleaned up correctly.

The operator explicitly authorized completing the goal without supplying more
billing numbers. Therefore the successor removes only the interactive rate
handshake and makes no compute-unit claim. It does not relax any scientific,
training, recovery, or robot boundary.

## Frozen correction

- One fresh named T4 diagnostic session, no retry/resume/reuse.
- Hard total wall ceiling 300 seconds and 60-second named-stop reserve.
- No compute-rate input, projection, estimate, or maximum-CU claim. Record
  compute usage as `UNMEASURED`.
- After exact named idle-T4 identity, upload the same exact 21 files and run the
  same report-before-raise wrapper.
- Recover and hash the report atomically, classify it by the already-frozen
  three result classes, then stop the named session.
- The wrapper must terminate before `training_command`; PPO processes and steps
  remain zero under every outcome.
- Pass still requires report recovery, successful named stop, and total wall
  <=300 seconds.

Before allocation, a zero-session CPU contract must prove the handshake and all
rate/CU parsing are absent, exact 21 assets and source hashes remain unchanged,
idle-T4 status precedes uploads, wrapper pass/fail fixtures stop before PPO,
atomic recovery/cleanup/wall enforcement remain present, and session inventory
is unchanged.

A passing contract plus the operator's continuing authorization permits one
wall-only diagnostic allocation. No exact billing statement, training,
behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action is
authorized.
