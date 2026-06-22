# Diagnostic Thresholds And Stop/Go Rules

Last updated: 2026-06-22

## Purpose

Define project-specific diagnostic terms and stop/go thresholds so warnings do
not become open-ended blockers.

These thresholds are engineering gates for the Open Duck Mini RDK-X5
sim-to-real bridge. They are not manufacturer acceptance limits.

## Glossary

| term | project meaning |
|---|---|
| CRC/checksum error | A received servo packet failed packet-integrity validation. It means the packet was damaged or could not be trusted; it does not automatically prove the policy observation was corrupted. |
| retry failure | The bus layer retried or reported a read/write failure. Treat this as stronger evidence than one raw terminal CRC line, especially if it changes telemetry counters. |
| bus error rate | `read_error_count / policy_tick_count` or terminal CRC count divided by samples when counters are unavailable. |
| burst | Three or more read/write events inside a short tick window, currently `3` events within `3` ticks in `analyze_suspended_replay.py`. |
| dt jitter | Deviation of the control-loop sample time from the intended `0.02 s` tick. |
| control budget warning | Runtime warning that policy/control work exceeded its allotted per-tick time. |
| tracking error | Absolute difference between commanded/sent joint target and measured actual joint position. |
| action saturation | ONNX action at or near its `tanh` limit, currently treated as `abs(action) >= 0.98` in analyzers. |
| observation outlier | Policy observation dimension several standard deviations outside ONNX normalization expectations, especially IMU accel/gyro or joint feedback at home pose. |
| startup transient | Initial ticks after starting a test where one-time settling can be reviewed as warning-only if it does not persist. Suspended replay uses `25` startup ticks. |
| control damage | Evidence that a warning affected behavior: dt spike, action jump, large tracking spike, write failure, visible twitch, corrupted observation, repeated burst, or exception. |

## Gate Labels

Use these labels for high-level decisions:

| gate | meaning |
|---|---|
| `PASS` | Evidence is clean enough for the next planned gate. |
| `WARN_PROCEED_WITH_CAUTION` | Warning exists, but no control damage is shown; proceed only to the next low-risk planned gate. |
| `HOLD_CONTROL_IMPACT` | A warning correlates with control damage or exceeds red thresholds. Stop and diagnose before the next gate. |
| `HOLD_INSUFFICIENT_CONTEXT` | Required telemetry, terminal logs, labels, or operator observations are missing. Re-run or collect missing evidence. |

Some tools also emit more specific hold labels such as `HOLD_TRACKING`,
`HOLD_IMU`, or `HOLD_ACTION_SATURATION`. Treat these as specific forms of
`HOLD_CONTROL_IMPACT`.

## Suspended Replay Thresholds

These are project thresholds for the current `50 Hz` runtime.

| metric | green | warning / proceed carefully | hold |
|---|---:|---:|---:|
| read CRC/retry errors | `0-0.2%` ticks | `0.2-2%` ticks, isolated, no control damage | `>2%`, bursts, or correlated with control damage |
| write errors | `0` | one isolated event, review carefully | repeated write error or write error with motion issue |
| dt at 50 Hz | p99 `<0.022 s`, max `<0.030 s` | one isolated `0.030-0.050 s` tick | repeated `>0.030 s` or any `>0.050 s` |
| control budget warning | `0` | one isolated warning | repeated warnings |
| action saturation | `0%` | isolated `<1%` on one joint | sustained or multiple joints |
| free-air p95 tracking | `<0.02 rad` | `0.02-0.05 rad` | `>0.05 rad` sustained |
| free-air max tracking | startup-only spike allowed | `<0.15-0.20 rad` if startup-only | steady-state `>0.15 rad` or visible twitch |
| IMU upright accel | +Z dominant | small stable x/y bias | wrong dominant axis or negative Z |
| bus event correlation | none | unclear | within a few ticks of dt/action/tracking damage |

## Current Stop/Go Rule

Do not treat nonzero CRC/read retries as an automatic blocker.

Hold only when read/write warnings correlate with control damage:

- dt spike
- action jump or saturation burst
- post-startup tracking spike
- corrupted or missing observation values
- visible twitch/asymmetry reported by the operator
- repeated burst
- write failure
- runtime exception

If read retries are isolated and timing, action, tracking, and operator
observation remain sane, classify as `WARN_PROCEED_WITH_CAUTION`.

## Evidence Requirements

Suspended replay evidence must include:

- telemetry JSONL
- terminal log
- command vector
- dt summary
- ONNX action saturation
- target and actual joint tracking
- bus counters when available
- terminal warning counts
- operator visual note

If terminal logs are missing, CRC/control warning correlation is incomplete and
the safest result is warning or `HOLD_INSUFFICIENT_CONTEXT`, depending on the
planned next gate.

## Manufacturer Facts vs Project Thresholds

Manufacturer and protocol documents establish facts such as servo feedback
fields, baud rate, packet checksums/CRC, and real-time timing concepts. They do
not provide an Open Duck Mini acceptance threshold such as "1% read retries is
safe." The green/warning/hold thresholds above are project-derived from observed
control impact on this robot.

See [RESEARCH_NOTES.md](RESEARCH_NOTES.md) for source links and citation notes.
