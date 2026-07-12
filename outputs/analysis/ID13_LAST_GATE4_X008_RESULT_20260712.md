# ID-13-last suspended x=0.08 Gate 4 result

Date: 2026-07-12

Status: `HOLD_TRACKING_CRC_BUS_RESOLVED_VISUAL_CLEAN`

## Scope

- Frozen rate165 candidate SHA256
  `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`.
- Candidate-5 HWI SHA256
  `f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc`.
- Suspended on stand, command exactly `x=0.08`, 15 seconds, action scale 0.25.
- No grounded replay and no GPU use.

## CRC and bus-control result

```text
samples:                    747 / 747
CRC/read errors:            0
transport resets:           0
write errors:               0
control-budget overruns:    0
dt p95 / max:               0.02009 / 0.02029 s
```

The original Gate-4 CRC/bus-control-impact hold is resolved. Compared with the
pre-fix run (25 CRC errors, 3.35%, with correlated tracking spikes), the matched
candidate-5 validation had no bus event or timing impact.

## Independent tracking decision

The unchanged preferred p95 tracking threshold is `<0.05 rad`. Two joints miss:

```text
left hip pitch p95: 0.0513 rad
left knee p95:      0.0572 rad
```

There were 143 post-startup samples/joint events above 0.05 rad, although no
timing or bus event correlated with them. Therefore Gate 4 remains
`HOLD_TRACKING`. Do not weaken the threshold and do not proceed grounded.

## Visual and cleanup

Rob reported the run looked clean. That closes the visual review without
overriding the numeric hold. Torque-off cleanup passed; post-run checks found no
runtime and no owner of `/dev/ttyACM0`.

## Evidence hashes

```text
JSONL:    f03f85182c8830762fc9de4643bd49286eaec7907929acc20a2e439f653f2fc4
terminal: 42f436eb2a54375acda2a1472942afac9c3aeb9ee37f7471e4e09e762fb9447c
analysis: d9be08184d7fda8a850f4fa631250550d2ab9eade1dfb0a5e876527e1ea20315
```

## Objective audit

- Diagnose CRC mechanism: complete; full-14 response order corrupts ID 13 when
  it is followed by ID 14.
- Resolve CRC/control impact: complete; request ID 13 last and restore canonical
  value order, yielding zero errors and zero timing impact at x=0 and x=0.08.
- Preserve rate165 and x=0: complete; hashes unchanged and x=0 passed cleanly.
- Minimum suspended validation: complete; one isolated 15-second x=0.08 run.
- No gate weakening, local GPU, or grounded replay: satisfied.
- Grounded eligibility: not satisfied because the independent tracking gate
  holds; grounded testing remains blocked.
