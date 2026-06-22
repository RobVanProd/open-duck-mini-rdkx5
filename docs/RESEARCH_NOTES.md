# Research Notes

Last updated: 2026-06-22

## Scope

These notes support the diagnostic threshold policy. They do not change robot
behavior and do not approve new robot tests.

## Servo Facts

Primary source:

- Waveshare ST3215 Servo wiki: <https://www.waveshare.com/wiki/ST3215_Servo>

Relevant facts recorded from the Waveshare ST3215 documentation:

- 1 Mbps bus servo communication.
- 6-12.6 V input range.
- position sensor resolution `360 deg / 4096`.
- feedback includes position, load, speed, and input voltage.
- published no-load speed is `0.222 s / 60 deg` at `12 V`, about `4.72 rad/s`.
- locked-rotor current is listed around `2.7 A`.

Project interpretation:

- Published no-load speed is a best-case actuator spec. It is not the same as
  loaded multi-joint gait tracking with linkages, reversals, voltage sag, print
  compliance, bus scheduling, and feedback noise.
- The suspended `x=0.08` policy target waveform had pitch-chain target
  velocity in the `3-5 rad/s` range, which is close to the no-load speed range
  for at least some joints. That supports modeling lower effective velocity
  limits in sim/training.

## Packet Integrity

Primary sources:

- ROBOTIS DYNAMIXEL Protocol 2.0: <https://emanual.robotis.com/docs/en/dxl/protocol2/>
- ROBOTIS DYNAMIXEL Protocol 1.0: <https://emanual.robotis.com/docs/en/dxl/protocol1/>

Relevant facts:

- Protocol 2.0 packets include a CRC field used to detect damaged packets.
- Protocol 1.0 status packets include a checksum for packet-damage detection.

Project interpretation:

- ST3215 is not a DYNAMIXEL servo, but the protocol docs are useful as a
  general serial-servo packet-integrity reference.
- A CRC/checksum warning means a packet should not be trusted. It does not by
  itself prove the control tick was damaged, because the runtime may retry or
  hold prior state.
- Read errors are a stronger watch item than isolated terminal text when they
  are counted in synchronized telemetry.

## Real-Time Timing Context

Primary sources:

- Linux Foundation real-time documentation: <https://wiki.linuxfoundation.org/realtime/documentation/start>
- Intel ECI real-time development tutorial: <https://eci.intel.com/docs/3.3/development/performance/rt-dev-tutorial.html>
- Ubuntu real-time kernel tuning article: <https://ubuntu.com/blog/real-time-kernel-tuning>

Relevant facts:

- Real-time systems are judged by whether they respond within a defined time
  frame.
- Jitter measurement is a normal part of evaluating a real-time application.
- Kernel/runtime tuning can improve worst-case scheduling behavior, but it does
  not replace application-level measurement.

Project interpretation:

- The Open Duck runtime control tick is `0.02 s` at `50 Hz`.
- A single isolated slightly long tick is not equivalent to a failed gait.
- Repeated long ticks, or long ticks correlated with bus errors or tracking
  spikes, are control-impact evidence and should hold the next gate.

## No Manufacturer Acceptance Threshold Found

No source found during this audit provided a manufacturer-backed threshold for
acceptable ST3215 read CRC/checksum retry rate on the Open Duck Mini wiring,
RDK-X5 runtime, `rustypot`, and 14-servo gait workload.

Therefore the project threshold policy is based on observed control impact:

```text
warning without control damage -> WARN_PROCEED_WITH_CAUTION
warning with control damage    -> HOLD_CONTROL_IMPACT
missing evidence               -> HOLD_INSUFFICIENT_CONTEXT
```

## Current Project Evidence

Suspended `x=0.0` evidence:

- clean `dt`
- `0%` action saturation
- good free-air p95 tracking
- nonzero read retries
- no post-startup tracking damage

Classification:

```text
WARN_PROCEED_WITH_CAUTION
```

Suspended `x=0.08` evidence:

- coherent air-walking visually
- sustained pitch-chain tracking lag
- p95 pitch tracking roughly `0.12-0.17 rad`
- target velocities in the `3-5 rad/s` range
- bus retries increased

Classification:

```text
HOLD_CONTROL_IMPACT / HOLD_TRACKING
```

The dominant cause is now modeled as actuator dynamic mismatch, not isolated
CRC text.
