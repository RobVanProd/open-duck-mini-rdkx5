# Ground-Up Torso-COM Reset-Estimator GPU Expansion Diagnostic Preregistration — 2026-07-15

## Question and authority

The approved hosted launch stopped before PPO because the T4 checkpoint
expansion reported only `step_zero_outputs_exact` as failed against 1e-7. Its
detailed report was written remotely but was not recovered after the fail-
closed stop, so the six per-z actor/critic errors are unknown.

This diagnostic asks only: what exact values did the frozen T4 expansion gate
measure? It does not retry training, alter the tolerance, or evaluate behavior.
The prior approval is consumed. This preregistration authorizes only a zero-
session local package contract; a new explicit approval is required before the
diagnostic allocation.

## Frozen hosted diagnostic

- One fresh named T4 session, one diagnostic process, no retry/resume/reuse.
- Total session wall <=300 seconds and projected compute <=0.25 units.
- Use the same live same-session Resources-UI rate/balance handshake before
  upload; wait <=60 seconds. A rate above 3.0/hour fails the .25-unit cap.
- Upload the exact prior 19 assets, the hash-locked hosted training source, and
  one diagnostic wrapper.
- The wrapper imports the frozen hosted module, wraps only `hosted_expand`,
  runs the module's unchanged setup/restore/expansion path, reads the report
  immediately whether the expansion returns or raises, emits exactly one
  machine-readable report marker, and terminates successfully before
  `training_command` or any runner/PPO process.
- Recover the report JSON locally before named-session cleanup. Pass requires
  successful recovery, hash agreement with the marker, successful stop, and
  total wall <=300 seconds.
- Record versions/devices, source and expanded directory hashes, every check,
  all three z cells, actor/critic errors, inserted rows, normalizer values,
  preserved/save errors, and reference-tail identity exactly as reported.

No package, dependency, patch order, checkpoint, observation, actor, critic,
normalizer, z set, dtype, or 1e-7 threshold may change.

## Zero-session package contract

Before allocation, a CPU-only contract must prove exact upstream hashes,
wrapper monkeypatch scope, report-before-raise behavior on deterministic pass
and fail fixtures, forced termination before training, exact 21-file upload
set, 300-second/.25-unit/60-second handshake limits, atomic recovery, named
cleanup, no retry surface, and unchanged session inventory with zero remote
bytes or PPO steps.

## Frozen result classes

The diagnostic is valid only if CUDA/T4 is proven, the exact source checkpoint
and expanded hashes are present, all three z cells and both error fields are
finite, and every expansion check other than `step_zero_outputs_exact` passes.

1. If maximum error <=1e-7, report
   `GPU_EQUIVALENCE_PASSES_ORIGINAL_1E7_NOT_REPRODUCED`. The prior failure is
   not reproduced; no training is selected. Only a separately preregistered
   replication/method-stability study may follow.
2. If maximum error >1e-7 with every other check passing, report
   `FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7`. This selects only a separate
   action-distribution/ULP sensitivity audit using the measured magnitude. It
   does not authorize relaxing 1e-7 or training.
3. If any structural check, finiteness, hash, device, recovery, cleanup, or
   wall/CU condition fails, report `INVALID_OR_STRUCTURAL_GPU_EXPANSION` and
   close this diagnostic without selecting the closest result.

Training reward is never used. No policy promotion, behavior evaluation,
local GPU/iGPU, RDK-X5, runtime, or robot action is authorized.
