# ID-13-last suspended x=0.08 readiness

Date: 2026-07-12

Status: `READY_AWAITING_EXPLICIT_X008_APPROVAL`

Read-only live audit:

```text
config:     131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b
policy:     e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
HWI:        f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc
walker:     d81ad59c29e3a24d5c8e278eaf0898b4d3505ad22bb60ee74776537202eb2dfc
diagnostic: 083af9c85b797699ebd44b1b98de29b931cd27e8cbeaf06d10914d2559e5a698
turn_off:   99451bfa66f838e617585be695e03970b789222e00724fadc40f722b5f2c2090
start_paused: true
runtime process: none
/dev/ttyACM0 owner: none
```

The dedicated runner exposes only suspended `x=0.08`, 15 seconds, action scale
0.25, every-tick telemetry, exact hash checks, fresh snapshot validation,
physical-presence and exact-confirmation gates, isolated remote logs, and
independent torque-off cleanup. It contains no grounded continuation.

Candidate 5 already passed suspended x=0 with zero CRC errors and symmetric
motion. Gate 4 remains a distinct motor stage and requires explicit approval.
