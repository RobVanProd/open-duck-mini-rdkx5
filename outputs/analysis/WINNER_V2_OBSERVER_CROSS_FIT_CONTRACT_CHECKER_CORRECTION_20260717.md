# Winner-v2 Observer Cross-Fit Contract Checker Correction

Status: `INVALID_INITIAL_INVOCATION_TEMPFILE_LIFETIME_FIXED`

The first default-off contract invocation launched and completed both requested
CPU evaluator subprocesses but raised `FileNotFoundError` before producing a
contract result. The checker retained a `Path` to the default-off trace, exited
the `TemporaryDirectory` context, and only then attempted to hash that deleted
file.

No formal 32-cell outcome matrix ran and no pass/fail decision artifact was
written. The correction calculates and retains the trace SHA-256 while still
inside the temporary-directory context. No evaluator code, simulator data,
policy, fit, command, reset, tolerance, gate, matrix or authority changes. This
correction is committed before the valid contract rerun.
