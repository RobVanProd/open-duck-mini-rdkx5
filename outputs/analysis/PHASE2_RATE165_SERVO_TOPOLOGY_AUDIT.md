# Rate165 Servo Topology Audit

Date: 2026-07-12

Status: `NO_AUTHORITATIVE_PHYSICAL_BUS_TOPOLOGY_FOUND`

The repository proves the runtime ID mapping:

```text
12 right_hip_pitch
13 right_knee
14 right_ankle
23 left_knee
```

It does not contain an authoritative wiring schematic, connector map, cable
route, or daisy-chain order tying those numeric IDs to physical upstream and
downstream positions. CAD/MJCF structure proves mechanical hierarchy only and
must not be used as electrical topology evidence.

Diagnostic control selection is therefore:

- ID 13: localized suspect;
- IDs 12 and 14: same-leg numeric-neighbor controls, without topology claims;
- ID 23: homologous left-knee servo control.

The power-off inspection must follow the actual visible right-knee cable and
connectors on the robot rather than assuming ID order. Any discovered physical
chain order should be photographed or written into a new wiring artifact before
it is used for causal interpretation.

No robot connection, motor action, or GPU workload occurred in this audit.
