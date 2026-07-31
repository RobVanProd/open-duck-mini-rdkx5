# Ground-Up Torso-COM Reset-Estimator Hosted Launch Preregistration

status: `PREREGISTERED_LAUNCH_CONTRACT_REQUIRED_EXPLICIT_ALLOCATION_APPROVAL`

## Purpose

The `RESET_EST_LATCH_U05` hosted job passes its complete CPU package contract,
but that contract intentionally does not define or authorize session
allocation. This document freezes the missing orchestration boundary so that
a later approval cannot trigger ad hoc CLI choices.

It authorizes construction and read-only validation of a launch helper only.
It does not authorize `colab new`, uploads to a live VM, hosted execution, or
training.

## Frozen CLI and session

- CLI: `colab` version `0.6.0`;
- accelerator: `T4`, matching the preceding ground-up hosted path;
- session name: `open-duck-reset-estimator-t4`;
- create exactly one fresh session with
  `colab new --session open-duck-reset-estimator-t4 --gpu T4`;
- do not adopt, reuse, or stop any other session;
- do not use `colab run --keep` or mount Drive;
- execute the contracted local job using `colab exec --session ... --file ...`
  after uploading only its exact hash-locked assets to `/content/<basename>`.

The helper must require an explicit `--allow-colab-allocation` flag and fail
before `colab new` without it. Presence of the helper, this preregistration, or
the passing package contract is not that approval.

## Frozen total budget enforcement

Start the external wall clock immediately before `colab new`. The complete
session lifetime—including allocation, status readback, uploads, job setup,
training, artifact recovery, and cleanup—is capped at 2,400 seconds.

Immediately after allocation, run `colab status` for only the named session and
parse the reported approximate compute-unit usage rate. Before uploading or
executing, require:

`reported_rate_per_hour * 2400 / 3600 <= 2.0`.

If the rate is absent, nonfinite, nonpositive, or projects above 2.0 units,
stop the named session and fail before job execution. The remote job retains
its own 2,400-second ceiling; the launch helper must pass only the smaller
remaining external time to `colab exec`, so uploads and allocation reduce the
time available to the job rather than extending the budget.

Always attempt to stop the named session in `finally`, without addressing any
other session. No retry, new accelerator, reconnect, resume, or second session
is allowed after any failure.

## Frozen assets and execution

Before allocation, locally run the contracted job's asset-only validator over
the exact staged asset directory. Upload exactly the files in its
`EXPECTED_HASHES` mapping; the local job file is transmitted by `colab exec`
and is not an additional remote asset. Reject symlinks, missing files, hash
mismatches, extra staged files, or a dirty/overwriting recovery destination.

After successful execution, download exactly:

- `/content/GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json`;
- `/content/GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz`.

Use temporary local names, then verify the manifest/artifact contract and
atomic local replacement before finalizing them. Preserve the complete local
CLI stdout/stderr, session status, timestamps, rate projection, upload list,
download hashes, stop result, and elapsed session time in a launch record.

Training reward remains nonselective and behavior remains unevaluated. A
successful download authorizes only the already named local artifact contract,
not behavior evaluation.

## Required zero-session contract

Before allocation, a committed CPU-only contract must prove:

1. exact hosted preregistration, job, package-contract, CLI version, asset
   mapping, session name, T4 accelerator, and command construction;
2. allocation is impossible without `--allow-colab-allocation`;
3. rate parsing/projection, remaining-time execution timeout, no-retry logic,
   named-session-only cleanup, exact upload/download sets, and atomic local
   recovery are present;
4. a dry-run plan validates all assets and records commands without calling
   any state-changing Colab command;
5. contract execution uses CPU only, creates zero sessions, uploads/downloads
   zero remote bytes, and runs zero training steps.

## Authority boundary

This document authorizes only implementation, dry-run planning, and CPU/static
contract validation of the launch helper. It does not authorize Colab
allocation, hosted uploads/execution, compute use, PPO, local GPU/iGPU,
behavior evaluation, R2/R3, runtime work, RDK-X5, robot access, deployment,
torque, or motors. A later explicit user approval must name or unmistakably
approve the single hosted `RESET_EST_LATCH_U05` run before the allocation flag
may be used.
