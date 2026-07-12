# Rustypot transport recovery suspended x=0 attempt 1

Date: 2026-07-12

Status: `REJECT_TRANSPORT_RECOVERY_CANDIDATE_1`

## Scope

- Robot suspended on its stand.
- Frozen rate165 policy, command exactly `x=0.00`, intended duration 15 seconds.
- No nonzero or grounded command and no GPU use.

## Result

The first corrupt response was the already observed ID-13 pattern:

```text
read crc: 180, computed crc: 52 data: [255, 255, 13, 4, 0, 175, 11, 180]
```

Candidate 1 then attempted to reopen the port and received `Device or resource
busy`. The active Python exception traceback still retained the bound PyO3
method and its exclusive serial handle. Because candidate 1 cleared `self.io`
before reopening, subsequent reads failed with `NoneType` errors. The resulting
556 telemetry rows are not a valid control evaluation and must not be treated
as a passing x=0 gate.

The diagnostic's internal torque-off could not use the cleared IO. The runner's
independent `turn_off.py` fallback executed, followed by an additional explicit
torque-off. Post-run checks found no robot runtime and no owner of
`/dev/ttyACM0`.

## Rollback

The exact pre-test files were restored from:

```text
/home/sunrise/duck_backups/20260712T060357Z_rustypot_transport_recovery
```

Restored live hashes:

```text
HWI:        42721154f4d1b435a7d7af8c7d937f3dc4e069079d9c96751e1627348f939768
walker:     fd9991f8136f3ff23bd696f10ea4f2296257a9d827078dc0a728ee3e9dddf91d
diagnostic: d2e8df200fae773ed2c45200da9b67ab1e809db537d5cb93756c73bece1cd33b
```

## Candidate 2 correction

The transport call now occurs in a short-lived helper frame that converts an
exception to inert type/text diagnostics. No exception or traceback survives
to retain the bound serial method when the old IO is released. The CPU test
now models an exclusive device and refuses reopen while the old object exists;
both recovery and clean-path tests pass.
