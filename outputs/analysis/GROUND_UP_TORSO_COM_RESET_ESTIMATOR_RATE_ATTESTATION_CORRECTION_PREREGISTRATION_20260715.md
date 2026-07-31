# Ground-Up Torso-COM Reset-Estimator Rate-Attestation Launch Correction Preregistration — 2026-07-15

## Authority and causal evidence

This document freezes one launch-method correction after the single approved
`RESET_EST_LATCH_U05` launch stopped at
`STOP_NO_RETRY_STATUS_RATE_UNAVAILABLE`. It does not retry that launch and does
not authorize a new Colab allocation.

The failure is localized before implementation:

- Colab CLI is exactly 0.6.0.
- Installed `colab_cli/commands/session.py` has SHA-256
  `59d50c3fe04bfcd1eaa7e2441e79d5e2bed2d0201c469c37e5e614351bbe0c1c`.
- Its `sessions_command()` prints assignment identity only, and its `status()`
  prints session identity, accelerator, variant, and idle/busy state only.
  Neither implementation reads or prints compute balance or usage rate.
- The real launch record confirms the session-specific status response was
  `[open-duck-reset-estimator-t4] ... | Hardware: T4 | Variant: GPU | Status: IDLE`
  with no rate field.
- The previous zero-session contract exercised `parse_rate()` only on a
  synthetic string. That proved parser arithmetic, not availability of the
  field from the frozen CLI command.
- Google's Colab FAQ states that resource availability and usage limits may
  change over time; therefore no hard-coded T4 rate is substituted.
  Source: <https://research.google.com/colaboratory/faq.html>.

The causal decision is
`REPLACE_NONEXISTENT_CLI_RATE_WITH_FRESH_OPERATOR_ATTESTATION`. No training,
policy, reward, seed, architecture, checkpoint, asset, command, horizon, or
behavior-evaluation variable is changed.

## Frozen executable correction

The launch helper must make exactly these interface changes:

1. Require `--compute-rate-per-hour`, `--available-compute-units`, and
   `--rate-observed-at` for every dry run or allocation request.
2. Treat those values as an operator transcription from Colab's Resources UI,
   not as CLI-derived or estimated data. Store the exact values and source
   label `COLAB_RESOURCES_UI_OPERATOR_ATTESTATION` in the plan and launch
   record.
3. Parse `--rate-observed-at` as timezone-aware ISO 8601. At launcher start it
   must be no more than 600 seconds old and no more than 60 seconds in the
   future.
4. Require finite `compute_rate_per_hour > 0`, finite
   `available_compute_units >= 2.0`, and calculate
   `projected_max_compute_units = compute_rate_per_hour * 2400 / 3600`.
5. Fail before `session_created = True` and before `colab new` unless the
   projected value is at most 2.0 units. Equality at 2.0 passes.
6. Keep the post-allocation named `colab status` command, but validate only the
   exact named session, `Hardware: T4`, `Variant: GPU`, and `Status: IDLE`.
   It must not be parsed for a rate.
7. Keep every prior cleanup, stop reserve, total-wall, upload, execution,
   recovery, no-resume, and no-retry invariant unchanged.

The correction must not scrape a private endpoint, infer a rate from hardware,
reuse the earlier 1.07 observation as if current, or silently default any
attestation field.

## Frozen zero-allocation contract

Before any further allocation, a CPU-only contract must establish all of the
following with `colab sessions` unchanged before and after:

- the prior failed-launch result and raw launch record hashes are exact;
- the installed CLI version and session-source hash above are exact;
- static source order proves attestation validation completes before
  `session_created = True` and `colab new`;
- the plan contains the exact attested rate, balance, timestamp, source label,
  projected units, and 600/60-second freshness limits;
- rate 1.07 projects to 0.7133333333333334 units and passes with balance 91.29;
- rate 3.0 projects to exactly 2.0 units and passes;
- rate 3.000001 fails;
- balance 1.999999 fails;
- observations 600 seconds old and 60 seconds future pass at the boundary;
- observations older than 600 seconds or more than 60 seconds future fail;
- missing, nonfinite, zero, negative, or timezone-naive values fail;
- real captured session-status text from the failed launch passes T4 identity
  validation despite containing no rate, while wrong session/hardware/variant/
  state fails;
- dry-run staging still validates exactly 19 hash-locked assets and creates no
  session, upload, training process, or PPO step;
- no training job, asset, checkpoint, or package hash changes.

The contract may use fixed timestamps for deterministic boundary tests. It may
not allocate a session to obtain an outcome.

## Decision rule and next boundary

If every frozen check passes, report
`PASS_RESET_COM_ESTIMATOR_RATE_ATTESTATION_LAUNCH_CORRECTION_CONTRACT`. That
authorizes only asking the operator for a fresh Resources-UI rate, available
balance, observation timestamp, and new explicit approval for one corrected
launch. It does not itself authorize allocation.

If any check fails, report
`FAIL_RESET_COM_ESTIMATOR_RATE_ATTESTATION_LAUNCH_CORRECTION_CONTRACT` and stop.
Do not weaken the 2.0-CU ceiling, freshness limits, T4 identity gate, cleanup,
or no-retry rule after observing a failure.

No behavior result or robot clearance can follow from this methods contract.
Local GPU/iGPU, RDK-X5, runtime, and robot access remain prohibited.
