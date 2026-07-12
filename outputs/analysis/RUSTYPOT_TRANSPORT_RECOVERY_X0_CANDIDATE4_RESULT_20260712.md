# Rustypot transport recovery candidate 4 — suspended x=0 result

Date: 2026-07-12

Status: `NUMERIC_PASS_WITH_CRC_WARNING_VISUAL_PENDING`

## Contract

- Robot suspended on stand.
- Frozen rate165 policy SHA256 `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`.
- Command exactly `x=0.00`, 15 seconds, action scale 0.25.
- No nonzero/grounded command and no GPU use.

## Isolated result

```text
samples:                         747
read CRC/retry events:           14 (1.87%, warning)
transport resets:                14
write errors:                    0
control-budget overruns:         0
dt p95 / max:                    0.02009 / 0.02015 s
dt > 0.030 s:                    0
tracking spikes > 0.05 rad:      0
action saturation:               0%
cleanup:                         passed
post-run runtime/port owner:     none / none
```

Maximum joint tracking error was below 0.03 rad. Candidate 4 therefore solves
the control-impact failure of candidates 1–3: every detected CRC exception was
recovered on a fresh serial handle without a measurable control-loop overrun.

This does not remove the physical/protocol corruption itself. Every printed
corrupt response remains ID 13 and the 1.87% rate remains a warning. Treat
transport recovery and underlying signal integrity as two separate problems.

## Implementation conclusion

The efficient compatibility-preserving implementation is:

1. pass an operation name into `_retry`, never a bound PyO3 method;
2. isolate the bus call so no exception traceback retains the handle;
3. clear the internal bound method;
4. release the old IO through normal CPython reference counting;
5. reopen the same path at 1,000,000 baud and retry;
6. record `transport_reset_count` in telemetry.

No full garbage collection, library upgrade, gain/offset change, or additional
bus transaction is used on the clean path.

Raw evidence remains outside Git by default at:

```text
outputs/first_evidence/20260712T061250Z_rustypot_recovery4_clean_gate3_x0/
```
