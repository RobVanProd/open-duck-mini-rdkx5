# Rustypot transport recovery suspended x=0 attempt 2

Date: 2026-07-12

Status: `REJECT_TRANSPORT_RECOVERY_CANDIDATE_2`

Candidate 2 reproduced candidate 1's failure at the first ID-13 corrupt packet:

```text
read crc: 178, computed crc: 50 data: [255, 255, 13, 4, 0, 177, 11, 178]
Device or resource busy
```

Although the exception was converted in a helper frame, the caller still passed
the bound PyO3 method into `_retry`; that external reference retained the old
exclusive serial handle. Subsequent `NoneType` rows are invalid evidence and
the run is rejected. Independent and explicit torque-off cleanup passed, no
runtime or port owner remained, and the exact pre-test hashes were restored.

A host-only probe opened and destroyed Rustypot IO objects without issuing any
bus operation. Reopen passed with delays of 0, 3, 10, 30, and 100 ms; zero-delay
reopen took about 0.35 ms. USB/driver release latency is therefore rejected.

Candidate 3 passes an operation-name string into `_retry`, resolves the bound
method only inside `_retry`, clears it before dropping `self.io`, and preserves
the exclusive-open regression test.
