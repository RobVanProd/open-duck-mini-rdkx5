# Winner-v2 Observer Cross-Fit Contract Reporting Correction

Status: `INVALID_SECOND_INVOCATION_ENABLED_REPORTING_FIXED`

The second contract invocation again produced no contract result. Both CPU
subprocesses completed, and the enabled JSONL trace contained the separately
recorded observer target, but `evaluate_ground_up_policy.py` did not propagate
the closed-loop runner's `policy_observer_fit_enabled` field into its per-run
report. The checker therefore raised `KeyError` before evaluating its checks.

The correction adds the observer-enabled flag, fit path and SHA-256 to enabled
run and input reporting only. When the feature is default-off, no keys are
added, preserving the already-proven byte-identical trace and canonical result.
No simulator behavior, matrix, policy, fit, command, threshold, selection rule
or authority changes. This correction is committed before the valid rerun.
