# Ground-Up Torso-COM Reset-Estimator GPU Diagnostic Validity Correction Preregistration — 2026-07-15

## Scope

Correct only the two validity predicates that caused the recovered diagnostic
to be labeled invalid. No new Colab session, expansion, tolerance, or policy
work is allowed.

## Frozen checks

1. Hash-lock the raw plan, report, launch record, source archive, hosted source,
   wrapper, and wall-only contract.
2. Extract only the frozen T2 source checkpoint from the archive on CPU and run
   the exact hosted `sha256_directory` function. Require its hash to equal the
   report's `source_directory_sha256`.
3. Require the launch command/status to prove the exact named T4/GPU session,
   and require report devices exactly `['cuda:0']`. This jointly satisfies the
   preregistered CUDA/T4 validity requirement; do not require an implementation-
   specific `CudaDevice` spelling.
4. Require successful report marker/hash recovery, successful stop, wall <=300,
   zero training, exactly three ordered z cells, six finite errors, and every
   expansion check except `step_zero_outputs_exact` true.
5. Apply the original frozen threshold without modification: maximum <=1e-7 is
   `GPU_EQUIVALENCE_PASSES_ORIGINAL_1E7_NOT_REPRODUCED`; maximum >1e-7 is
   `FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7`; any failed validity check is
   `INVALID_OR_STRUCTURAL_GPU_EXPANSION`.

The correction must preserve the launcher's original raw classification and
report the corrected classification separately. A finite exceedance selects
only the already-named action-distribution/ULP sensitivity audit, not tolerance
relaxation or training. No GPU/iGPU, Colab, RDK-X5, runtime, robot, or behavior
evaluation is authorized.
