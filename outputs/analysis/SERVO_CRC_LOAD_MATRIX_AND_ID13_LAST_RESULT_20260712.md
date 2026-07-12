# Servo CRC load matrix and ID-13-last result

Date: 2026-07-12

Status: `PASS_ID13_LAST_RUNTIME_FIX_X0_VISUAL_PENDING`

## Causal matrix

| phase | order/group | sync reads | CRC errors | resets |
|---|---|---:|---:|---:|
| torque disabled | 12,13,14 | 1,490 | 0 | 0 |
| torque disabled | 12,14,13 | 1,490 | 0 | 0 |
| torque disabled | 12,13,14,23 | 1,490 | 0 | 0 |
| torque disabled | full 14 canonical | 1,490 | 13 | 13 |
| static-home torque enabled | full 14 canonical | 1,490 | 8 | 8 |
| torque disabled replication | full 14 canonical | 1,490 | 10 | 10 |
| torque disabled matched test | full 14, ID 13 last | 1,490 | 0 | 0 |

The small groups were clean regardless of order. Full-bus canonical order was
bad both torque-disabled and static-home torque-enabled, while the matched
full-bus ID-13-last order was clean. Torque/current is not required. Full-bus
response density plus response order is sufficient and reproducible.

## Runtime fix

Only the synchronous read order changes: ID 13 is requested last. Returned
position and velocity values are mapped by servo ID back into the original
canonical 14-joint order before observations or telemetry use them. Write order,
policy, gains, offsets, action scale, baud rate, and EEPROM remain unchanged.

An offline test proves both position and velocity mapping preserve canonical
joint order while ID 13 is last on the bus.

## Suspended x=0 validation

```text
samples:                     747 / 747
CRC/read errors:             0
transport resets:            0
write errors:                0
control-budget overruns:     0
dt p95 / max:                0.02009 / 0.02066 s
tracking spikes >0.05 rad:   0
numeric gate:                PASS_X0
cleanup:                     passed
```

This is the first completely green live bus result in the current sequence.
Visual symmetry confirmation remains required to close the full gate.

Evidence hashes:

```text
load-matrix JSON:       7de1d7966dd7a1fa11c9162c7a02bb6bf094864f2579b2ae0f86ed12154fd696
load-matrix terminal:   58fbfbfb071bc79535b1e1cee40a54520edf630bb9c10b3530ebe893d2b88f34
full-order JSON:        029f2277251e807d577913edfb56f0191037274a7dc8563fe9cf43ea5f5333e6
full-order terminal:    9572b950497735318284df57bb475398e5f34ed174db20a99c9346e15d7b978a
```
