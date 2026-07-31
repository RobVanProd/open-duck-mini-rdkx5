# Rustypot transport recovery suspended x=0 attempt 3

Date: 2026-07-12

Status: `HOLD_TRANSPORT_RECOVERY_LATENCY`

Candidate 3 resolved the exclusive-handle failure. During the 15-second
suspended `x=0.00` run it recovered all 11 ID-13 CRC errors with:

- no `Device or resource busy` error;
- no `NoneType` cascade;
- zero write errors;
- zero tracking spikes above 0.05 rad;
- maximum tracking error below 0.03 rad;
- normal torque-off cleanup.

The run nevertheless holds because every recovery produced a control-loop
pause near 98 ms. There were 11 `dt > 0.05 s` and 11 control-budget warnings,
exactly correlated with the 11 recovered errors. The explicit `gc.collect()`
in candidate 3 is the dominant cost; a no-bus-IO probe measured actual serial
close/reopen at approximately 0.35 ms with no delay.

Candidate 4 removes full cyclic collection. Because operations are now passed
by name rather than as externally retained bound methods, normal CPython
reference counting releases the PyO3 serial object before reopen.
