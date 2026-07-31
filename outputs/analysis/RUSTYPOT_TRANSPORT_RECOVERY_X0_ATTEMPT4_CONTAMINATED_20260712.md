# Rustypot transport recovery suspended x=0 attempt 4 (contaminated)

Date: 2026-07-12

Status: `INVALID_COMBINED_LOG_RERUN_REQUIRED`

Candidate 4's terminal log showed 10 recovered CRC events, no reopen failure,
no `NoneType` cascade, and only one control-budget warning of approximately
3 ms. However, the runner reused an append-mode remote telemetry filename. The
downloaded JSONL contained 2,044 rows from multiple candidates, including the
old candidate-3 98 ms GC pauses. The analyzer's hold cannot be attributed to
candidate 4, so this run is not graded.

The runner now removes only its two designated remote output files before
starting, ensuring the next authorized `x=0.00` run is isolated.
