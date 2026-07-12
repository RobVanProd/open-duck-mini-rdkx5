# Left pitch-chain gain tracking preregistration

Date: 2026-07-12

Status: `OFFLINE_READY_AWAITING_X0_APPROVAL`

## Measurement interpretation

```text
0.0513 rad = 2.939 deg
0.0572 rad = 3.278 deg
0.0500 rad = 2.865 deg
left hip miss = 0.0013 rad = 0.075 deg
left knee miss = 0.0072 rad = 0.413 deg
```

The x=0.08 signed means are near zero (`+0.00060 rad` hip and `-0.00354 rad`
knee), and errors change sign with phase. Large errors occur at higher target
rates. Alignment/offset error is rejected; the supported mechanism is dynamic
lag of roughly three 50 Hz ticks.

A saved-trace target-slew counterfactual was rejected as the first intervention:
the knee would require roughly a 1.2 rad/s cap, changing its target by as much
as 4.4 degrees and affecting about 14% of samples merely to approach the gate.

## Frozen one-factor intervention

The walker, not the HWI default, sets normal body P gain to 30 at startup. Freeze:

```text
left_hip_pitch P: 30 -> 31
left_knee P:      30 -> 34
all other P:      unchanged
all D:            unchanged at 0
```

The values are derived from the measured p95 ratios rather than a sweep:
`30 * 0.0513 / 0.0500 = 30.78` and
`30 * 0.0572 / 0.0500 = 34.32`, rounded to integer servo coefficients.

Frozen unchanged variables: rate165 policy and hash, command, action scale,
offsets, phase timing, max runtime velocity, ID-13-last read order, baud rate,
EEPROM, and all other gains.

## Staged gates

1. Suspended x=0, 15 seconds. Require zero CRC/write/control errors, unchanged
   timing, tracking p95 below 0.05 rad, and symmetric visual motion. Abort on
   jerk, oscillation, asymmetry, or operator concern.
2. Only after x=0 passes, obtain separate suspended x=0.08 approval. Require
   both left hip pitch and left knee p95 strictly below 0.05 rad under the
   unchanged analyzer; no visual result overrides a numeric miss.
3. Restore normal RAM gains (body 30, head 8, D 0) and disable torque after
   every attempt, including aborts. No EEPROM write occurs.

No grounded movement is authorized by this experiment.

## Runner readiness

`scripts/collect_left_pitch_gain_x0.sh` is syntax-checked and refusal-tested. It
is fixed to x=0, 15 seconds, gains 31/34, exact artifact hashes, isolated logs,
physical-presence and exact-confirmation gates. Its cleanup restores normal RAM
gains and disables torque on success, abort, or failure. The runner has no
x=0.08 or grounded command path and has not been deployed or run.
