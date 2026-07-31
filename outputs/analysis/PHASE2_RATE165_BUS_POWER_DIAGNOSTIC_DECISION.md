# Rate165 Bus/Power Diagnostic Decision

Date: 2026-07-12

Status: `LOCALIZED_ID13_SIGNAL_INTEGRITY_SUSPECT; DIAGNOSTIC_NOT_RUN`

## What The Existing Evidence Proves

Across three current hardware captures:

| condition | samples | CRC failures | rate | failed response ID |
|---|---:|---:|---:|---|
| supported home | 205 | 3 | 1.46% | 13 only |
| suspended x=0 | 747 | 7 | 0.94% | 13 only |
| suspended x=0.08 | 747 | 25 | 3.35% | 13 only |

Runtime mapping identifies servo ID 13 as `right_knee`. Every captured corrupt
packet is a plausible ID-13 status response with a bad received checksum. Most
checksum XOR masks are `0x80` or `0xc0`; the nonzero-command run also includes
other high-bit masks. Retries recover, and there are no write failures.

Event-window medians do not support a deterministic speed/phase defect:

```text
x=0.08 right-knee target velocity:
  event ±2 ticks 0.2744 rad/s vs non-event 0.2995 rad/s
x=0.08 phase event counts by quadrant:
  [7, 7, 5, 4]
x=0.08 dt median:
  event 0.02009 s vs non-event 0.02009 s
```

The rate increases with the more aggressive whole-robot motion, but within that
run events are not concentrated at high right-knee target speed or one gait
phase. This supports localized response signal integrity at ID 13 as the
leading hypothesis. It does not yet distinguish servo electronics, connector,
cable/strain, ground/reference, shared power noise, or adapter/bus effects.

No current run captured battery voltage, so voltage sag is untested. Do not
claim a power cause from the existing logs.

## Minimum Next Diagnostic

First, with robot power removed, visually inspect/reseat only as authorized:

```text
right-knee ID-13 servo connector
right-knee cable strain/pinch/motion path
adjacent right-leg bus and power connectors
shared ground/power connector seating
USB/serial adapter connector seating
```

Do not alter offsets, horn position, gains, firmware, servo ID, or EEPROM.

Then, if separately approved, run the torque-disabled polling diagnostic:

```text
runtime/scripts/servo_crc_isolation.py
IDs: 12 right_hip_pitch, 13 right_knee, 14 right_ankle,
     23 left_knee (homologous-servo control)
operations: raw position and velocity reads
rate: 50 cycles/s
duration: 15 s
writes: torque-disable only
position targets: none
policy: none
```

This control distinguishes an ID-13 read-response fault at zero motor load from
a fault that appears only under commanded motion/load. IDs 12 and 14 are
same-leg numeric-neighbor controls, while ID 23 is the homologous left-knee
control. The repository contains no authoritative wiring/daisy-chain diagram,
so numeric adjacency must not be presented as physical bus topology.

## Preregistered Interpretation

- ID 13 red/yellow while IDs 12/14/23 remain green with torque disabled:
  localized servo/connector/cable response path remains primary; correct that
  physical/electrical fault before any policy repeat.
- all control IDs degrade with torque disabled: investigate shared bus adapter,
  cable, ground, termination, baud/signal integrity, and supply before motion.
- all four are green torque-disabled: load-dependent EMI/power/cable-motion
  remains plausible; the next test must add real voltage measurement and a
  bounded non-policy load, under a new motor authorization.

No branch authorizes repeating `x=0.08` immediately. A repeat is justified only
after the supported cause is addressed and the diagnostic returns below the
existing bus thresholds.

## Evidence Artifacts

```text
tools/analyze_servo_crc_localization.py
outputs/analysis/PHASE2_RATE165_SERVO_CRC_LOCALIZATION.md
outputs/analysis/phase2_rate165_servo_crc_localization.json
runtime/scripts/servo_crc_isolation.py
```

The localization analysis was offline and CPU-only. The torque-disabled
diagnostic has not been deployed or run.
