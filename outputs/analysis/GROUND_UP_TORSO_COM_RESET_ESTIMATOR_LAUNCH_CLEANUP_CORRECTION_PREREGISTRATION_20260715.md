# Ground-Up Torso-COM Reset-Estimator Launch Cleanup Correction Preregistration

status: `PREREGISTERED_PRESESSION_FAIL_CLOSED_CLEANUP_CORRECTION`

## Pre-run defect

The launch dry-run contract passed with zero sessions, but code review before
allocation found two fail-closed gaps:

1. `session_created` became true only after `colab new` returned success. A
   partial server-side allocation paired with a nonzero CLI result could
   therefore skip the named cleanup attempt.
2. work commands could consume the full 2,400-second external budget and leave
   only an additional stop timeout. The record measured this overrun but did
   not make it fail a nominally successful artifact recovery.

No session, upload, hosted execution, training, or outcome has occurred. This
is a pre-outcome orchestration correction, not a retry or budget change.

## Frozen correction

- Set the named-session cleanup-required flag immediately before invoking
  `colab new`, so `finally` attempts `colab stop --session
  open-duck-reset-estimator-t4` even if allocation returns nonzero.
- Freeze `STOP_RESERVE_SECONDS = 120.0` inside the unchanged 2,400-second total
  session ceiling.
- Every post-allocation status, upload, exec, and download timeout must use
  `remaining_total - STOP_RESERVE_SECONDS`; fail before starting work if that
  quantity is nonpositive.
- The named stop attempt may consume only the remaining total wall time, with a
  minimum practical CLI timeout of one second when the measured remainder is
  positive. Cleanup remains mandatory even after earlier failure.
- A launch can report `PASS_HOSTED_ARTIFACTS_RECOVERED` only if the stop command
  returns zero and measured allocation-through-cleanup time is `<=2400.0`
  seconds. Otherwise record `FAIL_HOSTED_CLEANUP_OR_SESSION_CEILING`, retaining
  any recovered artifacts as nonpromotable evidence.
- Do not alter accelerator, session name, assets, remote job, training recipe,
  compute ceiling, artifact contract, retry prohibition, or any policy value.

## Contract and authority

A replacement zero-session contract must hash-lock the corrected helper,
prove cleanup-required ordering, the 120-second reserve on every work command,
mandatory named stop, and pass dependence on stop/total-wall success. It must
repeat the exact dry run with no active-session change, zero remote bytes, and
zero training.

This document authorizes only that source correction and replacement dry-run
contract. It does not authorize Colab allocation, compute, uploads, hosted
execution, PPO, behavior evaluation, GPU/iGPU, RDK-X5, runtime, deployment,
torque, motors, or robot access. Explicit user approval of the single hosted
run remains required.
