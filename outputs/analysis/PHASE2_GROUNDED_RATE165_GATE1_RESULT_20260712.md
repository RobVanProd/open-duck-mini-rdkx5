# Grounded Rate165 Gate-1 Result

Date: 2026-07-12

Status: `PASS_GATE1_WITH_RECOVERED_READ_RETRY_WARNING`

Scope: supported runtime home pose only. No policy replay, candidate staging,
walking command, grounded load, gain change, offset change, or configuration
write occurred.

## Operator Evidence

After the robot reached home on its stand, Rob reported:

```text
visually looks really good
```

This satisfies the required operator visual component for current bilateral
hip/knee/ankle/foot geometry. It is recorded together with, not replaced by,
the numeric telemetry component.

## Telemetry Result

```text
samples: 205
post-startup samples: 180
gyro absolute p95 max: 0.0055 rad/s
accel mean: [1.6678, 0.3582, 9.6821] m/s^2
write errors: 0
tracking holds: 0
```

Pitch-chain post-startup tracking p95:

| joint | p95 abs rad | consecutive samples >0.10 rad |
|---|---:|---:|
| left hip pitch | 0.0010 | 0 |
| left knee | 0.0000 | 0 |
| left ankle | 0.0010 | 0 |
| right hip pitch | 0.0030 | 0 |
| right knee | 0.0030 | 0 |
| right ankle | 0.0050 | 0 |

All are far inside the acceptable `<0.08 rad` p95 gate, with no sustained
post-startup error above `0.10 rad`.

## Read-Retry Warning

Three CRC/read retries occurred at ticks 35, 94, and 125:

```text
read retry rate: 3 / 205 = 1.46%
write errors: 0
tracking correlation: none
control-budget errors: 0
exceptions: 0
```

The original stationary analyzer treated any nonzero final read counter as a
hold. That contradicted the repository's established rule: recovered read
retries are warnings unless they exceed the red rate or correlate with control
damage. The analyzer now holds above 2% and reports lower recovered rates as a
warning. The observed 1.46% therefore yields
`PASS_TELEMETRY_COMPONENT_WITH_WARNINGS`, not a clean pass and not a hold.

## Torque Cleanup

The first runner version omitted `--torque-off-on-exit`, so the diagnostic
likely left the servos holding home. A torque-disable-only cleanup was issued.
The first cleanup attempt failed at import before hardware access; the corrected
command returned:

```text
TORQUE_OFF_CLEANUP_COMPLETE
```

The runner now always supplies `--torque-off-on-exit` for future Gate-1 runs.

## Clock Verification

The board initially booted at year 2000, then synchronized without a manual
clock write. A fresh read-only snapshot proved:

```text
remote UTC: 2026-07-12T05:11:38.049613+00:00
trusted collector UTC: 2026-07-12T05:11:37.388077+00:00
offset: +0.662 s
remote_clock_plausible: true
System clock synchronized: yes
```

No manual time or timezone change was needed. The board display timezone is
Asia/Shanghai, while all evidence timestamps use UTC.

```text
clock-verified snapshot:
  outputs/first_evidence/20260712T051137Z_gate0_clock_verified/
    20260712T051138Z_rdkx5_config_snapshot.json
SHA256:
  4f663e1fa717c8476f58568b622c6abcf05d416f2a8bea0d4c972ff3bd6f0f1d
```

## Artifact Hashes

```text
raw telemetry (kept outside Git by default):
  ce12e48d6cdda85e0b6ea21197ba9d65a28eeb950971df0c07464ecb3121a50d
terminal log (kept outside Git by default):
  8b13f79ce84fe1b27dea02b35be07daa9f895822f9f7d9229270fdbbfbc10188
analyzer JSON:
  6af15bf92040d4d06a968cc2ab7f41782021143d230adc867780edf1c4fb3910
analyzer Markdown:
  3c27abc7e02d8c6bdc8360d26a6cf6dbdb91db1ade0c40c38173ada42722023d
```

## Decision

Gate 1 passes with a retained recovered-read-retry warning. Stop here under the
current authorization. Gate 2 is paused candidate staging and requires a new,
explicit approval. Gate 3 suspended `x=0` remains blocked until Gate 2 evidence
is reviewed.
