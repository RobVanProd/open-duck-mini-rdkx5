# Servo CRC torque-disabled synchronous-read ordering result

Date: 2026-07-12

Status: `PASS_TORQUE_OFF_ORDERING_REJECT_STATIC_COLLISION`

## Safety contract

- Torque disabled before and after collection.
- No position target, torque enable, policy, mode, or EEPROM operation.
- No runtime or serial-port owner after cleanup.

## Result

| order | IDs | sync reads | errors | resets | max call |
|---|---|---:|---:|---:|---:|
| canonical | 12, 13, 14 | 1,490 | 0 | 0 | 1.340 ms |
| ID 13 last | 12, 14, 13 | 1,490 | 0 | 0 | 1.027 ms |
| four-servo control | 12, 13, 14, 23 | 1,490 | 0 | 0 | 1.121 ms |

All 4,470 synchronous position/velocity read operations completed without a
checksum error. Reordering ID 13 had no observable effect because the canonical
order was already clean under torque-disabled conditions.

## Decision

A simple static ID-13/ID-14 response-order collision is not supported. Do not
write the STS3215 return-delay EEPROM register from this evidence.

The fault is conditional on a difference between this test and control runs:

1. torque/current and associated supply/ground noise;
2. full 14-servo response density rather than the tested 3/4-servo groups;
3. powered control state or temperature.

The next efficient discriminator is a matched matrix that separates full-bus
density from torque/load, with simultaneous servo-rail voltage capture if the
hardware exposes it. Do not infer ID-13 mechanical failure.

Evidence hashes:

```text
JSON:     5de6470f1c835d8cbd4f13bd4715c6150d479853ff5cf87db87cb76dc80fc4a3
terminal: e768a2414cea4f2e01ef841cd5c8d8f870021b2666c08f54995d1778dc73625e
```
